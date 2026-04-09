# Desktop Toolbox

A desktop application that bundles multiple internal tools as modules. Built incrementally — Flet UI is planned, currently only a CLI exists for the first module.

## Modules

- **Video Frame Extractor** — Extracts the first frame from video files (MP4, AVI, MOV, MKV, WEBM) as JPG/PNG. Entry point: `main.py`. Core library: `extractor.py`.

## Commands

```bash
pip install -r requirements.txt

# Video Frame Extractor (CLI)
python main.py <folder_or_file_path> [--format png]
```

## Architecture

- **`extractor.py`** — Core library for the Video Frame Extractor module. Video discovery (`find_videos`) and frame extraction using OpenCV. Two extraction variants: disk-write (`extract_first_frame`) and in-memory bytes (`extract_first_frame_bytes`).
- **`main.py`** — CLI entry point for the Video Frame Extractor module. Writes extracted frames to `output/` directory on disk.

## Key Design Decisions

- Each module currently lives at the top level of this folder. Once a second module is added, modules will be reorganized into subfolders (e.g., `modules/frame_extractor/`).
- Videos are read directly from the user's filesystem path — never copied. This avoids storage overhead for large video files.
- The CLI writes to a project-local `output/` directory (gitignored).
- Supported video formats are defined in `extractor.py:VIDEO_EXTENSIONS`.

## Roadmap

- Add a Flet desktop UI as the primary interface, with the Video Frame Extractor as its first module.
- Add additional tool modules over time.
