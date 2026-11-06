"""Step 4 §14, "four Colabs on one account do not hit a per-second limit": four processes stand for
four Colabs, each writing its own file 3 times a second for a minute. Every write is tried once, and
the 403s and 429s are counted, not waited out; that is what this experiment measures.

A write here is a multipart update of 1 KB with a property, a head file's call at a size that keeps
this machine's upload bandwidth out of the count: the limit is on requests, not bytes.

Run once, on 6 Kasım; the user then decided against measuring it further (the core backs off on
403/429 anyway, and Google documents only per-minute quotas), so its 20-file variant was not run.
"""

from __future__ import annotations

import multiprocessing
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from common import Drive, media, reason, stats
from googleapiclient.errors import HttpError


def worker(token: str, file_id: str, start_at: float, seconds: int, rate: int, out: Any) -> None:
    d = Drive(token)
    rows: list[dict[str, Any]] = []
    content = b"w" * 1024

    def write(k: int) -> None:
        svc = d.service()
        sent = time.time()
        try:
            svc.files().update(
                fileId=file_id,
                body={"properties": {"k": str(k)}},
                media_body=media(content),
                fields="id",
            ).execute()
            status, why = 200, ""
        except HttpError as error:
            status, why = error.resp.status, reason(error)
        except OSError as error:
            status, why = 0, type(error).__name__
        took = round(time.time() - sent, 3)
        at = round(sent - start_at, 3)
        rows.append({"k": k, "sent_s": at, "status": status, "reason": why, "s": took})

    def warm(_: int) -> None:  # the token and the threads' connections, before the clock starts
        d.call(lambda s: s.files().get(fileId=file_id, fields="id"))

    with ThreadPoolExecutor(8) as pool:
        list(pool.map(warm, range(8)))
        for k in range(seconds * rate):
            wait = start_at + k / rate - time.time()
            if wait > 0:
                time.sleep(wait)
            pool.submit(write, k)
    out.put(rows)


def rate_limit(
    d: Drive, folder: str, token: str, processes: int = 4, seconds: int = 60, rate: int = 3
) -> dict[str, Any]:
    files = [d.create(folder, f"colab-{i}.bin", b"0").value["id"] for i in range(processes)]
    context = multiprocessing.get_context("spawn")
    out = context.Queue()
    start_at = time.time() + 20  # every process warmed up and waiting
    workers = [
        context.Process(target=worker, args=(token, f, start_at, seconds, rate, out)) for f in files
    ]
    for process in workers:
        process.start()
    per_process = [out.get() for _ in workers]
    for process in workers:
        process.join()
    rows = [row for rows in per_process for row in rows]
    refused = [r for r in rows if r["status"] != 200]
    by_second = Counter(int(r["sent_s"]) for r in refused)
    return {
        "summary": {
            "processes": processes,
            "seconds": seconds,
            "writes_per_second_each": rate,
            "writes": len(rows),
            "ok": len(rows) - len(refused),
            "refused": dict(Counter(f"{r['status']} {r['reason']}" for r in refused)),
            "refused_per_process": [sum(r["status"] != 200 for r in p) for p in per_process],
            "first_refused_at_s": min((r["sent_s"] for r in refused), default=None),
            "write_s": stats([r["s"] for r in rows if r["status"] == 200]),
            "sent_over_s": round(max(r["sent_s"] for r in rows), 3),
        },
        "samples": {"refused_by_second": dict(sorted(by_second.items())), "rows": rows},
    }
