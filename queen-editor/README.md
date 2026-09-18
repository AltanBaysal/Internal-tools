# Queen Editor

A web UI for making a sequence of frames. A project holds frames; a frame starts as a photo and can
carry a video and a sound layer on top of it, and the export joins them into one folder you can hand
on. Photos and videos are rendered by ComfyUI, sound by MMAudio inside the app's own process, and
everything lands in Google Drive.

Runs on Google Colab: `queeneditor.ipynb` mounts Drive, clones this repo, installs the producers,
starts Flask and prints a cloudflared link. Colab never builds — it only serves.

## Before the first run

Upload `queen-editor/queeneditor.ipynb` to Colab (**File → Upload notebook**), then add these in the
**Secrets** panel (🔑, left sidebar) with **Notebook access** on. They live in your Colab account:
set once, nothing to paste again and nothing to commit.

| Secret | What it is for |
|---|---|
| `GITHUB_TOKEN` | Cloning this repo. Make it fine-grained, **this repository only, Contents: read-only** — leaked, it can only read this one repo. |
| `CIVITAI_COOKIE` | The `__Secure-civ-token` cookie from `civitai.red` (log in → F12 → Application → Cookies). The notebook downloads the gated photo and video files with it. It expires every ~30 days; re-paste it when an install stops with Civitai's own response. A sound-only run needs none. |
| `XAI_API_KEY` | Video only: a video's prompt is written by xAI when the job's turn comes. Without it photos still render and a video job stops with the client's own sentence. |

## Run

In the **CONFIG** cell pick the producers you want — `INSTALL_PHOTO` (~8 GiB), `VIDEO_MODEL`
(`WAN` ~39 GiB or `H3` ~37 GiB; one per session, and H3 does not run on a T4), `INSTALL_AUDIO`
(~9 GiB). Pick the runtime for what you install: a T4 carries photo and sound, video wants more disk
and H3 more memory. Everything starts off and the notebook stops if nothing is chosen, because an
app with no producer opens fine and renders nothing.

Then **Runtime → Run all** and grant Drive access in the popup. Open the printed link: the
**Üreticiler** panel says what is on the machine, and anything missing is installed by running the
notebook again with that box ticked — never from the app. **+ Yeni proje** creates a folder under
`MyDrive/queenEditor/`.

## Rules

Principles: [FOUNDATION.md](FOUNDATION.md) · layering and structure:
[CODE-STANDARD.md](CODE-STANDARD.md) · how we work: [CLAUDE.md](../CLAUDE.md).

The frontend ships pre-built, so a source change is not a change until `dist/` is rebuilt and
committed with it — and not testable until it is pushed, because the notebook clones the repo.
