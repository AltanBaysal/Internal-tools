# Queen Editor — Foundation

Engineering principles and architecture decisions, independent of any product shape.
Principles say which value wins when two collide while writing code; decisions record the
stack choices. Product decisions — screens, flows, behaviour — never enter
this file; they live in the current version's specs.

## Principles

Ordered: when two principles collide, the one higher on this list wins.

**1. The user's work is sacred.**
No scenario may lose data or finished work: machines die, jobs don't. Nothing is
overwritten, nothing is silently deleted; every destructive action is explicit and
confirmed. A half-done job survives a restart and continues from where it stopped.

**2. Truth lives on disk.**
Process memory is as disposable as the machine it runs on. Any state that matters — job
progress, user arrangements, outputs — is written to the persistent store as files, and
the app rebuilds itself from those files after a restart.

**3. Correctness > simplicity > generality > performance.**
YAGNI is ruthless: no abstraction before a proven need, no optimization before a measured
problem, no feature before a real user ask.

**4. Code is optimized for regenerability — it is written and maintained with AI.**
AI inverts the human cost curve: volume is cheap, complexity is expensive. It writes large
amounts of simple code fast and correctly, and it breaks dense code on every later edit.
So every unit stays simple and bounded enough to be rewritten from its spec alone;
unavoidable cleverness is confined to one small, isolated, heavily tested core. A file too
big to hold comfortably in context is doing too much — split it.

## Decisions

**1. The app runs on Colab; git is the delivery channel.**
The notebook clones this **private** repo with a GitHub token read from Colab Secrets (the
token is never printed) and runs what it finds there. Why: Colab provides the GPU for free /
cheap and we already live there; the repo stays the single source of truth — no separate
deploy artifact. Consequence: **every Colab test needs commit+push first**; unpushed work is
invisible to Colab.

**2. Backend is sync Flask; frontend is React 18 built with Vite.**
Why: the backend is thin — file operations, kicking off a job, polling status — so sync Flask
is enough and is preinstalled in Colab; the UI comes from the claude.ai/design project, which
is React. We deliberately do not copy ComfyUI's aiohttp/Vue choices — it made them for a
heavy concurrent engine, our needs differ. Layering rules and the full reasoning:
[CODE-STANDARD.md](CODE-STANDARD.md).

**3. The frontend ships pre-built; Colab never builds.**
`frontend/dist/` is committed and served as static files. Why: no node toolchain in the
runtime keeps Colab startup fast and removes a whole class of install failures. Consequence:
after any change under `frontend/src/`, run `npm run build` and commit the regenerated
`dist/` **in the same commit**, or Colab serves a stale UI. `vendor/` files come verbatim
from the claude.ai/design project.

**4. The frontend is a view; the rules live in the backend.**
The browser renders state and collects input. It never reaches Drive or ComfyUI directly, and
it never owns a decision a test would assert. Why: rules stay testable with no browser, no GPU
and no mounted Drive, and they have exactly one home — a rule copied into the UI drifts from
the server's the first time either side changes. The tunnel URL is also public and
unauthenticated, so a browser able to read the store would hand it to anyone with the link.
Consequence: a new capability needs an endpoint, never a direct file read — photos included,
which the backend serves. Presentation concerns (formatting, what is enabled, an estimate shown
while typing) stay in the UI; an estimate that mirrors a server rule is shown as a preview and
never enforced.

**5. The browser reaches the server through a cloudflared tunnel.**
Why: Colab has no public ingress; the tunnel gives a shareable URL with zero infrastructure.

**6. ComfyUI is the engine for pictures and video; sound runs in our own process.**
ComfyUI runs headless on the Colab machine as a local API, and we write our own client and job
handling on top of it — for photos and for videos, each one a graph we ship. We never patch or
embed ComfyUI itself. Sound is the exception: MMAudio is called as a library inside the Flask
process, with no graph at all.

Why one engine for two of the three: the picture and video pipelines (models, custom nodes, graph)
are proven and not worth rebuilding, while our own code stays testable and swappable. Why not the
third: the sound pipeline that is proven drives MMAudio directly, and reaching it through ComfyUI
would have meant building a graph nobody has — a second way of doing something that already works.
The cost is a second engine to install and a second model on the card; the alternative was untested
work standing between us and a library call.

**7. Google Drive is the only persistent store.**
Everything that must survive the Colab session — outputs, project data — lives under one
Drive root, and that root folder is named in exactly one place: the notebook's CONFIG cell.
Why: Colab machines are disposable, Drive is where the user already works, and a single
naming point makes renaming a one-line change.

**8. No runtime dependency on `collab-toolbox/`.**
Knowledge and verbatim copies are inherited; no imported cell, no shared file, no shared
Drive folder. Why: the tools must be able to evolve and break independently. The full rule
and table: [CODE-STANDARD.md](CODE-STANDARD.md).

**9. The notebook installs the producers; the app only says what is here.**
Everything a producer needs — every model file — comes down in the notebook, before the server
starts. The app downloads nothing: its producers panel reads the disk and reports, and its Kur
button says where the install happens.
Why: the download machinery in `collab-toolbox` is proven against these sources and ours was not —
a gated file is served by a redirect to a storage host that answers 403 if the login cookie
travels with it, which the working cell knows and works around. Buying that knowledge twice, in a
second downloader, is work spent to arrive where we already are.
Consequence: a fresh machine is set up by one Run all, and a missing producer is fixed in the
notebook rather than in the app. The cost, stated plainly: the panel reports what another place
installed, so it can tell you what is missing but cannot fix it. It looks at real files, so it
cannot be wrong about what is there — only powerless about what is not.
This reverses an earlier version of this rule, which put installing in the app to stop the panel
from lying. The lie is still gone: the panel counts files, never an empty list.
