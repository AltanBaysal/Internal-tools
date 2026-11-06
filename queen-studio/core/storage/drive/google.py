"""DriveApi on Drive's official Python client (step 5), as the measurements reached it (528).

Each call has a socket timeout — 30 s for small ones, 120 s for an upload or a download — so a
hung connection ends and the adapter's budget decides what follows. httplib2 is not thread-safe,
so each thread has its own client, one per timeout. The library's own retries are off: the
adapter waits on its clock.

The token's path is handed in; nothing here prints it or anything read from it (FOUNDATION 6). A
Drive error is kept in Drive's words, which never carry it: the token is in the request's header.
"""

import json
import threading
from pathlib import Path
from typing import Any, ClassVar, Literal

import httplib2
from google.auth.exceptions import RefreshError, TransportError
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import AuthorizedHttp  # pyright: ignore[reportMissingTypeStubs]
from googleapiclient.discovery import (  # pyright: ignore[reportMissingTypeStubs]
    build,  # pyright: ignore[reportUnknownVariableType]
)
from googleapiclient.errors import HttpError  # pyright: ignore[reportMissingTypeStubs]
from googleapiclient.http import (  # pyright: ignore[reportMissingTypeStubs]
    MediaInMemoryUpload,
    build_http,
)

from core.storage.drive.api import FOLDER, PAGE, DriveError, DriveLost, Page

Kind = Literal["small", "transfer"]


def quote(value: str) -> str:
    """A value inside a `q` string's quotes."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def query(parent: str, folders: bool | None, name: str | None) -> str:
    parts = [f"'{quote(parent)}' in parents", "trashed = false"]
    if folders is not None:
        parts.append(f"mimeType {'=' if folders else '!='} '{FOLDER}'")
    if name is not None:
        parts.append(f"name = '{quote(name)}'")
    return " and ".join(parts)


def drive_error(failed: HttpError) -> DriveError:
    status = int(failed.resp.status)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    content: bytes = failed.content  # pyright: ignore[reportUnknownMemberType]
    try:
        error = json.loads(content)["error"]
        return DriveError(status, str(error["errors"][0]["reason"]), str(error["message"]))
    except (ValueError, KeyError, IndexError, TypeError):
        return DriveError(status, str(status), content.decode("utf-8", "replace")[:300])


class GoogleDrive:
    SMALL: ClassVar[float] = 30
    TRANSFER: ClassVar[float] = 120

    def __init__(
        self,
        credentials: Credentials,
        small: float = SMALL,
        transfer: float = TRANSFER,
        endpoint: str | None = None,
    ) -> None:
        self._credentials = credentials
        self._timeouts: dict[Kind, float] = {"small": small, "transfer": transfer}
        self._endpoint = endpoint
        self._local = threading.local()

    @classmethod
    def from_token(cls, path: Path) -> "GoogleDrive":
        """The test account's authorized-user file (`.secrets/drive-token.json`); read here only."""
        return cls(Credentials.from_authorized_user_file(str(path)))  # pyright: ignore[reportUnknownMemberType]

    def get(self, file_id: str, fields: str) -> dict[str, Any]:
        files = self._files("small")
        return _object(_run(files.get(fileId=file_id, fields=fields)))

    def download(self, file_id: str, most: int) -> bytes:
        request = self._files("transfer").get_media(fileId=file_id)
        # Never more than one byte past the caller's bound is fetched.
        request.headers["Range"] = f"bytes=0-{most}"
        try:
            found = _run(request)
        except DriveError as failed:
            if failed.status == 416:  # an empty file has no byte 0
                return b""
            raise
        if not isinstance(found, bytes):
            raise DriveError(502, "badResponse", "Drive's download gave no bytes.")
        return found

    def children(
        self,
        parent: str,
        fields: str,
        *,
        folders: bool | None = None,
        name: str | None = None,
        page: str | None = None,
    ) -> Page:
        found = _object(
            _run(
                self._files("small").list(
                    q=query(parent, folders, name),
                    fields=f"nextPageToken,files({fields})",
                    pageSize=PAGE,
                    pageToken=page,
                    orderBy="createdTime",
                    spaces="drive",
                )
            )
        )
        files = found.get("files", [])
        token = found.get("nextPageToken")
        if not isinstance(files, list) or not all(isinstance(each, dict) for each in files):  # pyright: ignore[reportUnknownVariableType]
            raise DriveError(502, "badResponse", "Drive's listing gave no list of files.")
        return Page(files, token if isinstance(token, str) else None)  # pyright: ignore[reportUnknownArgumentType]

    def create(
        self, metadata: dict[str, Any], content: bytes | None, fields: str
    ) -> dict[str, Any]:
        files = self._files("small" if content is None else "transfer")
        return _object(
            _run(files.create(body=metadata, media_body=_media(content, metadata), fields=fields))
        )

    def update(
        self, file_id: str, metadata: dict[str, Any], content: bytes | None, fields: str
    ) -> dict[str, Any]:
        files = self._files("small" if content is None else "transfer")
        media = _media(content, metadata)
        return _object(
            _run(files.update(fileId=file_id, body=metadata, media_body=media, fields=fields))
        )

    def generate_ids(self, count: int) -> list[str]:
        found = _object(
            _run(self._files("small").generateIds(count=count, space="drive", type="files"))
        )
        ids = found.get("ids")
        if not isinstance(ids, list) or not all(isinstance(each, str) for each in ids):  # pyright: ignore[reportUnknownVariableType]
            raise DriveError(502, "badResponse", "Drive's generateIds gave no list of ids.")
        return ids  # pyright: ignore[reportUnknownVariableType]

    def _files(self, kind: Kind) -> Any:
        services: dict[Kind, Any] | None = getattr(self._local, "services", None)
        if services is None:
            services = {}
            self._local.services = services
        if kind not in services:
            # build_http, not a bare Http: it keeps httplib2 from taking a resumable upload's
            # 308 for a redirect.
            http: Any = build_http()
            http.timeout = self._timeouts[kind]
            options = None if self._endpoint is None else {"api_endpoint": self._endpoint}
            services[kind] = build(
                "drive",
                "v3",
                http=AuthorizedHttp(self._credentials, http=http),
                cache_discovery=False,
                static_discovery=True,
                client_options=options,
            )
        return services[kind].files()


def _run(request: Any) -> Any:
    try:
        return request.execute(num_retries=0)
    except HttpError as failed:
        raise drive_error(failed) from None
    except RefreshError as failed:
        raise DriveError(401, "authError", str(failed)) from None
    except (OSError, httplib2.HttpLib2Error, TransportError) as failed:
        raise DriveLost(f"{type(failed).__name__}: {failed}") from None


def _media(content: bytes | None, metadata: dict[str, Any]) -> Any:
    if content is None:
        return None
    kind = str(metadata.get("mimeType", "application/octet-stream"))
    return MediaInMemoryUpload(content, mimetype=kind, resumable=False)


def _object(found: Any) -> dict[str, Any]:
    if not isinstance(found, dict):
        raise DriveError(502, "badResponse", "Drive's answer is not a JSON object.")
    return found  # pyright: ignore[reportUnknownVariableType]
