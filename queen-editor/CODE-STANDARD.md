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

## Services (`backend/services/`)
A service does one job, lives in its own folder, and knows **no feature**. Examples (land later):
`comfy/` (photo generator: prompt+negative+seed → bytes), `drive/` (read/write/list files).
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
- **vendor/** is copied from the claude.ai/design project and never hand-edited.

## Language
Code comments, docstrings, this file, and commit messages: **English**.
User-facing UI text and notebook markdown / `print` / `assert`: **Turkish**.

## Tests
Run `pytest` from `queen-editor/`. Domain and use cases test with fake ports — no ComfyUI, no Drive.
