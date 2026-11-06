# CLAUDE.md

Four tools, a folder each: `collab-toolbox` (Colab notebooks), `queen-editor`, `queen-agent` and
`queen-studio` (web apps). Their rules sit beside them and say why the code is shaped as it is:
`FOUNDATION.md` and `CODE-STANDARD.md` in the three apps, `NOTEBOOK-STANDARD.md` in collab-toolbox.

## Commands

```bash
# One suite at a time, whoever runs it: side by side they nearly fill this machine's 16 GB.
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
# queen-studio's Python lives in its own .venv, nothing installed globally; ruff and pyright run in
# its suite, tsc and eslint in its UI's.
queen-studio/.venv/Scripts/python -m pytest queen-studio -q
npm test --prefix queen-studio/ui

# The notebooks clone this repo and do not build, so a frontend change is committed together with its
# rebuilt dist, and reaches a notebook once it is pushed.
npm run build --prefix queen-agent/frontend
npm run build --prefix queen-editor/frontend
npm run build --prefix queen-studio/ui
```

The suites an item runs are its tool's: queen-editor's and queen-agent's four for an item of either;
queen-studio's alone for a queen-studio item, since it shares no code with the others. Every tool's
suites run once before a queen-studio run merges into `main`.

Tests cover code. Documents are for people, and a test that reads a `.md` file breaks each time one is
reworded, so none does (item 431). The exception is the `.md` files in
`queen-agent/backend/features/workspace/skills/`: they are the model's input, read by the code, and tests
read them as they read any constant (item 495).

## Roadmaps

Work goes through a roadmap in `docs/roadmaps/`, one per version of one tool, named and headed like the
ones there. It records what the user asked for and decided, and specs are written from it.

- Items come from the user's words, quoted with the date, or from a tool's `BACKLOG.md`. A new item is
  `UNALIGNED`: what it says is still a guess at what the user meant. Say it back, write the user's
  answer in their words, and it becomes `ALIGNED` — item by item or once the document is written, as
  the user chooses.
- An item says what the user wants and how the result will be seen. How it is built belongs to the
  spec, written once the code has been read.
- Items are numbered `v<N>-1`, `v<N>-2`, … until the run gives them real numbers, from one count shared
  by every roadmap. Specs cite those numbers, so they stay fixed. Work found during a run is added to
  that roadmap with the next number.
- The header's waves say which items run at the same time. Items in one wave touch different places,
  and no two of them the same tool's frontend: each rebuilds the whole `dist`, and two builds collide
  on merge.
- A roadmap's first item raises the version its tool's screen shows to the roadmap's own, so the user
  can tell which run a screen comes from (the user, 27 Ekim — "her roadmapin başında şun uyapmanı
  istiyorum ui daki sürümü arttıralım"; "ilk görev o olsun").
- A finished roadmap moves to `docs/arsiv/roadmaps/` with its specs, plans, research and design-needs,
  by `git mv`, and every link to them is rewritten, so `docs/` holds only open work (the user, 27 Ekim —
  "eklensin"; item 500). The archive repeats `docs/`'s folders, so links between two archived
  documents stay as they are.
- The user's approval starts the run and covers it to the end, and the user tests the roadmap once it
  is finished. So the run goes from item to item, and asks when a question comes up that nothing it
  has can settle: one question, numbered options, a recommendation.

## Subagents

The main agent talks with the user, hands the building to subagents, checks what comes back, and does
the git.

- An item goes to one [coder](.claude/agents/coder.md): one spec and one plan —
  `docs/specs/YYYY-MM-DD-<tool>-m<number>-<topic>-design.md` and `docs/plans/…-plan.md` — and the code,
  test-driven (TDD). A spec says what is built, why, its limits and when it is done; a plan lists the steps
  file by file.
- The coder writes with the reviewer's eye, and every item's change then goes through the
  [reviewer](.claude/agents/reviewer.md), always (the user, 9 Ekim — "her kodlama reviewer'dan
  geçer her zaman"; "coder direkt yazsın dikkat ederek, sonra review kontrol etsin sadece"), as a
  senior developer: each thing in its own place, no part it does not need, what each operation
  costs, what can be lost or broken. The two cost lenses are there because 446 found every Archive
  press reading all projects three times, a cost no review had looked for. When the structure
  itself is in question, the main agent first asks the reviewer for a design, argues it, and takes
  it to the user before any code. A coder shapes new code itself, but asks before it restructures
  code already written; a fault it finds in passing is reported, not rewritten.
- A [qa](.claude/agents/qa.md) agent then checks the items that change the screen or what the tool
  does, as a tester: against the item and its spec, the item's suites, and the screen with
  Playwright. It comes once the reviewer's findings are fixed, so it tests the code that is
  committed. A change of tests, comments or documents alone goes without it.
- A design item — a tool's screens, designed in this repo — goes to the
  [designer](.claude/agents/designer.md) in place of the coder, and the
  [design reviewer](.claude/agents/design-reviewer.md) looks at the experience before the reviewer
  reads the code, as on any item. A designed screen is wired to the core by a later item, a coder's,
  and its look stays (the user, 6 Kasım). So a code item goes coder → reviewer → QA where it applies
  → main agent, and a design item designer → design reviewer → reviewer → QA → main agent.
- They report and the agent that built the item fixes it. The main agent reads their reports and the
  diff, checks the spec against the item, and runs the item's suites itself. What falls short goes
  back to that same agent, which still holds the context; what passes, the main agent commits.
- A coder or the designer can ask the main agent at any time and wait for the answer. The main agent
  answers from what it has — the roadmap, the code, the rules, the conversation — and asks the user
  whenever it cannot answer itself.
- An agent working alone works in the main folder, on the run's branch. A worktree is opened only
  while two or more agents build at the same time, because each worktree's installs and suites weigh
  on this machine (the user, 10 Ekim — "aynı anda tek agent çalışıyorsa worktree oluşturma, bilgisayarı
  kırıyordu").
- Then each works in a worktree at `.claude/worktrees/m<number>` on the branch
  `<run branch>-m<number>`, opened from the run's branch: the Agent tool's own worktree isolation opens
  from `main`, which lacks the run's work.
- The main agent merges finished items from their worktrees into the run's branch one at a time, with
  the item's suites after each merge, so a break points at one item, and removes each worktree once its
  item is merged. Branches such as the run's stay, for the history.

## Browser

Playwright MCP (`.mcp.json`) is the main agent's and QA's — on a design item the designer's and the
design reviewer's too — for seeing a running tool the way the user does. It opens the tools on this
machine; any other address is the user's call, since the allow-list flag misses redirects and is no
security boundary.

It has one browser, and everyone who calls it shares that browser's tabs: one agent's navigation moves
the page under another's (tried on 9 Ekim). So one agent uses it at a time — no main-agent look while
QA has the screen, and no two QA agents trying a screen at once.

## Designs

queen-editor's and queen-agent's screens are designed in `D:\Github\queen-design`
(`AltanBaysal/queen-design`), a folder per tool under `projects/`. Its `main` is what the tools already
build; each round arrives on a branch the user names, per tool. Fetch, diff that branch against `main`,
and each difference becomes a roadmap item.

queen-studio's are not drawn there: the [designer](.claude/agents/designer.md) builds them in this
repo, in the tool's own UI code (the user, 6 Kasım — "queen-design reposunda çizmesin, kendimiz
yapalım").

## Tools

Where a dedicated tool does the job (Read, Edit, Write, Grep, Glob), it is used rather than the shell:
the user follows the work through those calls, and a file edited by a script or `sed` is harder to
check. The shell is for what has no tool: git, the suites, builds, processes.

## Git and memory

- Commit messages go through a PowerShell here-string, which a double quote breaks, so they carry none.
- Another session may share the branch, so commits are not amended.
- The user cannot see Claude's memory, so nothing is written there; what should last goes in a file
  they can read.

## Style

- Of the solutions that work, the simplest: every extra part is paid for on every later edit.
- A comment says why, and what is true now; the history is in git.
- An error message prints what the command or the service actually said, not a guessed cause.
- Turkish for what a person reads: notebook markdown and output, queen-editor's UI, everything under
  `docs/`. English for code, comments, commits and the rule files — and QueenAgent's and queen-studio's
  UI, on purpose (their `CODE-STANDARD.md` says why).
