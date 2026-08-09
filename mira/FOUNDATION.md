# Mira — Foundation

Engineering principles and architecture decisions, independent of any product shape.
Principles say which value wins when two collide while writing code; decisions record the
stack choices. Product decisions — screens, flows, behaviour — never enter this file; they
live in the specs.

## Principles

Ordered: when two principles collide, the one higher on this list wins.

**1. The user's work is sacred.**
No scenario may lose work the user already did. A message is written to disk *before* it is sent to
the engine, so a dropped connection cannot swallow it. A deleted file is moved, not destroyed, and
the move is reversible. Every destructive action is either explicitly confirmed or explicitly
undoable — never neither.

**2. Truth lives on disk.**
Process memory is as disposable as the machine it runs on. Any state that matters — projects, chats,
messages, files — is written to the store as files, and the app rebuilds itself from those files
after a restart.

**3. Correctness > simplicity > generality > performance.**
YAGNI is ruthless: no abstraction before a proven need, no optimization before a measured problem,
no feature before a real user ask.

**4. Code is optimized for regenerability — it is written and maintained with AI.**
AI inverts the human cost curve: volume is cheap, complexity is expensive. It writes large amounts of
simple code fast and correctly, and it breaks dense code on every later edit. So every unit stays
simple and bounded enough to be rewritten from its spec alone. A file too big to hold comfortably in
context is doing too much — split it.

## Decisions

**1. The app runs on the user's own machine.**
`python main.py` serves it on localhost. Why: the engine is a remote API, so there is no GPU to
borrow — Colab's one benefit does not apply here, while all of its costs (a dead session, secrets,
cloning the repo on every start) would. Consequence: the app is reachable only from that machine;
sharing it would need a decision we have not made.

**2. Backend is sync Flask; frontend is React 18 built with Vite.**
Why: the backend is thin — file operations, one outbound API call, streaming its result back — so
sync Flask is enough. The UI comes from a claude.ai/design project, which is React.

**3. The frontend is built on the machine that runs it; `dist/` is not committed.**
Why: the developer and the runtime are the same machine, so a pre-built artifact in the repo would
buy nothing and go stale. Consequence: a fresh clone needs `npm install && npm run build` before
`main.py` has anything to serve.

**4. The frontend is a view; the rules live in the backend.**
The browser renders state and collects input. It never reaches the store or the engine directly, and
it never owns a decision a test would assert. Why: rules stay testable with no browser and no
network, and they have exactly one home — a rule copied into the UI drifts from the server's the
first time either side changes. Presentation concerns (formatting, what is enabled, what is shown
while typing) stay in the UI.

**5. Disk is the only persistent store.**
Everything lives under one root, named in exactly one place: `MIRA_ROOT`. The root sits outside the
repo, so user data never lands in the source tree and `git status` never sees it.

**6. xAI Grok is the engine, behind our own thin layer.**
We write our own transport, our own agent loop and our own tools on top of it. Why: the loop and the
tools are the product; the vendor behind them should be replaceable without touching either.

**7. No dependency on `collab-toolbox/` or `queen-editor/`.**
No imported module, no shared file, no shared store. What Mira inherits from queen-editor is
documents, not code: the layering rules, the language split and the test discipline. Why: the tools
must be able to evolve and break independently.
