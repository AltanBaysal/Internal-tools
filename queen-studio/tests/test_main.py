import json
from pathlib import Path

import pytest

import main
from core.about import NAME, VERSION
from tests.contract import checked_client

pytestmark = pytest.mark.usefixtures("restore_root_logger")


@pytest.fixture
def ui(tmp_path: Path) -> Path:
    ui = tmp_path / "dist"
    ui.mkdir()
    (ui / "index.html").write_text("<p>the page</p>", encoding="utf-8")
    return ui


def test_health_answers_with_the_identity_on_the_disk(tmp_path: Path, ui: Path) -> None:
    disk = tmp_path / "disk"
    client = checked_client(main.build(disk, ui), api="/api")

    identity = json.loads((disk / "core.json").read_text(encoding="utf-8"))["core"]
    assert client.get("/api/health").json()["core"] == identity
    assert client.get("/").text == "<p>the page</p>"


def test_the_start_is_in_the_log_on_the_disk(tmp_path: Path, ui: Path) -> None:
    disk = tmp_path / "disk"
    main.build(disk, ui)

    identity = json.loads((disk / "core.json").read_text(encoding="utf-8"))["core"]
    assert f"INFO core: {NAME} {VERSION}, core {identity}\n" in (disk / "core.log").read_text(
        encoding="utf-8"
    )


def test_an_unreadable_identity_ends_the_start_saying_why_and_what_to_do(
    tmp_path: Path, ui: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    disk = tmp_path / "disk"
    disk.mkdir()
    (disk / "core.json").write_text("{", encoding="utf-8")

    with pytest.raises(SystemExit) as stopped:
        main.build(disk, ui)

    assert stopped.value.code == 1
    logged = (disk / "core.log").read_text(encoding="utf-8")
    assert str(disk / "core.json") in logged
    assert "orphan" in logged and "resume" in logged
    # Said once: the log's console line, not again by the exit.
    assert capsys.readouterr().err.count(str(disk / "core.json")) == 1
