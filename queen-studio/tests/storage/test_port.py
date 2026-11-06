import ast
import inspect
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import get_args

import pytest

from core.storage.port import (
    WRITES,
    Op,
    Port,
    check_count,
    check_project,
    check_time,
)

CORE = Path(__file__).resolve().parents[2] / "core"


@pytest.mark.parametrize("project", ["k3v9q2mz7a", "0000000000"])
def test_a_project_id_is_ten_lowercase_letters_or_digits(project: str) -> None:
    check_project(project)


@pytest.mark.parametrize(
    "project", ["", "k3v9q2mz7", "k3v9q2mz7ab", "K3V9Q2MZ7A", "../k3v9q2m", "k3v9q2mz7\n"]
)
def test_any_other_id_is_refused_before_the_store_is_asked(project: str) -> None:
    # It comes from the address: unchecked, it would name a file (CODE-STANDARD, Cost).
    with pytest.raises(ValueError, match="project id"):
        check_project(project)


def test_a_time_is_utc_to_the_second() -> None:
    check_time(datetime(2026, 11, 6, 9, 12, tzinfo=UTC))
    check_time(datetime(2026, 11, 6, 9, 12, tzinfo=timezone(timedelta(0))))


@pytest.mark.parametrize(
    "time",
    [
        datetime(2026, 11, 6, 9, 12),
        datetime(2026, 11, 6, 12, 12, tzinfo=timezone(timedelta(hours=3))),
        datetime(2026, 11, 6, 9, 12, 0, 500_000, tzinfo=UTC),
    ],
    ids=["naive", "not-utc", "under-a-second"],
)
def test_any_other_time_is_refused(time: datetime) -> None:
    # Step 6 writes a time to the second, in UTC; Drive's properties are text, so a finer time
    # would come back other than it went in.
    with pytest.raises(ValueError):
        check_time(time)


def test_a_count_is_held_to_its_bound() -> None:
    check_count("n", 1, 3)
    check_count("n", 3, 3)

    with pytest.raises(ValueError, match="1 to 3"):
        check_count("n", 0, 3)
    with pytest.raises(ValueError, match="1 to 3"):
        check_count("n", 4, 3)


def test_every_operation_of_the_port_is_named_and_none_deletes() -> None:
    # The in-memory store injects faults by these names, so a new operation cannot miss them; and
    # nothing is deleted for good, only trashed (FOUNDATION 1).
    operations = {name for name, _ in inspect.getmembers(Port) if not name.startswith("_")}

    assert operations == set(get_args(Op))
    assert operations > WRITES
    assert not [name for name in operations if "delete" in name or "remove" in name]


def _storage_imports(path: Path) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
        elif isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
    return {name for name in found if name.startswith("core.storage")}


def test_the_core_reaches_its_data_only_through_the_port() -> None:
    # FOUNDATION 3: a group is handed a Port; which adapter stands behind it is the start file's.
    outside = [path for path in CORE.rglob("*.py") if "storage" not in path.relative_to(CORE).parts]
    reaching = {
        str(path.relative_to(CORE)): sorted(imports - {"core.storage.port"})
        for path in outside
        if (imports := _storage_imports(path)) - {"core.storage.port"}
    }

    assert outside
    assert reaching == {}
