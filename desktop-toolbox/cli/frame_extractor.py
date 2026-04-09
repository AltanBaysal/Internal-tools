"""Video Frame Extractor — CLI entry point.

Usage (run from desktop-toolbox/):
    python -m cli.frame_extractor <folder_or_file_path> [--format png]
"""

import argparse
import sys
from pathlib import Path

from core.extractor import find_videos, extract_first_frame_bytes

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def _save_frame(video: Path, out_path: Path, fmt: str) -> bool:
    data = extract_first_frame_bytes(video, fmt)
    if data is None:
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    return True


def process(input_path: Path, fmt: str) -> None:
    videos = find_videos(input_path)
    if not videos:
        print(f"No video files found in: {input_path}")
        return

    print(f"Found {len(videos)} video(s)")

    # Determine the base for relative paths
    base = input_path if input_path.is_dir() else input_path.parent

    succeeded = 0
    failed = 0

    for video in videos:
        rel = video.relative_to(base)
        out_name = rel.with_suffix(f".{fmt}")
        out_path = OUTPUT_DIR / out_name

        if _save_frame(video, out_path, fmt):
            succeeded += 1
            print(f"  OK  {rel}")
        else:
            failed += 1
            print(f"  FAIL  {rel}")

    print(f"\nDone — {succeeded} extracted, {failed} failed")
    print(f"Output: {OUTPUT_DIR.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract first frame from videos.")
    parser.add_argument("path", help="Path to a video file or folder of videos")
    parser.add_argument("--format", choices=["jpg", "png"], default="jpg",
                        help="Output image format (default: jpg)")
    args = parser.parse_args()

    input_path = Path(args.path).resolve()
    if not input_path.exists():
        print(f"Path not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    process(input_path, args.format)


if __name__ == "__main__":
    main()
