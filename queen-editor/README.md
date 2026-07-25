# Queen Editor

A two-screen web UI over the `nova-3dcg` ComfyUI photo pipeline: create a project, paste a prompt
list, generate photos into a Google Drive folder. Runs on Google Colab.

Built in cumulative parts — see
[`docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md`](../docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md).
So far: **Part 1** proved the private repo clones on Colab; **Part 2** serves the pre-built
frontend with Flask and opens a tunnel — the page shows "sunucuya bağlı ✓". No Drive, no ComfyUI yet.

## Run on Colab

`app.ipynb` clones this repo (the built `frontend/dist/` ships with it), starts the Flask server,
and prints a cloudflared link. Open it to see the app connect to the server. Colab never builds —
it only serves.

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
3. That's it. The token lives in your Colab account, not in the notebook. Set it once; every
   session and every notebook can read it. Nothing to paste again, nothing to commit.

### 3. Run

**Runtime → Run all.** The notebook clones the repo, starts Flask (which serves the pre-built
`frontend/dist/`), and prints a cloudflared link. Open it — the page should show **"sunucuya bağlı ✓"**.
The token is read from Secrets and never appears in any output or in the notebook source.

Developer note: the frontend ships pre-built — after changing `frontend/src/`, run `npm run build`
in `frontend/` and commit the regenerated `dist/` (Colab never builds). Run the backend tests
locally with `pytest` from `queen-editor/`.
