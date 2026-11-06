"""The rest of step 4's "reserved ids stay valid for days": on day 1, 3 or 7 after they were
reserved, creates a file with each of that day's ids, writes what Drive said into drive.json, and
moves the files to Drive's trash.

    python check_reserved_ids.py --token <token file> --day 1|3|7 [--results drive.json]

The files go to the test account's My Drive root, not the item's folder: that folder is in the trash
by then, and a file made inside it would be trashed with it. Each is trashed as soon as it is made.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

from common import Drive, message, write_json
from googleapiclient.errors import HttpError

RESULTS = Path(__file__).resolve().parent.parent / "drive.json"


def check(d: Drive, file_id: str) -> dict[str, Any]:
    body = {"id": file_id, "name": "queen-studio m528 reserved id check"}
    try:
        made = d.call(lambda s: s.files().create(body=body, fields="id")).value["id"]
    except HttpError as error:
        return {
            "id": file_id,
            "made": False,
            "status": error.resp.status,
            "message": message(error),
        }
    d.trash(made)
    return {"id": file_id, "made": made == file_id, "status": 200, "message": ""}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="the test account's token file")
    parser.add_argument("--day", required=True, choices=["1", "3", "7"])
    parser.add_argument("--results", type=Path, default=RESULTS)
    args = parser.parse_args()

    results = json.loads(args.results.read_text(encoding="utf-8"))
    entry = results["assumptions"]["reserved_ids"]
    due = entry["local"]["pending"]["checks"][args.day]
    now = datetime.datetime.now(datetime.UTC).replace(microsecond=0)
    if now < datetime.datetime.fromisoformat(due["due"]):
        print(f"day {args.day} is due at {due['due']}; it is {now.isoformat()}")
        return 2
    d = Drive(args.token)
    due["result"] = {"checked_at": now.isoformat(), "ids": [check(d, i) for i in due["ids"]]}
    checks = entry["local"]["pending"]["checks"].values()
    if all("result" in c for c in checks):
        entry["holds"] = all(r["made"] for c in checks for r in c["result"]["ids"])
    elif not all(r["made"] for r in due["result"]["ids"]):
        entry["holds"] = False
    write_json(args.results, results)
    print(json.dumps(due["result"], indent=1))
    return 0 if all(r["made"] for r in due["result"]["ids"]) else 1


if __name__ == "__main__":
    sys.exit(main())
