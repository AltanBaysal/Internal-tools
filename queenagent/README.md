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

Two environment variables:

| Variable | What it does |
|---|---|
| `QUEENAGENT_ROOT` | Where your projects live. Defaults to `QueenAgent` in your home folder. |
| `XAI_API_KEY` | Your xAI key. The app starts without it, but chats cannot answer. |

## Develop

Run Vite and Flask side by side so a UI change costs no build:

```bash
cd queenagent/frontend && npm run dev     # serves the UI, proxies /api to Flask
cd queenagent && python main.py           # serves the API
```

## Test

```bash
cd queenagent && pytest
cd queenagent/frontend && npm test
```

## Rules

Principles and stack decisions: [FOUNDATION.md](FOUNDATION.md).
Layering and structure: [CODE-STANDARD.md](CODE-STANDARD.md).
What gets built and in what order: [the v2 roadmap](../docs/superpowers/plans/2026-08-15-queenagent-v2-roadmap.md).
