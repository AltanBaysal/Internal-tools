# Madde 336 — Yalnız Queen Flash kalır · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Arka ucun tablosu ve ön ucun listesi DeepSeek'ten yalnız `deepseek-flash`'ı tutar; test
turunun kırmızıları yeşile döner.

**Architecture:** İki tablo değişir: `config.py`'nin `MODELS`'u ve sabitleri, `models.js`'in `MODELS`'u
ve `DEFAULT_MODEL`'i. Eski id'lerin yolu bugünkü geri düşüş kuralı; kod eklenmez.

**Tech Stack:** Python, React (yalnız bir JS modülü).

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m336-yalniz-flash-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Fiyat yazısı (`$0.22 / $0.66 per 1M`) ve `grok-4.3`'ün satırı olduğu gibi kalır.
- `ModelPicker.jsx`, `main.py`, `xai_engine.py`, `engine_for` değişmez.
- `dist` derlenmez, commit'lenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: `config.py`

**Files:**
- Modify: `queen-agent/backend/config.py`

- [ ] **Step 1:** `DEEPSEEK_API_KEY`'in yorumu:

```python
# The second provider's key, since Madde 146, and it travels the same road. The notebook demands
# both: each spends a row of the table below, and a run opened on one key would have a model wired
# that it cannot answer with.
```

- [ ] **Step 2:** `MODELS`'un DeepSeek satırları:

```python
    # No /v1: this is DeepSeek's own documented base, and the client appends /chat/completions to
    # whatever it is handed.
    #
    # One name of DeepSeek's since Madde 336, the one the model has today. DeepSeek's notice of 10
    # September closed deepseek-v4-pro -- its requests go to Flash, billed as Flash, with no error --
    # and left deepseek-v4-flash an alias. Messages on disk still name both; neither is a row here,
    # so both are answered by the default.
    "deepseek-flash": {"base_url": "https://api.deepseek.com", "key": "DEEPSEEK_API_KEY"},
```

- [ ] **Step 3:** `DEFAULT_MODEL = "deepseek-flash"`; yorumu:

```python
# The one model the composer offers since Madde 336, and the same id models.js defaults to: one of
# them answers what an empty button says and this one answers where the request goes, and the two
# parting would show a name on the screen that nothing on the wire matched.
```

- [ ] **Step 4:** `PROMPT_MODEL = "deepseek-flash"`.

### Task 2: `models.js`

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/models.js`

- [ ] **Step 1:** Baş yorum ve liste:

```js
// Which models a chat can be answered by, and what each one costs. One since Madde 336: DeepSeek
// closed deepseek-v4-pro on 14 September and answers it with Flash, so a Queen Pro row would name one
// model and be answered by another. Grok left the menu rather than the app in Madde 177 -- it is
// wired in config.py, kept knowingly, and nothing picks it.
//
// The list lives here rather than in the backend, exactly as the skills' does: what the server
// knows is what an id MEANS -- its address and the key it spends (config.py) -- never which one is
// selected. The selection is the session's and rides on each message.
//
// The names are this file's own, and only this file's. An id is what the provider is told the model
// is called -- client.py sends it as the model field -- so renaming one in config.py would break
// the call, and Queen Flash is what a person sees instead. Nothing enforces that the ids here match
// config.py's table: Python and JS cannot read each other, and this sentence is the whole of what
// keeps the two in step.
//
// The detail is the price, off-peak, as the roadmap's Madde 146 read it.
export const MODELS = [
  {
    id: "deepseek-flash",
    name: "Queen Flash",
    detail: "$0.22 / $0.66 per 1M",
  },
];
```

- [ ] **Step 2:** `export const DEFAULT_MODEL = "deepseek-flash";`

### Task 3: Yeşil, ve commit

- [ ] **Step 1: Dört satırı paralel koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent'ın iki süiti yeşil; queen-editor'ün arka ucu 377'nin bilinen iki kırmızısı,
ön ucu yeşil.

- [ ] **Step 2: Farkı baştan oku** — `git diff 8383f1e5..HEAD` ve çalışma kopyası: *bitti sayılır*,
  FOUNDATION'ın 6. kararı, CODE-STANDARD, CLAUDE.md'nin Style'ı.

- [ ] **Step 3: Commit**

```powershell
git add queen-agent/backend/config.py queen-agent/frontend/src/features/workspace/models.js docs/specs/2026-09-29-queenagent-m336-yalniz-flash-uygulama-design.md docs/plans/2026-09-29-queenagent-m336-yalniz-flash-uygulama-plan.md
git commit -m @'
feat: Madde 336 -- only Queen Flash is left, under DeepSeek's name of today, deepseek-flash, and old chats are answered by it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
