"""Extract first frame from video files."""

import cv2
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def is_video(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


def extract_first_frame(video_path: Path, output_path: Path, fmt: str = "jpg") -> bool:
    """Extract the first frame from a video and save it. Returns True on success."""
    cap = cv2.VideoCapture(str(video_path))
    try:
        if not cap.isOpened():
            return False
        ret, frame = cap.read()
        if not ret or frame is None:
            return False
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return cv2.imwrite(str(output_path), frame)
    finally:
        cap.release()


def extract_first_frame_bytes(video_path: Path, fmt: str = "jpg") -> bytes | None:
    """Extract the first frame and return as image bytes (no disk write)."""
    ext = ".jpg" if fmt == "jpg" else ".png"
    cap = cv2.VideoCapture(str(video_path))
    try:
        if not cap.isOpened():
            return None
        ret, frame = cap.read()
        if not ret or frame is None:
            return None
        ok, buf = cv2.imencode(ext, frame)
        return buf.tobytes() if ok else None
    finally:
        cap.release()


def find_videos(root: Path) -> list[Path]:
    """Recursively find all video files under root."""
    if root.is_file():
        return [root] if is_video(root) else []
    return sorted(p for p in root.rglob("*") if p.is_file() and is_video(p))
