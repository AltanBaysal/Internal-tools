# CLAUDE.md

Internal tools monorepo, one folder per tool: `collab-toolbox`, `queen-editor`, `queen-agent`.

## Commands

```bash
# Tests — per tool, always these fixed lines, both of them, verbatim.
# Independent — run them in parallel; each one's red fails its own call, nothing is masked.
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend

# Both tools ship their built frontend: each one's notebook clones this repo and never builds. So
# build and commit dist in the SAME commit as the source — a frontend change is not finished
# otherwise — and on the notebook side nothing is seeable until it is pushed.
npm run build --prefix queen-agent/frontend
npm run build --prefix queen-editor/frontend
```

How a tool is installed and run is its own README's, not this file's.

## Workflow

**IMPORTANT — approval starts a task, nothing else does.** Once given, run to the end. Stop only for
a decision with two readings or no way back, and ask it in plain text: one question, numbered
options, a recommendation.

**An item ending is not a stop.** With nothing to ask, the next item starts in the same breath —
finishing one and waiting for permission to begin the next is the stop this rule forbids. One
approval carries the whole run.

**YOU MUST run every task as two full superpowers tours**, down to a two-line deletion:

1. **Test tour** — spec, plan, then implement *the tests only*. Run the suite, see them fail,
   commit them red (`skip`/`xfail` are not how a suite is made green).
2. **Implementation tour** — a second spec and plan, now for the code itself. Implement what the
   committed tests describe, see the suite go green, commit.

Never write test and code in one pass: written together, a test inherits the code's blind spots.

The user tests at the end of a run, not between items.

Roadmaps live in [docs/superpowers/plans/](docs/superpowers/plans/), one file per run, highest `vN`
current. One problem, one item, ordered so nothing is built before what it stands on, each saying
what will work and how it will be seen. Numbering never shifts: written specs cite it. A spec
derives from its source document, never the reverse — and that source lives in
[docs/superpowers/research/](docs/superpowers/research/): the decision ledgers, briefs, problem
lists and investigations a run is written from. Nothing else sits under `docs/`.

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
