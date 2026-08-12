# Queen Editor

A two-screen web UI over the `nova-3dcg` ComfyUI photo pipeline: create a project, paste a prompt
list, generate photos into a Google Drive folder. Runs on Google Colab.

Built in cumulative parts — see
[`docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md`](../docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md).
So far: **Part 1** proved the private repo clones on Colab; **Part 2** serves the pre-built frontend
with Flask and opens a tunnel; **Part 3** adds the projects screen; **Part 4** brings ComfyUI up and
generates one photo per prompt into the project folder. Needs a **T4 GPU** runtime and a
`CIVITAI_COOKIE` secret from Part 4 on.

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
4. That's it. Both live in your Colab account, not in the notebook. Set them once; every
   session and every notebook can read them. Nothing to paste again, nothing to commit.

### 3. Run

**Runtime → Change runtime type → T4 GPU**, then **Runtime → Run all.** The notebook mounts Drive
(**grant access in the popup**), clones the repo, installs ComfyUI, its custom nodes and the sound
library (~5-10 min on the first run of a session), starts Flask and prints a cloudflared link.
**No model comes down here** — open the link and install the producers you need from the
**Üreticiler** panel, which is also where you can see what is already on the machine. Then
**+ Yeni proje** creates a folder under `MyDrive/queenEditor/`, and clicking a project opens the
screen where a prompt produces one photo. The secrets are read from Colab and never appear in any
output or in the notebook source.

Developer note: the frontend ships pre-built — after changing `frontend/src/`, run `npm run build`
in `frontend/` and commit the regenerated `dist/` (Colab never builds). Run the backend tests
locally with `pytest` from `queen-editor/`.
