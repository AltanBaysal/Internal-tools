# QueenAgent

A small AI workspace. A **project** holds two sibling collections: **chats** and **files**. Chats
produce files; a file belongs to the project, never to a chat. You read files — you never upload
them.

## Run it

```bash
cd queenagent/frontend
npm install
npm run build

cd ..
python main.py          # http://127.0.0.1:8100
```

Then open **Settings** at the foot of the sidebar and paste your xAI key. It is saved beside your
projects and read again on every request, so changing it needs no restart. The app starts without
one; only asking for an answer fails.

Where your projects live is `QUEENAGENT_ROOT` — that and every other setting are named in
[backend/config.py](backend/config.py), which is the one place they exist.

## Develop

Run Vite and Flask side by side so a UI change costs no build:

```bash
cd queenagent/frontend && npm run dev     # serves the UI, proxies /api to Flask
cd queenagent && python main.py           # serves the API
```

The test command lives in [CLAUDE.md](../CLAUDE.md), once.

## Rules

Principles and stack decisions: [FOUNDATION.md](FOUNDATION.md).
Layering and structure: [CODE-STANDARD.md](CODE-STANDARD.md).
What gets built and in what order: the roadmaps under
[`docs/superpowers/plans/`](../docs/superpowers/plans/) — the highest `vN` is the current one.
