import json
from pathlib import Path

import write_openapi
from core.server import create_api


def test_the_rendered_document_is_the_cores() -> None:
    assert json.loads(write_openapi.render()) == create_api(core_id="").openapi()


def test_write_puts_the_document_in_place(tmp_path: Path) -> None:
    target = tmp_path / "openapi.json"

    write_openapi.write(target)

    assert target.read_text(encoding="utf-8") == write_openapi.render()
    assert [path.name for path in tmp_path.iterdir()] == ["openapi.json"]


def test_the_uis_copy_is_current() -> None:
    # The UI's types are generated from this copy: a core change it does not carry is a UI built
    # against the old API.
    committed = write_openapi.TARGET.read_text(encoding="utf-8")

    assert committed == write_openapi.render(), (
        "ui/src/api/openapi.json is not the core's: "
        "run queen-studio/.venv/Scripts/python queen-studio/write_openapi.py"
    )
