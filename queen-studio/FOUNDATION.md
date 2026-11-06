# Queen Studio — Foundation

Engineering principles and architecture decisions, independent of any product shape. Principles say
which value wins when two collide while writing code; decisions record the stack choices and why.
Product decisions — endpoints, screens, behaviour — never enter this file: they live in the design
steps and the specs. The steps are in [docs/research](../docs/research/2026-11-03-yeni-editor-v1-tasarim-adimlar.md),
in Turkish; "the new editor" there is this tool.

## Principles

Ordered: when two principles collide, the one higher on this list wins.

**1. The user's work is sacred.**
Nothing is done twice and nothing is lost — not when the core restarts mid-job, a response is lost and
the call is sent again, or a Colab closes. A change happens whole or not at all, and counts as done
only once the store has accepted it. Nothing in the store is deleted for good, only moved to Drive's
trash.
([Step 4, Değerlendirme](../docs/research/2026-11-03-yeni-editor-v1-4-depo.md#1-dayanıklılık))

**2. Truth lives in the store.**
Process memory is as disposable as the Colab it runs on. Reads are answered from memory, checked
against Drive at most every 5 s
([step 4, Başka Colab'ın yaptığını görmek](../docs/research/2026-11-03-yeni-editor-v1-4-depo.md#başka-colabın-yaptığını-görmek));
every change is written to Drive within its request, never later in the background. Why: a change not yet on Drive
is one the other Colabs cannot see, and one a dying core loses while the agent thinks it done
([step 4, Ana fikir](../docs/research/2026-11-03-yeni-editor-v1-4-depo.md#ana-fikir)).

**3. Every Drive call is counted.**
On Drive each call is a round trip, and a needless one shows no error: it only makes everything slower
and dearer, so only a test catches it. The rules: [CODE-STANDARD, Cost](CODE-STANDARD.md#cost).

**4. The agent's context is paid on every call.**
The agent is the core's main user, and what enters its context it pays for on each turn after: the API's
index, a list's default fields and the errors stay short, measured against recorded limits, and an
image reaches it as an image, never as text ([step 8](../docs/research/2026-11-03-yeni-editor-v1-8-agent-tarafi.md),
[step 12](../docs/research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md#mutlaka-sıkı-test-edilenler)).

**5. Correctness > simplicity > generality > performance.**
YAGNI: no abstraction before a proven need, no optimization before a measured problem, no feature
before a real user ask. Principles 3 and 4 are not optimization in this sense: they are budgets, set
in the design and tested.

**6. Code is optimized for regenerability — it is written and maintained with AI.**
Volume is cheap, complexity is expensive: it breaks dense code on every later edit. So every unit stays
simple and bounded enough to be rewritten from its spec alone. A file too big to hold comfortably in
context is doing too much — split it.

## Decisions

**1. One core, every rule in it; the agent and the UI call the same endpoints.**
The agent reaches the core through an MCP adapter of ours that offers one tool; the UI is a view that
renders and collects input. Why: a rule has one home and cannot drift, and a new agent or harness
changes nothing in the core ([overview](../docs/research/2026-11-03-yeni-editor-v1-tasarim.md),
[step 8](../docs/research/2026-11-03-yeni-editor-v1-8-agent-tarafi.md)).

**2. Python with FastAPI; the UI in React and TypeScript.**
Why FastAPI: the skeleton of `GET /api` — endpoints, their fields and types — comes out of the code
and changes with it, and the same OpenAPI becomes the UI's TypeScript types, so a core change the UI
does not follow fails at the UI's build, not on the screen. Its own terse error messages are replaced
by ours. Endpoints are plain `def`, not `async`, so a slow Drive call holds one worker, not the
server. An endpoint that reads memory only is `async` (the index, health): it needs no worker, so it
still answers while waiting requests hold them all, and the agent never reads a busy core as gone.
The whole stack: [step 5](../docs/research/2026-11-03-yeni-editor-v1-5-backend-yigini.md).

**3. The core reaches its data through a storage port.**
The port speaks of a project's records, not of Drive's files, and has no permanent delete. Two
adapters stand behind it: Drive's, through the Drive API rather than a mount, and an in-memory one the
tests run on, which can inject faults. Why: the same contract tests run on both, and moving to a
single database later is an adapter change ([step 4, Depo portu](../docs/research/2026-11-03-yeni-editor-v1-4-depo.md#depo-portu)).

**4. It runs on Colab, started by a notebook.**
The notebook clones this repo, installs ComfyUI and its nodes and starts the core; it downloads no
model — the agent has the core download what it needs. The core reads its settings and secrets from
the environment, since Colab Secrets answer only the notebook. The tunnel opens only on Pro
([step 10](../docs/research/2026-11-03-yeni-editor-v1-10-barindirma.md)). On this machine one
command, from the repo's root, opens the core with its UI at `http://127.0.0.1:8200`:
`queen-studio/.venv/Scripts/python queen-studio/main.py`. Its log and identity go to the repo's
git-ignored `tmp/queen-studio/`.

**5. The address carries no password.**
It is random and lasts one session, and whoever holds it can do everything. Accepted knowingly: what
is deleted goes to Drive's trash ([step 10, Erişim](../docs/research/2026-11-03-yeni-editor-v1-10-barindirma.md#erişim)).

**6. Tests touch only the test account, and no agent reads a secret.**
Tests and measurements run on a separate test Google account, never the company's. Its keys live in
the git-ignored `.secrets/` folder, which no agent reads: scripts take a path and never print a value.
Colab Secrets cannot be fetched from a Colab CLI session, so CLI runs get their values from an env
file sent to the VM. Why, and how each is enforced: [decisions log, Sapmalar 1–4](../docs/roadmaps/2026-11-06-queen-studio-v1-kararlar.md#sapmalar).

**7. The UI ships pre-built.**
Its `dist` is committed with the source it was built from: the notebook clones and never builds
(root [CLAUDE.md](../CLAUDE.md#commands)).

**8. Nothing is shared with the other tools.**
No code comes from queen-editor, queen-agent or collab-toolbox, and none goes to them. From
queen-editor come its behaviour, its rules and its data — the model list, the ComfyUI graphs, the
warning image — copied in as our own files. Why: the tools evolve and break apart, and queen-editor
stays as it is until this tool proves itself and takes its place
([step 13, Kod](../docs/research/2026-11-03-yeni-editor-v1-13-yapim-plani.md#kod)).

**9. The name is written once.**
`queen-studio` is a working name: if the tool proves itself it becomes `queen-editor`. So the app's
name is written in one place in the code, and renaming it is one edit (step 13).
