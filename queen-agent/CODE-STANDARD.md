# QueenAgent — Code Standard

Two building blocks, feature-first. Read this before adding code.
The principles and stack decisions these rules serve: [FOUNDATION.md](FOUNDATION.md).

## Stack

Backend **Flask** (sync) + frontend **React 18** (JSX, built with Vite). The backend is thin: file
operations, one outbound API call, streaming its result back. Live progress is server-sent events,
not websockets — the stream is one-way and short-lived.

`frontend/dist` is committed, in the same commit as the source it was built from — the notebook
clones this repo and never builds (FOUNDATION, Decision 3). In development the UI runs on Vite's own
server and proxies `/api` to Flask, so a UI change does not cost a full build; the bundle is rebuilt
and committed when the change is finished, not on every save.

## Independence

QueenAgent depends on nothing under `collab-toolbox/` or `queen-editor/` — no imported module, no
shared file, no shared store. What it inherits from queen-editor is **documents, not code**: the layering
rules below, the language split, and the test discipline. The two tools must be able to evolve and
break independently.

## Separation of concerns

One artifact, one job: keep two things apart when they answer different questions, are written at
different moments, or have different lifetimes.

The store follows the same rule, and it is why there is no file-index file:

| Artifact | The question it answers | Written when |
|---|---|---|
| `project.json` | what is this project called, and since when | on create, on rename |
| `chats/<id>.json` | what was said in this conversation, and what it answers with | after each message, and on a model or skill choice |
| `files/<name>` | what did QueenAgent produce | when a file is created |
| `trash/<name>` | what did the user just delete | on delete — a chat and a file alike |

**No file repeats another's answer.** The file list is the directory listing itself: the name is the
filename, "2h ago" is its mtime, the order is mtime descending. The count on a sidebar project row is
a directory count. Before adding a field, ask which question it answers — a field that answers a fifth
question wants a fifth artifact, and a field that restates an answer already on disk wants deleting.

## Services (`backend/services/`)

A service does one job, lives in its own folder, and knows **no feature**:

- `store/` — read / write / list / move under one root. Knows nothing about projects, chats or files.
  Rejects any path that escapes the root.
- `xai/` — Grok HTTP transport: a request, an SSE stream, a resolved tool call. Knows no prompt, no
  filename, and nothing about what any tool does.

A service never imports a feature and never imports another service.

## Features (`backend/features/<name>/`)

A user-facing capability, composed of three layers:

- **domain/** — pure rules, port definitions (`Protocol`), use cases. Imports nothing external (no
  `flask`, no `requests`, no file-path or schema knowledge).
- **data/** — implements the ports using services; the only place that knows file schemas.
- **presentation/** — Flask routes; translates request/response, no business logic.

Dependency direction: `presentation → domain ← data → services`.
Bans (no exceptions): `feature ↛ feature`, `service ↛ feature`, `service ↛ service`.
Concrete classes are wired only in the composition root (`main.py`).

### One feature: `workspace`

`workspace` is one feature and not four. Projects, chats, files and messages cannot be separated,
because **writing a file in reply to a message touches all of them at once** — splitting them would
break `feature ↛ feature` on the first real use case. They are one aggregate.

And it is the only one. **The app has no feature for its own configuration**: everything it is told
from outside arrives in the environment and stops at `config.py`. There was a `settings` feature
once, holding the xAI key — it was deleted because the endpoint that served the key back was written
for a machine only its owner could reach, and Colab put the app behind a public address. The next
setting goes in `config.py` too; a feature is what the user makes things in, not where the app keeps
what it was told.

A third feature is created on the same test: a genuinely separate bounded context (sharing,
identity). Today there is none.

## Infrastructure (`backend/web/`)

Cross-cutting HTTP plumbing that is not a domain feature: the app factory (`app.py`) and probes like
`health.py`. It imports no feature — blueprints are handed to `create_app` by the composition root.

## Frontend (`frontend/src/`)

Same feature-first shape: `features/<name>/` with components and data access; `shared/` for what no
single feature owns — the two request roads and the one rule that reads a failure off a response, the
router, the clock, and the Markdown parser. Nothing in `shared/` imports a feature, and nothing in it
renders: the parser returns tokens and the component that turns them into elements lives with the
feature that draws them.

**There is no `vendor/` directory, and the design is a visual specification rather than source code.**
queen-editor copies component files verbatim from its design project; QueenAgent cannot. Its
prototype is a single monolithic `DCLogic` component with inline style strings and DC-only attributes such as
`style-hover` — there is no component file to copy. So we write the React ourselves and stay faithful
to the design's colours, type, measurements and behaviour.

`shared/app.css` owns the colour variables, the radii, the focus ring and the two keyframes — a
140–220ms `fadeIn` and the three dots' `blink`. A component never writes its own focus outline and
never invents a third animation. The only motion that is not a fade is the rail's width. The accent
`--accent` marks the primary action and nothing else.

## Language

**Everything is English**: UI text, code, comments, docstrings, test names and commit messages. The
superpowers specs and plans under `docs/` are Turkish.

This differs from queen-editor deliberately. That tool's rule is "UI text is Turkish"; QueenAgent's UI is
English because every string in its design was written in English, and translating them would stop
the design from being the source. Do not carry the neighbouring tool's rule over here.

## Tests

Backend: domain and use cases test with fake ports — no network, no real store.

Frontend: vitest + jsdom. Test files sit next to their source
as `<name>.test.js(x)`; they are never imported, so they stay out of `dist/`. Network and clock are
faked (`vi.stubGlobal("fetch", …)`, `vi.useFakeTimers()`) — no test waits a real second, and none of
them needs a browser or a network. Testing Library's `waitFor` does not understand vitest's fake
clock: advance it inside `act()` instead.
