import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
import uvicorn
from starlette.types import Receive, Scope, Send
from uvicorn.server import ServerState

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


class Transport:
    """What the server's protocol writes to, in place of a socket."""

    def __init__(self) -> None:
        self.written = b""
        self.closed = False

    def get_extra_info(self, name: str, default: Any = None) -> Any:
        return ("127.0.0.1", 8200) if name in ("peername", "sockname") else default

    def write(self, data: bytes) -> None:
        self.written += data

    def close(self) -> None:
        self.closed = True

    def is_closing(self) -> bool:
        return self.closed


async def nothing(scope: Scope, receive: Receive, send: Send) -> None:
    raise AssertionError("the app was reached")


def test_the_server_refuses_an_unfinished_head_past_its_guard() -> None:
    # Only a head still incomplete past the guard: one that arrives whole is parsed at any size, and
    # the core's own QUERY_BYTES bounds the query (tests/test_query.py). Set small here.
    options: dict[str, Any] = {**main.SERVER, "h11_max_incomplete_event_size": 64}
    config = uvicorn.Config(nothing, **options)
    config.load()
    loop = asyncio.new_event_loop()
    try:
        protocol_class: Any = config.http_protocol_class
        protocol = protocol_class(
            config=config, server_state=ServerState(), app_state={}, _loop=loop
        )
        transport = Transport()
        protocol.connection_made(transport)

        protocol.data_received(b"GET /api/notes?" + b"a" * 100)

        assert transport.written.startswith(b"HTTP/1.1 400 ")
        assert transport.closed
    finally:
        loop.close()


def test_the_server_is_h11_with_its_16_kb_guard() -> None:
    assert (main.SERVER["http"], main.SERVER["h11_max_incomplete_event_size"]) == ("h11", 16384)
