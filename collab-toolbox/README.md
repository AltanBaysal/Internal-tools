# collab-toolbox

AI media generation/cleanup notebooks (`.ipynb`) that run on Google Colab. Each notebook is
self-contained; the shared input/output channel is **Google Drive** (`MyDrive/...`). Most tools bring
ComfyUI up in the background as an API and batch-process files from Drive.

**Reference structure: [loop_maker/comfy_ui.ipynb](loop_maker/comfy_ui.ipynb)** — a new notebook
starts by copying it. Shared patterns: **[NOTEBOOK-STANDARD.md](NOTEBOOK-STANDARD.md)**.

| Notebook | Purpose | Hardware |
|---|---|---|
| [photo_generator/PhotoGenerator_API.ipynb](photo_generator/PhotoGenerator_API.ipynb) | Photo generation (SDXL + IPAdapter) | GPU |
| [video_generator/imageToVideo.ipynb](video_generator/imageToVideo.ipynb) | Image-to-video (WAN 2.2) | A100 (Colab Pro) |
| [video_generator/wan22-smooth-t2v/api.ipynb](video_generator/wan22-smooth-t2v/api.ipynb) | Text-to-video (WAN 2.2 SmoothMix) — prompt list, one video per prompt, resumable | A100 (Colab Pro) |
| [video_generator/wan22-smooth-t2v/manual.ipynb](video_generator/wan22-smooth-t2v/manual.ipynb) | Same graph behind a cloudflared tunnel, driven by hand in the ComfyUI UI — for finding settings to export into `api.ipynb` | A100 (Colab Pro) |
| [loop_maker/comfy_ui.ipynb](loop_maker/comfy_ui.ipynb) | Batch video loop (Wan 2.1 VACE) | GPU |
| [mmaudio_generate.ipynb](mmaudio_generate.ipynb) | Audio for video (MMAudio, NSFW fine-tune) | T4 GPU |
| [mp4_converter.ipynb](mp4_converter.ipynb) | Video → H.264 mp4 | CPU |
| [frame_extractor.ipynb](frame_extractor.ipynb) | First frame from video (JPG/PNG) | CPU |
| [watermark/watermark_detection.ipynb](watermark/watermark_detection.ipynb) | Watermark detection (YOLOv11) → `results.json` | GPU |
| [watermark/watermark_remove.ipynb](watermark/watermark_remove.ipynb) | Watermark removal (ProPainter), driven by `results.json` | GPU |
| [queen-tools/prompt_converter.ipynb](queen-tools/prompt_converter.ipynb) | Queen Editor export → motion prompts (Grok), one request per frame | CPU |
| [queen-tools/photo_to_video.ipynb](queen-tools/photo_to_video.ipynb) | That plan file → video, photo by photo (WAN 2.2 I2V) | A100 (Colab Pro) |

**queen-tools is one chain, not two tools.** Queen Editor's Export file is turned into motion prompts
by `prompt_converter`, and `photo_to_video` reads the result and writes the videos under
`MyDrive/queen-tools/<project>/`. Queen Editor's own folder is only ever read — the design and its
reasoning: [docs/superpowers/specs/2026-08-09-queen-tools-design.md](../docs/superpowers/specs/2026-08-09-queen-tools-design.md).
Both notebooks take their work order from a file you upload, so nothing is picked from Drive by name.

Usage: [Colab](https://colab.research.google.com/) → **File → Upload notebook** → **Runtime → Change runtime type** and pick the hardware from the table → fill in the first **CONFIG** cell → **Run all**.

[video_experiments/](video_experiments/) — visual workflow experiments in the ComfyUI UI (no Drive).
