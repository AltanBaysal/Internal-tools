"""Runs item 528's Drive measurements on the test account and writes each one's raw result.

    python run.py --token <token file> --out <dir> --host local|colab [--reserve-pending] [name ...]

Everything goes in one new Drive folder, but for the experiments in OWN_FOLDER, and every folder is
moved to Drive's trash at the end (FOUNDATION 1: nothing is deleted for good). Each experiment's
result is written to <out>/<name>.json as soon as it ends, so a failure keeps the ones before it; a
failed experiment records Drive's words and the run goes on. With no names, every experiment but
those in ALONE runs.
"""

from __future__ import annotations

import argparse
import datetime
import platform
import sys
import time
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

from common import Drive, write_json
from consistency import content_and_properties, cut_upload, list_delay, read_after_write
from durations import durations
from naming import name_contains, reserved_ids
from rate_limit import rate_limit
from scale import list_pages, revisions, trash_folder, trash_limit

Run = Callable[[Drive, str, argparse.Namespace, dict[str, Any]], dict[str, Any]]


def _list_pages(d: Drive, folder: str, _: argparse.Namespace, kept: dict[str, Any]) -> Any:
    kept["listed"] = folder  # trash_folder fills the same folder to 2,000 and trashes it
    return list_pages(d, folder)


def _trash_folder(d: Drive, folder: str, _: argparse.Namespace, kept: dict[str, Any]) -> Any:
    return trash_folder(d, kept.get("listed", folder), 1000 if "listed" in kept else 0)


EXPERIMENTS: dict[str, Run] = {
    "durations": lambda d, f, a, k: durations(d, f),
    "read_after_write": lambda d, f, a, k: read_after_write(d, f),
    "content_and_properties": lambda d, f, a, k: content_and_properties(d, f),
    "cut_upload": lambda d, f, a, k: cut_upload(d, f),
    "list_delay": lambda d, f, a, k: list_delay(d, f),
    "name_contains": lambda d, f, a, k: name_contains(d, f),
    "reserved_ids": lambda d, f, a, k: reserved_ids(d, f, a.reserve_pending),
    "list_pages": _list_pages,
    "trash_folder": _trash_folder,
    "revisions": lambda d, f, a, k: revisions(d, f),
    "rate_limit": lambda d, f, a, k: rate_limit(d, f, a.token),
    "trash_limit": lambda d, f, a, k: trash_limit(d, f),
}
# Run by name only: rate_limit alone, from this machine (decisions log, Koşudan önce 3); trash_limit
# from this machine, as what it finds is Drive's rule, not the host's.
ALONE = {"rate_limit", "trash_limit"}
# Not under the run's folder: under drive.file Drive refuses to trash a folder with a few thousand
# files below it (appNotAuthorizedToChild, measured on this item), and these 2,000 would hold the
# run's folder back. trash_folder trashes this one itself; the end of the run makes sure.
OWN_FOLDER = {"list_pages", "trash_limit"}


def now() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="the test account's token file")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--host", required=True, choices=["local", "colab"])
    parser.add_argument("--reserve-pending", action="store_true")
    parser.add_argument("names", nargs="*", help=", ".join(EXPERIMENTS))
    args = parser.parse_args()
    if unknown := set(args.names) - set(EXPERIMENTS):
        parser.error(f"no such experiment: {', '.join(sorted(unknown))}")
    names = args.names or [n for n in EXPERIMENTS if n not in ALONE]

    d = Drive(args.token)
    title = f"queen-studio m528 {args.host} {now()}"
    root = d.folder(title)
    folders = [root]
    write_json(args.out / "root.json", {"folders": folders, "started": now()})
    kept: dict[str, Any] = {}
    failed = 0
    try:
        for name in names:
            print(f"{now()} {name} ...", flush=True)
            d.retries.clear()
            began = time.perf_counter()
            record: dict[str, Any] = {"host": args.host, "started": now()}
            if name in OWN_FOLDER:
                folder = d.folder(f"{title} {name}")
                folders.append(folder)
                write_json(args.out / "root.json", {"folders": folders, "started": now()})
            else:
                folder = d.folder(name, root)
            try:
                record.update(EXPERIMENTS[name](d, folder, args, kept))
            except Exception as error:
                failed += 1
                record["error"] = f"{type(error).__name__}: {error}"
                record["traceback"] = traceback.format_exc()
            record["seconds"] = round(time.perf_counter() - began, 1)
            record["retries"] = dict(d.retries)
            record["platform"] = {"system": platform.platform(), "python": sys.version.split()[0]}
            write_json(args.out / f"{name}.json", record)
            print(f"{now()} {name} {'failed' if 'error' in record else 'done'}", flush=True)
    finally:
        for folder in folders:
            d.trash(folder)  # already trashed is fine: Drive answers it as a success
        write_json(args.out / "root.json", {"folders": folders, "trashed": now()})
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
