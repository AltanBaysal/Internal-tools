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

## Working a roadmap

Work arrives from the user in pieces, across days and sessions that do not remember each other. The
roadmap is that memory: what is being built, what was decided and why, and where it stands. Specs
derive from it, never the reverse.

A roadmap is one version of one tool, and a version is a branch. The user is not there between
items, so the roadmap runs as a loop:

1. **A branch is opened, and one roadmap is written for it.** It goes in
   [docs/superpowers/roadmaps/](docs/superpowers/roadmaps/), apart from the per-item plans in
   `plans/`, as `YYYY-MM-DD-<tool>-v<N>-roadmap.md`: the day it opened, the tool's own folder name,
   that tool's version. Its header names the branch and shows progress as *Durum: N/M*.
2. **Items are written.** One problem, one item, each saying what will work and how it will be
   seen.
3. **Items are ordered by what depends on what**: nothing is built before what it stands on. The
   user may reorder them, and the order they give is the order worked.
4. **IMPORTANT — approval is given, and the roadmap runs.** Nothing else starts it. Once given, it
   runs to the end: one approval carries the whole roadmap.
5. **YOU MUST work each item as two full superpowers tours**, down to a two-line deletion. Every
   spec starts from the tool's `FOUNDATION.md` and `CODE-STANDARD.md`:
   - **Test tour:** spec, plan, then the tests only. The suite is run, seen failing, and committed
     red (`skip`/`xfail` are not how a suite is made green).
   - **Implementation tour:** a second spec and plan, for the code itself. What the committed tests
     describe is implemented, the suite is seen green, and it is committed.

   Test and code are never written in one pass: written together, a test inherits the code's blind
   spots.
6. **What an item needs from the user is written at the top of its spec**, and asked for there — not
   discovered halfway, where it leaves an item that cannot be marked.
7. **The user is stopped for only a decision with two readings or no way back**, asked in plain
   text: one question, numbered options, a recommendation.
8. **Work that turns up mid-roadmap is added as an item** to the roadmap already running, never a
   second document. Numbers never shift: written specs cite them.
9. **A finished item is marked, and the next one starts in the same breath.** Finishing one and
   waiting for permission to begin the next is the stop this loop forbids.
10. **The user tests at the end of the roadmap**, not between items.

**Versions.** A version belongs to one tool's counter, which starts at v1. A roadmap that reaches
into the other tool says which items did so in its own header and claims no counter of its own.
Work done with no branch of its own is the first section of the roadmap whose branch came next.

**Why the name matters.** Listing the roadmaps folder is how you see which version a tool is on, so
the name is the record, and it only stays one while every roadmap's name matches the branch in its
own header: those parted company here, unnoticed for eight roadmaps, until thirteen documents sat on
four branches.

## Gotchas

- **Commit messages carry no double quotes** — they break the PowerShell here-string and git reads
  the pieces as pathspecs. **Never amend**: another session may share the branch.
- Reach for Read, Grep, Glob, Edit, Write — not the shell, and never a file through `python -c` or a
  heredoc. No subagents or workflows unless asked for.

## Style

- **Of the solutions that work, the simplest is chosen.** AI overengineers by default: a layer
  nobody needed, an option nobody asked for, a guard against a case that does not happen. Each one
  is paid for on every later edit. When in doubt, fewer parts.
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
`NOTEBOOK-STANDARD.md`). They bind, the code does not repeat them, and this file does not either.

**YOU MUST read the tool's `FOUNDATION.md` and `CODE-STANDARD.md` before its spec is written.**
FOUNDATION says which value wins when two collide — correctness, then simplicity, then generality,
then performance — and why code is kept simple enough to be rewritten from its spec. CODE-STANDARD
says where code goes and what may import what.
