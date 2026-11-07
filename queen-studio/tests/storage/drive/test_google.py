import json
import socket
import threading
import time
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httplib2
import pytest
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError  # pyright: ignore[reportMissingTypeStubs]

from core.storage.drive.api import DriveError, DriveLost
from core.storage.drive.google import GoogleDrive, drive_error, held, query, quote


def test_a_value_in_a_query_has_its_quotes_escaped() -> None:
    # Drive's q is text: a name with a quote would end the string and change the query.
    assert quote("it's") == "it\\'s"
    assert quote("a\\b") == "a\\\\b"
    assert quote("x\\'") == "x\\\\\\'"


def test_a_query_names_the_parent_and_leaves_the_trash_out() -> None:
    assert query("p'1", folders=True, name="a'b") == (
        "'p\\'1' in parents and trashed = false"
        " and mimeType = 'application/vnd.google-apps.folder' and name = 'a\\'b'"
    )
    assert query("p", folders=False, name=None) == (
        "'p' in parents and trashed = false and mimeType != 'application/vnd.google-apps.folder'"
    )
    assert query("p", folders=None, name=None) == "'p' in parents and trashed = false"


def http_error(status: int, body: object) -> HttpError:
    content = body if isinstance(body, bytes) else json.dumps(body).encode()
    return HttpError(httplib2.Response({"status": status}), content)


def test_drives_error_keeps_its_status_reason_and_words() -> None:
    body = {
        "error": {
            "errors": [{"reason": "userRateLimitExceeded"}],
            "message": "User rate limit exceeded.",
        }
    }

    found = drive_error(http_error(403, body))

    assert (found.status, found.reason, found.said) == (
        403,
        "userRateLimitExceeded",
        "User rate limit exceeded.",
    )


def test_an_error_with_no_json_keeps_what_drive_said() -> None:
    found = drive_error(http_error(502, b"<html>Bad Gateway</html>"))

    assert (found.status, found.reason, found.said) == (502, "502", "<html>Bad Gateway</html>")


@pytest.fixture
def silent() -> Iterator[str]:
    """An address that takes the connection and never answers: a hung Drive."""
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(8)
    try:
        yield f"http://127.0.0.1:{server.getsockname()[1]}/"
    finally:
        server.close()


def drive(endpoint: str, small: float, transfer: float) -> GoogleDrive:
    # A made-up token: the request never reaches Google.
    return GoogleDrive(Credentials(token="test"), small=small, transfer=transfer, endpoint=endpoint)


def test_a_small_call_that_hangs_ends_at_its_timeout(silent: str) -> None:
    started = time.monotonic()

    with pytest.raises(DriveLost, match="timed out"):
        drive(silent, small=0.05, transfer=60).get("x", "id")

    assert time.monotonic() - started < 5


def test_a_download_that_hangs_ends_at_the_transfer_timeout(silent: str) -> None:
    started = time.monotonic()

    with pytest.raises(DriveLost, match="timed out"):
        drive(silent, small=60, transfer=0.05).download("x", 10)

    assert time.monotonic() - started < 5


def test_the_timeouts_are_thirty_seconds_and_two_minutes() -> None:
    assert GoogleDrive.SMALL == 30
    assert GoogleDrive.TRANSFER == 120


def test_a_drive_error_is_not_lost() -> None:
    assert isinstance(drive_error(http_error(404, {})), DriveError)


# -- transfers (the m534 spec) -------------------------------------------------------------------


def test_a_chunk_that_hangs_ends_at_the_transfer_timeout_and_hides_its_session(
    silent: str,
) -> None:
    # The session's upload_id is enough to go on with the upload: never in a message.
    session = f"{silent}upload/drive/v3/files?uploadType=resumable&upload_id=SECRET42"
    started = time.monotonic()

    with pytest.raises(DriveLost, match="timed out") as lost:
        drive(silent, small=60, transfer=0.05).upload_chunk(session, b"0123", 0, 10)

    assert "SECRET42" not in str(lost.value)
    assert time.monotonic() - started < 5


def test_a_stream_that_hangs_ends_at_the_transfer_timeout(silent: str) -> None:
    started = time.monotonic()

    with pytest.raises(DriveLost, match="timed out"):
        drive(silent, small=60, transfer=0.05).stream("x", 10, lambda piece: None)

    assert time.monotonic() - started < 5


def test_drives_range_says_how_many_bytes_it_holds() -> None:
    assert held("bytes=0-41") == 42
    assert held(None) == 0
    with pytest.raises(DriveError):
        held("bytes=5-9")


class Server:
    """A local Drive that answers every request as `answer` says: (status, headers, body)."""

    def __init__(self, answer: tuple[int, dict[str, str], bytes]) -> None:
        status, headers, body = answer

        class Handler(BaseHTTPRequestHandler):
            def answer(self) -> None:
                length = int(self.headers.get("Content-Length") or 0)
                self.rfile.read(length)
                self.send_response(status)
                for key, value in {**headers, "Content-Length": str(len(body))}.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(body)

            do_GET = do_PUT = do_POST = answer

            def log_message(self, format: str, *args: object) -> None:
                pass

        self.http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.http.server_address[1]}/"
        threading.Thread(target=self.http.serve_forever, args=(0.01,), daemon=True).start()

    def close(self) -> None:
        self.http.shutdown()
        self.http.server_close()


@contextmanager
def served(answer: tuple[int, dict[str, str], bytes]) -> Generator[Server]:
    server = Server(answer)
    try:
        yield server
    finally:
        server.close()


def test_a_stream_takes_no_more_than_one_byte_past_its_bound_whatever_drive_sends() -> None:
    # A server that ignores Range sends it all: the client stops one byte past the bound.
    with served((200, {}, b"x" * 100_000)) as server:
        pieces: list[bytes] = []
        drive(server.url, small=5, transfer=5).stream("x", 9, pieces.append)

        assert len(b"".join(pieces)) == 10


def test_a_chunk_drive_kept_part_of_says_so_and_a_whole_upload_is_its_file() -> None:
    with served((308, {"Range": "bytes=0-5"}, b"")) as server:
        assert drive(server.url, 5, 5).upload_chunk(f"{server.url}u", b"0123456789", 0, 20) == 6
    body = json.dumps({"id": "f1", "md5Checksum": "a" * 32, "size": "20"}).encode()
    with served((200, {"Content-Type": "application/json"}, body)) as server:
        assert drive(server.url, 5, 5).upload_status(f"{server.url}u", 20) == json.loads(body)


def test_a_transfers_error_keeps_drives_words() -> None:
    body = json.dumps(
        {"error": {"errors": [{"reason": "notFound"}], "message": "Upload session gone."}}
    ).encode()
    with (
        served((404, {"Content-Type": "application/json"}, body)) as server,
        pytest.raises(DriveError) as failed,
    ):
        drive(server.url, 5, 5).upload_status(f"{server.url}u", 20)

    assert (failed.value.status, failed.value.reason, failed.value.said) == (
        404,
        "notFound",
        "Upload session gone.",
    )


def test_a_session_starts_at_the_location_drive_gives() -> None:
    with served((200, {"Location": "https://example.invalid/s?upload_id=1"}, b"")) as server:
        started = drive(server.url, 5, 5).upload_start({"name": "a"}, 10, "id")

    assert started == "https://example.invalid/s?upload_id=1"


def test_a_transfers_error_hides_a_session_drive_quotes() -> None:
    body = json.dumps(
        {
            "error": {
                "errors": [{"reason": "badRequest"}],
                "message": "Bad chunk for /upload?upload_id=SECRET42&x=1.",
            }
        }
    ).encode()
    with (
        served((400, {"Content-Type": "application/json"}, body)) as server,
        pytest.raises(DriveError) as failed,
    ):
        drive(server.url, 5, 5).upload_status(f"{server.url}u", 20)

    assert "SECRET42" not in failed.value.said


def test_an_upload_answer_past_its_byte_budget_is_refused() -> None:
    with (
        served((200, {"Content-Type": "application/json"}, b"[" + b" " * 100_000 + b"]")) as server,
        pytest.raises(DriveError, match="past"),
    ):
        drive(server.url, 5, 5).upload_status(f"{server.url}u", 20)


def test_a_download_drive_redirects_is_not_followed() -> None:
    with (
        served((302, {"Location": "https://example.invalid/elsewhere"}, b"moved")) as server,
        pytest.raises(DriveError, match="302"),
    ):
        drive(server.url, 5, 5).stream("x", 9, lambda piece: None)
