"""Step 4 §14, the two assumptions about ids and names: an id reserved by `files.generateIds` can be
used later (today's control here; the days-long check is check_reserved_ids.py), and `name contains`
finds export folders whatever their case.
"""

from __future__ import annotations

import datetime
import time
from typing import Any

from common import FOLDER, Drive, message
from googleapiclient.errors import HttpError

CHECK_DAYS = (1, 3, 7)


def reserved_ids(d: Drive, folder: str, pending: bool) -> dict[str, Any]:
    """Today's control: a reserved id makes a file and a folder, and creating with it again is
    refused with 409, as step 4's retries rely on. With `pending`, ten more ids are reserved for the
    checks after 1, 3 and 7 days."""
    ids = d.call(lambda s: s.files().generateIds(count=3, space="drive", type="files")).value["ids"]
    made = d.create(folder, "reserved.bin", b"x", file_id=ids[0]).value["id"] == ids[0]
    again: dict[str, Any] = {"status": None}
    try:
        d.create(folder, "reserved-again.bin", b"y", file_id=ids[0])
    except HttpError as error:
        again = {"status": error.resp.status, "message": message(error)}
    body = {"id": ids[1], "name": "reserved-folder", "mimeType": FOLDER, "parents": [folder]}
    as_folder = d.call(lambda s: s.files().create(body=body, fields="id")).value["id"] == ids[1]
    summary: dict[str, Any] = {
        "file_made_with_reserved_id": made,
        "folder_made_with_reserved_id": as_folder,
        "same_id_again": again,
    }
    if pending:
        later = d.call(lambda s: s.files().generateIds(count=10, space="drive", type="files"))
        reserved = later.value["ids"]
        now = datetime.datetime.now(datetime.UTC).replace(microsecond=0)
        summary["pending"] = {
            "reserved_at": now.isoformat(),
            "checks": {
                str(day): {"due": (now + datetime.timedelta(days=day)).isoformat(), "ids": part}
                for day, part in zip(
                    CHECK_DAYS, (reserved[0:3], reserved[3:6], reserved[6:9]), strict=True
                )
            },
            "spare": reserved[9:],
        }
    return {"summary": summary, "samples": {}}


EXPORTS = [
    "2026-11-06 10-00 Final",
    "2026-11-06 10-01 final",
    "2026-11-06 10-02 FINAL (1)",
    "2026-11-06 10-03 Finale",
    "2026-11-06 10-04 My Final Cut",
    "2026-11-06 10-05 xFinal",
    "2026-11-06 10-06 Final_cut",
    "2026-11-06 10-07 Işık",
    "2026-11-06 10-08 ışık",
    "2026-11-06 10-09 İz",
    "2026-11-06 10-10 iz",
]
QUERIES = [
    "Final",
    "final",
    "FINAL",
    "inal",
    "Final Cut",
    "My Final",
    "Final (1)",
    "Final_cut",
    "cut",
    "Işık",
    "ışık",
    "IŞIK",
    "İz",
    "iz",
    "Iz",
    "10-04",
    "2026-11-06 10-04 My Final Cut",
]


def quoted(text: str) -> str:
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"


def name_contains(d: Drive, folder: str, again_after_s: int = 60) -> dict[str, Any]:
    """Export-like folder names, queried with `name contains` in several cases and parts; asked as
    soon as the folder's listing shows them all, and again `again_after_s` later in case the name
    search lags the listing."""
    for name in EXPORTS:
        body = {"name": name, "mimeType": FOLDER, "parents": [folder]}
        d.call(lambda s, b=body: s.files().create(body=b, fields="id"))
    began = time.perf_counter()
    while len(d.listing(f"'{folder}' in parents and trashed=false", "id")[0]) < len(EXPORTS):
        time.sleep(0.5)
    listed_after = round(time.perf_counter() - began, 3)

    def ask() -> dict[str, list[str]]:
        found: dict[str, list[str]] = {}
        for text in QUERIES:
            query = f"'{folder}' in parents and trashed=false and name contains {quoted(text)}"
            pages = d.listing(query, "name")
            found[text] = sorted(f["name"][17:] for page in pages for f in page)
        return found

    first = ask()
    time.sleep(again_after_s)
    second = ask()
    return {
        "summary": {
            "names": [name[17:] for name in EXPORTS],
            "found": second,
            "changed_after_wait": {q: first[q] for q in QUERIES if first[q] != second[q]},
            "listed_after_s": listed_after,
        },
        "samples": {"first": first},
    }
