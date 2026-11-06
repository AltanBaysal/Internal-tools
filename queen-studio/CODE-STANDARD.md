# Queen Studio — Code Standard

How the code is laid out and the rules it is written by, decided in
[step 11](../docs/research/2026-11-03-yeni-editor-v1-11-kod-standardi.md). From now on this file is
the rule: a deviation changes it as well as the step. The principles and decisions it serves:
[FOUNDATION.md](FOUNDATION.md).

The folders: `core/` is the core, a folder per group (`core/api/`) and per gate (`core/disk/`);
`main.py` is the start file; `tests/` mirrors `core/`; `ui/` is the UI, its `dist/` committed. The
app's name and version are in `core/about.py` alone. From the repo's root — everything installs inside
the repo, nothing globally:

```bash
queen-studio/.venv/Scripts/python -m pip install --no-cache-dir -r queen-studio/requirements-dev.txt
npm ci --prefix queen-studio/ui --cache tmp/npm-cache
queen-studio/.venv/Scripts/python queen-studio/main.py        # the core and its UI, http://127.0.0.1:8200
queen-studio/.venv/Scripts/python -m pytest queen-studio -q   # the core's suite, ruff and pyright included
npm test --prefix queen-studio/ui                             # tsc, eslint and Vitest
npm run build --prefix queen-studio/ui
queen-studio/.venv/Scripts/python queen-studio/write_openapi.py   # after a core change the UI must follow
```

## Layout

- **The core is grouped as its API is:** `projects`, `frames` (media included), `edits`, `jobs`,
  `queue`, `exports`, `history`, `models`; discovery and health in a small `api` group. Why: whoever
  looks for an endpoint opens the folder of the same name.
- **A group holds three things:** its rules, which know nothing outside them; its record, how it is
  written to the store; its endpoints. Why: the rules test with no store and no HTTP, and each of the
  three changes for its own reason.
- **Gates stand apart:** `storage` (the port, with its Drive and in-memory adapters), `comfy`, `ffmpeg`,
  `downloads` (from Hugging Face and Civitai; their rules are the `models` group's), the clock, the
  Colab disk and the graphics card. A gate looks at no group and at no other gate, but for the type
  of one it is handed: storage takes a `Clock` to wait on, never builds one. Why: everything
  outside the process is behind a gate, so a test puts a fake in its place; a gate handed another
  is faked as easily.
- **Groups may call each other, never in a cycle.** Deleting a frame, `frames` asks `jobs`; were
  `jobs` to ask `frames` too, that is a cycle, and forbidden.
- **`core/`'s root holds the app's assembly and what every group shares:** the name and version
  (`about.py`), the HTTP app (`server.py`), the log (`log.py`). A group's rule never goes there. Why:
  each group's rules stay in its own folder, and the root stays small enough to read whole. A shared
  piece that needs more than one file has its own folder there: `core/lists/`, the query every list
  takes.
- The real gates are wired in one start file.
- The UI is laid out by the same groups.
- Each file has one job.

## Language

Code, comments, API descriptions, error messages and the UI are English; the specs, plans and every
document under `docs/` are Turkish. The UI is English by the user's decision, as queen-agent's is
([step 9](../docs/research/2026-11-03-yeni-editor-v1-9-ui.md#ne-yapar)), so queen-editor's Turkish UI
does not carry over.

## Messages

- Endpoints and fields are described as if to the agent: the descriptions are what it learns the API
  from.
- An error says what is missing or wrong, and why — "`prompt` is missing. `t2i` cannot make a photo
  without one; describe the scene."
- A service's error — Drive's, ComfyUI's, ffmpeg's — reaches the caller in the service's own words.
- Every error comes back in one shape of four fields, `code`, `message`, `details` and `hint`, the
  adapter's and FastAPI's own validation errors included. The errors themselves are in
  [step 6](../docs/research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md#hatalar).
- `hint` says only what the core knows for certain. For an error from the core's own rule it says
  what to do ("removing the job from the queue is enough"). For a service's error it guesses no cause
  and gives no order, only the state and the option at hand ("the queue stopped on this error; once
  the cause is fixed, `resume` continues it"). With nothing certain to say, it stays empty.

## Cost

- Each endpoint's cost is in its spec: how many store requests it makes and how many files it reads,
  matched by a test, with exact equality, against
  [step 4's table](../docs/research/2026-11-03-yeni-editor-v1-4-depo.md#maliyet-işlem-işlem).
- No request reads every project or every frame without need; an operation that grows with a list
  says why.
- Idle — no request, no job, no new log line — the core calls Drive not at all.
- Every cost an input can drive is bounded before it is spent. Input is whatever comes from outside
  the process: the caller, Drive's files, ComfyUI's and the model hosts' answers, the media. Each
  text, list and count has a maximum in its model; each outbound call, subprocess and download a
  timeout; each answer a byte budget; each disk write a free-space check first. Past a bound the core
  refuses with the four-field error before doing the work, and never truncates silently. No input
  reaches an engine that runs it as a program — regex, eval, a shell, a template: compiling one
  pattern from a query filled this machine's 16 GB (530). A spec names each bound, and a test reaches
  it with the bound set small.

## UI

- Its types are generated from the core's `/api/openapi.json`, never written by hand, and `tsc`
  checks against them ([FOUNDATION 2](FOUNDATION.md#decisions)).
- A screen's sample data stays behind one seam, which wiring the screen to the core replaces without
  touching its look. How often a wired screen polls and how many requests it makes are counted in its
  spec and tested: the UI's refresh is the largest share of the Drive quota
  ([step 4](../docs/research/2026-11-03-yeni-editor-v1-4-depo.md#9-kota-hız-sınırı-ve-depolama)).

## Checks

Python: `ruff` and `pyright` in strict mode. UI: TypeScript's strict mode and `eslint`. They run with
the tests, and a change is not finished while one of them reports an error.

## Tests

Every change of behaviour starts with a failing test, in every part — core, storage adapters, MCP
adapter, UI, notebook and launcher code. No test waits a real second: the clock is a gate. A race is
set up with hooks in the fakes, never with a time window, so every run gives the same result — in
queen-editor, QA rather than tests found most races (512, 513, 522, 523). There is no known red test.
The layers, what each fakes and what is tested hardest:
[step 12](../docs/research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md).
