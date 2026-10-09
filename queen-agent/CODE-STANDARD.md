# QueenAgent — Code Standard

Two building blocks, feature-first.
The principles and stack decisions these rules serve: [FOUNDATION.md](FOUNDATION.md).

## Stack

Backend Flask (sync) + frontend React 18 (JSX, built with Vite) — why: FOUNDATION, Decision 2. Live
progress is server-sent events, not websockets — the stream is one-way and short-lived.

`frontend/dist` is committed with its source (FOUNDATION, Decision 3). In development the UI runs on
Vite's own server and proxies `/api` to Flask, so a UI change does not cost a full build; the bundle
is rebuilt and committed when the change is finished, not on every save.

## Independence

QueenAgent depends on nothing under `collab-toolbox/` or `queen-editor/` — no imported module, no
shared file, no shared store. What it inherits from queen-editor is documents, not code: the
layering rules below, the language split, and the test discipline.

## Separation of concerns

One artifact, one job: keep two things apart when they answer different questions, are written at
different moments, or have different lifetimes.

The store follows the same rule:

| Artifact | The question it answers | Written when |
|---|---|---|
| `projects.json` | which projects there are; what each is called, since when, whether it is pinned (and since when) or archived; which chats and files it holds, with what a list shows of them | by the one queued writer, a moment after any of these changes |
| `<id>/chats/<cid>.json` | what was said in this conversation, and what it answers with | after each message, on opening a version, and on a trim — before its entry |
| `<id>/files/<name>` | what did QueenAgent produce | when a file is written — before its entry |
| `<id>/trash/<name>` | what did the user just delete | on a file's delete |
| `trash/<id>/` | which project did the user delete — its folder whole, with its entry as `project.json` | on a project's delete |

`projects.json` is the one place a list is read from (Madde 447): the project list, the sidebar's
chats, the files panel and the agent's file names all come out of the server's memory of it, and a
chat or a file is opened only once its entry names it. To be that, it repeats on purpose what a list
shows of a chat — its title, birth and last activity — and of a file — its time. That is the one
exception to "no file repeats another's answer" (Madde 346), and it holds because both copies are
written by the same server at the same moment, contents first. Nothing else is repeated: the
counts, a project's last use (its newest chat's, or its createdAt while it has none) and a file's
chip are read off the entries and never written. Before adding a field, ask which question it
answers — a field that answers a new question wants an artifact of its own, and a field that
restates an answer already on disk wants deleting.

## Services (`backend/services/`)

A service does one job, lives in its own folder, and knows no feature:

- `store/` — read / write / list / move under one root. Knows nothing about projects, chats or files.
  Rejects any path that escapes the root.
- `model/` — HTTP transport to an OpenAI-compatible chat API: a request, an SSE stream, a resolved
  tool call. Knows no prompt, no filename, and nothing about what any tool does.

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
because writing a file in reply to a message touches all of them at once — splitting them would
break `feature ↛ feature` on the first real use case. They are one aggregate.

And it is the only one. The app has no feature for its own configuration: everything it is told
from outside arrives in the environment and stops at `config.py`. There was a `settings` feature
once, holding the API key — it was deleted because the endpoint that served the key back was written
for a machine only its owner could reach, and Colab put the app behind a public address. The next
setting goes in `config.py` too; a feature is what the user makes things in, not where the app keeps
what it was told.

A second feature is created on the same test: a genuinely separate bounded context (sharing,
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

There is no `vendor/` directory, and the design is a visual specification rather than source code.
queen-editor copies component files verbatim from its design project; QueenAgent cannot. Its
prototype is a single monolithic `DCLogic` component with inline style strings and DC-only attributes
such as `style-hover` — there is no component file to copy. So we write the React ourselves and stay
faithful to the design's colours, type, measurements and behaviour.

`shared/app.css` owns what every surface shares — the colour variables, the radii, the focus ring and
the shared keyframes — so a component writes no focus outline of its own. The accent `--accent` marks
the primary action alone.

## Language

Everything is English — UI text, code, comments, docstrings, test names and commit messages — and
the specs and plans under `docs/` are Turkish.

The UI differs from queen-editor's Turkish on purpose, so that tool's rule does not carry over here:
every string in the design was written in English, and translating them would stop the design from
being the source.

## Tests

Backend: domain and use cases test with fake ports — no network, no real store.

Frontend: vitest + jsdom. Test files sit next to their source as `<name>.test.js(x)`; they are never
imported, so they stay out of `dist/`. Network and clock are faked (`vi.stubGlobal("fetch", …)`,
`vi.useFakeTimers()`) — no test waits a real second or needs a browser. Testing Library's
`waitFor` does not understand vitest's fake clock: advance it inside `act()` instead.
