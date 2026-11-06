"""Builds queen-studio/measurements/drive.json from run.py's raw results: for each of step 4's
unmeasured assumptions (§14), what it claimed, what it was measured as on each host, and whether it
holds by the rule written beside it. Later code and its tests take their numbers from that file.

    python summarize.py --raw <dir holding local/ and colab/> [--out drive.json]

The reserved-id checks check_reserved_ids.py has already written into the file are kept.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from common import write_json

OUT = Path(__file__).resolve().parent.parent / "drive.json"
HOSTS = ("local", "colab")
Hosts = dict[str, dict[str, Any]]


def every(hosts: Hosts, test: Callable[[dict[str, Any]], bool]) -> bool:
    return all(test(summary) for summary in hosts.values())


def at_pace(s: dict[str, Any]) -> bool:
    return not s["refused"] and s["ok_per_second"] >= 0.9 * s["asked_per_second"]


def pace(record: dict[str, Any]) -> dict[str, Any]:
    """The pace Drive kept in rate_limit, from its rows: writes answered per second, start to last
    answer. Drive slowed the writes rather than refusing them, so this is the number that tells."""
    rows = record["samples"]["rows"]
    s = record["summary"]
    finished = max(r["sent_s"] + r["s"] for r in rows)
    return {
        "asked_per_second": s["processes"] * s["writes_per_second_each"],
        "ok_per_second": round(s["ok"] / finished, 2),
        "finished_over_s": round(finished, 1),
        "decision": "Not measured further by the user's decision (6 Kasım): the core backs off on"
        " 403/429, and Google documents only per-minute quotas.",
    }


ASSUMPTIONS: dict[str, tuple[str, str, Callable[[Hosts], bool | None]]] = {
    "read_after_write": (
        "A read by id (md5) right after another client's write returns the new md5.",
        "Ana fikir 4, look before writing",
        lambda h: every(h, lambda s: s["stale_reads"] == 0),
    ),
    "content_and_properties": (
        "Content and properties in one multipart files.update land together or not at all.",
        "the main-list row and the content agreeing",
        lambda h: every(
            h,
            lambda s: (
                s["by_id"]["md5_and_property_apart"] == 0
                and s["by_list"]["md5_and_property_apart"] == 0
                and s["downloads"]["partial"] == 0
            ),
        ),
    ),
    "cut_upload": (
        "An existing file's new content shows only once its upload has finished.",
        "no half-written head file",
        lambda h: every(
            h,
            lambda s: (
                s["multipart_cut_left_old"] == s["multipart_cut_trials"]
                and s["old_after_all_cuts"]
                and s["resumable"]["left_old_after_first_chunk"] == s["resumable"]["trials"]
            ),
        ),
    ),
    "list_delay": (
        "files.list returns properties and md5; a write shows in the listing within 5 s.",
        "seeing another Colab's change (the 5 s list cache)",
        lambda h: every(
            h,
            lambda s: (
                s["list_returns_md5_and_properties"]
                and all(
                    s[k]["never_seen_in_60s"] == 0 and s[k]["delay_s"]["max"] <= 5
                    for k in ("create", "update")
                )
            ),
        ),
    ),
    "list_pages": (
        "files.list with pageSize=1000 returns up to 1,000 projects in one page, mostly.",
        "the main list and the quota",
        lambda h: every(h, lambda s: s["one_page"] * 2 > s["listings"]),
    ),
    "reserved_ids": (
        "An id from files.generateIds can still be used days later.",
        "ids reserved ahead for blocks, folders and outputs",
        lambda h: None,  # decided by check_reserved_ids.py after day 7
    ),
    "trash_folder": (
        "A folder of many files goes to the trash in one call, its files with it.",
        "deleting a project",
        lambda h: every(h, lambda s: s["all_trashed_after_s"] is not None),
    ),
    "trash_limit": (
        "Under drive.file, a folder goes to the trash in one call whatever it holds below it.",
        "deleting a project, whose folder holds every frame's media",
        lambda h: every(h, lambda s: s["first_refused"] is None),
    ),
    "rate_limit": (
        "Four Colabs on one account, 3 writes/s each to its own file, meet no per-second limit:"
        " nothing refused, and Drive keeps at least 90% of the pace asked.",
        "the quota sums (Değerlendirme 9)",
        lambda h: every(h, at_pace),
    ),
    "revisions": (
        "Every update leaves a revision, and old revisions do not count against the quota.",
        "storage (Değerlendirme 9)",
        lambda h: every(
            h,
            lambda s: (
                s["revisions_listed"] >= min(s["updates"], 100)
                and s["quota_delta_last"] < 2 * s["file_bytes"]
            ),
        ),
    ),
    "name_contains": (
        "name contains ignores case in export names.",
        "numbering export folders (1), (2)",
        lambda h: every(
            h,
            lambda s: all(
                {"Final", "final"} <= set(s["found"][q]) for q in ("Final", "final", "FINAL")
            ),
        ),
    ),
}

# Step 4, Varsayımlar: the durations the design's sums are made of, assumed from Colab.
ASSUMED_S = {
    "get_metadata": 0.25,
    "list_small_folder": 0.25,
    "update_properties": 0.25,
    "trash": 0.25,
    "generate_ids_1000": 0.25,
    "about": 0.25,
    "copy_1m": 0.25,
    "update_head_110k": 0.6,
    "update_head_250k": 0.6,
    "create_head_110k_reserved_id": 0.6,
    "download_250k": 0.3,
    "download_1m": 0.3,
}


def durations(hosts: Hosts) -> dict[str, Any]:
    """Each call's assumed time beside its measured ones; it holds when Colab's median is within."""
    table: dict[str, Any] = {}
    for call, assumed in ASSUMED_S.items():
        row: dict[str, Any] = {"assumed_s": assumed}
        for host, summary in hosts.items():
            row[host] = summary[call]
        if "colab" in hosts:
            row["holds_on_colab"] = hosts["colab"][call]["p50"] <= assumed
        table[call] = row
    for extra in ("parallel_8_get_metadata", "upload_video_20m_resumable"):
        table[extra] = {host: summary[extra] for host, summary in hosts.items()}
    return table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    raw: dict[str, dict[str, Any]] = {host: {} for host in HOSTS}
    for host in HOSTS:
        for path in sorted((args.raw / host).glob("*.json")):
            if path.stem != "root":
                raw[host][path.stem] = json.loads(path.read_text(encoding="utf-8"))
    failed = [f"{h}/{n}" for h in HOSTS for n, r in raw[h].items() if "error" in r]
    if failed:
        print(f"these runs failed, run them again first: {', '.join(failed)}")
        return 1

    def hosts(name: str) -> Hosts:
        found = {h: raw[h][name]["summary"] for h in HOSTS if name in raw[h]}
        if name == "rate_limit":
            found = {h: {**s, **pace(raw[h][name])} for h, s in found.items()}
        return found

    assumptions: dict[str, Any] = {}
    for name, (claim, relied_on, rule) in ASSUMPTIONS.items():
        found = hosts(name)
        assumptions[name] = {
            "claim": claim,
            "relied_on_by": relied_on,
            "holds": rule(found) if found else None,
            **found,
        }
    timed = hosts("durations")
    calls = durations(timed)
    on_colab = [r["holds_on_colab"] for r in calls.values() if "holds_on_colab" in r]
    assumptions["durations"] = {
        "claim": "Calls take 0.25 s (small), 0.6 s (head upload), 0.3 s (download up to 1 MB).",
        "relied_on_by": "every duration in step 4",
        "holds": all(on_colab) if on_colab else None,
        "calls": calls,
    }
    keep_checks(args.out, assumptions)

    write_json(
        args.out,
        {
            "item": 528,
            "summarized": datetime.date.today().isoformat(),
            "account": "the test account, drive.file scope",
            "hosts": {
                h: {"platform": next(iter(raw[h].values()))["platform"]} for h in HOSTS if raw[h]
            },
            "assumptions": assumptions,
            "retries": {
                h: {n: r["retries"] for n, r in raw[h].items() if r["retries"]} for h in HOSTS
            },
        },
    )
    return 0


def keep_checks(out: Path, assumptions: dict[str, Any]) -> None:
    """Carries over what check_reserved_ids.py wrote, with the verdict it reached."""
    if not out.exists():
        return
    old = json.loads(out.read_text(encoding="utf-8"))["assumptions"]["reserved_ids"]
    new = assumptions["reserved_ids"]
    old_checks = old.get("local", {}).get("pending", {}).get("checks", {})
    for day, check in new.get("local", {}).get("pending", {}).get("checks", {}).items():
        if "result" in old_checks.get(day, {}) and old_checks[day]["ids"] == check["ids"]:
            check["result"] = old_checks[day]["result"]
            new["holds"] = old["holds"]


if __name__ == "__main__":
    sys.exit(main())
