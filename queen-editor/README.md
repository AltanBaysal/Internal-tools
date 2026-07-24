# Queen Editor

A two-screen web UI over the `nova-3dcg` ComfyUI photo pipeline: create a project, paste a prompt
list, generate photos into a Google Drive folder. Runs on Google Colab.

Built in cumulative parts — see
[`docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md`](../docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md).
**Part 1** is only this: prove the private repo clones on Colab.

## Part 1 — Repo checkout

`app.ipynb` clones this private repo onto Colab and prints what it fetched. No server, no UI, no
Drive, no ComfyUI yet.

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

**Runtime → Run all.** The last cell prints the cloned commit and the contents of `queen-editor/`.
The token is read from Secrets and never appears in any output or in the notebook source.
