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
- **A quantiser can stamp its output**, leaving a line of ASCII after the last tensor — `L2P_bypass_<source file>_<unix time>`, 85 bytes on `Abiray/MiniMax-H3-GGUF`'s int4 text encoder, and the server's `content-length` matches the download byte for byte. ComfyUI's own parser walks `data_offsets` and never sees it; the Rust `safetensors` parser demands the tensors cover the whole file and refuses to open it, so the same checkpoint loads or does not depending on which reader runs ([ComfyUI #15602](https://github.com/Comfy-Org/ComfyUI/issues/15602)). Worse, that refusal — *"incomplete metadata, file not fully covered"* — is also what a genuinely truncated file says, so the message cannot tell you which you have. **Cut the unreferenced tail before validating and print what came off**: those bytes lie past every declared tensor, so a file long enough to reach them is holding all of its data. An unexplained re-download of 15 GB is what this costs otherwise.

## 4) Civitai (login-gated) downloads

`loop_maker` only downloads from HuggingFace; the gated-download example is **[video_experiments/ltx23-eros/ltx23-eros.ipynb](video_experiments/ltx23-eros/ltx23-eros.ipynb)** (`civitai_url` / `cookie_header` / `civitai_probe`). These facts were learned in a run and cannot be guessed from the code:

- **Host `civitai.red`** — same-origin with the cookie. Sending to `.com` is cross-domain → returns the login+turnstile page.
- **Cookie name `__Secure-civ-token`** — auth moved to `auth.civitai.com` (2026-06); NOT the old `__Secure-civitai-token`. The value is a short ES256 JWT (~420 chars).
- **How to get it:** log in at `civitai.red` → F12 → Application → Cookies → **double-click the value → Ctrl+A → Ctrl+C**. Single-clicking the table cell truncates the token: `assert len>200` still passes but the token is invalid — a silent failure.
- **The cookie is read from Colab Secrets as `CIVITAI_COOKIE`**, never pasted into CONFIG — `COOKIE_VALUE = userdata.get('CIVITAI_COOKIE')`, then one assert that it was read and one that it is longer than 200 characters, each saying which mistake it caught. Secrets belong to the Google account, not to a notebook, and queen-editor reads the same name: `exp` is ~30 days, and a pasted copy per notebook made every refresh ten edits, while a stale token sat committed in each (owner's decision, 18 Sep 2026).
- **Never use a `?token=` API key** — the request then authenticates as that key's account → gated asset returns 401.
- **Probe first** — range-fetch the first 1 KB to verify access before any heavy download. The probe needs the **bare URL**; a file selector (`?fp=fp8`) returns 401 on probe but works on download.
- **B2 vs R2** — files redirected to `b2.civitai.com` get **403** from aria2c (it forwards the cookie to the store) but pass with curl → `curl_first=True`. R2 works with both. (A browser UA alone did not fix it.)

## 5) Batch

Resume: existing outputs are skipped, and a dropped session picks up where it left off. A `*Loader` failure is infrastructure (model corrupt/missing) → every video would hit the same error → the batch stops; a video-specific failure skips only that video. Example: `process_all()`.

## 6) Drive ↔ Colab disk

ComfyUI and the models live on local disk (speed), only data on Drive; the Colab copy is removed once the work is done.

## 7) Language and comments

See the root [../CLAUDE.md](../CLAUDE.md) — Working rules. One rule belongs here rather than there,
because it is about a kind of task only notebooks get: **when only the comments are being updated,
the code does not change** — prints, values, function logic and cell order stay as they are.
