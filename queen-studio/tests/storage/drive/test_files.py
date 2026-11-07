"""The Drive adapter's file operations, on the fake API: each one's calls counted exactly against
the m534 spec's table (step 4's), the places' folders, the repeats, the races and the bounds."""

import hashlib
import threading
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

from core.storage.drive.api import DriveApi
from core.storage.drive.limits import Limits
from core.storage.port import (
    InExport,
    InProject,
    NotFound,
    Rejected,
    Space,
    Stored,
    Taken,
    TooLarge,
)
from tests.storage.contract import change, create, entry, load, new_id, written
from tests.storage.drive.fake import Before, FakeFile
from tests.storage.drive.test_adapter import SMALL, World, records

# Past four bytes a file goes in chunks of four.
CHUNKED = Limits(simple_most=4, chunk=4)
# A large put looks at its ref first: Drive's 409 would come only with its last chunk (534).
UPLOAD = ["get", "upload_start", "upload_chunk", "upload_chunk", "upload_chunk"]


@pytest.fixture
def world(tmp_path: Path) -> Iterator[World]:
    made = World(tmp_path)
    yield made
    made.close()


@pytest.fixture
def paged(tmp_path: Path) -> Iterator[World]:
    made = World(tmp_path, page_size=2)
    yield made
    made.close()


def md5(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


class Project:
    """A project on one port, and files to put into it."""

    def __init__(self, world: World, limits: Limits | None = None) -> None:
        self.world = world
        self.port = world.open(limits)
        self.id, self.version = create(self.port)
        self.place = InProject(self.id)
        self.count = 0

    def put(self, content: bytes = b"photo", name: str = "17.png") -> Stored:
        (ref,) = self.port.reserve(1)
        return self.port.put(ref, self.source(content), name, self.place)

    def source(self, content: bytes) -> Path:
        self.count += 1
        return written(self.world.tmp_path, f"source-{self.count}", content)

    def media(self) -> FakeFile:
        (found,) = [
            file
            for file in self.world.drive.files.values()
            if file.name == "media" and not file.trashed
        ]
        return found


def parents(world: World, stored: Stored) -> list[str]:
    return world.drive.files[stored.ref].parents


# -- what each operation costs -------------------------------------------------------------------


def test_a_put_into_a_known_place_is_one_create(world: World) -> None:
    project = Project(world)
    project.put()
    world.watch()

    stored = project.put(b"second")

    assert world.made() == ["create"]
    assert stored == Stored(stored.ref, 6, md5(b"second"))
    assert world.drive.files[stored.ref].mime == "image/png"


def test_a_large_put_is_a_session_and_its_chunks(world: World) -> None:
    # Step 4's video: "resumable 1+2 parça"; here ten bytes in chunks of four.
    project = Project(world, CHUNKED)
    project.put(b"01")
    world.watch()

    stored = project.put(b"0123456789", "233.mp4")

    assert world.made() == UPLOAD
    assert stored == Stored(stored.ref, 10, md5(b"0123456789"))


def test_a_projects_first_file_opens_its_folder_and_media_there(world: World) -> None:
    # No seal yet, so no <p>/: the first file opens it at the id its head names.
    project = Project(world)
    world.watch()

    stored = project.put()

    assert world.made() == ["children", "create", "children", "create", "children", "create"]
    folder = world.head(project.id).properties["folder"]
    assert world.drive.files[folder].name == project.id
    assert project.media().parents == [folder]
    assert parents(world, stored) == [project.media().id]


def test_the_first_seal_goes_on_in_the_folder_the_first_file_opened(world: World) -> None:
    project = Project(world, SMALL)
    stored = project.put()
    folder = world.head(project.id).properties["folder"]

    version = project.port.commit(
        project.id, project.version, change(entry(2), records=records(1, 3))
    )

    assert world.head(project.id).properties["folder"] == folder
    # Three records seal; two history entries do not.
    assert {f.name for f in world.drive.live(folder)} == {"media", "records-1.jsonl.gz"}
    project.port.commit(project.id, version, change(entry(3)))
    assert world.drive.files[stored.ref].parents == [project.media().id]


def test_the_sweep_never_touches_media(world: World) -> None:
    # The sweep lists <p>/ for blocks no head names (532): media/ is a folder, out of it.
    project = Project(world, SMALL)
    stored = project.put()
    version = project.version
    for seq in range(2, 5):
        version = project.port.commit(
            project.id, version, change(entry(seq), records=records(seq * 10, 3))
        )
    world.clock.sleep(3 * SMALL.retire_after)

    project.port.commit(project.id, version, change(entry(5), records=records(50, 3)))

    assert not world.drive.files[stored.ref].trashed
    assert not project.media().trashed


def test_another_core_finds_media_by_its_name_once(world: World) -> None:
    project = Project(world)
    project.put()
    other = world.open()
    (one, two) = other.reserve(2)
    world.watch()

    for ref in (one, two):
        other.put(ref, project.source(b"x"), "17.png", project.place)

    assert world.made() == ["children", "create", "create"]


def test_a_project_the_port_does_not_know_is_looked_up_by_name_first(world: World) -> None:
    project = Project(world)
    project.put()
    later = world.open()
    unknown, _ = create(project.port)  # after `later` listed projects/
    (ref,) = later.reserve(1)
    world.watch()

    later.put(ref, project.source(b"x"), "17.png", InProject(unknown))

    assert world.made()[:2] == ["children", "children"]  # its head by name, then <p>/'s media


def test_two_cores_making_media_at_once_meet_in_the_oldest(world: World) -> None:
    project = Project(world)
    other = world.open()
    (theirs,) = other.reserve(1)
    put: list[Stored] = []

    def other_core_first() -> None:
        put.append(other.put(theirs, project.source(b"b"), "18.png", project.place))

    # The hook runs as the first core makes media/: the second core has made its own by then.
    world.drive.inject(
        "create", Before(lambda: world.drive.inject("create", Before(other_core_first)))
    )

    ours = project.put(b"a")

    medias = [f for f in world.drive.files.values() if f.name == "media"]
    assert len(medias) == 2
    oldest = min(medias, key=lambda each: each.order)
    assert parents(world, ours) == parents(world, put[0]) == [oldest.id]


def test_a_folder_id_drive_no_longer_takes_is_replaced_and_named_in_the_properties(
    world: World,
) -> None:
    # Reserved ids may expire (528, 6): <p>/ is made at a new id, and the head's `folder`
    # property alone turns to it; the content, so the version, stays.
    project = Project(world, SMALL)
    reserved = world.head(project.id).properties["folder"]
    world.drive.expire()
    (ref,) = world.drive.generate_ids(1)
    world.watch()

    stored = project.port.put(ref, project.source(b"x"), "17.png", project.place)

    assert world.made() == [
        "children",  # <p>/'s media: 404, no <p>/
        "create",  # <p>/ at the reserved id: refused
        "generate_ids",
        "create",  # <p>/ at a new one
        "get",  # what the head names now
        "update",  # its folder property
        "children",
        "create",  # media/
        "children",
        "create",  # the file
    ]
    folder = world.head(project.id).properties["folder"]
    assert folder != reserved
    assert project.media().parents == [folder]
    assert parents(world, stored) == [project.media().id]
    assert project.port.version(project.id).version == project.version
    # The version given still stands, and the first seal goes on in the new folder.
    project.port.commit(project.id, project.version, change(entry(2), records=records(1, 3)))
    assert world.head(project.id).properties["folder"] == folder
    assert len(load(world.open(SMALL), project.id).records) == 3


def test_a_new_folder_another_core_named_first_is_taken_and_ours_trashed(world: World) -> None:
    project = Project(world)
    other = world.open()  # knows the reserved id from its listing
    world.drive.expire()
    (first, second) = world.drive.generate_ids(2)
    project.port.put(first, project.source(b"a"), "17.png", project.place)
    named = world.head(project.id).properties["folder"]

    stored = other.put(second, project.source(b"b"), "18.png", project.place)

    assert world.head(project.id).properties["folder"] == named
    assert parents(world, stored) == [project.media().id]
    stray = [f for f in world.drive.files.values() if f.name == project.id and f.id != named]
    assert [f.trashed for f in stray] == [True]


def test_exists_is_one_look(world: World) -> None:
    project = Project(world)
    stored = project.put()
    world.watch()

    assert project.port.exists(stored.ref) == stored
    assert world.made() == ["get"]


def test_get_is_one_look_and_one_stream_whatever_its_size(world: World, tmp_path: Path) -> None:
    project = Project(world)
    stored = project.put(b"0123456789abcdef")  # four of the fake's pieces
    world.watch()

    assert project.port.get(stored.ref, tmp_path / "back.png", most=100) == stored
    assert world.made() == ["get", "stream"]


def test_copy_is_one_call_and_its_repeat_two_looks(world: World) -> None:
    project = Project(world)
    stored = project.put()
    (ref,) = project.port.reserve(1)
    world.watch()

    made = project.port.copy(stored.ref, ref, "001.png", project.place)
    assert world.made() == ["copy"]
    world.watch()

    assert project.port.copy(stored.ref, ref, "001.png", project.place) == made
    assert world.made() == ["copy", "get", "get"]
    assert made == Stored(ref, stored.size, stored.md5)


def test_trash_is_one_update(world: World) -> None:
    project = Project(world)
    stored = project.put()
    world.watch()

    project.port.trash(stored.ref)

    assert world.made() == ["update"]
    assert world.drive.files[stored.ref].trashed


def test_the_first_export_finds_or_makes_exports_then_each_is_one_create(world: World) -> None:
    port = world.open()
    (one, two, three) = port.reserve(3)
    world.watch()

    port.export_folder(one, "2026-11-07 09-00 a")
    assert world.made() == ["children", "create", "children", "create"]
    world.watch()
    port.export_folder(two, "2026-11-07 09-00 b")
    assert world.made() == ["create"]
    world.watch()
    port.export_folder(two, "2026-11-07 09-00 b")
    assert world.made() == ["create", "get"]

    other = world.open()
    world.watch()
    other.export_folder(three, "2026-11-07 09-00 c")
    assert world.made() == ["children", "create"]
    (exports,) = [f for f in world.drive.files.values() if f.name == "exports"]
    assert exports.parents == [world.root]


def test_export_names_with_no_exports_folder_is_one_listing_and_makes_none(world: World) -> None:
    port = world.open()
    world.watch()

    assert port.export_names("2026") == ()
    assert world.made() == ["children"]
    assert not [f for f in world.drive.files.values() if f.name == "exports"]


def test_export_names_is_a_listing_a_page_and_refused_past_its_pages(paged: World) -> None:
    world = paged
    port = world.open(Limits(pages=3))
    for ref, number in zip(port.reserve(5), range(5), strict=True):
        port.export_folder(ref, f"2026-11-07 09-00 {number}")
    world.watch()

    assert len(port.export_names("2026")) == 5
    assert world.made() == ["children"] * 3  # 2 + 2 + 1

    with pytest.raises(Rejected, match="pages"):
        world.open(Limits(pages=2)).export_names("2026")


def test_the_prefix_never_reaches_a_query(world: World) -> None:
    # Compared in code: a quote or a backslash in it is only text.
    port = world.open()
    asked: list[str | None] = []
    children = world.drive.children

    def watched(parent: str, fields: str, **given: Any) -> Any:
        asked.append(given.get("name"))
        return children(parent, fields, **given)

    world.drive.children = watched
    (ref,) = port.reserve(1)
    port.export_folder(ref, "it's \\ here")

    assert port.export_names("it's \\") == ("it's \\ here",)
    assert set(asked) <= {"exports", None}


def test_space_is_one_call_and_reads_the_quota(world: World) -> None:
    port = world.open()
    (folder, kept, gone) = port.reserve(3)
    port.export_folder(folder, "2026-11-07 09-00 a")
    port.put(kept, written(world.tmp_path, "a", b"abc"), "a.png", InExport(folder))
    port.put(gone, written(world.tmp_path, "b", b"abcde"), "b.png", InExport(folder))
    port.trash(gone)
    world.drive.quota = 10**6
    world.watch()

    assert port.space() == Space(10**6, 8, 5)
    assert world.made() == ["about"]
    world.drive.quota = None
    assert port.space().quota is None


def test_a_quota_drive_gives_oddly_is_rejected(world: World) -> None:
    port = world.open()
    world.drive.about = lambda fields: {"storageQuota": {"usage": "lots"}}

    with pytest.raises(Rejected, match="quota"):
        port.space()


# -- the repeats ---------------------------------------------------------------------------------


def test_a_put_again_is_one_look_more_and_a_large_one_sends_no_byte(world: World) -> None:
    project = Project(world, CHUNKED)
    for content, again in ((b"0123", ["create", "get"]), (b"0123456789", ["get"])):
        (ref,) = project.port.reserve(1)
        source = project.source(content)
        stored = project.port.put(ref, source, "17.png", project.place)
        world.watch()

        assert project.port.put(ref, source, "17.png", project.place) == stored
        assert world.made() == again


def test_a_large_put_at_a_ref_holding_other_bytes_is_taken_before_any_byte(world: World) -> None:
    project = Project(world, CHUNKED)
    (ref,) = project.port.reserve(1)
    project.port.put(ref, project.source(b"0123456789"), "233.mp4", project.place)
    world.watch()

    with pytest.raises(Taken):
        project.port.put(ref, project.source(b"9876543210"), "233.mp4", project.place)
    assert world.made() == ["get"]


def test_a_large_put_meeting_another_finished_first_is_the_same_file(world: World) -> None:
    # The 409 comes with the last chunk when two uploads of one ref overlap: compared, not lost.
    project = Project(world, CHUNKED)
    project.put(b"01")
    (ref,) = project.port.reserve(1)
    source = project.source(b"0123456789")
    other = world.open(CHUNKED)
    theirs: list[Stored] = []

    def finish_theirs() -> None:
        theirs.append(other.put(ref, source, "233.mp4", project.place))

    # Before our last chunk, the other core's whole upload of the same ref.
    world.drive.inject(
        "upload_chunk",
        Before(lambda: world.drive.inject("upload_chunk", Before(finish_theirs))),
    )

    ours = project.port.put(ref, source, "233.mp4", project.place)

    assert ours == theirs[0] == Stored(ref, 10, md5(b"0123456789"))
    assert [f.id for f in world.drive.files.values() if f.name == "233.mp4"] == [ref]


def test_a_folder_renamed_while_a_commit_is_in_flight_waits_for_it(world: World) -> None:
    # The rename runs under the project's lock: a commit that looked at the old folder writes
    # first, then the rename reads the properties again, and its folder stands.
    project = Project(world)
    world.drive.expire()
    (ref,) = world.drive.generate_ids(1)
    waited: list[bool] = []
    putting = threading.Thread(
        target=lambda: project.port.put(ref, project.source(b"x"), "17.png", project.place)
    )

    def put_meanwhile() -> None:
        putting.start()
        putting.join(timeout=0.2)  # held at the project's lock while the commit writes
        waited.append(putting.is_alive())

    world.drive.inject("update", Before(put_meanwhile), file=world.head(project.id).id)

    project.port.commit(project.id, project.version, change(entry(2)))
    putting.join(timeout=5)

    assert waited == [True]
    folder = world.head(project.id).properties["folder"]
    assert world.drive.files[folder].name == project.id
    assert world.drive.files[ref].parents == [project.media().id]


def test_one_projects_first_file_does_not_wait_for_anothers(world: World) -> None:
    one, two = Project(world), Project(world)
    done: list[Stored] = []
    other = threading.Thread(target=lambda: done.append(two.put()))

    def two_meanwhile() -> None:
        other.start()
        other.join(timeout=5)  # one's media/ is being found: two's needs no lock of one's

    world.drive.inject("children", Before(two_meanwhile))

    one.put()

    assert len(done) == 1


def test_a_put_whose_bytes_drive_holds_otherwise_is_taken(world: World) -> None:
    # The md5 is the bytes sent; Drive's answer only checks it.
    project = Project(world)
    project.put()
    create_file = world.drive.create

    def other_bytes(metadata: dict[str, Any], content: bytes | None, fields: str) -> Any:
        return {**create_file(metadata, content, fields), "md5Checksum": "0" * 32}

    world.drive.create = other_bytes

    with pytest.raises(Taken, match="differs from the bytes sent"):
        project.put()


def test_an_export_folder_at_a_ref_used_elsewhere_is_taken(world: World) -> None:
    port = world.open()
    (folder, photos) = port.reserve(2)
    port.export_folder(folder, "2026-11-07 09-00 a")
    port.export_folder(photos, "photos", inside=folder)

    for name, inside in (("other", folder), ("photos", None)):
        with pytest.raises(Taken):
            port.export_folder(photos, name, inside)


# -- what is refused before Drive is asked -------------------------------------------------------


def test_a_malformed_ref_is_refused_before_drive_is_asked(world: World, tmp_path: Path) -> None:
    project = Project(world)
    stored = project.put()
    source = project.source(b"x")
    bad = "../" + stored.ref
    world.watch()

    asked: list[Callable[[], object]] = [
        lambda: project.port.put(bad, source, "a.png", project.place),
        lambda: project.port.put(stored.ref, source, "a.png", InExport(bad)),
        lambda: project.port.exists(bad),
        lambda: project.port.get(bad, tmp_path / "x", most=10),
        lambda: project.port.copy(bad, stored.ref, "a.png", project.place),
        lambda: project.port.copy(stored.ref, bad, "a.png", project.place),
        lambda: project.port.trash(bad),
        lambda: project.port.export_folder(bad, "a"),
        lambda: project.port.export_folder(stored.ref, "a", inside=bad),
    ]
    for call in asked:
        with pytest.raises(ValueError, match="ref"):
            call()
    assert world.made() == []


def test_a_get_that_would_fill_the_disk_writes_nothing(world: World, tmp_path: Path) -> None:
    project = Project(world, Limits(keep_free=10**18))
    stored = project.put()
    target = tmp_path / "cache"
    target.mkdir()

    with pytest.raises(TooLarge) as large:
        project.port.get(stored.ref, target / "17.png", most=100)

    assert (large.value.size, large.value.most) == (stored.size, 0)
    assert list(target.iterdir()) == []


def test_a_project_never_there_takes_no_file_and_makes_no_folder(world: World) -> None:
    port = world.open()
    (ref,) = port.reserve(1)
    before = set(world.drive.files)

    with pytest.raises(NotFound):
        port.put(ref, written(world.tmp_path, "a", b"x"), "a.png", InProject(new_id()))

    assert set(world.drive.files) == before


def test_drive_api_has_no_way_to_delete_for_good() -> None:
    # The core only trashes (FOUNDATION 1): the trash is an update, and no call deletes.
    calls = {name for name in vars(DriveApi) if not name.startswith("_")}

    assert calls == {
        "get",
        "download",
        "children",
        "create",
        "update",
        "generate_ids",
        "stream",
        "copy",
        "about",
        "upload_start",
        "upload_chunk",
        "upload_status",
    }
