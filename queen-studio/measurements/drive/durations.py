"""Step 4's call durations (Varsayımlar: 0.25 s a small call, 0.6 s a head file's upload, 0.3 s a
download up to 1 MB) and its "at most 8 calls at once": each kind of call the design makes, timed
one attempt at a time, the kinds taken in turn so that a slow minute falls on all of them alike.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from common import HEAD_LARGE, HEAD_SMALL, Drive, Timed, md5, media, stats, tagged
from googleapiclient.http import MediaInMemoryUpload

MB = 1024 * 1024
VIDEO = 20 * MB  # a video's upload, step 4: resumable, 16 MB chunks
CHUNK = 16 * MB


def durations(d: Drive, folder: str, rounds: int = 100, videos: int = 5) -> dict[str, Any]:
    small = d.create(folder, "small.bin", b"s", {"n": "0"}).value["id"]
    head_small = d.create(folder, "head-small.bin", tagged(0, HEAD_SMALL)).value["id"]
    head_large = d.create(folder, "head-large.bin", tagged(0, HEAD_LARGE)).value["id"]
    one_mb = d.create(folder, "one-mb.bin", tagged(0, MB)).value["id"]
    copies = d.folder("copies", folder)
    made = d.folder("made", folder)
    pool: list[str] = []
    created: list[str] = []

    def reserved(s: Any) -> Any:
        return s.files().generateIds(count=1000, space="drive", type="files")

    def create_head(s: Any) -> Any:
        if not pool:
            pool.extend(d.call(reserved).value["ids"])
        body = {"id": pool.pop(), "name": "head.bin", "parents": [made], "properties": {"n": "0"}}
        return s.files().create(body=body, media_body=media(tagged(0, HEAD_SMALL)), fields="id")

    def trash_one(s: Any) -> Any:
        return s.files().update(fileId=created.pop(), body={"trashed": True}, fields="id")

    calls: dict[str, Callable[[Any], Any]] = {
        "get_metadata": lambda s: s.files().get(fileId=small, fields="id,md5Checksum,properties"),
        "list_small_folder": lambda s: s.files().list(
            q=f"'{folder}' in parents and trashed=false",
            fields="nextPageToken,files(id,name,md5Checksum,properties,modifiedTime)",
            pageSize=1000,
        ),
        "update_properties": lambda s: s.files().update(
            fileId=small, body={"properties": {"n": str(time.time_ns())}}, fields="id"
        ),
        "update_head_110k": lambda s: s.files().update(
            fileId=head_small,
            body={"properties": {"n": str(time.time_ns())}},
            media_body=media(tagged(1, HEAD_SMALL)),
            fields="md5Checksum",
        ),
        "update_head_250k": lambda s: s.files().update(
            fileId=head_large,
            body={"properties": {"n": str(time.time_ns())}},
            media_body=media(tagged(1, HEAD_LARGE)),
            fields="md5Checksum",
        ),
        "create_head_110k_reserved_id": create_head,
        "trash": trash_one,
        "generate_ids_1000": reserved,
        "download_250k": lambda s: s.files().get_media(fileId=head_large),
        "download_1m": lambda s: s.files().get_media(fileId=one_mb),
        "copy_1m": lambda s: s.files().copy(
            fileId=one_mb, body={"name": "copy.bin", "parents": [copies]}, fields="id"
        ),
        "about": lambda s: s.about().get(fields="storageQuota"),
    }
    seconds: dict[str, list[float]] = {name: [] for name in calls}
    for name, make in calls.items():  # warm-up: the token, the connection
        result = d.call(make)
        if name == "create_head_110k_reserved_id":
            created.append(result.value["id"])
    for _ in range(rounds):
        for name, make in calls.items():
            if name == "trash" and not created:
                continue
            result = d.call(make)
            seconds[name].append(result.seconds)
            if name == "create_head_110k_reserved_id":
                created.append(result.value["id"])

    summary: dict[str, Any] = {name: stats(values) for name, values in seconds.items()}
    summary["parallel_8_get_metadata"] = parallel(d, calls["get_metadata"], rounds)
    summary["upload_video_20m_resumable"] = stats([video(d, made) for _ in range(videos)])
    return {"summary": summary, "samples": {}}


def parallel(d: Drive, make: Callable[[Any], Any], count: int, width: int = 8) -> dict[str, Any]:
    """`count` calls, `width` in flight at once: each call's time, and the whole's."""
    with ThreadPoolExecutor(width) as threads:
        list(threads.map(lambda _: d.call(make), range(width)))  # each thread's own connection
        began = time.perf_counter()
        results: list[Timed] = list(threads.map(lambda _: d.call(make), range(count)))
        wall = time.perf_counter() - began
    return {"width": width, "call_s": stats([r.seconds for r in results]), "wall_s": round(wall, 3)}


def video(d: Drive, folder: str) -> float:
    """One 20 MB file created by resumable upload in 16 MB chunks; the whole upload's time."""
    content = tagged(0, VIDEO)
    upload = MediaInMemoryUpload(
        content, mimetype="application/octet-stream", chunksize=CHUNK, resumable=True
    )
    began = time.perf_counter()
    request = (
        d.service()
        .files()
        .create(
            body={"name": "video.bin", "parents": [folder]}, media_body=upload, fields="md5Checksum"
        )
    )
    response = None
    while response is None:
        _, response = request.next_chunk()
    assert response["md5Checksum"] == md5(content), "the video arrived changed"
    return time.perf_counter() - began
