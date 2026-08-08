# prompt-chat

Our own chat window onto Grok. What you use it for is up to you — asking questions, drafting text,
working a prompt into shape. Everyone on the team runs their own copy; there is no shared instance
and nothing is deployed.

## Run

```bash
cd prompt-chat
npm install     # once
npm run dev     # http://localhost:5173
```

On the first load, paste an API key from [console.x.ai](https://console.x.ai) into the field in the
settings panel. It is kept in the browser's `localStorage`, never written into the source — which is
why the code can be committed freely. (`.env` is not an option either: Vite inlines every `VITE_`
variable into the build, so it would hide nothing.)

Next to it is the model name, `grok-4.3` by default. If the console shows a different id, fix it
here — no code change needed. Switching to another model is the same field.

## Use

Enter sends, Shift+Enter starts a new line. **Kopyala** under each reply puts the whole text on the
clipboard, line breaks included.

The left column lists your chats. **+ Yeni sohbet** starts one; hovering a row reveals a `×` that
asks before it deletes. Chats, the one you had open, and whatever you left half-typed in each of
them are all kept in `localStorage` — close the tab, come back tomorrow, and you are where you left
off.

There is no system prompt. If you want the model working under a fixed instruction, write it as the
first message; the chat keeps it, so you go back to that chat rather than retyping it.

The key and the model name live under **⚙ Ayarlar** at the bottom left. It stays closed once a key
is stored, and opens itself when there is none.

## Test

```bash
npm test
```

Vitest against jsdom: no browser opens, nothing reaches the network, `fetch` is stubbed.

## Three things worth knowing

**Your chats are yours and this browser's.** There is no server behind any of it. Nobody sees your
chats and you cannot open anyone else's — what moves between people is text you copy out. Clearing
browser data loses them.

**Deleting cannot be undone.** That is why it asks first: a chat may hold something you spent real
time on.

**A reply in flight is lost if you close the page.** Your message stays, the answer never arrives;
send it again when you come back. Nothing tries to resume it.

## Where the decisions live

Why there is no backend, why the key is typed on the page, why `dist/` is not committed —
[FOUNDATION.md](FOUNDATION.md).
Layers, file layout and the testing idiom — [CODE-STANDARD.md](CODE-STANDARD.md).
