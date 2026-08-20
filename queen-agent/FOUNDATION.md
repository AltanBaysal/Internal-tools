# QueenAgent — Foundation

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

**5. What a model would have to repeat, code does instead.**
Anything that must come out identical every time is assembled by a deterministic function, and the
model is left the part that genuinely needs judgement — the text itself. Why: attention is not a
guarantee. A character description copied by hand into forty prompts drifts, and the drift is
invisible until the images come back wrong; the same description resolved from one entry cannot
drift at all. Consequence: a tool that only joins known pieces (`build_prompts`) is preferred over
an instruction asking for care, and its input is data on disk the user can read and correct.

## Decisions

**1. The app runs on the user's own machine, and on Colab when it is being shared.**
`python main.py` on localhost is the primary road and stays that way: the engine is a remote API, so
there is no GPU to borrow and Colab's one benefit still does not apply. What settled the second road
was sharing — which this file used to call a decision we had not made. Handing the app to someone
else meant either an executable, rebuilt and re-sent by hand on every change, or a notebook that
clones this repo; and the app was already shaped for the notebook, since everything it is told from
outside travels in the environment — the root in `QUEENAGENT_ROOT`, the key in `XAI_API_KEY` — and
the only third-party dependency is Flask.
Consequence: Colab is a second surface, never a replacement, and its costs are paid where they land.
Drive holds the work, and the address is a public tunnel — Colab's own kernel proxy would have been
private, but it forwards only GET, and this app creates, sends and deletes. **The app carries no
login, so whoever holds the address holds everything behind it**: the files it keeps, and the key it
spends on their behalf. The key itself cannot be read back — the app stores none and there is no
endpoint that answers with one — but that is a limit on the damage, not a defence of the address.
What guards the address is that it is random and lasts one session. That is thin, and it is
accepted knowingly (owner's decision, 20 August) — the alternative was a password, and the cost of
one on every visit was judged higher than the risk of an address nobody has been given.

**2. Backend is sync Flask; frontend is React 18 built with Vite.**
Why: the backend is thin — file operations, one outbound API call, streaming its result back — so
sync Flask is enough. The UI comes from a claude.ai/design project, which is React.

**3. `frontend/dist` is committed, in the same commit as the source it was built from.**
Why: the premise of the old rule was that the developer and the runtime are the same machine, and
Decision 1 ended that. The notebook clones this repo and never builds, so a bundle that lives only on
the developer's disk arrives as a blank page — and a blank page never says why. Consequence: a
frontend change is not finished until `dist` is rebuilt and committed **with** its source; a bundle
committed one commit late is a lie about what the source says, and `test_dist_is_committed.py` is
what refuses it.

**4. The frontend is a view; the rules live in the backend.**
The browser renders state and collects input. It never reaches the store or the engine directly, and
it never owns a decision a test would assert. Why: rules stay testable with no browser and no
network, and they have exactly one home — a rule copied into the UI drifts from the server's the
first time either side changes. Presentation concerns (formatting, what is enabled, what is shown
while typing) stay in the UI.

**5. Disk is the only persistent store.**
Everything lives under one root, named in exactly one place: `QUEENAGENT_ROOT`. The root sits
outside the repo, so user data never lands in the source tree and `git status` never sees it.

**6. xAI Grok is the engine, behind our own thin layer.**
We write our own transport, our own agent loop and our own tools on top of it. Why: the loop and the
tools are the product; the vendor behind them should be replaceable without touching either.

**7. No dependency on `collab-toolbox/` or `queen-editor/`.**
No imported module, no shared file, no shared store. What QueenAgent inherits from queen-editor is
documents, not code: the layering rules, the language split and the test discipline. Why: the tools
must be able to evolve and break independently.
