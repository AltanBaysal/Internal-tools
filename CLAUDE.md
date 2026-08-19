# CLAUDE.md

Internal tools monorepo, one folder per tool: `collab-toolbox`, `queen-editor`, `queenagent`.

## Commands

```bash
# QueenAgent — the whole suite, always this one line
python -m pytest queenagent -q; npm test --prefix queenagent/frontend

# QueenAgent — run it (dist is NOT committed, so build first)
npm run build --prefix queenagent/frontend
python queenagent/main.py            # http://127.0.0.1:8100 — restart it after a backend change

# queen-editor — dist IS committed; build and commit it in the SAME commit as the source
npm run build --prefix queen-editor/frontend
```

Skipping that last build makes Colab serve a stale UI — it clones the repo and never builds.
Verifying a queen-editor change also needs a push, for the same reason.

## Workflow

**IMPORTANT — approval starts a task, nothing else does.** Once given, run to the end. Stop only for
a decision with two readings or no way back, and ask it in plain text: one question, numbered
options, a recommendation.

**YOU MUST split every task into two cycles**, down to a two-line deletion: the tests alone first,
committed red (`skip`/`xfail` are not how a suite is made green), then the implementation. Written
together, a test inherits the code's blind spots.

The user tests at the end of a run, not between items.

Roadmaps live in [docs/superpowers/plans/](docs/superpowers/plans/), one file per run, highest `vN`
current. One problem, one item, ordered so nothing is built before what it stands on, each saying
what will work and how it will be seen. Numbering never shifts: written specs cite it. A spec
derives from its source document, never the reverse.

## Gotchas

- **Commit messages carry no double quotes** — they break the PowerShell here-string and git reads
  the pieces as pathspecs. **Never amend**: another session may share the branch.
- Reach for Read, Grep, Glob, Edit, Write — not the shell, and never a file through `python -c` or a
  heredoc. No subagents or workflows unless asked for.

## Style

- **A comment says WHY, and only what is true now.** `# OLD:` / `# NEW:` traces are banned; on a
  conflict the comment is fixed to match the code.
- **Never invent a cause in an error message.** Print what the command or the service actually said;
  a Civitai 401 is not "cookie expired".
- **A doc says what the code cannot.** Why a thing is so, a rule that binds code not yet written,
  what happens outside the repo. It never restates what the code already states — it names the file
  instead, because a copy is what goes stale.
- **Language splits by reader.** Turkish is what a human sees: notebook markdown cells, runtime
  output, queen-editor's UI, everything under `docs/`. English is what a developer reads: code,
  comments, commit messages — and QueenAgent's UI, which is English on purpose.

## Where the rest lives

Each tool carries its own README and its own rules (`FOUNDATION.md`, `CODE-STANDARD.md`,
`NOTEBOOK-STANDARD.md`). They bind, the code does not repeat them, and this file does not either —
read them before touching that tool.
