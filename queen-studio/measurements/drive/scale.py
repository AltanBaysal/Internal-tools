"""Step 4 §14, the assumptions that grow with a count: a 1,000-file folder listed in one page, a
2,000-file folder trashed in one call, how many files below a folder drive.file still lets it be
trashed, and 500 updates of one file against its revisions and the quota.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from common import HEAD_LARGE, Drive, message, reason, stats, tagged
from googleapiclient.errors import HttpError

ROW_FIELDS = "id,name,md5Checksum,properties,modifiedTime"


def row(n: int) -> dict[str, str]:
    """A main-list row as step 4 keeps it in a head file's properties, its name split in three as a
    64-character Turkish name would be."""
    name = f"Proje {n:04d} — çok uzun bir ad, Türkçe harflerle: ışık, gölge, ağaç, üzüm "
    return {
        "name0": name[:40],
        "name1": name[40:80],
        "name2": name[80:],
        "archived": "false",
        "created": "2026-11-06T09:00:00Z",
        "updated": "2026-11-06T09:00:00Z",
        "runner": "core-0123456789abcdef",
    }


def populate(d: Drive, folder: str, start: int, count: int, threads: int = 4) -> dict[str, Any]:
    """`count` small files, a main-list row each, `threads` at a time, backing off when refused."""
    began = time.perf_counter()

    def one(n: int) -> float:
        return d.create(folder, f"{n:04d}.json.gz", f"head {n}".encode(), row(n)).seconds

    with ThreadPoolExecutor(threads) as pool:
        seconds = list(pool.map(one, range(start, start + count)))
    return {
        "files": count,
        "wall_s": round(time.perf_counter() - began, 1),
        "create_s": stats(seconds),
    }


def list_pages(d: Drive, folder: str, files: int = 1000, listings: int = 100) -> dict[str, Any]:
    """A folder of `files` head files listed `listings` times with pageSize=1000 and the fields the
    main list asks for: how many pages each listing took."""
    made = populate(d, folder, 0, files)
    query = f"'{folder}' in parents and trashed=false"
    pages: list[int] = []
    sizes: list[list[int]] = []
    seconds: list[float] = []
    for _ in range(listings):
        began = time.perf_counter()
        found = d.listing(query, ROW_FIELDS)
        seconds.append(time.perf_counter() - began)
        pages.append(len(found))
        sizes.append([len(page) for page in found])
    return {
        "summary": {
            "files": files,
            "listings": listings,
            "one_page": sum(p == 1 for p in pages),
            "pages_max": max(pages),
            "complete": sum(sum(s) == files for s in sizes),
            "listing_s": stats(seconds),
            "populate": made,
        },
        "samples": {"page_sizes": sizes},
    }


def trash_folder(d: Drive, folder: str, already: int, files: int = 2000) -> dict[str, Any]:
    """Fills the folder to `files` and trashes the folder alone, in one call: are its files trashed
    with it, and how soon does a listing show it."""
    made = populate(d, folder, already, files - already)
    trashed = d.trash(folder)
    called = time.perf_counter()
    query = f"'{folder}' in parents"
    checks: list[dict[str, Any]] = []
    while True:
        found = [f for page in d.listing(query, "id,trashed,explicitlyTrashed") for f in page]
        trashed_now = sum(bool(f.get("trashed")) for f in found)
        explicit = sum(bool(f.get("explicitlyTrashed")) for f in found)
        after = round(time.perf_counter() - called, 3)
        checks.append({"after_s": after, "listed": len(found), "trashed": trashed_now})
        if trashed_now == files or after > 300:
            break
        time.sleep(2)
    hidden = len(d.listing(f"'{folder}' in parents and trashed=false", "id")[0])
    return {
        "summary": {
            "files": files,
            "trash_call_s": round(trashed.seconds, 3),
            "listed_after_trash": checks[-1]["listed"],
            "trashed_at_first_check": checks[0]["trashed"],
            "all_trashed_after_s": checks[-1]["after_s"]
            if checks[-1]["trashed"] == files
            else None,
            "explicitly_trashed": explicit,
            "untrashed_listing_shows": hidden,
            "populate": made,
        },
        "samples": {"checks": checks},
    }


def trash_limit(
    d: Drive, folder: str, start: int = 1900, step: int = 50, stop: int = 3000, part: int = 100
) -> dict[str, Any]:
    """How many files a folder can hold below it and still be trashed in one call under drive.file.
    The folder fills in parts of `part` files, as a project folder holds media/ and its blocks; at
    `start` and every `step` after, it is trashed, and a success is undone at once. At the first
    refusal its parts are moved out in groups small enough to trash, so everything reaches the
    trash; nothing is deleted."""
    parts: list[list[Any]] = []  # [folder id, files in it]
    count = 0
    attempts: list[dict[str, Any]] = []
    refused = False
    while count < stop and not refused:
        target = start if count == 0 else count + step
        while count < target:
            if not parts or parts[-1][1] == part:
                parts.append([d.folder(f"part-{len(parts):03d}", folder), 0])
            n = min(part - parts[-1][1], target - count)
            populate(d, parts[-1][0], count, n)
            parts[-1][1] += n
            count += n
        try:
            took = d.trash(folder).seconds
            d.call(lambda s: s.files().update(fileId=folder, body={"trashed": False}, fields="id"))
            attempts.append({"files": count, "parts": len(parts), "trashed": True, "s": took})
        except HttpError as error:
            refused = True
            said = {"reason": reason(error), "message": message(error)}
            attempts.append({"files": count, "parts": len(parts), "trashed": False, **said})
    if refused:
        for group in range(0, len(parts), 10):  # 1,000 files a group: well under the limit
            holding = d.folder(f"queen-studio m528 trash_limit holding {group // 10}")
            for found, _ in parts[group : group + 10]:
                d.call(
                    lambda s, f=found, h=holding: s.files().update(
                        fileId=f, addParents=h, removeParents=folder, fields="id"
                    )
                )
            d.trash(holding)
    d.trash(folder)
    ok = [a["files"] for a in attempts if a["trashed"]]
    return {
        "summary": {
            "largest_trashed": max(ok, default=None),
            "first_refused": next((a for a in attempts if not a["trashed"]), None),
            "part_size": part,
        },
        "samples": {"attempts": attempts},
    }


def revisions(
    d: Drive, folder: str, updates: int = 500, watch_s: int = 300, every_s: int = 30
) -> dict[str, Any]:
    """One file updated `updates` times with incompressible content: how many revisions Drive keeps,
    and whether the quota counts them. The quota is watched for `watch_s` after, as it may lag."""
    before = d.quota()
    file_id = d.create(folder, "revisions.bin", tagged(0, HEAD_LARGE)).value["id"]
    seconds: list[float] = []
    for n in range(1, updates + 1):
        seconds.append(d.update(file_id, tagged(n, HEAD_LARGE)).seconds)
    found: list[dict[str, Any]] = []
    token = None
    while True:
        page = d.call(
            lambda s, t=token: s.revisions().list(
                fileId=file_id,
                pageSize=1000,
                pageToken=t,
                fields="nextPageToken,revisions(id,keepForever,size,modifiedTime)",
            )
        ).value
        found += page.get("revisions", [])
        token = page.get("nextPageToken")
        if not token:
            break
    watched: list[dict[str, Any]] = []
    began = time.perf_counter()
    while True:
        quota = d.quota()
        after = round(time.perf_counter() - began)
        watched.append({"after_s": after, "usage_delta": quota["usage"] - before["usage"]})
        if after >= watch_s:
            break
        time.sleep(every_s)
    kept_bytes = sum(int(r.get("size", 0)) for r in found)
    return {
        "summary": {
            "updates": updates,
            "file_bytes": HEAD_LARGE,
            "revisions_listed": len(found),
            "revisions_keep_forever": sum(bool(r.get("keepForever")) for r in found),
            "revisions_bytes": kept_bytes,
            "quota_delta_first": watched[0]["usage_delta"],
            "quota_delta_last": watched[-1]["usage_delta"],
            "update_s": stats(seconds),
        },
        "samples": {"quota": watched, "before": before},
    }
