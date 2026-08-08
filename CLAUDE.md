# CLAUDE.md

Internal tools monorepo. Each tool lives in its own subfolder; currently two tools: **collab-toolbox** and **queen-editor**. Tool documentation lives in this file — when adding a tool, create a subfolder and add a section here.

## Working Rules

**Don't run shell/terminal commands (Bash, PowerShell, git CLI) unless necessary.** Use the dedicated tools for exploring, reading, searching and editing: Read, Grep, Glob, Edit, Write, NotebookEdit. Don't turn into a command what a file read or these tools can do.

**If a command really is needed, state the reason explicitly first** — one sentence on which job you couldn't do with which tool and what the command gives you, then run it.

**Don't spawn subagents or run workflows unless explicitly asked for them.** Research, reading and multi-file work happen inline, with the ordinary tools. A subagent run is expensive and returns nothing at all when it is interrupted before finishing — the output is lost whole, not partially, so the cost is paid for zero.

## collab-toolbox — Colab notebooks

AI media generation/cleanup notebooks (`.ipynb`) that run on Google Colab. Each notebook is self-contained; the shared input/output channel is **Google Drive** (`MyDrive/...`). Most tools bring ComfyUI up in the background as an API and batch-process files from Drive.

**Reference structure: [collab-toolbox/loop_maker/comfy_ui.ipynb](collab-toolbox/loop_maker/comfy_ui.ipynb)** — a new notebook starts by copying it. Shared patterns: **[collab-toolbox/NOTEBOOK-STANDARD.md](collab-toolbox/NOTEBOOK-STANDARD.md)**.

| Notebook | Purpose | Hardware |
|---|---|---|
| [photo_generator/PhotoGenerator_API.ipynb](collab-toolbox/photo_generator/PhotoGenerator_API.ipynb) | Photo generation (SDXL + IPAdapter) | GPU |
| [video_generator/imageToVideo.ipynb](collab-toolbox/video_generator/imageToVideo.ipynb) | Image-to-video (WAN 2.2) | A100 (Colab Pro) |
| [video_generator/wan22-smooth-t2v/api.ipynb](collab-toolbox/video_generator/wan22-smooth-t2v/api.ipynb) | Text-to-video (WAN 2.2 SmoothMix) — prompt list, one video per prompt, resumable | A100 (Colab Pro) |
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

## queen-editor — Queen Editor (web UI)

A web UI over the same ComfyUI photo pipeline as `nova-3dcg`, running on Colab. Engineering
principles and stack decisions live in [queen-editor/FOUNDATION.md](queen-editor/FOUNDATION.md);
structure and layering rules in [queen-editor/CODE-STANDARD.md](queen-editor/CODE-STANDARD.md); the
build order is the roadmap
[docs/superpowers/plans/2026-08-08-queen-editor-v4-roadmap.md](docs/superpowers/plans/2026-08-08-queen-editor-v4-roadmap.md),
whose items are grounded in
[the design v2 difference report](docs/superpowers/research/2026-08-08-queen-editor-tasarim-v2-farklari.md)
(the [v3](docs/superpowers/plans/2026-08-08-queen-editor-v3-roadmap.md) and
[v2](docs/superpowers/plans/2026-08-03-queen-editor-v2-roadmap.md) roadmaps are closed).

**Same engine, separate tool.** Queen Editor depends on nothing under `collab-toolbox/` at runtime;
it inherits the graph and the node ids as knowledge and writes its own code for them. The boundary,
in full: [queen-editor/CODE-STANDARD.md](queen-editor/CODE-STANDARD.md).

**Build before commit.** The frontend ships pre-built — `frontend/dist/` is committed and Colab
serves it as-is (it never runs npm/build). After any change under `queen-editor/frontend/src/`, run
`npm run build` in `queen-editor/frontend/` and commit the regenerated `dist/` in the SAME commit,
or Colab serves a stale UI.
