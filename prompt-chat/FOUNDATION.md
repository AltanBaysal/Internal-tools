# prompt-chat — Foundation

Engineering principles and architecture decisions, independent of any product shape.
Principles say which value wins when two collide while writing code; decisions record the
stack choices. Product decisions — screens, flows, behaviour — never enter this file; they
live in the specs under `docs/superpowers/specs/`.

## Principles

Ordered: when two principles collide, the one higher on this list wins.

**1. The user's work is sacred.**
Nothing a person typed disappears without them asking. A half-written draft belongs to its chat and
survives a closed tab; deleting a chat asks first, because it may hold an instruction someone spent
an hour on and there is no undo. No destructive action happens on a single click.

**2. Truth lives in the browser's store.**
Process memory is as disposable as the tab it runs in. Any state that matters — the chats, which
one is open, each chat's draft, the key and the model — is written to `localStorage`, and the app
rebuilds itself from there on the next load. A stored value that cannot be read must not stop the
app: it falls back to the empty state.

**3. Correctness > simplicity > generality > performance.**
YAGNI is ruthless: no abstraction before a proven need, no optimization before a measured
problem, no feature before a real user ask.

**4. Code is optimized for regenerability — it is written and maintained with AI.**
AI inverts the human cost curve: volume is cheap, complexity is expensive. It writes large
amounts of simple code fast and correctly, and it breaks dense code on every later edit.
So every unit stays simple and bounded enough to be rewritten from its spec alone. A file too
big to hold comfortably in context is doing too much — split it.

Principles 3 and 4 are shared verbatim with [Queen Editor](../queen-editor/FOUNDATION.md): they are
the repo's engineering stance, and there is no reason for two tools here to hold different ones.

## Decisions

**1. Everyone runs their own copy; git is the delivery channel.**
`npm install` once, `npm run dev` whenever it is needed. There is no shared instance, no server to
keep alive, and nothing deployed. Why: the app is a static page talking to a public API — hosting it
would add an operational burden that buys nothing. Consequence: **chats are private to one person
and one browser.** Nobody sees anyone else's work, and nobody can hand a chat to a colleague; what
travels between people is the prompt text, copied out.

**2. There is no backend.**
The browser calls `api.x.ai` directly. Why: xAI allows cross-origin requests (verified by preflight
on 2026-08-08 — `access-control-allow-origin: *`), so a proxy would solve no problem and add a
second thing to run. Consequence: the API key lives in the browser, which decision 5 covers.

**3. React 18 + Vite + Vitest, at Queen Editor's exact versions.**
Why: one toolkit across the repo — the same commands, the same test idiom, nothing extra to learn
when moving between the two. Folding this tool into Queen Editor one day is an open option and this
makes that a copy rather than a rewrite, but that is a side benefit, not the reason.

**4. `localStorage` is the only persistent store.**
No server, no backup, no sync, no export. Why: a single-user page has nothing to synchronise, and a
store the app cannot reach without a network is a store that fails when the network does.
Consequence, stated plainly wherever a user can read it: **clearing browser data loses the chats.**

**5. The API key is typed on the page — never in the source, never in `.env`.**
Why: a key committed into the source stays in git history and has to be revoked. `.env` is not an
answer either — Vite inlines every `VITE_`-prefixed variable into the build, so it would hide
nothing while looking like it did. Consequence: each person enters their own key, which is also how
usage stays attributable per person.

**6. Error text is passed through verbatim.**
The HTTP status and the response body are shown as they arrived. Why: the same status has several
causes — a 401 is equally a bad key and a bad model id — so naming one would send the reader down
the wrong path. This holds for network failures too: the browser's own message is printed.

**7. No runtime dependency on anything else in this repo.**
No imported file, no shared folder, no shared storage key. Only design tokens are inherited from
Queen Editor, as values copied into our own stylesheet. Why: the tools must be able to evolve and
break independently. Merging the two is an open option, **not a plan** — until someone decides
otherwise, neither may reach into the other. The rule in full:
[CODE-STANDARD.md](CODE-STANDARD.md).

**8. `dist/` is not committed.**
Why: Queen Editor commits its build because Colab never runs npm and must serve the files as found.
This tool is run from source by the person using it, so the built output is a local artifact.
