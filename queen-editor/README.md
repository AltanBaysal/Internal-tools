# Queen Editor

A web UI for making a sequence of frames. A project holds frames; a frame starts as a photo and can
carry a video and a sound layer on top of it, and the export joins them into one folder you can
hand on. Photos and videos are rendered by ComfyUI, sound by MMAudio inside the app's own process,
and everything lands in a Google Drive folder. Runs on Google Colab.

The app installs its own producers — no model file comes down in the notebook. Built roadmap by
roadmap; the closed ones are under
[`docs/superpowers/plans/`](../docs/superpowers/plans/). Needs a **T4 GPU** runtime, a
`CIVITAI_COOKIE` secret, and an `XAI_API_KEY` if you want video.

## Run on Colab

`app.ipynb` mounts Google Drive, clones this repo (the built `frontend/dist/` ships with it), starts
the Flask server, and prints a cloudflared link. Colab never builds — it only serves.

### 1. Create a GitHub token (once)

A fine-grained token scoped to this repo only, read-only:

1. GitHub → **Settings → Developer settings → Fine-grained tokens → Generate new token**.
2. **Repository access → Only select repositories → `Internal-tools`**.
3. **Repository permissions → Contents → Read-only**. No other permission is needed.
4. Generate and copy the token.

If the token leaks, it can only *read* this one repo — nothing else.

### 2. Store the token in Colab (once)

1. Download `queen-editor/app.ipynb` from GitHub and upload it to Colab (**File → Upload notebook**).
2. Open the **Secrets** panel (🔑 icon, left sidebar) → **Add new secret**:
   - **Name:** `GITHUB_TOKEN`
   - **Value:** the token from step 1
   - Toggle **Notebook access** on.
3. Add a second secret the same way — **Name:** `CIVITAI_COOKIE`, **Value:** the
   `__Secure-civ-token` cookie from `civitai.red` (log in → F12 → Application → Cookies). The
   notebook hands it to the app, which uses it for the gated model downloads. It expires every
   ~30 days; re-paste it when an install stops with Civitai's response.
4. A third one if you want video — **Name:** `XAI_API_KEY`. A video's prompt is written by xAI when
   the job's turn comes; without the key photos still render and a video job stops with the
   client's own sentence.
5. That's it. They live in your Colab account, not in the notebook. Set them once; every session
   and every notebook can read them. Nothing to paste again, nothing to commit.

### 3. Run

**Runtime → Change runtime type → T4 GPU**, then **Runtime → Run all.** The notebook mounts Drive
(**grant access in the popup**), clones the repo, installs ComfyUI and its custom nodes (~5-10 min
on the first run of a session), starts Flask and prints a cloudflared link. **Nothing a producer
needs comes down here** — open the link and install the producers you want from the **Üreticiler**
panel, which is also where you can see what is already on the machine. Then **+ Yeni proje**
creates a folder under `MyDrive/queenEditor/`, and clicking a project opens the screen where
prompts become frames, a frame grows a video and a sound layer, and the export writes the whole
sequence out. The secrets are read from Colab and never appear in any output or in the notebook
source.

Developer note: the frontend ships pre-built — after changing `frontend/src/`, run `npm run build`
in `frontend/` and commit the regenerated `dist/` (Colab never builds). Run the backend tests
locally with `pytest` from `queen-editor/`.
