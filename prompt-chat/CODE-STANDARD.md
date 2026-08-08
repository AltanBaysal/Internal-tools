# prompt-chat — Code Standard

Three layers, one folder. Read this before adding code.
The principles and stack decisions these rules serve: [FOUNDATION.md](FOUNDATION.md).

## Stack
**React 18 + Vite + Vitest**, pinned to the same versions as
[queen-editor/frontend](../queen-editor/frontend/package.json). There is no backend to choose: the
page talks to xAI directly, and why that is safe and sufficient is decision 2 in
[FOUNDATION.md](FOUNDATION.md).

Matching Queen Editor's versions is deliberate. Two tools in one repo on two React majors, two test
runners or two build tools would mean two sets of habits for the same work, and every upgrade would
be argued twice. When Queen Editor moves, this moves with it.

## Independence
prompt-chat reads no file from any other tool in this repo, writes nothing into one, and shares no
storage. What it inherits is **design tokens only** — the colour, type and radius values in
`src/app.css`, copied as values from
[queen-editor/frontend/src/vendor/styles.css](../queen-editor/frontend/src/vendor/styles.css).

| Inherited (values) | Never (dependency) |
|---|---|
| Palette, radii, the IBM Plex families — copied into our own `app.css` | Importing that stylesheet, or any file under `queen-editor/` |
| The convention of a `test-setup.js` that cleans up after each test | Sharing the file itself |
| — | `vendor/kit.jsx`. It is Queen Editor's component library, built for its screens; copying it would drag in a design system this app has no use for |

Two files may look alike; neither may import the other.

## Layers
The whole app is `src/`. Every file belongs to exactly one layer, and each layer is defined by what
it is **not allowed to know**:

| Layer | Files | Knows nothing about |
|---|---|---|
| **pure** | `chat.js`, `storage.js` | the network, React, `localStorage` |
| **io** | `api.js` — the only `fetch`; `usePersisted.js` — the only `localStorage` access | the rules; it moves data, it does not decide |
| **render** | `App.jsx`, `Sidebar.jsx`, `Message.jsx` | file schemas, HTTP; it shows what it is given |

Dependency direction: `render → io → pure`, and `render → pure` directly for helpers like
`titleOf`. Nothing points back up.

**This split is the reason the tests are cheap.** The pure layer runs with no browser, no network
and no stored state, so the rules that actually matter — which messages go into a request, how an
error reads, what a chat is called — are tested in milliseconds. If a rule is hard to test, it is
usually because it landed in the wrong layer.

Two bans with no exceptions: **no `fetch` outside `api.js`**, and **no `localStorage` outside
`usePersisted.js`**. A second call site for either is how a store quietly grows two sources of
truth.

`Sidebar.jsx` holds one piece of state — whether the settings panel is open. That is a property of
the screen, not of the data, so it does not break the rule above.

## Data shape
Four keys in `localStorage`:

| Key | Content |
|---|---|
| `chats` | `[{ id: number, messages: [{role, content}], draft: string }]` |
| `active_chat` | the open chat's `id` |
| `xai_key` | the API key, as typed |
| `xai_model` | the model name, as typed |

`role` is `"user"`, `"assistant"` or `"error"`. Error rows are kept so the user can see what
happened but are filtered out of every request — xAI rejects a role it does not know, and the
filtering lives in `toRequestBody` where it has a test.

**A chat's name is not stored.** `titleOf(messages)` derives it from the first user message, every
time. Why: a stored title is a second copy of something the messages already say, and the two drift
the moment either changes. The cost is visible and accepted — a chat with only a draft and no
message is called "Yeni sohbet", because there is no message to name it after.

**`id` is `max + 1`, never random.** No `crypto.randomUUID`, no `Date.now`, no `Math.random`. Why:
the id is produced inside the pure layer, and a pure layer that reaches for a clock or an entropy
source stops being testable without stubbing globals.

## Language
**English:** code comments, docstrings, test names, this file, `FOUNDATION.md`, `README.md` and
commit messages.
**Turkish:** the text that appears on screen — and only that.

Design specs and plans under `docs/superpowers/` are Turkish, matching every other document there.

The line falls where it does because of who is reading. A button label is read by whoever is using
the app; everything else here is read by whoever is changing it. `queen-editor` draws it the same
way, and following it means one habit across the repo rather than two.

## Tests
`npm test` from `prompt-chat/` — Vitest against jsdom. No test opens a browser, reaches the network
or waits a real second: `fetch` is replaced with `vi.stubGlobal`, and `test-setup.js` unmounts,
un-stubs and clears `localStorage` after each one.

Test files sit next to their source as `<name>.test.js(x)` and are never imported by the app.
`jest-dom` is **not** installed — assert on the DOM directly (`expect(btn.disabled).toBe(true)`),
which is also what Queen Editor does.

One trap worth knowing before you write a query: **a chat's first user message is also its sidebar
title**, so the same text is on screen twice and a bare `getByText` throws "found multiple
elements". Scope assertions about the conversation to the conversation:

```js
const inChat = () => within(document.querySelector(".chat"));
```

This is not a workaround — it says what the assertion actually means, which is that the message is
in the chat rather than merely somewhere on the page.
