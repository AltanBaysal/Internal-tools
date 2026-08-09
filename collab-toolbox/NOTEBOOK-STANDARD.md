# Notebook standard — collab-toolbox

Reference: **[loop_maker/comfy_ui.ipynb](loop_maker/comfy_ui.ipynb)** — a new notebook starts by copying it.

Below is **the rule + where the example lives in code**. Detailed rationale sits in the example's docstrings; **when they disagree, the code is right**.

## 1) CONFIG

All settings in one cell; **Drive mount first** — the auth prompt should appear in the first second, not halfway through a 40-minute model download. Example: `loop_maker` CONFIG cell.

## 2) Error policy

Errors are **loud** — a corrupt model, a service that never starts, or HTML downloaded as a "model" never passes silently: `RuntimeError`. The message is printed **raw** (the command's or server's own output); never invent a cause. Example: `run()`, `describe_comfy_error()`.

## 3) Model downloads

Every downloaded file is validated; on corruption the run stops and nothing is deleted (the invalid file stays on disk for inspection). Example: `fetch()`, `check_safetensors()`.

Traps that cost real time — don't rediscover them:
- **Never ask for the size via HEAD / `Content-Length`.** HF's Xet CDN answers HEAD on a signed URL with **403**, and that 403's 48-byte body was read as "file size" — a fully downloaded 34.7 GB model got declared truncated.
- **`curl --fail-with-body`, not `--fail`.** `--fail` swallows the body, leaving only "403".
- **HF Xet rejects parallel byte ranges with 403** → single-connection curl (`parallel=False`).

## 4) Civitai (login-gated) downloads

`loop_maker` only downloads from HuggingFace; the gated-download example is **[video_experiments/ltx23-eros/ltx23-eros.ipynb](video_experiments/ltx23-eros/ltx23-eros.ipynb)** (`civitai_url` / `cookie_header` / `civitai_probe`). These facts were learned in a run and cannot be guessed from the code:

- **Host `civitai.red`** — same-origin with the cookie. Sending to `.com` is cross-domain → returns the login+turnstile page.
- **Cookie name `__Secure-civ-token`** — auth moved to `auth.civitai.com` (2026-06); NOT the old `__Secure-civitai-token`. The value is a short ES256 JWT (~420 chars).
- **How to get it:** log in at `civitai.red` → F12 → Application → Cookies → **double-click the value → Ctrl+A → Ctrl+C**. Single-clicking the table cell truncates the token: `assert len>200` still passes but the token is invalid — a silent failure.
- **The cookie lives in CONFIG and is committed with the notebook** — accepted practice here; don't try to strip it. `exp` ~30 days; log in again to refresh once it expires. One exception, by owner's decision: `queen-tools/photo_to_video.ipynb` reads it from Colab Secrets (`CIVITAI_COOKIE`), because that notebook already reads a secret and a half-and-half CONFIG read badly.
- **Never use a `?token=` API key** — the request then authenticates as that key's account → gated asset returns 401.
- **Probe first** — range-fetch the first 1 KB to verify access before any heavy download. The probe needs the **bare URL**; a file selector (`?fp=fp8`) returns 401 on probe but works on download.
- **B2 vs R2** — files redirected to `b2.civitai.com` get **403** from aria2c (it forwards the cookie to the store) but pass with curl → `curl_first=True`. R2 works with both. (A browser UA alone did not fix it.)

## 5) Batch

Resume: existing outputs are skipped, and a dropped session picks up where it left off. A `*Loader` failure is infrastructure (model corrupt/missing) → every video would hit the same error → the batch stops; a video-specific failure skips only that video. Example: `process_all()`.

## 6) Drive ↔ Colab disk

ComfyUI and the models live on local disk (speed), only data on Drive; the Colab copy is removed once the work is done.

## 7) Language

See the root [../CLAUDE.md](../CLAUDE.md) — Notebook Comment Conventions.
