# Desktop Toolbox

A Flet-based desktop application that bundles multiple internal tools as modules. Modular from day one — adding a new tool means dropping a folder under `modules/` and adding one line to `app/routes.py`.

## Modules

- **Video Frame Extractor** (`modules/frame_extractor/`) — Extracts the first frame from video files (MP4, AVI, MOV, MKV, WEBM) as JPG/PNG.

## Commands

```bash
pip install -r requirements.txt

# GUI (Flet desktop app)
python main.py

# CLI (fallback / smoke test of the service path)
python -m cli.frame_extractor <folder_or_file_path> [--format png]
```

## Project Structure

```
desktop-toolbox/
├── main.py                      # Flet entry point
├── requirements.txt
├── app/                         # App shell — framework-level concerns
│   ├── module.py                # ModuleSpec dataclass — the module contract
│   ├── routes.py                # Single source of truth for mounted modules
│   ├── shell.py                 # NavigationRail + content slot (root view "/")
│   └── theme.py                 # Visual constants
├── modules/                     # One folder per tool
│   └── frame_extractor/
│       ├── __init__.py          # Exports `module_spec`
│       ├── view.py              # FrameExtractorView — pure UI
│       ├── controller.py        # State + event handlers + page.run_task
│       └── service.py           # Async wrapper around core; the only place asyncio lives
├── core/                        # Framework-agnostic libraries shared by modules
│   └── extractor.py             # OpenCV frame extraction (find_videos, extract_first_frame, ...)
└── cli/                         # Command-line entry points (kept as fallbacks)
    └── frame_extractor.py
```

## Architecture

The app follows a four-layer separation. Each layer only knows about the one directly below.

| Layer | Lives in | Knows about | Examples |
|---|---|---|---|
| **View** | `modules/<m>/view.py` | Flet, controller | Widgets, layouts, event bindings |
| **Controller** | `modules/<m>/controller.py` | View, service, `ft.Page` | UI state, event handlers, `page.run_task(...)` |
| **Service** | `modules/<m>/service.py` | Core | `asyncio.to_thread(...)` wrapping blocking calls |
| **Core** | `core/<lib>.py` | Stdlib + third-party only | Pure Python, no Flet, no asyncio |

The shell (`app/shell.py`, `app/routes.py`) is the only place that knows the full list of modules. A `ModuleSpec` (`app/module.py`) is the contract: each module exports one of these and the shell wires it into navigation.

## Key Design Decisions

- **Flet is pinned to `0.28.3`** (last stable release before the 1.0-alpha line). The 0.80+ alpha churned APIs weekly and shipped internally inconsistent builds. Lift the pin only when Flet 1.x is actually stable.
- **No third-party Flet framework.** We use Flet's built-in `page.on_route_change` + `page.views` stack. Community frameworks (FletX, Flet-Easy, Fletched) are single-maintainer hobby projects — KISS says no.
- **Long-running work uses `page.run_task` + `asyncio.to_thread`.** `threading.Thread` is documented to deadlock after `flet build` — the official async path is the safe choice.
- **Core stays framework-agnostic.** `core/extractor.py` has zero `import flet` and zero `import asyncio`. This keeps it CLI-friendly, test-friendly, and reusable.
- **Per-module state lives in the controller.** No global state store. If/when a second module needs to share state with the first, we'll add it then.
- **The CLI is a feature, not a leftover.** It validates the service path end-to-end without involving Flet, which makes debugging much easier.
- Videos are read directly from the user's filesystem — never copied. Avoids storage overhead for large videos.
- Supported video formats are defined in `core/extractor.py:VIDEO_EXTENSIONS`.

## Adding a New Module

1. Create `modules/<your_module>/` with `service.py`, `controller.py`, `view.py`, and `__init__.py`.
2. In `__init__.py`, build a `ModuleSpec` and assign it to a top-level `module_spec` name.
3. Open `app/routes.py` and add your module to the `MODULES` list. That's it.

## Roadmap

- Thumbnail previews of extracted frames
- Persisting last-used input/output folders
- `flet build windows` packaging
- Additional tool modules
