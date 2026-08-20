# QueenAgent

A small AI workspace. A **project** holds two sibling collections: **chats** and **files**. Chats
produce files; a file belongs to the project, never to a chat. You read files — you never upload
them.

## Run it

```bash
cd queen-agent/frontend
npm install
npm run build           # dist is committed, so this is only needed after a source change

cd ..
export XAI_API_KEY=...  # or set it however your shell does
python main.py          # http://127.0.0.1:8100
```

The bundle is committed because this is no longer the only place the app runs: sharing it means a
Colab notebook that clones this repo and never builds ([FOUNDATION.md](FOUNDATION.md), Decisions 1
and 3). So a frontend change is not finished until `dist` is rebuilt and committed **with** its
source — `backend/tests/test_dist_is_committed.py` refuses the alternative.

The key is read at startup and the app saves none of it — there is no screen for typing one and no
endpoint that answers with one, which is what makes the Colab address survivable. Without a key the
app still starts; only asking for an answer fails, and it fails saying so.

Where your projects live is `QUEENAGENT_ROOT` — that, the key and every other setting are named in
[backend/config.py](backend/config.py), which is the one place they exist.

## Develop

Run Vite and Flask side by side so a UI change costs no build:

```bash
cd queen-agent/frontend && npm run dev    # serves the UI, proxies /api to Flask
cd queen-agent && python main.py          # serves the API
```

The test command lives in [CLAUDE.md](../CLAUDE.md), once.

## Rules

Principles and stack decisions: [FOUNDATION.md](FOUNDATION.md).
Layering and structure: [CODE-STANDARD.md](CODE-STANDARD.md).
What gets built and in what order: the roadmaps under
[`docs/superpowers/plans/`](../docs/superpowers/plans/) — the highest `vN` is the current one.
