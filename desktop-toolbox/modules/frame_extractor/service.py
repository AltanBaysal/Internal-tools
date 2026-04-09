"""Async-friendly wrapper around the synchronous core extractor.

Frame extraction is split into two phases: extract-to-memory and save-to-disk.
The view drives them independently so the user can extract first, see the
result, then choose where to save.
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable

from core.extractor import extract_first_frame_bytes, find_videos


ProgressCallback = Callable[[int, int, str], Awaitable[None] | None]


@dataclass(frozen=True)
class ExtractedFrame:
    """One in-memory frame ready to be written to disk later."""

    rel_path: Path  # relative to input root, with image suffix
    data: bytes


@dataclass(frozen=True)
class ExtractionResult:
    total: int
    succeeded: int
    failed: int
    frames: list[ExtractedFrame]


@dataclass(frozen=True)
class SaveResult:
    written: int
    target_dir: Path


class FrameExtractorService:
    """Stateless: every call is independent. Easy to unit test."""

    async def extract_all(
        self,
        input_path: Path,
        fmt: str,
        progress_cb: ProgressCallback | None = None,
    ) -> ExtractionResult:
        videos = await asyncio.to_thread(find_videos, input_path)
        total = len(videos)
        if total == 0:
            return ExtractionResult(0, 0, 0, [])

        base = input_path if input_path.is_dir() else input_path.parent
        frames: list[ExtractedFrame] = []
        succeeded = 0
        failed = 0

        for idx, video in enumerate(videos, start=1):
            rel = video.relative_to(base).with_suffix(f".{fmt}")
            data = await asyncio.to_thread(extract_first_frame_bytes, video, fmt)
            if data is not None:
                frames.append(ExtractedFrame(rel_path=rel, data=data))
                succeeded += 1
            else:
                failed += 1
            if progress_cb is not None:
                result = progress_cb(idx, total, str(rel))
                if asyncio.iscoroutine(result):
                    await result

        return ExtractionResult(total, succeeded, failed, frames)

    async def save_frames(
        self,
        frames: list[ExtractedFrame],
        target_dir: Path,
    ) -> SaveResult:
        def _write_all() -> int:
            count = 0
            for frame in frames:
                out_path = target_dir / frame.rel_path
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(frame.data)
                count += 1
            return count

        written = await asyncio.to_thread(_write_all)
        return SaveResult(written=written, target_dir=target_dir)
