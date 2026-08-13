# CLAUDE.md

Internal tools monorepo, one folder per tool: **collab-toolbox** (Colab notebooks), **queen-editor**
(web UI) and **mira** (web UI). Adding a tool means a new subfolder and a section here.

## Working rules

- **Don't run shell/terminal commands unless you must.** Read, Grep, Glob, Edit, Write and
  NotebookEdit do the exploring and the editing. When a command really is needed, say in one
  sentence what no tool could have done, then run it.
- **Don't spawn subagents or run workflows unless asked for them.** An interrupted run returns
  nothing at all — the output is lost whole, not partially — so the cost buys zero.
- **Language splits by reader.** Turkish is what a human sees: notebook markdown cells, everything
  printed at runtime (`print` / `log` / `assert` / `RuntimeError`), queen-editor's UI, and the specs
  and plans under `docs/`. English is what a developer reads: code, comments, docstrings, commit
  messages, these repo docs — and Mira's UI, which is English on purpose.
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

## mira — Mira (web UI)

A small AI workspace: a **project** holds two sibling collections, **chats** and **files**. Chats
produce files; a file belongs to the project, never to a chat, and the user reads files rather than
uploading them. xAI Grok drives an agent loop with three tools (`list_files`, `read_file`,
`create_file`) and decides whether a reply becomes a file. Principles:
[FOUNDATION.md](mira/FOUNDATION.md); layering: [CODE-STANDARD.md](mira/CODE-STANDARD.md); build
order: [the v1 roadmap](docs/superpowers/plans/2026-08-09-mira-v1-roadmap.md), grounded in
[the design](docs/superpowers/specs/2026-08-09-mira-v1-design.md).

**Two things differ from queen-editor — do not carry that tool's habits over.** Mira's UI text is
English, because its design was written in English and translating it would stop the design from
being the source. And `dist/` is not committed: Mira runs locally, `python mira/main.py` on port
8100, so whoever runs it also builds it.
