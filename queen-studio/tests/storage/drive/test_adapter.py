"""The Drive adapter's own tests, on the fake API: each operation's calls, counted exactly against
the m532 spec's table (step 4's), the seal, the races, the waits and the bounds."""

import threading
from collections import Counter
from collections.abc import Iterator
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from core.clock.clock import ManualClock
from core.disk.cache import DiskCache
from core.storage.drive.adapter import PROJECTS, DrivePort
from core.storage.drive.api import FOLDER
from core.storage.drive.head import Head, read_head
from core.storage.drive.limits import Limits
from core.storage.port import (
    Exists,
    NotFound,
    Record,
    Rejected,
    Stale,
    Taken,
    Unconfirmed,
    Unreadable,
)
from tests.storage.contract import T0, change, create, entry, load, new_id, opening, row
from tests.storage.drive.fake import Before, Fail, FakeDrive, Hang, Lose

RATE = Fail(403, "userRateLimitExceeded", "User rate limit exceeded.")
# A tail of two records seals: a test reaches the seal in a few changes.
SMALL = Limits(tail_count=2, tail_bytes=10**6, block_full=10**6, block_most=2 * 10**6)


class World:
    """One Drive and its clock; each `open` another core with its own disk."""

    def __init__(self, tmp_path: Path, page_size: int = 1000) -> None:
        self.clock = ManualClock(T0)
        self.drive = FakeDrive(self.clock, page_size)
        self.root = self.drive.folder("root")
        self.tmp_path = tmp_path
        self.ports: list[DrivePort] = []

    def open(self, limits: Limits | None = None) -> DrivePort:
        cache = DiskCache(self.tmp_path / f"core-{len(self.ports)}", most=10**7, keep_free=0)
        port = DrivePort.open(self.drive, self.root, self.clock, cache, limits)
        self.ports.append(port)
        return port

    def close(self) -> None:
        for port in self.ports:
            port.close()

    def watch(self) -> None:
        self.drive.calls.clear()

    def made(self) -> list[str]:
        return list(self.drive.made())

    def head(self, project: str) -> Any:
        return self.drive.named(f"{project}.json.gz")

    def written(self, project: str) -> Head:
        return read_head(self.head(project).content or b"")[0]

    def named(self, project: str) -> set[str]:
        return self.written(project).named()

    def blocks(self, project: str) -> set[str]:
        """The block files in the project's folder, out of the trash."""
        return {file.id for file in self.drive.live(self.drive.named(project).id)}


@pytest.fixture
def world(tmp_path: Path) -> Iterator[World]:
    made = World(tmp_path)
    yield made
    made.close()


@pytest.fixture
def paged(tmp_path: Path) -> Iterator[World]:
    """A Drive that pages its listings two at a time."""
    made = World(tmp_path, page_size=2)
    yield made
    made.close()


def records(start: int, count: int) -> tuple[Record, ...]:
    return tuple(Record("frame", n, {"n": n}) for n in range(start, start + count))


def grow(port: DrivePort, project: str, version: str, seqs: range, per: int = 1) -> str:
    """Commits one entry and `per` records each, from seq `seqs.start`."""
    for seq in seqs:
        version = port.commit(project, version, change(entry(seq), records=records(seq * 10, per)))
    return version


# -- what each operation costs -------------------------------------------------------------------


def test_opening_a_new_root_makes_projects_and_after_that_lists_twice(world: World) -> None:
    # Made, then listed again: two cores opening a new root at once both take the oldest.
    world.open()
    assert world.made() == ["children", "generate_ids", "create", "children", "children"]

    world.watch()
    world.open()
    assert world.made() == ["children", "children"]


def test_the_list_is_one_call_a_page(paged: World) -> None:
    world = paged
    port = world.open()
    made = {create(port)[0] for _ in range(5)}
    world.watch()

    listed = port.projects()

    assert {found.id for found in listed} == made
    assert world.made() == ["children"] * 3


def test_a_list_past_its_pages_is_refused_not_cut(paged: World) -> None:
    port = paged.open(Limits(pages=2))
    for _ in range(5):
        create(port)

    with pytest.raises(Rejected, match="pages"):
        port.projects()


def test_version_is_one_call_known_or_not(world: World) -> None:
    a = world.open()
    known, _ = create(a)
    b = world.open()
    later, _ = create(a)
    world.watch()

    b.version(known)
    b.version(later)

    assert world.made() == ["get", "children"]


def test_create_is_one_call(world: World) -> None:
    port = world.open()
    (ref,) = port.reserve(1)
    world.watch()

    port.create(new_id(), ref, opening())

    assert world.made() == ["create"]


def test_reserve_takes_from_a_pool_drive_fills_a_thousand_at_a_time(world: World) -> None:
    world.open()  # makes projects/, from a pool of its own
    port = world.open()
    world.watch()

    port.reserve(1)
    port.reserve(999)
    port.reserve(1)

    assert world.made() == ["generate_ids", "generate_ids"]


def test_a_change_is_two_calls_however_large_the_project(world: World) -> None:
    # The acceptance's own line: a change is a look and a write, and grows with nothing.
    port = world.open(SMALL)
    small, small_version = create(port)
    large, large_version = create(port)
    large_version = grow(port, large, large_version, range(2, 40), per=3)
    world.watch()

    port.commit(small, small_version, change(entry(2)))
    port.commit(large, large_version, change(entry(40)))

    assert world.made() == ["get", "update", "get", "update"]


def test_loading_is_the_head_and_the_blocks_not_on_disk(world: World) -> None:
    a = world.open(SMALL)
    project, version = create(a)
    grow(a, project, version, range(2, 8))
    head = load(a, project).recent  # its own: every block is on its disk
    assert len(head) == 7
    b = world.open(SMALL)
    world.watch()

    first = load(b, project)

    blocks = len(world.named(project))
    assert blocks >= 2
    assert Counter(world.made()) == Counter({"get": 1, "download": 1 + blocks})
    # Again, nothing changed: one look, and the blocks from its disk.
    world.watch()
    assert load(b, project) == first
    assert world.made() == ["get"]


def test_catching_up_downloads_the_head_alone(world: World) -> None:
    # Closed blocks stay on the disk (m531, Sonraki maddeler için).
    a, b = world.open(), world.open()
    project, version = create(a)
    load(b, project)
    a.commit(project, version, change(entry(2), name="A"))
    world.watch()

    assert load(b, project).row == row("A")
    assert world.made() == ["get", "download"]


def test_history_before_the_tail_reads_its_blocks_once(world: World) -> None:
    a = world.open(SMALL)
    project, version = create(a)
    grow(a, project, version, range(2, 10))
    b = world.open(SMALL)
    world.watch()

    found = b.history(project, 3, 2)

    assert [each.seq for each in found] == [2, 1]
    assert world.made() == ["get", "download", "download"]
    world.watch()
    b.history(project, 3, 2)
    assert world.made() == ["get", "download"]  # the head again: history keeps no base


def test_load_reads_only_the_history_since_the_time_asked(world: World) -> None:
    a = world.open(SMALL)
    project, version = create(a)
    for seq in range(2, 8):
        at = T0 + timedelta(hours=seq)
        version = a.commit(project, version, change(entry(seq, at)))
    b = world.open(SMALL)
    world.watch()

    recent = load(b, project, T0 + timedelta(hours=7)).recent

    assert [each.seq for each in recent] == [7]
    assert world.made() == ["get", "download"]


def test_trashing_a_project_is_its_head_then_its_folder(world: World) -> None:
    a = world.open()
    project, _ = create(a)
    world.watch()

    a.trash_project(project)
    assert world.made() == ["update", "update"]

    b = world.open()
    other, _ = create(a)
    world.watch()
    b.trash_project(other)  # not in b's map: one lookup by name first
    assert world.made() == ["children", "update", "update"]


# -- the seal ------------------------------------------------------------------------------------


def test_the_first_seal_opens_the_folder_then_a_block_then_writes_the_head(world: World) -> None:
    port = world.open(SMALL)
    project, version = create(port)
    version = port.commit(project, version, change(entry(2), records=records(1, 1)))
    world.watch()

    port.commit(project, version, change(entry(3), records=records(2, 2)))

    # The look, the folder, a records and a history block, the head; once it stands, the sweep.
    assert world.made() == ["get", "create", "create", "create", "update", "children"]
    folder = world.drive.named(project)
    assert folder.mime == FOLDER
    assert {file.name for file in world.drive.files.values() if folder.id in file.parents} == {
        "records-1.jsonl.gz",
        "history-1.jsonl.gz",
    }


def test_an_open_block_is_replaced_by_a_new_one_and_retired(world: World) -> None:
    # Never written again in place: two cores sealing at once each write their own file.
    port = world.open(SMALL)
    project, version = create(port)
    version = grow(port, project, version, range(2, 4), per=0)  # the history block opens
    (opened,) = world.named(project)
    world.watch()

    grow(port, project, version, range(4, 7), per=0)

    # Its own block is on its disk: no download; the old one waits, retired.
    assert world.made() == ["get", "update", "get", "update", "get", "create", "update", "children"]
    head = world.written(project)
    assert opened not in head.named()
    assert [each.id for each in head.retired] == [opened]
    assert opened in world.blocks(project)
    assert len(load(world.open(), project).recent) == 6


def test_a_retired_block_goes_to_the_trash_with_a_seal_once_no_core_can_name_it(
    world: World,
) -> None:
    # A commit still in flight may write a head built on an older one, naming the block again:
    # it goes to the trash only retire_after later, never deleted for good (FOUNDATION 1).
    port = world.open(SMALL)
    project, version = create(port)
    version = grow(port, project, version, range(2, 10), per=0)  # sealed at 3, 6 and 9
    retired = [each.id for each in world.written(project).retired]
    assert len(retired) == 2
    assert set(retired) <= world.blocks(project)  # an hour has not passed
    world.clock.sleep(SMALL.retire_after)
    world.watch()

    grow(port, project, version, range(10, 13), per=0)

    # The seal at 12: its block, the head; then the two retired to the trash and the sweep.
    assert world.made()[-6:] == ["get", "create", "update", "update", "update", "children"]
    assert all(world.drive.files[each].trashed for each in retired)
    assert not set(retired) & {each.id for each in world.written(project).retired}
    assert len(load(world.open(), project).recent) == 12


def test_an_open_block_not_on_disk_is_downloaded_to_seal(world: World) -> None:
    port = world.open(SMALL)
    project, version = create(port)
    grow(port, project, version, range(2, 4), per=0)
    other = world.open(SMALL)
    # Loaded for the last day only: its history block is not on its disk.
    seen = load(other, project, T0 + timedelta(days=1))
    world.watch()

    other.commit(project, seen.version, change(entry(4), entry(5), entry(6)))

    # A new core's pool is empty: the fresh block's id takes one generateIds.
    assert world.made() == ["download", "generate_ids", "get", "create", "update", "children"]


def test_a_full_block_closes_and_the_next_is_new(world: World) -> None:
    port = world.open(Limits(tail_count=1, tail_bytes=10**6, block_full=100, block_most=10**6))
    project, version = create(port)

    grow(port, project, version, range(2, 6), per=2)

    assert len(world.written(project).records.blocks) >= 2
    assert len(load(world.open(), project).records) == 8


def test_a_block_whose_head_was_never_written_is_swept_later(world: World) -> None:
    # Step 4, Dayanıklılık: a block written, its head not. No head names it, so a reader never
    # reads it; a seal more than twice retire_after later trashes it.
    port = world.open(SMALL)
    project, version = create(port)
    version = port.commit(project, version, change(entry(2), records=records(1, 1)))
    world.drive.inject("update", Fail(400, "badRequest", "Bad Request"))
    with pytest.raises(Rejected, match="Bad Request"):
        port.commit(project, version, change(entry(3), records=records(2, 2)))
    assert len(load(world.open(), project).records) == 1
    world.watch()

    version = port.commit(project, version, change(entry(3), records=records(5, 2)))

    # The folder's create meets its earlier try's 409; two new blocks at fresh ids.
    assert world.made() == ["get", "create", "create", "create", "update", "children"]
    assert [each.id for each in load(world.open(), project).records] == [1, 5, 6]
    orphans = world.blocks(project) - world.named(project)
    assert len(orphans) == 2
    world.clock.sleep(2 * SMALL.retire_after + 1)

    port.commit(project, version, change(entry(4), entry(5), entry(6)))

    assert all(world.drive.files[orphan].trashed for orphan in orphans)
    head = world.written(project)
    assert world.blocks(project) == head.named() | {each.id for each in head.retired}


def test_two_seals_at_once_each_write_their_own_and_the_later_head_stands(world: World) -> None:
    # The look is no lock: A writes its block, B its block and head, then A its head. A's head
    # stands whole, as the port promises; B's block is named by no head, for a later sweep.
    a, b = world.open(SMALL), world.open(SMALL)
    project, version = create(a)
    version = grow(a, project, version, range(2, 4))  # an open history block
    load(b, project)
    theirs = change(*(entry(seq, who="b") for seq in (4, 5, 6)))
    hook = Before(lambda: b.commit(project, version, theirs))
    world.drive.inject("update", hook, file=world.head(project).id)

    a.commit(project, version, change(*(entry(seq, who="a") for seq in (4, 5, 6))))

    recent = load(world.open(SMALL), project).recent
    assert [(each.seq, each.data.get("who")) for each in recent][-3:] == [
        (4, "a"),
        (5, "a"),
        (6, "a"),
    ]
    assert len(world.blocks(project) - world.named(project)) == 2  # B's, and the one retired


def test_a_second_commit_on_the_same_version_in_one_core_waits_and_is_stale(
    world: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    # One project's commits in one core go one at a time, as on the in-memory store.
    port = world.open()
    project, version = create(port)
    found: list[str] = []
    arrived = threading.Event()
    lock_of = port._lock_of  # pyright: ignore[reportPrivateUsage]

    def second() -> None:
        try:
            port.commit(project, version, change(entry(2), name="B"))
            found.append("made")
        except Stale:
            found.append("stale")

    other = threading.Thread(target=second)

    def arriving(project: str) -> threading.Lock:
        if threading.current_thread() is other:
            arrived.set()
        return lock_of(project)

    monkeypatch.setattr(port, "_lock_of", arriving)

    def start_and_wait() -> None:
        other.start()
        arrived.wait(5)

    world.drive.inject("update", Before(start_and_wait), file=world.head(project).id)

    port.commit(project, version, change(entry(2), name="A"))
    other.join(5)

    assert found == ["stale"]
    assert load(world.open(), project).row == row("A")


def test_the_same_content_twice_is_two_versions(world: World) -> None:
    # The write counter: state A, B, A again with no history entry still moves the version.
    port = world.open()
    project, first = create(port)
    second = port.commit(project, first, change(state={"x": 2}))
    third = port.commit(project, second, change(state={"frames": []}))

    assert len({first, second, third}) == 3


# -- waits and Drive's words ---------------------------------------------------------------------


def test_a_lost_write_that_was_made_is_seen_and_not_made_again(world: World) -> None:
    port = world.open()
    project, version = create(port)
    world.drive.inject("update", Lose(after=True))
    world.watch()

    moved = port.commit(project, version, change(entry(2), name="Yeni"))

    assert world.made() == ["get", "update", "get"]
    assert load(world.open(), project).version == moved


def test_a_lost_write_that_was_not_made_is_made_again(world: World) -> None:
    port = world.open()
    project, version = create(port)
    world.drive.inject("update", Lose())
    world.watch()

    port.commit(project, version, change(entry(2), name="Yeni"))

    assert world.made() == ["get", "update", "get", "update"]
    assert load(world.open(), project).row == row("Yeni")


def test_a_lost_write_with_another_cores_after_it_is_unconfirmed(world: World) -> None:
    # Writing again blindly would overwrite the other Colab's change.
    a, b = world.open(), world.open()
    project, version = create(a)
    load(b, project)
    world.drive.inject(
        "update", Before(lambda: b.commit(project, version, change(entry(2), name="B")))
    )
    world.drive.inject("update", Lose())

    with pytest.raises(Unconfirmed, match="Another core"):
        a.commit(project, version, change(entry(2), name="A"))

    assert load(world.open(), project).row == row("B")


def test_the_rate_limit_slows_a_change_and_loses_nothing(world: World) -> None:
    port = world.open()
    project, version = create(port)
    world.drive.inject("update", RATE, times=2)
    world.watch()

    moved = port.commit(project, version, change(entry(2), name="Yeni"))

    assert world.made() == ["get", "update", "get", "update", "get", "update"]
    assert world.clock.now() >= T0 + timedelta(seconds=3)
    assert load(world.open(), project).version == moved


def test_a_rate_limit_that_lasts_is_rejected_in_drives_words(world: World) -> None:
    port = world.open()
    project, version = create(port)
    world.drive.inject("update", RATE, times=100)

    with pytest.raises(Rejected) as rejected:
        port.commit(project, version, change(entry(2)))

    assert (rejected.value.said, rejected.value.code) == (RATE.said, RATE.reason)
    assert world.clock.now() < T0 + timedelta(seconds=61)
    assert load(world.open(), project).version == version


def test_a_write_lost_until_the_budget_ends_is_unconfirmed(world: World) -> None:
    port = world.open()
    project, version = create(port)
    world.drive.inject("update", Lose(said="Connection reset by peer"), times=100)

    with pytest.raises(Unconfirmed, match="Connection reset"):
        port.commit(project, version, change(entry(2)))


def test_a_read_is_tried_again_then_rejected_in_drives_words(world: World) -> None:
    port = world.open()
    project, _ = create(port)
    world.drive.inject("get", Fail(503, "transientError", "Transient failure"), times=2)
    port.version(project)
    world.drive.inject("get", Fail(503, "transientError", "Transient failure"), times=100)

    with pytest.raises(Rejected) as rejected:
        port.version(project)

    assert (rejected.value.said, rejected.value.code) == ("Transient failure", "transientError")


def test_a_hung_call_holds_its_timeout_inside_the_budget(world: World) -> None:
    # A hung socket must not hold a project forever: each try ends at its timeout, and the
    # budget counts that time.
    port = world.open()
    project, _ = create(port)
    world.drive.inject("get", Hang(30), times=100)
    world.watch()

    with pytest.raises(Rejected, match="timed out"):
        port.version(project)

    assert world.made() == ["get", "get"]
    assert world.clock.now() - T0 < timedelta(seconds=65)


def test_a_write_into_a_head_trashed_meanwhile_is_not_found(world: World) -> None:
    a, b = world.open(), world.open()
    project, version = create(a)
    world.drive.inject("update", Before(lambda: b.trash_project(project)), times=1)

    with pytest.raises(NotFound):
        a.commit(project, version, change(entry(2)))


def test_a_lost_create_that_was_made_is_the_creation(world: World) -> None:
    port = world.open()
    project = new_id()
    (ref,) = port.reserve(1)
    world.drive.inject("create", Lose(after=True))
    world.watch()

    version = port.create(project, ref, opening())

    assert world.made() == ["create", "create", "get"]
    assert load(world.open(), project).version == version


def test_a_create_at_a_folder_is_taken_and_at_an_unreserved_id_rejected(world: World) -> None:
    port = world.open()
    (ref,) = port.reserve(1)
    world.drive.create({"id": ref, "name": "x", "mimeType": FOLDER}, None, "id")

    with pytest.raises(Taken):
        port.create(new_id(), ref, opening())
    with pytest.raises(Rejected, match="not usable"):
        port.create(new_id(), "notreserved", opening())


def test_a_second_create_at_a_used_ref_exists(world: World) -> None:
    port = world.open()
    project, _ = create(port)
    ref = world.head(project).id

    with pytest.raises(Exists):
        port.create(new_id(), ref, opening())


# -- what the port keeps -------------------------------------------------------------------------


def test_a_project_out_of_the_base_cache_reads_its_head_once_to_commit(world: World) -> None:
    port = world.open(Limits(bases=1))
    one, one_version = create(port)
    create(port)
    world.watch()

    port.commit(one, one_version, change(entry(2)))

    assert world.made() == ["get", "download", "update"]


def test_a_head_changing_while_read_is_read_again_then_refused(world: World) -> None:
    a, b = world.open(), world.open()
    project, version = create(a)
    load(b, project)
    versions = [version]

    def write() -> None:
        versions.append(a.commit(project, versions[-1], change(entry(len(versions) + 1))))

    write()  # b's base is now behind: its load downloads the head
    world.drive.inject("download", Before(write))
    world.watch()
    load(b, project)
    assert world.made().count("download") == 2

    write()
    world.drive.inject("download", Before(write), times=3)
    with pytest.raises(Rejected, match="changed while"):
        load(b, project)


def test_a_half_trashed_project_has_its_folder_trashed_on_opening(world: World) -> None:
    # Once the head is in the trash the project is gone: a folder left behind is logged, and
    # the next opening takes it.
    port = world.open(SMALL)
    project, version = create(port)
    grow(port, project, version, range(2, 4))
    folder = world.drive.named(project)
    world.drive.inject("update", Fail(400, "badRequest", "Bad Request"), file=folder.id)

    port.trash_project(project)

    assert world.head(project).trashed
    assert not folder.trashed

    world.open()

    assert folder.trashed
    assert project not in {found.id for found in world.open().projects()}


def test_every_folder_of_a_trashed_project_goes_on_opening(world: World) -> None:
    # A project may have two <p>/: one made at a new id when Drive refused the reserved one.
    port = world.open()
    project, _ = create(port)
    projects = world.head(project).parents[0]
    folders = [world.drive.folder(project, projects) for _ in range(2)]
    port.trash_project(project)

    world.open()

    assert all(world.drive.files[each].trashed for each in folders)


# -- bounds and the unreadable -------------------------------------------------------------------


def test_a_head_past_its_bound_is_unreadable_and_never_downloaded(world: World) -> None:
    project, _ = create(world.open())
    port = world.open(Limits(head_most=50))
    world.watch()

    with pytest.raises(Unreadable, match="bytes"):
        load(port, project)
    assert world.made() == ["get"]


def test_a_change_past_the_heads_bound_is_refused_before_drive_is_asked(world: World) -> None:
    port = world.open(Limits(head_most=400))
    project, version = create(port)
    world.watch()

    with pytest.raises(ValueError, match="head file"):
        port.commit(project, version, change(entry(2), state={"x": "y" * 400}))
    assert world.made() == []


def test_a_head_whose_properties_drive_holds_wrongly_is_left_out(world: World) -> None:
    port = world.open()
    project, _ = create(port)
    kept, _ = create(port)
    world.head(project).properties["archived"] = "maybe"

    assert {found.id for found in port.projects()} == {kept}
    with pytest.raises(Unreadable, match="archived"):
        port.version(project)


def test_a_block_missing_from_drive_is_unreadable(world: World) -> None:
    port = world.open(SMALL)
    project, version = create(port)
    grow(port, project, version, range(2, 5))
    del world.drive.files[world.drive.named("records-1.jsonl.gz").id]

    with pytest.raises(Unreadable, match="not on Drive"):
        load(world.open(SMALL), project)


def test_a_change_to_a_head_whose_properties_lost_their_folder_is_refused(world: World) -> None:
    # Every write sends the properties whole: without the folder it would write an empty one.
    port = world.open()
    project, version = create(port)
    del world.head(project).properties["folder"]
    world.watch()

    with pytest.raises(Unreadable, match="folder"):
        port.commit(project, version, change(entry(2)))
    assert "update" not in world.made()


def test_a_create_whose_tail_no_block_could_hold_is_refused_before_drive_is_asked(
    world: World,
) -> None:
    # Unsealable, every later change of the project would fail at its seal.
    port = world.open(Limits(block_most=200))
    (ref,) = port.reserve(1)
    big = tuple(Record("frame", n, {"pad": "x" * 50}) for n in range(5))
    world.watch()

    with pytest.raises(ValueError, match="records"):
        port.create(new_id(), ref, opening(records=big))
    assert world.made() == []


def test_a_project_past_its_whole_bound_is_unreadable_before_its_blocks_are_read(
    world: World,
) -> None:
    a = world.open(SMALL)
    project, version = create(a)
    grow(a, project, version, range(2, 8))
    port = world.open(replace(SMALL, project_most=300))
    world.watch()

    with pytest.raises(Unreadable, match="opens to"):
        load(port, project)
    assert world.made() == ["get", "download"]


def test_the_base_heads_kept_are_bounded_in_bytes_too(world: World) -> None:
    port = world.open(Limits(bases_bytes=1))
    one, one_version = create(port)
    create(port)
    world.watch()

    port.commit(one, one_version, change(entry(2)))

    assert world.made() == ["get", "download", "update"]


# -- Drive's 404, ids it no longer takes, a new root ---------------------------------------------


def test_a_root_drive_does_not_have_is_rejected_in_drives_words(world: World) -> None:
    cache = DiskCache(world.tmp_path / "none", most=10**6, keep_free=0)

    with pytest.raises(Rejected, match="File not found"):
        DrivePort.open(world.drive, "noroot", world.clock, cache)


def test_a_projects_folder_gone_from_drive_is_said_never_an_inner_error(world: World) -> None:
    port = world.open()
    create(port)
    del world.drive.files[world.drive.named(PROJECTS).id]

    with pytest.raises(NotFound, match=PROJECTS):
        port.version(new_id())
    with pytest.raises(Rejected, match=PROJECTS):
        port.projects()


def test_ids_drive_no_longer_takes_are_replaced_and_the_folder_named_anew(world: World) -> None:
    # Reserved ids may expire (528, 6): the folder reserved at the creation and the pool's
    # block ids are both refused; new ones are taken and the head's properties name the folder.
    port = world.open(SMALL)
    project, version = create(port)
    version = port.commit(project, version, change(entry(2), records=records(1, 1)))
    reserved = world.head(project).properties["folder"]
    world.drive.expire()
    world.watch()

    port.commit(project, version, change(entry(3), records=records(2, 2)))

    folder = world.head(project).properties["folder"]
    assert folder != reserved
    assert reserved not in world.drive.files
    assert world.drive.files[folder].mime == FOLDER
    # One, for the folder: the blocks are planned again from the new pool at once.
    assert world.made().count("generate_ids") == 1
    assert [each.id for each in load(world.open(SMALL), project).records] == [1, 2, 3]


def test_a_new_folder_no_head_names_goes_to_the_trash_when_the_change_fails(
    world: World,
) -> None:
    # The reserved folder id refused, a new folder made, then the head's write refused: no head
    # names the new folder, so it goes, with the blocks put in it.
    port = world.open(SMALL)
    project, version = create(port)
    version = port.commit(project, version, change(entry(2), records=records(1, 1)))
    world.drive.expire()
    world.drive.inject(
        "update", Fail(400, "badRequest", "Bad Request"), file=world.head(project).id
    )

    with pytest.raises(Rejected, match="Bad Request"):
        port.commit(project, version, change(entry(3), records=records(2, 2)))

    (made,) = [f for f in world.drive.files.values() if f.name == project and f.mime == FOLDER]
    assert made.trashed
    assert world.head(project).properties["folder"] not in world.drive.files


# -- the commit's deadline and the trash's backstop ----------------------------------------------


def test_a_head_write_past_the_commits_deadline_is_rejected(world: World) -> None:
    # A head written late could name a block another core has put in the trash meanwhile; past
    # commit_most it is not written, and the blocks already written are the sweep's.
    port = world.open(SMALL)
    project, version = create(port)
    version = port.commit(project, version, change(entry(2)))
    late = Before(lambda: world.clock.sleep(SMALL.commit_most + 1))
    world.drive.inject("create", late)

    with pytest.raises(Rejected, match="deadline"):
        port.commit(project, version, change(entry(3), entry(4)))

    assert load(world.open(SMALL), project).version == version
    assert world.blocks(project) - world.named(project)  # written, named by no head


def test_the_deadline_ends_the_waits_too(world: World) -> None:
    port = world.open(replace(SMALL, commit_most=10))
    project, version = create(port)
    world.drive.inject("update", RATE, times=100)

    with pytest.raises(Rejected):
        port.commit(project, version, change(entry(2)))

    assert world.clock.now() - T0 < timedelta(seconds=11)


def test_a_named_block_found_in_the_trash_is_taken_back_out_by_the_next_sweep(
    world: World,
) -> None:
    # The backstop to the hour's wait: the sweep's listing is whole, so a named block missing
    # from it was trashed too early, and is untrashed before Drive empties the trash.
    port = world.open(SMALL)
    project, version = create(port)
    version = grow(port, project, version, range(2, 5))  # a records block, closed and named
    (records_block,) = [block.id for block in world.written(project).records.blocks]
    world.drive.files[records_block].trashed = True
    world.watch()

    grow(port, project, version, range(5, 8), per=0)

    assert not world.drive.files[records_block].trashed
    made = world.made()
    assert made.count("children") == 1  # one seal among these, one sweep
    assert made[made.index("children") + 1] == "update"  # the untrash, the only extra call
    assert len(load(world.open(SMALL), project).records) == 3


def test_two_cores_opening_a_new_root_at_once_meet_in_the_oldest_projects(world: World) -> None:
    theirs: list[str] = []
    made = Before(lambda: theirs.append(world.drive.folder(PROJECTS, world.root)))
    world.drive.inject("create", made)

    port = world.open()

    project, _ = create(port)
    assert world.head(project).parents == theirs
