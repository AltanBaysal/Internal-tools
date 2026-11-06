import json
import re
from pathlib import Path

import pytest

from core.disk.identity import UnreadableIdentity, core_id


def test_the_first_start_writes_an_identity(tmp_path: Path) -> None:
    disk = tmp_path / "disk"
    made = core_id(disk)

    assert re.fullmatch(r"[a-z0-9]{10}", made)
    assert json.loads((disk / "core.json").read_text(encoding="utf-8")) == {"core": made}


def test_a_restart_keeps_the_identity(tmp_path: Path) -> None:
    first = core_id(tmp_path)

    assert core_id(tmp_path) == first


def test_two_machines_get_two_identities(tmp_path: Path) -> None:
    assert core_id(tmp_path / "one") != core_id(tmp_path / "two")


def test_no_temporary_file_is_left_beside_it(tmp_path: Path) -> None:
    core_id(tmp_path)

    assert [path.name for path in tmp_path.iterdir()] == ["core.json"]


@pytest.mark.parametrize(
    "content",
    ['{"core": "k3v9q2mz', "[]", '{"other": "x"}', '{"core": 7}', '{"core": ""}', "\udcff"],
    ids=["cut", "not-an-object", "no-core", "not-a-string", "empty", "not-utf8"],
)
def test_an_unreadable_identity_stops_the_start_and_is_left_as_it_was(
    tmp_path: Path, content: str
) -> None:
    # A new identity would orphan every queue whose runner is the old one (step 4), so the file is
    # never taken as missing and written over.
    path = tmp_path / "core.json"
    raw = content.encode("utf-8", "surrogateescape")
    path.write_bytes(raw)

    with pytest.raises(UnreadableIdentity) as stopped:
        core_id(tmp_path)

    assert str(path) in str(stopped.value)
    assert path.read_bytes() == raw
