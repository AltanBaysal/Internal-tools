"""Async-friendly wrapper around the synchronous core extractor.

The service is the only place that knows about asyncio. The view/controller
above it call async methods; the core below it stays plain and testable.
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable

from core.extractor import extract_first_frame, find_videos


ProgressCallback = Callable[[int, int, str], Awaitable[None] | None]


@dataclass(frozen=True)
class ExtractionResult:
    total: int
    succeeded: int
    failed: int
    output_dir: Path


class FrameExtractorService:
    """Stateless: every call is independent. Easy to unit test."""

    async def extract_all(
        self,
        input_path: Path,
        output_dir: Path,
        fmt: str,
        progress_cb: ProgressCallback | None = None,
    ) -> ExtractionResult:
        videos = await asyncio.to_thread(find_videos, input_path)
        total = len(videos)
        if total == 0:
            return ExtractionResult(0, 0, 0, output_dir)

        base = input_path if input_path.is_dir() else input_path.parent
        succeeded = 0
        failed = 0

        for idx, video in enumerate(videos, start=1):
            rel = video.relative_to(base)
            out_path = output_dir / rel.with_suffix(f".{fmt}")
            ok = await asyncio.to_thread(extract_first_frame, video, out_path, fmt)
            if ok:
                succeeded += 1
            else:
                failed += 1
            if progress_cb is not None:
                result = progress_cb(idx, total, str(rel))
                if asyncio.iscoroutine(result):
                    await result

        return ExtractionResult(total, succeeded, failed, output_dir)
