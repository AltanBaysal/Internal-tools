# CLAUDE.md

Internal tools monorepo, one folder per tool: `collab-toolbox`, `queen-editor`, `queen-agent`.

Work here goes through a roadmap: one document for one version of one tool, holding what is being
built, what was decided and why, and how far the work has got. Specs are written from the roadmap,
never the other way round. There are two jobs here, with different rules for each:
**writing a roadmap** ([*Writing a roadmap*](#writing-a-roadmap)) and
**running a roadmap** ([*Running a roadmap*](#running-a-roadmap)).

## Commands

```bash
# Tests — two per tool, always these four lines, exactly as written: never piped, never filtered,
# never narrowed to one test or one file. A changed line is a new command, and a new command waits
# for an approval the user is not there to give.
# Independent — run the four in parallel; nothing is masked.
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend

# Each tool's notebook clones this repo and never builds, so the built frontend ships from here.
# Build and commit dist in the SAME commit as the source — a frontend change is not finished
# otherwise — and nothing is visible in the notebook until the commit is pushed.
npm run build --prefix queen-agent/frontend
npm run build --prefix queen-editor/frontend
```

## Writing a roadmap

**Four rules hold whenever a roadmap is written or added to:**

- **Each tool counts versions alone, starting at v1.** A roadmap that touches both tools is still
  one version of one tool — the tool the roadmap belongs to — and the header lists which items
  touched the other tool.
- **A branch is only a name while a roadmap is being written.**
  [Running the roadmap](#running-a-roadmap) opens the branch.
- **Before a roadmap runs, the items are numbered inside the document**: `v<N>-1`, `v<N>-2`, and on
  — the roadmap's version, then a count that starts at 1. The `v<N>-` prefix keeps a document number
  from looking like a real one. The items take their real numbers when
  [the roadmap starts running](#running-a-roadmap).
- **Work that turns up mid-roadmap is added as an item** to the roadmap already running, never a
  second document. The item goes at the end unless the user places the item somewhere else, and
  takes the next real number straight away — the run is open, so the count is readable.

**A roadmap is written in this order:**

1. **Create the document** in [docs/superpowers/roadmaps/](docs/superpowers/roadmaps/), named in
   this format: `YYYY-MM-DD-<tool>-v<N>-roadmap.md`
   - `YYYY-MM-DD` is the day the document is written.
   - `<tool>` is the name of the tool's folder at the root of this repo.
   - `v<N>` is the version being written — one past the highest `v<N>` that tool already has in the
     roadmaps folder.
   - `-roadmap.md` is literal, and ends every name.
2. **Copy the header shape from a roadmap already in the roadmaps folder.** Read an existing header
   before writing a new header. A header gives four things:
   - **The date** the roadmap was written.
   - **The branch** the run will open.
   - **`Durum: N/M`** — how many items are finished, out of how many.
   - **The version before**, with a link to the document and how the version ended.
3. **Write each item from what the user said, and add nothing of your own.** One problem, one item.
   A long answer makes a long item and a short answer makes a short item — the length comes from the
   user, not from you. **Mark the new item `UNALIGNED`**: anything added while the mark is on the
   item reads as a decision the user never made.
4. **Write on the item where the item came from**: the user's own words with the date, or the
   backlog entry the item came out of.
5. **Align each item with the user, and leave no item marked `UNALIGNED`**:
   [*Aligning an item*](#aligning-an-item). **Once the mark reads `ALIGNED`, write the item out in
   full** — what the user wants, and how the work will be seen once the work is done. Leave out how
   the work will be built: the run writes a spec for that, and a technical answer written before the
   code has been read is a guess.
6. **Point out the items that look too big, and ask the user whether to split.** Name the items you
   mean, and let the user decide. **Smaller is better** — the smaller an item is, the better the
   work on the item comes out — and every piece still has to be something that can be built and
   tested alone. The one thing that holds a split back is work that is easier done together.
7. **Order the items by what depends on what**: nothing is built before what the work stands on. The
   user may reorder the items, and the order the user gives is the order worked.

## Running a roadmap

**Five rules hold for the whole run:**

- **IMPORTANT — nothing but approval starts a run**, and one approval carries the whole roadmap to
  the end. The user is not there between items.
- **YOU MUST invoke the superpowers skills named in the steps, not imitate the shape.**
- **YOU MUST read the tool's `FOUNDATION.md` and `CODE-STANDARD.md` before writing a spec for the
  tool**, and every spec has to obey both.
- **A suite goes green by the code, never by the tests being silenced** — `skip` and `xfail` in
  pytest, `.skip` and `.todo` in the frontend suites.
- **The run stops to ask the user only when a decision can honestly be read two ways, or when a
  decision cannot be undone.** Ask in plain text: one question, numbered options, a recommendation.

**A run goes in this order:**

1. **Open the branch and write the branch into the header**, so the header names the branch that
   exists.
2. **Give the items their real numbers.** The numbers come from one count shared by the whole repo,
   and once taken a number never changes, because written specs refer to items by number.
3. **Work the items one at a time, in the roadmap's order**, going straight from a finished item to
   the next without asking. The approval given at the start covers every item. For each item:
4. **Read the item's mark.**
   - **`ALIGNED`** — go on.
   - **`UNALIGNED`** — stop and ask the user to align the item
     ([*Aligning an item*](#aligning-an-item)), then go on. Unaligned, the meaning of the item is
     still your guess, and a wrong guess is expensive.
5. **Test tour:**
   1. Write the test spec — `superpowers:brainstorming`. **Anything the item needs from the user —
      a decision, a file, a measurement — goes at the top of the test spec, and is asked before the
      work starts.** Finding out halfway leaves the item half-built and unfinishable: the item
      cannot be marked done, and the run stalls there.
   2. Write the test plan — `superpowers:writing-plans`.
   3. Write the tests, and nothing else.
   4. Run the suite — the four lines under [*Commands*](#commands), exactly as written — and watch
      the new tests fail.
   5. Commit the suite red.
6. **Implementation tour:**
   1. Write the implementation spec — `superpowers:brainstorming`.
   2. Write the implementation plan — `superpowers:writing-plans`.
   3. Write the code the implementation plan lays out — what the committed tests describe, and no
      more.
   4. Run the suite — the four lines under [*Commands*](#commands), exactly as written — and watch
      the suite go green.
   5. Commit the code.
7. **Mark the item finished**, and move the header's *Durum: N/M* on by one.
8. **When every item is marked, the user tests the roadmap** — at the end, not between items.

## Aligning an item

**YOU MUST align every item with the user**, one item at a time:

- **Say the item back:** in two or three sentences, what you understood the item to be.
- **The user confirms the item or corrects the item:** write what the user said, in the user's own
  words.
- **Ask what is still unclear to you**, and write the answers into the item.

Then the item's mark is changed from `UNALIGNED` to `ALIGNED`. Whether aligning happens as each item
is written, or after the whole document is written, is the user's call.

## Gotchas

- **Commit messages carry no double quotes** — double quotes break the PowerShell here-string, and
  git reads the pieces as pathspecs. **Never amend**: another session may share the branch.
- Reach for Read, Grep, Glob, Edit, Write — not the shell, and never a file through `python -c` or a
  heredoc. No subagents or workflows unless asked for.

## Style

- **Of the solutions that work, the simplest is chosen.** AI overengineers by default: a layer
  nobody needed, an option nobody asked for, a guard against a case that does not happen. Every
  extra part is paid for on every later edit. When in doubt, fewer parts.
- **A comment says WHY, and only what is true now.** `# OLD:` / `# NEW:` traces are banned; on a
  conflict the comment is fixed to match the code.
- **Never invent a cause in an error message.** Print what the command or the service actually said;
  a Civitai 401 is not "cookie expired".
- **A doc says what the code cannot.** Why a thing is so, a rule that binds code not yet written,
  what happens outside the repo. A doc never restates what the code already states — a doc names the
  file instead, because a copy is what goes stale.
- **Language splits by reader.** Turkish is what a human sees: notebook markdown cells, runtime
  output, queen-editor's UI, everything under `docs/`. English is what a developer reads: code,
  comments, commit messages — and QueenAgent's UI, which is English on purpose.

## Where the rest lives

Each tool carries a README and a set of rules (`FOUNDATION.md`, `CODE-STANDARD.md`,
`NOTEBOOK-STANDARD.md`). The rules bind, the code does not repeat the rules, and this file does not
either.

**`FOUNDATION.md`** says which value wins when two collide — correctness, then simplicity, then
generality, then performance — and why code is kept simple enough to be rewritten from a spec.
**`CODE-STANDARD.md`** says where code goes and what may import what.
