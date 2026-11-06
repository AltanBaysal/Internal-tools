"""Step 4 §14, the assumptions the write path rests on: a read by id right after another client's
write, content and properties written together, an update cut midway, and how late a listing is.

Each function takes the Drive and a folder of its own and returns {"summary", "samples"}.
"""

from __future__ import annotations

import http.client
import json
import queue
import threading
import time
from typing import Any

from common import HEAD_LARGE, HEAD_SMALL, Drive, md5, stats, tagged, untag
from googleapiclient.http import MediaInMemoryUpload


def read_after_write(d: Drive, folder: str, writes: int = 200) -> dict[str, Any]:
    """A writes a small file and tells B; B reads its md5 by id at once, on its own connection."""
    first = b"0"
    file_id = d.create(folder, "raw.bin", first).value["id"]
    handoff: queue.Queue[tuple[int, str, float] | None] = queue.Queue()
    done: queue.Queue[None] = queue.Queue()
    samples: list[dict[str, Any]] = []

    def reader() -> None:
        while (item := handoff.get()) is not None:
            n, written, at = item
            got = d.call(lambda s: s.files().get(fileId=file_id, fields="md5Checksum,version"))
            fresh = got.value["md5Checksum"] == written
            samples.append({"n": n, "fresh": fresh, "after_s": round(time.perf_counter() - at, 3)})
            done.put(None)

    thread = threading.Thread(target=reader)
    thread.start()
    md5_matches = 0
    write_seconds: list[float] = []
    for n in range(1, writes + 1):
        content = f"{n}:{time.time_ns()}".encode()
        wrote = d.update(file_id, content)
        write_seconds.append(wrote.seconds)
        md5_matches += wrote.value["md5Checksum"] == md5(content)
        handoff.put((n, wrote.value["md5Checksum"], time.perf_counter()))
        done.get()
    handoff.put(None)
    thread.join()
    stale = [s["n"] for s in samples if not s["fresh"]]
    return {
        "summary": {
            "writes": writes,
            "stale_reads": len(stale),
            "stale_at": stale,
            "update_returns_local_md5": md5_matches,
            # B asks the moment A's write is answered; this is how long after that B had its answer.
            "read_answered_after_write_s": stats([s["after_s"] for s in samples]),
            "write_s": stats(write_seconds),
        },
        "samples": samples,
    }


def content_and_properties(d: Drive, folder: str, writes: int = 200) -> dict[str, Any]:
    """One writer puts the same counter in the content and in a property, in one multipart update;
    three readers watch: metadata by id, the folder's listing (what the main list reads) and the
    content itself. In one metadata answer, md5 and property must name the same write; a download
    must be whole."""
    file_id = d.create(folder, "head.bin", tagged(0, HEAD_SMALL), {"n": "0"}).value["id"]
    by_md5: dict[str, int] = {}
    stop = threading.Event()
    seen: dict[str, list[tuple[str, str]]] = {"get": [], "list": []}
    downloads = {"whole": 0, "partial": 0, "errors": []}

    def by_id() -> None:
        while not stop.is_set():
            got = d.call(lambda s: s.files().get(fileId=file_id, fields="md5Checksum,properties"))
            seen["get"].append((got.value["md5Checksum"], got.value["properties"]["n"]))

    def by_list() -> None:
        query = f"'{folder}' in parents and trashed=false"
        while not stop.is_set():
            for page in d.listing(query, "id,md5Checksum,properties"):
                for found in page:
                    if found["id"] == file_id:
                        seen["list"].append((found["md5Checksum"], found["properties"]["n"]))

    def by_content() -> None:
        while not stop.is_set():
            content = d.call(lambda s: s.files().get_media(fileId=file_id)).value
            try:
                untag(content)
                downloads["whole"] += 1
            except ValueError as error:
                downloads["partial"] += 1
                downloads["errors"].append(str(error))

    first = d.call(lambda s: s.files().get(fileId=file_id, fields="md5Checksum")).value
    by_md5[first["md5Checksum"]] = 0
    readers = [threading.Thread(target=f) for f in (by_id, by_list, by_content)]
    for reader in readers:
        reader.start()
    for n in range(1, writes + 1):
        content = tagged(n, HEAD_SMALL)
        by_md5[md5(content)] = n
        d.update(file_id, content, {"n": str(n)})
    stop.set()
    for reader in readers:
        reader.join()

    def check(pairs: list[tuple[str, str]]) -> dict[str, int]:
        unknown = sum(m not in by_md5 for m, _ in pairs)
        apart = sum(m in by_md5 and by_md5[m] != int(p) for m, p in pairs)
        return {"reads": len(pairs), "md5_and_property_apart": apart, "unknown_md5": unknown}

    return {
        "summary": {
            "writes": writes,
            "by_id": check(seen["get"]),
            "by_list": check(seen["list"]),
            "downloads": {"whole": downloads["whole"], "partial": downloads["partial"]},
        },
        "samples": {"download_errors": downloads["errors"][:20]},
    }


BOUNDARY = "m528-boundary"


def multipart_body(content: bytes, properties: dict[str, str]) -> bytes:
    meta = json.dumps({"properties": properties}).encode()
    return b"".join(
        [
            f"--{BOUNDARY}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode(),
            meta,
            f"\r\n--{BOUNDARY}\r\nContent-Type: application/octet-stream\r\n\r\n".encode(),
            content,
            f"\r\n--{BOUNDARY}--\r\n".encode(),
        ]
    )


def send_cut(d: Drive, file_id: str, body: bytes, cut: int) -> None:
    """Sends a multipart update's headers and its first `cut` bytes, then drops the connection
    without reading an answer, as a Colab losing its network would."""
    connection = http.client.HTTPSConnection("www.googleapis.com", timeout=60)
    path = f"/upload/drive/v3/files/{file_id}?uploadType=multipart&fields=md5Checksum"
    connection.putrequest("PATCH", path)
    connection.putheader("Authorization", f"Bearer {d.bearer()}")
    connection.putheader("Content-Type", f"multipart/related; boundary={BOUNDARY}")
    connection.putheader("Content-Length", str(len(body)))
    connection.endheaders()
    connection.send(body[:cut])
    connection.close()


def state(d: Drive, file_id: str) -> tuple[str, str]:
    got = d.call(lambda s: s.files().get(fileId=file_id, fields="md5Checksum,properties")).value
    return got["md5Checksum"], got["properties"]["n"]


def cut_upload(d: Drive, folder: str, repeats: int = 5, settle: float = 3.0) -> dict[str, Any]:
    """An existing file's update cut midway: does it stay as it was? Multipart (the head file) at
    four cut points, then the whole body sent with no answer read (step 4's unconfirmed write), then
    a resumable update stopped after its first chunk (large uploads)."""
    old = tagged(0, HEAD_LARGE)
    file_id = d.create(folder, "cut.bin", old, {"n": "0"}).value["id"]
    trials: list[dict[str, Any]] = []
    n = 0
    for fraction in (0.1, 0.5, 0.9, "all_but_one"):
        for _ in range(repeats):
            n += 1
            body = multipart_body(tagged(n, HEAD_LARGE), {"n": str(n)})
            cut = len(body) - 1 if fraction == "all_but_one" else int(len(body) * float(fraction))
            send_cut(d, file_id, body, cut)
            time.sleep(settle)
            unchanged = state(d, file_id)[0] == md5(old)
            trials.append({"cut": fraction, "n": n, "unchanged": unchanged})
    still_old = state(d, file_id)[0] == md5(old)
    downloaded_old = d.call(lambda s: s.files().get_media(fileId=file_id)).value == old

    unanswered: list[dict[str, Any]] = []
    for _ in range(repeats):
        n += 1
        new = tagged(n, HEAD_LARGE)
        send_cut(d, file_id, multipart_body(new, {"n": str(n)}), cut=10**9)
        started = time.perf_counter()
        applied_after = None
        while time.perf_counter() - started < 30:
            if state(d, file_id)[0] == md5(new):
                applied_after = round(time.perf_counter() - started, 3)
                break
            time.sleep(0.5)
        unanswered.append({"n": n, "applied_after_s": applied_after})

    resumable = resumable_cut(d, folder, repeats)
    partial_left_old = sum(t["unchanged"] for t in trials)
    return {
        "summary": {
            "multipart_cut_trials": len(trials),
            "multipart_cut_left_old": partial_left_old,
            "old_after_all_cuts": still_old and downloaded_old,
            "whole_body_unanswered_applied": sum(
                u["applied_after_s"] is not None for u in unanswered
            ),
            "whole_body_unanswered_trials": len(unanswered),
            "whole_body_applied_after_s": stats(
                [u["applied_after_s"] for u in unanswered if u["applied_after_s"] is not None]
            ),
            "resumable": resumable,
        },
        "samples": {"multipart": trials, "unanswered": unanswered},
    }


def resumable_cut(d: Drive, folder: str, repeats: int) -> dict[str, Any]:
    chunk = 1024 * 1024
    old = tagged(0, 2 * chunk)
    file_id = d.create(folder, "cut-resumable.bin", old).value["id"]
    left_old = 0
    finished_new = False
    for n in range(1, repeats + 1):
        new = tagged(n, 2 * chunk)
        upload = MediaInMemoryUpload(
            new, mimetype="application/octet-stream", chunksize=chunk, resumable=True
        )
        request = (
            d.service().files().update(fileId=file_id, media_body=upload, fields="md5Checksum")
        )
        progress, response = request.next_chunk()
        assert response is None and progress is not None, "the first chunk finished the upload"
        time.sleep(1)
        found = d.call(lambda s: s.files().get(fileId=file_id, fields="md5Checksum")).value
        left_old += found["md5Checksum"] == md5(old)
        if n == repeats:  # the last session is finished, to show the upload itself worked
            while response is None:
                _, response = request.next_chunk()
            finished_new = response["md5Checksum"] == md5(new)
    return {"trials": repeats, "left_old_after_first_chunk": left_old, "finished_new": finished_new}


def list_delay(d: Drive, folder: str, trials: int = 100, every: float = 0.5) -> dict[str, Any]:
    """How long after a write the folder's listing shows it, with its md5 and properties: a new file
    (a new project) and an update (a changed project). Listed at once, then every `every` s."""
    query = f"'{folder}' in parents and trashed=false"
    fields = "id,md5Checksum,properties"
    updated_id = d.create(folder, "listed.bin", b"0", {"n": "0"}).value["id"]
    results: dict[str, list[dict[str, Any]]] = {"create": [], "update": []}
    has_fields = True
    for kind in ("create", "update"):
        for n in range(1, trials + 1):
            content = f"{kind}:{n}:{time.time_ns()}".encode()
            if kind == "create":
                file_id = d.create(folder, f"new-{n}.bin", content, {"n": str(n)}).value["id"]
            else:
                file_id = updated_id
                d.update(file_id, content, {"n": str(n)})
            written = time.perf_counter()
            polls = 0
            delay = None
            while time.perf_counter() - written < 60:
                polls += 1
                asked = time.perf_counter()
                for page in d.listing(query, fields):
                    for found in page:
                        has_fields = has_fields and "md5Checksum" in found and "properties" in found
                        if found["id"] == file_id and found.get("md5Checksum") == md5(content):
                            delay = round(asked - written, 3)
                if delay is not None:
                    break
                time.sleep(max(0.0, every - (time.perf_counter() - asked)))
            results[kind].append({"n": n, "polls": polls, "delay_s": delay})

    def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
        seen = [r["delay_s"] for r in rows if r["delay_s"] is not None]
        return {
            "trials": len(rows),
            "never_seen_in_60s": len(rows) - len(seen),
            "seen_on_first_listing": sum(r["polls"] == 1 for r in rows),
            "delay_s": stats(seen),
        }

    return {
        "summary": {
            "list_returns_md5_and_properties": has_fields,
            "create": summary(results["create"]),
            "update": summary(results["update"]),
        },
        "samples": results,
    }
