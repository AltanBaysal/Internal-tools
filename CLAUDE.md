# CLAUDE.md

Internal tools monorepo, one folder per tool: **collab-toolbox** (Colab notebooks), **queen-editor**
(web UI) and **queenagent** (web UI). Adding a tool means a new subfolder and a section here.

## Working rules

- **Don't run shell/terminal commands unless you must.** Read, Grep, Glob, Edit, Write and
  NotebookEdit do the exploring and the editing. When a command really is needed, say in one
  sentence what no tool could have done, then run it.
- **Don't spawn subagents or run workflows unless asked for them.** An interrupted run returns
  nothing at all — the output is lost whole, not partially — so the cost buys zero.
- **Language splits by reader.** Turkish is what a human sees: notebook markdown cells, everything
  printed at runtime (`print` / `log` / `assert` / `RuntimeError`), queen-editor's UI, and the specs
  and plans under `docs/`. English is what a developer reads: code, comments, docstrings, commit
  messages, these repo docs — and QueenAgent's UI, which is English on purpose.
- **A comment says WHY, and only what is true now.** e.g. `MAX_CHUNK_DURATION = 10  # model trained
  on 8s — large drift hurts quality`. `# OLD:` / `# NEW:` traces and claims about past behaviour are
  banned; on a conflict the comment is fixed to match the code, never the reverse.
- **Never invent a cause in an error message.** Print what the command or the service actually said
  — HTTP code and response body, `stderr` tail. A Civitai 401 is not "cookie expired"; a wrong
  selector returns 401 too.

## collab-toolbox — Colab notebooks

Self-contained notebooks that generate and clean up media. Google Drive (`MyDrive/...`) is the only
channel between them; most bring ComfyUI up in the background as an API and batch-process files.

Which notebook does what, the hardware each needs and how to run one:
[collab-toolbox/README.md](collab-toolbox/README.md). The patterns every notebook follows:
[collab-toolbox/NOTEBOOK-STANDARD.md](collab-toolbox/NOTEBOOK-STANDARD.md).

## queen-editor — Queen Editor (web UI)

A web UI over the same ComfyUI photo pipeline as `nova-3dcg`, running on Colab. Engineering
principles: [FOUNDATION.md](queen-editor/FOUNDATION.md). Layering rules, and the boundary that keeps
this tool from depending on anything under `collab-toolbox/` at runtime:
[CODE-STANDARD.md](queen-editor/CODE-STANDARD.md). Work is written down as roadmaps under
[docs/superpowers/plans/](docs/superpowers/plans/), one per run — the highest `vN` is the current
one, and whatever is still waiting stands at its foot.

**Build before commit.** `frontend/dist/` is committed and Colab serves it as-is; it never runs a
build. After any change under `queen-editor/frontend/src/`, run
`npm run build --prefix queen-editor/frontend` and commit the regenerated `dist/` in the SAME commit,
or Colab serves a stale UI.

**The notebook installs, the app reports.** `app.ipynb` installs the producers ticked in its CONFIG,
all before the server starts. The app downloads nothing; its Üreticiler panel reads the disk and says
what is here.

## queenagent — QueenAgent (web UI)

A small AI workspace: a **project** holds two sibling collections, **chats** and **files**. Chats
produce files; a file belongs to the project, never to a chat, and the user reads files rather than
uploading them. xAI Grok drives an agent loop with five tools (`list_files`, `read_file`,
`create_file`, `edit_file`, `build_prompts`) and decides whether a reply becomes a file. Principles:
[FOUNDATION.md](queenagent/FOUNDATION.md); layering:
[CODE-STANDARD.md](queenagent/CODE-STANDARD.md); what is being built now:
[the v2 roadmap](docs/superpowers/plans/2026-08-15-queenagent-v2-roadmap.md), grounded in
[the design v2 diff](docs/superpowers/research/2026-08-14-mira-tasarim-farklari.md) and
[the decisions it produced](docs/superpowers/research/2026-08-14-mira-tasarim-kararlari.md).

**It is the front end of one production line, not a general workspace.** A chat can be handed one of
six **skills** — Create scenario · Create character prompt · Split into shots · Generate prompts ·
Generate prompts+ · Verify shots — and together they run scenario → shot list → structure JSON →
`PROMPTS` list for the SDXL pipeline. A skill is an instruction text
(`domain/skills.py`), placed into the conversation once, in front of the turn it governs. The
intermediate steps live in the chat where the user approves them; only what is approved reaches
disk. And the rule the whole set turns on: **the model writes the text, code does the joining** —
`build_prompts` resolves the names and assembles every shot itself. Why each of these is so:
[the skills design decisions](docs/superpowers/research/2026-08-18-queenagent-beceriler-tasarim-kararlari.md).

**It was called Mira until v2.** The v1 documents keep that name and stay as they are — they record
what was true then: [the v1 roadmap](docs/superpowers/plans/2026-08-09-mira-v1-roadmap.md) and
[the v1 design](docs/superpowers/specs/2026-08-09-mira-v1-design.md).

**Two things differ from queen-editor — do not carry that tool's habits over.** QueenAgent's UI text
is English, because its design was written in English and translating it would stop the design from
being the source. And `dist/` is not committed: QueenAgent runs locally,
`python queenagent/main.py` on port 8100, so whoever runs it also builds it.
