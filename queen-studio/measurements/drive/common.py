"""What every Drive measurement shares: the test account's client, one per thread, polite calls that
time each attempt, statistics and writing results.

The token's path comes from the command line. Nothing here prints the token or anything read from it
(FOUNDATION 6); a Drive error is kept in Drive's own words, which never carry it.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import socket
import statistics
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import google_auth_httplib2
import httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaInMemoryUpload, build_http

FOLDER = "application/vnd.google-apps.folder"
HEAD_SMALL = 110_000  # a 1,000-frame project's head file, compressed (step 4)
HEAD_LARGE = 250_000  # a 20,000-frame one's
RATE_REASONS = {"userRateLimitExceeded", "rateLimitExceeded"}
BACKOFF_CAP = 32.0  # step 4, Değerlendirme 9: exponential, up to ~32 s, with jitter


def reason(error: HttpError) -> str:
    """Drive's own reason for an error, e.g. userRateLimitExceeded; its status if it gave none."""
    try:
        body = json.loads(error.content)
        return str(body["error"]["errors"][0]["reason"])
    except (ValueError, KeyError, IndexError, TypeError):
        return str(error.resp.status)


def message(error: HttpError) -> str:
    try:
        return str(json.loads(error.content)["error"]["message"])
    except (ValueError, KeyError, TypeError):
        return error.content.decode("utf-8", "replace")[:300]


def is_rate_limited(error: HttpError) -> bool:
    return error.resp.status == 429 or (error.resp.status == 403 and reason(error) in RATE_REASONS)


def retryable(error: Exception) -> bool:
    if isinstance(error, HttpError):
        return is_rate_limited(error) or error.resp.status >= 500
    return isinstance(error, (OSError, socket.timeout, httplib2.HttpLib2Error))


@dataclass
class Timed:
    value: Any
    seconds: float  # the attempt that succeeded, without the waits before it
    retries: int


class Drive:
    """The test account's Drive. `service()` gives each thread its own client: httplib2 is not
    thread-safe, and a separate client is also a separate connection, as a second Colab would be."""

    def __init__(self, token_path: str) -> None:
        self.creds = Credentials.from_authorized_user_file(token_path)
        self._local = threading.local()
        self._lock = threading.Lock()
        self.retries: dict[str, int] = {}

    def service(self) -> Any:
        svc = getattr(self._local, "svc", None)
        if svc is None:
            # build_http, not a bare Http: it stops httplib2 taking a resumable upload's 308 for a
            # redirect.
            http = google_auth_httplib2.AuthorizedHttp(self.creds, http=build_http())
            svc = build("drive", "v3", http=http, cache_discovery=False)
            self._local.svc = svc
        return svc

    def bearer(self) -> str:
        """The access token, for the one experiment that speaks raw HTTP to cut an upload midway."""
        with self._lock:
            if not self.creds.valid:
                self.creds.refresh(Request())
            return str(self.creds.token)

    def call(self, make: Callable[[Any], Any], tries: int = 8) -> Timed:
        """Runs `make(service).execute()`, backing off on Drive's rate limit and its 5xx as its
        guide asks. Each retry is counted by Drive's reason."""
        svc = self.service()
        for attempt in range(tries):
            started = time.perf_counter()
            try:
                value = make(svc).execute()
                return Timed(value, time.perf_counter() - started, attempt)
            except Exception as error:
                if not retryable(error) or attempt == tries - 1:
                    raise
                key = reason(error) if isinstance(error, HttpError) else type(error).__name__
                with self._lock:
                    self.retries[key] = self.retries.get(key, 0) + 1
                time.sleep(min(2**attempt, BACKOFF_CAP) + random.random())
        raise AssertionError("unreachable")

    def folder(self, name: str, parent: str | None = None) -> str:
        body: dict[str, Any] = {"name": name, "mimeType": FOLDER}
        if parent:
            body["parents"] = [parent]
        return self.call(lambda s: s.files().create(body=body, fields="id")).value["id"]

    def create(
        self,
        parent: str,
        name: str,
        content: bytes,
        properties: dict[str, str] | None = None,
        file_id: str | None = None,
    ) -> Timed:
        body: dict[str, Any] = {"name": name, "parents": [parent]}
        if properties:
            body["properties"] = properties
        if file_id:
            body["id"] = file_id
        return self.call(
            lambda s: s.files().create(
                body=body, media_body=media(content), fields="id,md5Checksum,version"
            )
        )

    def update(
        self, file_id: str, content: bytes, properties: dict[str, str] | None = None
    ) -> Timed:
        """Content and properties in one multipart `files.update`, as step 4 writes a head file."""
        body = {"properties": properties} if properties else {}
        return self.call(
            lambda s: s.files().update(
                fileId=file_id, body=body, media_body=media(content), fields="md5Checksum,version"
            )
        )

    def listing(self, query: str, fields: str, page_size: int = 1000) -> list[list[dict[str, Any]]]:
        """Every page of a listing, as the pages Drive gave."""
        pages: list[list[dict[str, Any]]] = []
        token: str | None = None
        while True:
            page = self.call(
                lambda s, t=token: s.files().list(
                    q=query,
                    fields=f"nextPageToken,files({fields})",
                    pageSize=page_size,
                    pageToken=t,
                )
            ).value
            pages.append(page.get("files", []))
            token = page.get("nextPageToken")
            if not token:
                return pages

    def quota(self) -> dict[str, int]:
        found = self.call(lambda s: s.about().get(fields="storageQuota")).value["storageQuota"]
        return {key: int(value) for key, value in found.items()}

    def trash(self, file_id: str) -> Timed:
        return self.call(
            lambda s: s.files().update(fileId=file_id, body={"trashed": True}, fields="id")
        )


def media(content: bytes) -> MediaInMemoryUpload:
    return MediaInMemoryUpload(content, mimetype="application/octet-stream", resumable=False)


def md5(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


def tagged(n: int, size: int) -> bytes:
    """`size` bytes carrying `n`: a header line, then random bytes, as incompressible as a gzipped
    head file. The header holds the rest's length and md5, so a half-read copy cannot pass for
    whole."""
    payload = os.urandom(size)
    header = json.dumps({"n": n, "len": len(payload), "md5": md5(payload)}).encode()
    return header + b"\n" + payload


def untag(content: bytes) -> int:
    """`n` from a `tagged` copy; raises ValueError if the copy is not whole."""
    header, _, payload = content.partition(b"\n")
    found = json.loads(header)
    if len(payload) != found["len"] or md5(payload) != found["md5"]:
        raise ValueError(f"partial: {len(payload)} of {found['len']} bytes")
    return int(found["n"])


def stats(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"n": 0}
    ordered = sorted(values)

    def pick(q: float) -> float:
        return round(ordered[min(len(ordered) - 1, int(q * len(ordered)))], 3)

    return {
        "n": len(ordered),
        "min": round(ordered[0], 3),
        "p50": pick(0.5),
        "p90": pick(0.9),
        "p99": pick(0.99),
        "max": round(ordered[-1], 3),
        "mean": round(statistics.fmean(ordered), 3),
    }


def write_json(path: Path, data: Any) -> None:
    """Whole or not at all: to a temporary file beside it, then replaced."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)
