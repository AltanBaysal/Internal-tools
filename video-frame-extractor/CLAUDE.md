# Video First Frame Extractor

Extracts the first frame from video files (MP4, AVI, MOV, MKV, WEBM) and outputs JPG/PNG images.

## Commands

```bash
pip install -r requirements.txt

# Web UI
streamlit run app.py

# CLI
python main.py <folder_or_file_path> [--format png]
```

## Architecture

Two entry points share a common extraction library:

- **`app.py`** — Streamlit web UI. Takes a folder path as text input (no file upload), extracts frames in-memory via `extract_first_frame_bytes()`, serves result as download (single image or ZIP).
- **`main.py`** — CLI. Writes extracted frames to `output/` directory on disk via `extract_first_frame()`.
- **`extractor.py`** — Core library. Video discovery (`find_videos`) and frame extraction using OpenCV. Two extraction variants: disk-write (`extract_first_frame`) and in-memory bytes (`extract_first_frame_bytes`).

## Key Design Decisions

- Videos are read directly from the user's filesystem path — never copied or uploaded. This avoids storage overhead for large video files.
- The web UI keeps frames in memory (~50KB each) and packages them into a ZIP on the fly. Nothing is written to disk.
- The CLI writes to a project-local `output/` directory (gitignored).
- Supported video formats are defined in `extractor.py:VIDEO_EXTENSIONS`.
