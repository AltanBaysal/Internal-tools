"""Writes the core's OpenAPI document where the UI generates its types from.

    queen-studio/.venv/Scripts/python queen-studio/write_openapi.py

The document `/api/openapi.json` serves, taken from the app without opening a server: its info,
paths and components are the same, and only the served copy adds `"servers": [{"url": "/api"}]`,
from the mount, which no type depends on. The UI's `npm test` and `npm run build` turn it into
src/api/schema.d.ts, and tsc checks the UI against that.
"""

import json
from pathlib import Path

from core.server import create_api

TARGET = Path(__file__).resolve().parent / "ui" / "src" / "api" / "openapi.json"


def render() -> str:
    # The identity is no part of the document's shape.
    return json.dumps(create_api(core_id="").openapi(), indent=2, ensure_ascii=False) + "\n"


def write(target: Path) -> None:
    # A generated file: one cut short by a crash is written again by the next run.
    target.write_text(render(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    write(TARGET)
