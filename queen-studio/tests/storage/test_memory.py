import math
import threading
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Any, get_args

import pytest

from core.clock.clock import ManualClock
from core.storage.faults import Drop, Refuse, Run, Slow
from core.storage.memory import MemoryPort, MemoryStore
from core.storage.port import (
    WRITES,
    Commit,
    InExport,
    InProject,
    NotFound,
    Op,
    Port,
    Record,
    Rejected,
    Stale,
    Unconfirmed,
)
from tests.storage.contract import (
    T0,
    PortContract,
    Rig,
    change,
    create,
    entry,
    load,
    new_id,
    opening,
    row,
    written,
)


class MemoryRig:
    def __init__(self, store: MemoryStore, clock: ManualClock) -> None:
        self.store = store
        self.clock = clock

    def open(self) -> Port:
        return self.store.open(self.clock)

    def spoil(self, project: str) -> None:
        self.store.spoil(project, "Not a gzipped file (b'xx')")


class TestMemoryContract(PortContract):
    @pytest.fixture
    def rig(self) -> Rig:
        return MemoryRig(MemoryStore(), ManualClock(T0))


@pytest.fixture
def clock() -> ManualClock:
    return ManualClock(T0)


@pytest.fixture
def store() -> MemoryStore:
    return MemoryStore()


def step(seq: int, name: str = "Bir") -> Commit:
    return change(entry(seq), name=name)


def every_call(port: MemoryPort, tmp_path: Path) -> dict[Op, Callable[[], object]]:
    """One call of each operation, on a project and files made for it."""
    project, version = create(port)
    ref, folder, fresh, copied, other = port.reserve(5)
    source = written(tmp_path, "a.png", b"one")
    port.put(ref, source, "a.png", InProject(project))
    port.export_folder(folder, "2026-11-06 09-00 x")
    return {
        "projects": port.projects,
        "version": lambda: port.version(project),
        "load": lambda: load(port, project),
        "create": lambda: port.create(new_id(), fresh, opening()),
        "commit": lambda: port.commit(project, version, step(2)),
        "history": lambda: port.history(project, None, 1),
        "trash_project": lambda: port.trash_project(project),
        "reserve": lambda: port.reserve(1),
        "put": lambda: port.put(other, source, "b.png", InProject(project)),
        "exists": lambda: port.exists(ref),
        "get": lambda: port.get(ref, tmp_path / "back.png", most=10),
        "copy": lambda: port.copy(ref, copied, "001.png", InExport(folder)),
        "trash": lambda: port.trash(ref),
        "export_folder": lambda: port.export_folder(fresh, "2026-11-06 09-00 y"),
        "export_names": lambda: port.export_names("2026"),
        "space": port.space,
    }


# -- faults --------------------------------------------------------------------------------------


@pytest.mark.parametrize("op", get_args(Op))
def test_any_operation_can_be_refused(
    store: MemoryStore, clock: ManualClock, tmp_path: Path, op: Op
) -> None:
    port = store.open(clock)
    calls = every_call(port, tmp_path)
    port.inject(op, Refuse("User rate limit exceeded.", "userRateLimitExceeded"))

    with pytest.raises(Rejected) as refused:
        calls[op]()

    assert (refused.value.said, refused.value.code) == (
        "User rate limit exceeded.",
        "userRateLimitExceeded",
    )
    assert port.calls[-1][0] == op
    calls[op]()


def test_a_refused_commit_writes_nothing(store: MemoryStore, clock: ManualClock) -> None:
    port = store.open(clock)
    project, version = create(port)
    port.inject("commit", Refuse("Quota exceeded.", "storageQuotaExceeded"))

    with pytest.raises(Rejected):
        port.commit(project, version, step(2, "Yeni"))

    assert load(port, project).version == version


def test_a_drop_before_the_write_writes_nothing(
    store: MemoryStore, clock: ManualClock, tmp_path: Path
) -> None:
    port = store.open(clock)
    project, version = create(port)
    (ref,) = port.reserve(1)
    port.inject("commit", Drop())
    port.inject("put", Drop())

    with pytest.raises(Unconfirmed):
        port.commit(project, version, step(2, "Yeni"))
    with pytest.raises(Unconfirmed):
        port.put(ref, written(tmp_path, "a.png", b"one"), "a.png", InProject(project))

    assert load(port, project).row == row("Bir")
    assert port.exists(ref) is None


def test_a_drop_after_the_write_has_written_it(
    store: MemoryStore, clock: ManualClock, tmp_path: Path
) -> None:
    # The answer is lost, the change is made: the core learns which by loading (step 4).
    port = store.open(clock)
    project, version = create(port)
    gone, _ = create(port)
    (ref,) = port.reserve(1)
    for op in ("commit", "put", "trash_project"):
        port.inject(op, Drop(after=True))

    with pytest.raises(Unconfirmed) as dropped:
        port.commit(project, version, step(2, "Yeni"))
    with pytest.raises(Unconfirmed):
        port.put(ref, written(tmp_path, "a.png", b"one"), "a.png", InProject(project))
    with pytest.raises(Unconfirmed):
        port.trash_project(gone)

    assert dropped.value.said
    assert dropped.value.code is None
    # The version given is still the one built on: written again, the change is Stale.
    with pytest.raises(Stale):
        port.commit(project, version, step(2, "Yeni"))
    loaded = load(port, project)
    assert loaded.version != version
    assert loaded.row == row("Yeni")
    assert port.exists(ref) is not None
    assert gone not in {found.id for found in port.projects()}


def test_slow_moves_the_clock_and_no_real_second_passes(
    store: MemoryStore, clock: ManualClock
) -> None:
    port = store.open(clock)
    port.inject("projects", Slow(40))

    port.projects()
    port.projects()

    assert clock.now() == T0 + timedelta(seconds=40)


def test_run_runs_before_the_operation(store: MemoryStore, clock: ManualClock) -> None:
    port = store.open(clock)
    project, _ = create(port)
    seen: list[str] = []
    port.inject("load", Run(lambda: seen.append(port.version(project).row.name)))

    load(port, project)

    assert seen == ["Bir"]
    assert [op for op, _ in port.calls[-2:]] == ["load", "version"]


def test_two_commits_at_once_the_later_wins_whole(store: MemoryStore, clock: ManualClock) -> None:
    # Step 4, Değerlendirme 4: both pass the look, the later write wins, and the earlier change is
    # lost entirely — its row, state, records and history — while the project stays whole.
    a, b = store.open(clock), store.open(clock)
    project, version = create(a)
    load(b, project)
    theirs = change(
        entry(2, core="b"),
        name="B",
        state={"frames": [[2, None]]},
        records=(Record(kind="frame", id=2, data={}),),
    )
    a.inject("commit", Run(lambda: b.commit(project, version, theirs), between=True))
    mine = change(
        entry(2, core="a"),
        name="A",
        state={"frames": [[3, None]]},
        records=(Record(kind="frame", id=3, data={}),),
    )

    won = a.commit(project, version, mine)

    loaded = load(b, project)
    assert loaded.version == won
    assert loaded.row == row("A")
    assert loaded.state == {"frames": [[3, None]]}
    assert loaded.records == mine.records
    assert loaded.recent == (entry(1, key="create-1"), entry(2, core="a"))


def test_a_commit_can_be_held_while_another_project_is_written(
    store: MemoryStore, clock: ManualClock
) -> None:
    # The store holds no lock across a hook: a held write on one project keeps no other waiting.
    a, b = store.open(clock), store.open(clock)
    held, held_version = create(a)
    other, other_version = create(b)
    holding, release = threading.Event(), threading.Event()

    def hold() -> None:
        holding.set()
        release.wait(5)

    a.inject("commit", Run(hold, between=True))
    writer = threading.Thread(target=lambda: a.commit(held, held_version, step(2, "A")))
    writer.start()
    holding.wait(5)

    b.commit(other, other_version, step(2, "B"))
    other_row = load(b, other).row
    release.set()
    writer.join(5)

    assert other_row == row("B")
    assert load(b, held).row == row("A")


def test_a_fault_fires_on_as_many_calls_as_asked(store: MemoryStore, clock: ManualClock) -> None:
    port = store.open(clock)
    port.inject("space", Refuse("Backend Error", "backendError"), times=2)

    for _ in range(2):
        with pytest.raises(Rejected):
            port.space()

    port.space()


def test_a_fault_can_let_calls_pass_first(store: MemoryStore, clock: ManualClock) -> None:
    port = store.open(clock)
    project, version = create(port)
    port.inject("commit", Refuse("Backend Error", None), skip=1)

    version = port.commit(project, version, step(2))
    with pytest.raises(Rejected):
        port.commit(project, version, step(3))
    port.commit(project, version, step(3))


def test_a_fault_can_be_held_to_one_project(store: MemoryStore, clock: ManualClock) -> None:
    port = store.open(clock)
    one, _ = create(port)
    two, _ = create(port)
    port.inject("load", Refuse("Backend Error", None), project=two)

    load(port, one)
    port.projects()
    with pytest.raises(Rejected):
        load(port, two)
    load(port, two)


def test_what_lets_a_call_go_on_fires_before_what_stops_it(
    store: MemoryStore, clock: ManualClock
) -> None:
    port = store.open(clock)
    seen: list[str] = []
    port.inject("projects", Refuse("first", None))
    port.inject("projects", Refuse("second", None))
    port.inject("projects", Slow(10))
    port.inject("projects", Run(lambda: seen.append("hook")))

    with pytest.raises(Rejected, match="first"):
        port.projects()
    # The second refusal was not spent by the first call: it waits for the next.
    with pytest.raises(Rejected, match="second"):
        port.projects()
    port.projects()

    assert clock.now() == T0 + timedelta(seconds=10)
    assert seen == ["hook"]


def test_faults_are_one_cores(store: MemoryStore, clock: ManualClock) -> None:
    a, b = store.open(clock), store.open(clock)
    a.inject("projects", Refuse("User rate limit exceeded.", "userRateLimitExceeded"))

    b.projects()
    with pytest.raises(Rejected):
        a.projects()


@pytest.mark.parametrize(
    ("op", "fault", "times", "skip"),
    [
        ("load", Drop(), 1, 0),
        ("reserve", Drop(after=True), 1, 0),
        ("put", Run(lambda: None, between=True), 1, 0),
        ("commit", Refuse("x", None), 0, 0),
        ("commit", Refuse("x", None), 1, -1),
    ],
    ids=["drop-a-read", "drop-reserve", "between-off-commit", "no-times", "skip-below-zero"],
)
def test_a_fault_that_cannot_happen_is_refused(
    store: MemoryStore,
    clock: ManualClock,
    op: Op,
    fault: Drop | Run | Refuse,
    times: int,
    skip: int,
) -> None:
    with pytest.raises(ValueError):
        store.open(clock).inject(op, fault, times, skip=skip)


def test_drop_is_offered_for_exactly_the_writes(store: MemoryStore, clock: ManualClock) -> None:
    port = store.open(clock)

    for op in get_args(Op):
        if op in WRITES:
            port.inject(op, Drop())
        else:
            with pytest.raises(ValueError):
                port.inject(op, Drop())


# -- what is counted -----------------------------------------------------------------------------


def test_every_call_is_counted_with_the_project_it_touches(
    store: MemoryStore, clock: ManualClock, tmp_path: Path
) -> None:
    # Later items' cost tests count an endpoint's store requests with this (CODE-STANDARD, Cost).
    port = store.open(clock)
    other = store.open(clock)
    project, _ = create(port)
    (ref, folder, copied) = port.reserve(3)
    port.put(ref, written(tmp_path, "a.png", b"one"), "a.png", InProject(project))
    port.export_folder(folder, "2026-11-06 09-00 x")
    port.copy(ref, copied, "001.png", InExport(folder))
    port.exists(ref)
    port.get(ref, tmp_path / "back.png", most=10)
    port.exists(copied)
    port.trash(ref)
    port.inject("load", Refuse("Backend Error", None))
    with pytest.raises(Rejected):
        load(port, project)

    assert port.calls == [
        ("reserve", None),
        ("create", project),
        ("reserve", None),
        ("put", project),
        ("export_folder", None),
        ("copy", project),
        ("exists", project),
        ("get", project),
        ("exists", None),
        ("trash", project),
        ("load", project),
    ]
    assert other.calls == []


# -- the data ------------------------------------------------------------------------------------


def test_the_data_is_kept_as_json_not_as_the_objects_given(
    store: MemoryStore, clock: ManualClock
) -> None:
    # As on Drive: what the core changes after writing, or in what it read, is not the store's.
    port = store.open(clock)
    state: dict[str, Any] = {"frames": [[17, None]]}
    data: dict[str, Any] = {"seed": 4}
    project, _ = create(port, opening(state, (Record(kind="frame", id=17, data=data),)))
    state["frames"].append([18, None])
    data["seed"] = 5

    loaded = load(port, project)
    loaded.state["frames"].clear()

    again = load(port, project)
    assert again.state == {"frames": [[17, None]]}
    assert again.records[0].data == {"seed": 4}


@pytest.mark.parametrize("value", [T0, math.nan, {1, 2}], ids=["datetime", "nan", "set"])
def test_a_value_json_cannot_hold_is_refused_and_nothing_written(
    store: MemoryStore, clock: ManualClock, value: object
) -> None:
    port = store.open(clock)
    project, version = create(port)

    with pytest.raises(ValueError):
        port.commit(project, version, change(entry(2), state={"x": value}))

    assert load(port, project).version == version


def test_a_record_is_put_once(store: MemoryStore, clock: ManualClock) -> None:
    # A record never changes once written (step 4): the same id again is the core's mistake. Only
    # this store looks: the Drive adapter does not hold every record.
    port = store.open(clock)
    project, version = create(port, opening(records=(Record(kind="frame", id=17, data={}),)))

    with pytest.raises(ValueError, match="17"):
        port.commit(
            project, version, change(entry(2), records=(Record(kind="job", id=17, data={}),))
        )

    assert load(port, project).version == version


def test_a_trashed_project_leaves_no_version_to_build_on(
    store: MemoryStore, clock: ManualClock
) -> None:
    # What a port remembers per project goes with the project: it grows with nothing gone.
    port = store.open(clock)
    project, version = create(port)

    port.trash_project(project)

    with pytest.raises(ValueError, match="version"):
        port.commit(project, version, step(2))


def test_spoiling_a_missing_project_is_refused(store: MemoryStore) -> None:
    with pytest.raises(NotFound):
        store.spoil(new_id(), "x")


# -- files ---------------------------------------------------------------------------------------


def test_the_quota_refuses_a_file_before_it_is_read(clock: ManualClock, tmp_path: Path) -> None:
    store = MemoryStore(quota=10)
    port = store.open(clock)
    project, _ = create(port)
    (fits, over, copied) = port.reserve(3)
    port.put(fits, written(tmp_path, "a.png", b"123456"), "a.png", InProject(project))

    with pytest.raises(Rejected) as full:
        port.put(over, written(tmp_path, "b.png", b"12345"), "b.png", InProject(project))
    with pytest.raises(Rejected):
        port.copy(fits, copied, "c.png", InProject(project))

    assert full.value.code == "storageQuotaExceeded"
    assert port.exists(over) is None
    space = port.space()
    assert (space.quota, space.used, space.trash) == (10, 6, 0)


def test_the_quota_changes_as_the_user_frees_their_drive(
    clock: ManualClock, tmp_path: Path
) -> None:
    # v1-18: the queue stops on storage_low and resumes once there is room.
    store = MemoryStore(quota=4)
    port = store.open(clock)
    project, _ = create(port)
    (ref,) = port.reserve(1)
    source = written(tmp_path, "a.png", b"12345")
    with pytest.raises(Rejected):
        port.put(ref, source, "a.png", InProject(project))

    store.quota = 5

    assert store.quota == 5
    port.put(ref, source, "a.png", InProject(project))
    assert port.space().quota == 5


def test_space_counts_the_trash_in_what_is_used(clock: ManualClock, tmp_path: Path) -> None:
    port = MemoryStore().open(clock)
    project, _ = create(port)
    (one, two) = port.reserve(2)
    port.put(one, written(tmp_path, "a.png", b"123"), "a.png", InProject(project))
    port.put(two, written(tmp_path, "b.png", b"45"), "b.png", InProject(project))

    port.trash(one)

    space = port.space()
    assert (space.quota, space.used, space.trash) == (None, 5, 3)


def test_a_trashed_project_or_folder_takes_its_files_at_once(
    store: MemoryStore, clock: ManualClock, tmp_path: Path
) -> None:
    # On Drive a folder's contents follow it 10-20 s later (528); here at once, a folder's own
    # folders too.
    port = store.open(clock)
    project, _ = create(port)
    (photo, folder, video, photos, copied) = port.reserve(5)
    port.put(photo, written(tmp_path, "a.png", b"one"), "a.png", InProject(project))
    port.export_folder(folder, "2026-11-06 09-00 x")
    port.export_folder(photos, "photos", inside=folder)
    port.put(video, written(tmp_path, "x.mp4", b"two"), "x.mp4", InExport(folder))
    port.copy(photo, copied, "001.png", InExport(photos))

    port.trash_project(project)
    port.trash(folder)

    assert port.exists(photo) is None
    assert port.exists(video) is None
    assert port.exists(copied) is None
    assert port.export_names("2026") == ()
    assert port.space().trash == 9
    with pytest.raises(NotFound):
        port.export_folder(port.reserve(1)[0], "more", inside=photos)
