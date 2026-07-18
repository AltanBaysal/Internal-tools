# CLAUDE.md

Internal tools monorepo. Each tool lives in its own subfolder; currently one tool: **collab-toolbox**. Tool documentation lives in this file — when adding a tool, create a subfolder and add a section here.

## Working Rules

**Don't run shell/terminal commands (Bash, PowerShell, git CLI) unless necessary.** Use the dedicated tools for exploring, reading, searching and editing: Read, Grep, Glob, Edit, Write, NotebookEdit. Don't turn into a command what a file read or these tools can do.

**If a command really is needed, state the reason explicitly first** — one sentence on which job you couldn't do with which tool and what the command gives you, then run it.

## collab-toolbox — Colab notebooks

AI media generation/cleanup notebooks (`.ipynb`) that run on Google Colab. Each notebook is self-contained; the shared input/output channel is **Google Drive** (`MyDrive/...`). Most tools bring ComfyUI up in the background as an API and batch-process files from Drive.

**Reference structure: [collab-toolbox/loop_maker/comfy_ui.ipynb](collab-toolbox/loop_maker/comfy_ui.ipynb)** — a new notebook starts by copying it. Shared patterns: **[collab-toolbox/NOTEBOOK-STANDARD.md](collab-toolbox/NOTEBOOK-STANDARD.md)**.

| Notebook | Purpose | Hardware |
|---|---|---|
| [photo_generator/PhotoGenerator_API.ipynb](collab-toolbox/photo_generator/PhotoGenerator_API.ipynb) | Photo generation (SDXL + IPAdapter) | GPU |
| [video_generator/imageToVideo.ipynb](collab-toolbox/video_generator/imageToVideo.ipynb) | Image-to-video (WAN 2.2) | A100 (Colab Pro) |
| [video_generator/wan22-smooth-t2v/api.ipynb](collab-toolbox/video_generator/wan22-smooth-t2v/api.ipynb) | Text-to-video (WAN 2.2 SmoothMix) — prompt in CONFIG, video out to Drive, one per run | A100 (Colab Pro) |
| [video_generator/wan22-smooth-t2v/manual.ipynb](collab-toolbox/video_generator/wan22-smooth-t2v/manual.ipynb) | Same graph behind a cloudflared tunnel, driven by hand in the ComfyUI UI — for finding settings to export into `api.ipynb` | A100 (Colab Pro) |
| [loop_maker/comfy_ui.ipynb](collab-toolbox/loop_maker/comfy_ui.ipynb) | Batch video loop (Wan 2.1 VACE) | GPU |
| [mmaudio_generate.ipynb](collab-toolbox/mmaudio_generate.ipynb) | Audio for video (MMAudio, NSFW fine-tune) | T4 GPU |
| [mp4_converter.ipynb](collab-toolbox/mp4_converter.ipynb) | Video → H.264 mp4 | CPU |
| [frame_extractor.ipynb](collab-toolbox/frame_extractor.ipynb) | First frame from video (JPG/PNG) | CPU |
| [watermark/watermark_detection.ipynb](collab-toolbox/watermark/watermark_detection.ipynb) | Watermark detection (YOLOv11) → `results.json` | GPU |
| [watermark/watermark_remove.ipynb](collab-toolbox/watermark/watermark_remove.ipynb) | Watermark removal (ProPainter), driven by `results.json` | GPU |

Usage: [Colab](https://colab.research.google.com/) → **File → Upload notebook** → **Runtime → Change runtime type** and pick the hardware from the table → fill in the first **CONFIG** cell → **Run all**.

[collab-toolbox/video_experiments/](collab-toolbox/video_experiments/) — visual workflow experiments in the ComfyUI UI (no Drive).

## Notebook Comment Conventions

- **Language splits by reader.** **Turkish** = human-facing text *inside notebooks*: markdown cells and runtime output (`print` / `log` / `assert` / `RuntimeError` messages). **English** = everything a developer reads as code: comments (`#`), docstrings, and these repo docs (`CLAUDE.md`, `NOTEBOOK-STANDARD.md`).
- **A comment explains WHY, not WHAT.** e.g. `MAX_CHUNK_DURATION = 10  # model trained on 8s — large drift hurts quality`.
- **No drift (most important):** a comment describes what the code does RIGHT NOW; `# OLD:` / `# NEW:` traces and claims about past behaviour are banned. On a conflict **the comment is fixed to match the code**, never the reverse.
- **Never invent a cause in an error message:** print the command's or service's **actual output** (HTTP code + response body, `stderr` tail). Don't hardcode one fixed cause (e.g. a Civitai 401 is not "cookie expired" — a wrong selector returns 401 too).
- When only comments are being updated, **the code doesn't change** (prints, values, function logic and cell order stay as they are).
