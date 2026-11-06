"""The start file: the one place the real gates are wired, and where the core is opened.

From the repo's root, `queen-studio/.venv/Scripts/python queen-studio/main.py` opens it at
http://127.0.0.1:8200.
"""

import logging
from pathlib import Path
from typing import Any

import uvicorn
from starlette.types import ASGIApp

from core.about import NAME, VERSION
from core.disk.identity import UnreadableIdentity, core_id
from core.log import start_log
from core.server import create_api, serve

HERE = Path(__file__).resolve().parent
# The machine's own disk: core.json and the log. On this machine the repo's git-ignored tmp/; where
# it is on Colab, and whether the notebook passes it in, is v1-25's.
DISK = HERE.parent / "tmp" / NAME
UI = HERE / "ui" / "dist"
# queen-editor has 8000, queen-agent 8100 and ComfyUI 8188: all four can run on one machine.
HOST, PORT = "127.0.0.1", 8200
# An outer guard only: h11 refuses a head still incomplete past this many bytes, so a head that
# trickles in cannot fill memory, but one that arrives in a single read is parsed at any size
# (tried by QA, 530). The bound a list's query rests on is the core's own, core.query.QUERY_BYTES.
# h11 is named rather than left to Uvicorn, which picks httptools when it is installed.
HEAD_BYTES = 16 * 1024
# log_config=None: Uvicorn sets up no logging of its own, so its lines reach start_log's file.
SERVER: dict[str, Any] = {
    "host": HOST,
    "port": PORT,
    "http": "h11",
    "h11_max_incomplete_event_size": HEAD_BYTES,
    "log_config": None,
}

log = logging.getLogger("core")


def build(disk: Path, ui: Path) -> ASGIApp:
    start_log(disk / "core.log")
    try:
        identity = core_id(disk)
    except UnreadableIdentity as unreadable:
        log.error(
            "%s did not start. %s. Nothing was written to it: a new identity would orphan every "
            "queue whose runner is the old one. Fix the file, or remove it to start with a new "
            "identity; the queues the old one ran then need resume.",
            NAME,
            unreadable,
        )
        # Said once, by the log's line on the console; the exit only carries the failure.
        raise SystemExit(1) from unreadable
    log.info("%s %s, core %s", NAME, VERSION, identity)
    return serve(create_api(identity), ui)


if __name__ == "__main__":
    uvicorn.run(build(DISK, UI), **SERVER)
