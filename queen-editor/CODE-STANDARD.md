# Queen Editor — Code Standard

Two building blocks, feature-first. Read this before adding code.

## Stack
Backend **Flask** (sync) + frontend **React 18** (JSX, built with Vite). We follow ComfyUI's
*deployment* pattern — the frontend is built by the developer and the built `dist/` ships in the
repo; Colab only clones and serves, it never runs npm/build. We deliberately do NOT copy ComfyUI's
*libraries*:
- **React, not Vue** — the UI comes verbatim from the claude.ai/design project, which is React;
  rewriting it in Vue would throw away the approved design for zero gain. We share no code with
  ComfyUI's frontend — we only talk to its HTTP/JSON API, and the browser framework is invisible
  across that boundary.
- **Flask, not aiohttp** — ComfyUI is async because it is a heavy, highly-concurrent engine
  (live websocket node execution, long GPU runs). Our backend is thin: file ops + kick off a job +
  poll status. Sync Flask is simpler and already preinstalled in Colab (nothing extra to install).
  Live progress, when needed, is polling or SSE — not aiohttp's websocket machinery.

Matching ComfyUI's frameworks without its reasons would be cargo-culting: it chose them for its
needs, ours differ. Revisit only if we ever embed the UI *inside* ComfyUI as a custom node.

## Independence from collab-toolbox
Queen Editor wraps the same ComfyUI photo pipeline as `collab-toolbox/photo_generator/nova-3dcg/`,
but it depends on nothing there at runtime — no imported cell, no shared file, no shared Drive
folder. What we inherit is knowledge, not code:

| Inherited (knowledge) | Never (dependency) |
|---|---|
| The ComfyUI graph — copied into `queen-editor/workflow_api.json` as our own file | Reading `collab-toolbox/photo_generator/nova-3dcg/workflow_api.json`, or Drive's copy of it |
| Injection node ids (`PROMPT_NODE` `"3"`, `NEGATIVE_NODE` `"4"`, `SEED_NODE` `"40"`) | `api.ipynb`'s CONFIG cell |
| Setup cells (custom nodes, the 5 models, download/verify/401 handling, headless ComfyUI) — copied **verbatim** into `app.ipynb`, because that machinery is proven | Running or importing their cells, or reading a file they own. A copy is not a dependency; its cost is that the two notebooks are maintained separately |
| Proven behaviour: `/prompt` → `/history` → `/view`, infra-vs-frame error split, stop after 3 in a row | Copying those functions — we write them into our own layers |

Every direct subfolder of our Drive root is a project, so the root must be ours alone: point it at
the notebook's folder and its `output/` shows up as a phantom project card. The root is never
hardcoded — the server reads `QE_DRIVE_ROOT`, and `app.ipynb`'s CONFIG cell is the one place that
names the folder (`DRIVE_FOLDER`, currently `queenEditor`). Renaming it is a one-line change there,
so do not repeat the name in comments, docstrings or here.

The batch behaviour is the notebook's, the code is ours: same rules, written into `services/comfy/`
(HTTP transport) and `features/photo_generation/` (node ids, file names, the worker), where they can
be tested. Rule of thumb: **graph and reasoning shared, code and folders separate.**

## Services (`backend/services/`)
A service does one job, lives in its own folder, and knows **no feature**: `comfy/` (ComfyUI HTTP
transport — submit a graph, wait for it, fetch the produced file; no node id, no prompt, no media
concept), `drive/` (read/write/list files under one root).
A service never imports a feature and never imports another service.

## Features (`backend/features/<name>/`)
A user-facing capability, composed of three layers:
- **domain/** — pure rules, port definitions (`Protocol`), use cases. Imports nothing external
  (no `flask`, `requests`, or file-path/schema knowledge).
- **data/** — implements the ports using services; the only place that knows file schemas.
- **presentation/** — Flask routes; translates request/response, no business logic.

Dependency direction: `presentation → domain ← data → services`.
Bans (no exceptions): `feature ↛ feature`, `service ↛ feature`, `service ↛ service`.
Concrete classes are wired only in the composition root (`backend/main.py`).

## Infrastructure (`backend/web/`)
Cross-cutting HTTP plumbing that is not a domain feature: the app factory (`app.py`) and probes
like `health.py`. No `features/` folder is created until a real feature exists (Part 3: projects).

## Frontend (`frontend/src/`)
Same feature-first shape: `features/<name>/` with components + hooks (data access);
`shared/` for the fetch wrapper and app CSS; `vendor/` for verbatim design files.
- **vendor/** is copied from the claude.ai/design project and never hand-edited. One exception,
  mechanical and reviewable: a file may be adapted **at its export boundary only** — the design
  project writes to globals (`Object.assign(window, {…})`), which no ES module can import, so that
  last block becomes `export {…}`. Component bodies, styles and comments stay verbatim, and
  re-pulling a file is still a one-line change. Anything the design copy gets wrong for our app
  (e.g. `.wf-scrim` being `position: absolute` because artboards are framed) is fixed in
  `shared/app.css`, never in `vendor/`.

## Language
Code comments, docstrings, this file, and commit messages: **English**.
User-facing UI text and notebook markdown / `print` / `assert`: **Turkish**.

## Tests
Run `pytest` from `queen-editor/`. Domain and use cases test with fake ports — no ComfyUI, no Drive.
