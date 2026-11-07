"""The storage port's contract: what every adapter passes (step 4, Depo portu; step 12).

An adapter's test file inherits PortContract and gives its `rig`; the Drive adapter's (v1-8, v1-9)
runs the same tests on the test account's Drive. So a test here looks only at what holds on every
store: the store need not be empty (ids are random, lists are compared as sets), a trashed folder's
contents may follow it a few seconds late (528, 7), quota is read for its shape only, and no two
writes race — each adapter tries its own races with its own hooks.
"""

import hashlib
import secrets
import string
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

import pytest

from core.storage.port import (
    MOST_ENTRIES,
    MOST_NAME,
    MOST_RESERVED,
    Commit,
    Entry,
    Exists,
    InExport,
    InProject,
    NewerFormat,
    NotFound,
    Port,
    Project,
    Record,
    Rejected,
    Row,
    Stale,
    Stored,
    Taken,
    TooLarge,
    Unreadable,
)

T0 = datetime(2026, 11, 6, 9, 0, tzinfo=UTC)
# The groups' format these tests write; a newer core's is FORMAT + 1.
FORMAT = 1


class Rig(Protocol):
    def open(self) -> Port:
        """A core's port onto the one store; each call is another core."""
        ...

    def spoil(self, project: str) -> None:
        """Makes the project's data unreadable, as a crash or a hand on Drive might."""
        ...


def new_id() -> str:
    return "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))


def row(name: str = "Yağmurlu gün", **changes: Any) -> Row:
    fields: dict[str, Any] = {
        "name": name,
        "archived": False,
        "created": T0,
        "updated": T0,
        "runner": None,
        **changes,
    }
    return Row(**fields)


def entry(seq: int, at: datetime = T0, **data: Any) -> Entry:
    return Entry(seq=seq, time=at, data={"what": f"change {seq}", **data})


def change(
    *entries: Entry,
    name: str = "Bir",
    state: dict[str, Any] | None = None,
    records: tuple[Record, ...] = (),
    format: int = FORMAT,
) -> Commit:
    return Commit(
        row=row(name),
        state={} if state is None else state,
        format=format,
        records=records,
        entries=entries,
    )


def opening(
    state: dict[str, Any] | None = None, records: tuple[Record, ...] = (), name: str = "Bir"
) -> Commit:
    return change(
        entry(1, key="create-1"),
        name=name,
        state={"frames": []} if state is None else state,
        records=records,
    )


def create(port: Port, made: Commit | None = None) -> tuple[str, str]:
    """A new project; its id and version."""
    project = new_id()
    (ref,) = port.reserve(1)
    return project, port.create(project, ref, made or opening())


def load(port: Port, project: str, since: datetime = T0) -> Project:
    return port.load(project, since, FORMAT)


def written(directory: Path, name: str, content: bytes) -> Path:
    path = directory / name
    path.write_bytes(content)
    return path


def md5(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


class PortContract:
    # -- projects --------------------------------------------------------------------------------

    def test_what_is_written_is_read_back_by_another_core(self, rig: Rig) -> None:
        a, b = rig.open(), rig.open()
        frame = Record(kind="frame", id=17, data={"prompt": "ışık, İstanbul", "seed": 4})
        project, version = create(a, opening({"frames": [[17, None]]}, (frame,)))

        loaded = load(b, project)

        assert loaded.id == project
        assert loaded.version == version
        assert loaded.row == row("Bir")
        assert loaded.state == {"frames": [[17, None]]}
        assert loaded.format == FORMAT
        assert loaded.records == (frame,)
        assert loaded.recent == (entry(1, key="create-1"),)

    def test_the_row_and_state_keep_their_values(self, rig: Rig) -> None:
        port = rig.open()
        state: dict[str, Any] = {
            "frames": [[17, 233], [18, None]],
            "queue": {"paused": True, "stop_reason": None, "running": None},
            "note": "Çığ — 東京",
            "score": 0.5,
        }
        later = T0 + timedelta(days=1, seconds=7)
        made = Commit(
            row=row("ŞÖĞÜÇİ ışık", archived=True, updated=later, runner="k3v9q2mz7a"),
            state=state,
            format=FORMAT,
            entries=(entry(1),),
        )
        project, _ = create(port, made)

        loaded = load(port, project)

        assert loaded.row == made.row
        assert loaded.state == state

    def test_the_list_carries_each_project_with_its_version(self, rig: Rig) -> None:
        a, b = rig.open(), rig.open()
        one, one_version = create(a)
        two, two_version = create(a, opening(name="İki"))

        listed = {found.id: found for found in b.projects()}

        assert listed[one].version == one_version
        assert listed[one].row == row("Bir")
        assert listed[two].version == two_version
        assert listed[two].row == row("İki")
        assert b.version(one) == listed[one]

    def test_a_second_create_at_the_same_ref_writes_nothing(self, rig: Rig) -> None:
        # The same creation sent again, after a restart, carries the ref creates.json kept (step 4).
        port = rig.open()
        project = new_id()
        (ref,) = port.reserve(1)
        version = port.create(project, ref, opening())

        with pytest.raises(Exists):
            port.create(project, ref, opening(name="Başka"))

        assert port.version(project).version == version
        assert load(port, project).row == row("Bir")

    def test_a_create_where_a_file_or_folder_is_is_taken(self, rig: Rig, tmp_path: Path) -> None:
        port = rig.open()
        project, _ = create(port)
        (file, folder) = port.reserve(2)
        port.put(file, written(tmp_path, "a.png", b"one"), "a.png", InProject(project))
        port.export_folder(folder, "2026-11-06 09-00 x")

        for ref in (file, folder):
            with pytest.raises(Taken):
                port.create(new_id(), ref, opening())

    def test_a_commit_moves_the_version_and_adds_what_it_carries(self, rig: Rig) -> None:
        a, b = rig.open(), rig.open()
        first = Record(kind="frame", id=17, data={"seed": 1})
        project, version = create(a, opening(records=(first,)))
        video = Record(kind="video", id=233, data={"seconds": 5})
        job = Record(kind="job", id=4401, data={"status": "done"})
        moving = Commit(
            row=row("Bir", updated=T0 + timedelta(seconds=30)),
            state={"frames": [[17, 233]]},
            format=FORMAT,
            records=(video, job),
            entries=(entry(2, T0 + timedelta(seconds=30)), entry(3, T0 + timedelta(seconds=30))),
        )

        moved = a.commit(project, version, moving)

        loaded = load(b, project)
        assert moved != version
        assert loaded.version == moved
        assert b.version(project).version == moved
        assert loaded.row == moving.row
        assert loaded.state == {"frames": [[17, 233]]}
        assert loaded.records == (first, video, job)
        assert [found.seq for found in loaded.recent] == [1, 2, 3]
        # Built on what it last gave, the next commit goes through.
        a.commit(project, moved, change(entry(4)))

    def test_a_commit_on_an_old_version_is_stale_and_writes_nothing(self, rig: Rig) -> None:
        # Two Colabs one after another (step 4, Değerlendirme 4): the second's old view is refused.
        a, b = rig.open(), rig.open()
        project, version = create(a)
        seen = load(b, project)
        moved = a.commit(project, version, change(entry(2), name="A", state={"frames": [[1, 0]]}))

        with pytest.raises(Stale):
            b.commit(project, seen.version, change(entry(2), name="B"))

        now = load(b, project)
        assert now.version == moved
        assert now.row == row("A")
        assert [found.seq for found in now.recent] == [1, 2]
        # On what it now sees, B's change goes through.
        b.commit(project, now.version, change(entry(3), name="B"))
        assert load(a, project).row == row("B")

    def test_a_version_this_port_did_not_give_is_refused(self, rig: Rig) -> None:
        # A change built on one version and written on another loses what came between.
        a, b = rig.open(), rig.open()
        project, version = create(a)
        listed = b.version(project).version
        moved = a.commit(project, version, change(entry(2)))

        for port, used in ((b, listed), (b, moved), (a, version), (b, "never")):
            with pytest.raises(ValueError, match="version"):
                port.commit(project, used, change(entry(3)))

        assert load(a, project).version == moved

    def test_history_must_follow_on_from_its_last_entry(self, rig: Rig) -> None:
        # Lost changes are found by their seq (v1-10): every change's entries go on from the last.
        port = rig.open()
        project, version = create(port)

        for seqs in ((3,), (2, 2), (1,), (2, 4)):
            with pytest.raises(ValueError, match="seq"):
                port.commit(project, version, change(*(entry(seq) for seq in seqs)))
        (ref,) = port.reserve(1)
        with pytest.raises(ValueError, match="seq"):
            port.create(new_id(), ref, change(entry(2)))

        assert load(port, project).version == version

    def test_a_newer_format_is_neither_read_nor_written(self, rig: Rig) -> None:
        # Step 4, Değerlendirme 11: a newer core's project is left to it.
        old, new = rig.open(), rig.open()
        project, version = create(old)
        load(new, project)
        newer = new.commit(project, version, change(entry(2), format=FORMAT + 1))

        with pytest.raises(NewerFormat) as found:
            load(old, project)
        with pytest.raises(NewerFormat):
            new.commit(project, newer, change(entry(3), format=FORMAT))

        assert (found.value.found, found.value.known) == (FORMAT + 1, FORMAT)
        assert new.load(project, T0, FORMAT + 1).format == FORMAT + 1
        assert old.version(project).version == newer

    def test_an_older_format_is_read_and_lifted_by_the_next_commit(self, rig: Rig) -> None:
        port = rig.open()
        project, version = create(port)

        assert port.load(project, T0, FORMAT + 1).format == FORMAT
        port.commit(project, version, change(entry(2), format=FORMAT + 1))
        assert port.load(project, T0, FORMAT + 1).format == FORMAT + 1

    def test_load_gives_the_history_since_the_time_asked(self, rig: Rig) -> None:
        port = rig.open()
        project, version = create(port)
        for seq in (2, 3):
            version = port.commit(project, version, change(entry(seq, T0 + timedelta(hours=seq))))

        since = load(port, project, T0 + timedelta(hours=2)).recent
        none = load(port, project, T0 + timedelta(hours=4)).recent

        assert [found.seq for found in since] == [2, 3]
        assert none == ()

    def test_history_gives_the_latest_before_a_seq(self, rig: Rig) -> None:
        port = rig.open()
        project, version = create(port)
        port.commit(project, version, change(*(entry(seq) for seq in range(2, 6))))

        assert [found.seq for found in port.history(project, None, 2)] == [5, 4]
        assert [found.seq for found in port.history(project, 4, 2)] == [3, 2]
        assert [found.seq for found in port.history(project, 3, 10)] == [2, 1]
        assert port.history(project, 1, 10) == ()
        assert port.history(project, None, 1) == (entry(5),)

    def test_an_unknown_project_is_not_found(self, rig: Rig) -> None:
        port = rig.open()
        project = new_id()

        for asked in (
            lambda: port.version(project),
            lambda: load(port, project),
            lambda: port.history(project, None, 1),
        ):
            with pytest.raises(NotFound):
                asked()

    def test_a_trashed_project_is_gone_and_trashing_it_again_succeeds(self, rig: Rig) -> None:
        a, b = rig.open(), rig.open()
        project, version = create(a)
        kept, _ = create(a)

        b.trash_project(project)
        b.trash_project(project)
        b.trash_project(new_id())

        assert project not in {found.id for found in a.projects()}
        assert kept in {found.id for found in a.projects()}
        with pytest.raises(NotFound):
            a.version(project)
        with pytest.raises(NotFound):
            load(a, project)
        # The core that had it loaded writes nothing to it either.
        with pytest.raises(NotFound):
            a.commit(project, version, change(entry(2)))

    def test_an_unreadable_project_is_listed_but_never_read_or_written(self, rig: Rig) -> None:
        # Never taken as empty and written over (step 4, Okunamayan baş dosyası).
        port = rig.open()
        project, version = create(port)
        rig.spoil(project)

        assert project in {found.id for found in port.projects()}
        assert port.version(project).row == row("Bir")
        with pytest.raises(Unreadable):
            load(port, project)
        with pytest.raises(Unreadable):
            port.history(project, None, 1)
        with pytest.raises(Stale):
            port.commit(project, version, change(entry(2)))
        with pytest.raises(Unreadable):
            load(port, project)
        port.trash_project(project)
        assert project not in {found.id for found in port.projects()}

    def test_a_malformed_project_id_is_refused_before_the_store_is_asked(
        self, rig: Rig, tmp_path: Path
    ) -> None:
        port = rig.open()
        project, _ = create(port)
        (ref, copied) = port.reserve(2)
        source = written(tmp_path, "a.png", b"one")
        port.put(ref, source, "a.png", InProject(project))
        bad = "../" + new_id()[:7]

        asked: list[Callable[[], object]] = [
            lambda: port.version(bad),
            lambda: load(port, bad),
            lambda: port.create(bad, copied, opening()),
            lambda: port.commit(bad, "1", change()),
            lambda: port.history(bad, None, 1),
            lambda: port.trash_project(bad),
            lambda: port.put(copied, source, "b.png", InProject(bad)),
            lambda: port.copy(ref, copied, "b.png", InProject(bad)),
        ]
        for call in asked:
            with pytest.raises(ValueError, match="project id"):
                call()
        assert port.exists(copied) is None

    def test_a_time_off_the_rule_is_refused(self, rig: Rig) -> None:
        port = rig.open()
        (ref,) = port.reserve(1)
        finer = T0 + timedelta(microseconds=1)

        with pytest.raises(ValueError):
            port.create(new_id(), ref, Commit(row=row(updated=finer), state={}, format=FORMAT))
        with pytest.raises(ValueError):
            port.create(new_id(), ref, change(entry(1, finer)))

    def test_a_row_past_what_drive_keeps_is_refused(self, rig: Rig) -> None:
        port = rig.open()
        project, version = create(port)
        (ref,) = port.reserve(1)
        longest = "ğ" * MOST_NAME

        for bad in (row("ğ" * (MOST_NAME + 1)), row(""), row(runner="../core")):
            with pytest.raises(ValueError):
                port.create(new_id(), ref, Commit(row=bad, state={}, format=FORMAT))
            with pytest.raises(ValueError):
                port.commit(project, version, Commit(row=bad, state={}, format=FORMAT))
        port.commit(project, version, change(entry(2), name=longest))
        assert load(port, project).row == row(longest)

    def test_counts_past_their_bounds_are_refused(self, rig: Rig) -> None:
        port = rig.open()
        project, _ = create(port)

        for count in (0, MOST_RESERVED + 1):
            with pytest.raises(ValueError):
                port.reserve(count)
        for count in (0, MOST_ENTRIES + 1):
            with pytest.raises(ValueError):
                port.history(project, None, count)

    # -- files -----------------------------------------------------------------------------------

    def test_reserved_refs_are_distinct(self, rig: Rig) -> None:
        a, b = rig.open(), rig.open()

        refs = a.reserve(3) + b.reserve(2)

        assert len(set(refs)) == 5

    def test_a_file_put_is_read_back_by_another_core(self, rig: Rig, tmp_path: Path) -> None:
        a, b = rig.open(), rig.open()
        project, _ = create(a)
        (ref,) = a.reserve(1)
        content = b"\x89PNG photo"

        stored = a.put(ref, written(tmp_path, "out.png", content), "17.png", InProject(project))
        got = b.get(ref, tmp_path / "back" / "17.png", most=len(content))

        assert stored == Stored(ref, len(content), md5(content))
        assert got == stored
        assert (tmp_path / "back" / "17.png").read_bytes() == content
        assert sorted(path.name for path in (tmp_path / "back").iterdir()) == ["17.png"]
        # A job whose output is already stored finishes from this, with no download (step 4).
        assert b.exists(ref) == stored

    def test_putting_the_same_file_again_leaves_one_file(self, rig: Rig, tmp_path: Path) -> None:
        # A retry after a lost answer (step 4, Değerlendirme 2).
        port = rig.open()
        project, _ = create(port)
        (ref,) = port.reserve(1)
        source = written(tmp_path, "out.png", b"photo")

        first = port.put(ref, source, "17.png", InProject(project))

        assert port.put(ref, source, "17.png", InProject(project)) == first

    def test_other_content_at_a_used_ref_is_taken(self, rig: Rig, tmp_path: Path) -> None:
        port = rig.open()
        project, _ = create(port)
        (ref,) = port.reserve(1)
        port.put(ref, written(tmp_path, "a.png", b"one"), "17.png", InProject(project))

        with pytest.raises(Taken):
            port.put(ref, written(tmp_path, "b.png", b"two"), "17.png", InProject(project))

        port.get(ref, tmp_path / "back.png", most=10)
        assert (tmp_path / "back.png").read_bytes() == b"one"

    def test_a_put_at_a_trashed_files_ref_is_taken(self, rig: Rig, tmp_path: Path) -> None:
        # The ref is used, and its file is not there: the core takes another (m534).
        port = rig.open()
        project, _ = create(port)
        (ref,) = port.reserve(1)
        source = written(tmp_path, "a.png", b"one")
        port.put(ref, source, "17.png", InProject(project))
        port.trash(ref)

        with pytest.raises(Taken):
            port.put(ref, source, "17.png", InProject(project))

    def test_a_ref_never_reserved_is_refused(self, rig: Rig, tmp_path: Path) -> None:
        a = rig.open()
        project, _ = create(a)
        (ref,) = a.reserve(1)
        source = written(tmp_path, "a.png", b"one")
        a.put(ref, source, "17.png", InProject(project))

        with pytest.raises(Rejected):
            a.put("not" + ref, source, "18.png", InProject(project))

    def test_get_refuses_a_file_over_its_bound_and_writes_nothing(
        self, rig: Rig, tmp_path: Path
    ) -> None:
        port = rig.open()
        project, _ = create(port)
        (ref,) = port.reserve(1)
        port.put(ref, written(tmp_path, "v.mp4", b"0123456789"), "233.mp4", InProject(project))
        target = tmp_path / "cache"
        target.mkdir()

        with pytest.raises(TooLarge) as large:
            port.get(ref, target / "233.mp4", most=9)

        assert (large.value.size, large.value.most) == (10, 9)
        assert list(target.iterdir()) == []

    def test_a_missing_file_is_not_found(self, rig: Rig, tmp_path: Path) -> None:
        port = rig.open()
        project, _ = create(port)
        (ref, other) = port.reserve(2)

        assert port.exists(ref) is None
        with pytest.raises(NotFound):
            port.get(ref, tmp_path / "x", most=10)
        with pytest.raises(NotFound):
            port.copy(ref, other, "x.png", InProject(project))

    def test_a_trashed_file_is_gone_and_trashing_again_succeeds(
        self, rig: Rig, tmp_path: Path
    ) -> None:
        a, b = rig.open(), rig.open()
        project, _ = create(a)
        (ref, never) = a.reserve(2)
        a.put(ref, written(tmp_path, "a.png", b"one"), "17.png", InProject(project))

        a.trash(ref)
        a.trash(ref)
        a.trash(never)

        assert b.exists(ref) is None
        with pytest.raises(NotFound):
            b.get(ref, tmp_path / "back.png", most=10)

    def test_a_copy_is_a_new_file_and_its_repeat_is_the_same(
        self, rig: Rig, tmp_path: Path
    ) -> None:
        port = rig.open()
        project, _ = create(port)
        (ref, folder, copied) = port.reserve(3)
        port.put(ref, written(tmp_path, "a.png", b"photo"), "17.png", InProject(project))
        port.export_folder(folder, "2026-11-06 09-00 kısa")

        made = port.copy(ref, copied, "001.png", InExport(folder))

        assert port.copy(ref, copied, "001.png", InExport(folder)) == made
        assert made == Stored(copied, 5, md5(b"photo"))
        port.get(copied, tmp_path / "copy.png", most=10)
        assert (tmp_path / "copy.png").read_bytes() == b"photo"
        assert port.exists(ref) is not None

    def test_an_export_has_its_video_and_a_photos_folder(self, rig: Rig, tmp_path: Path) -> None:
        # Step 2: `<stamp> <name>/<name>.mp4` beside `photos/001.png`.
        port = rig.open()
        project, _ = create(port)
        (folder, photos, video, photo, source) = port.reserve(5)
        stamp = f"2026-11-06 09-00 {new_id()}"
        port.put(source, written(tmp_path, "a.png", b"photo"), "17.png", InProject(project))
        port.export_folder(folder, f"{stamp} final")
        port.export_folder(folder, f"{stamp} final")
        port.export_folder(photos, "photos", inside=folder)
        port.export_folder(photos, "photos", inside=folder)

        port.put(video, written(tmp_path, "f.mp4", b"film"), "final.mp4", InExport(folder))
        port.copy(source, photo, "001.png", InExport(photos))

        assert port.exists(video) == Stored(video, 4, md5(b"film"))
        assert port.exists(photo) == Stored(photo, 5, md5(b"photo"))
        # Only the export itself is named among the exports.
        assert port.export_names(stamp) == (f"{stamp} final",)
        assert port.export_names("photos") == ()
        with pytest.raises(Taken):
            port.export_folder(photos, "photos")

    def test_a_folder_is_opened_only_inside_a_folder_that_is_there(self, rig: Rig) -> None:
        port = rig.open()
        (folder, never) = port.reserve(2)

        with pytest.raises(NotFound):
            port.export_folder(folder, "photos", inside=never)

    def test_export_folders_are_found_by_how_their_name_begins(self, rig: Rig) -> None:
        # Step 2: the (n) compares names ignoring case; Drive's own search misses the Turkish I
        # (528), so the comparison is the adapter's, with ilike's four i's.
        port = rig.open()
        stamp = f"2026-11-06 09-00 {new_id()}"
        names = [f"{stamp} Işık", f"{stamp} ışık (1)", f"{stamp} IŞIK final", f"{stamp} isik"]
        refs = port.reserve(len(names))
        for ref, name in zip(refs, names, strict=True):
            port.export_folder(ref, name)

        found = port.export_names(f"{stamp} ışık")
        port.trash(refs[1])

        assert sorted(found) == sorted(names[:3])
        assert sorted(port.export_names(f"{stamp} IŞIK")) == sorted([names[0], names[2]])
        assert port.export_names(f"{stamp} yok") == ()

    def test_no_file_is_put_into_a_project_never_there(self, rig: Rig, tmp_path: Path) -> None:
        port = rig.open()
        (ref,) = port.reserve(1)

        with pytest.raises(NotFound):
            port.put(ref, written(tmp_path, "a.png", b"one"), "17.png", InProject(new_id()))
        assert port.exists(ref) is None

    def test_space_says_quota_use_and_trash(self, rig: Rig) -> None:
        space = rig.open().space()

        assert space.used >= 0
        assert 0 <= space.trash <= space.used
        assert space.quota is None or space.quota >= 0
