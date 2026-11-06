import json
import socket
import time
from collections.abc import Iterator

import httplib2
import pytest
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError  # pyright: ignore[reportMissingTypeStubs]

from core.storage.drive.api import DriveError, DriveLost
from core.storage.drive.google import GoogleDrive, drive_error, query, quote


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
