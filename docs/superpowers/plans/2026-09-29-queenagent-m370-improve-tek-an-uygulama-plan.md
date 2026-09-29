# Madde 370 — Improve skill'i ve tek an kontrolü: uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** `e19f6d93`'ün kırmızı testlerini yeşile getiren metinler ve kayıtlar.

**Mimari:** Kontroller `prompt.THE_CHECKS`'te bir kez yazılır; `START_A_SCENARIO` ve `IMPROVE` onunla
biter. `skills.py` ve `skills.js` yeni skill'i kaydeder.

**Teknoloji:** Python (metin sabitleri), React (liste).

**Spec:** [2026-09-29-queenagent-m370-improve-tek-an-uygulama-design.md](../specs/2026-09-29-queenagent-m370-improve-tek-an-uygulama-design.md)

## Genel kısıtlar

- Modele giden metin sade, kısa İngilizce; kontroller bir kez yazılır.
- Yorum NEDEN'i söyler, yalnız bugünü.
- dist derlenmez *(Claude derler)*.
- Suite yalnız dört satırla; commit'te çift tırnak yok, amend yok.

---

### Görev 1: `prompt.py`

**Dosyalar:** Değişir: `queen-agent/backend/features/workspace/domain/prompt.py`

**Arayüzler:** Üretir: `THE_CHECKS: str`, `IMPROVE: str`.

- [ ] **Adım 1:** Skill bloğunun yorumu üç metni söyler.
- [ ] **Adım 2:** `THE_IMAGE_MODEL`'in docstring'inin altına `THE_CHECKS`, spec'teki metin birebir,
  docstring'iyle *(neden tek yer, neden başlıksız, 371–373 nereye ekler)*.
- [ ] **Adım 3:** `START_A_SCENARIO`: `five steps` → `six steps`; 5. adım:

```python
    "Step 5 -- the prompts\n"
    "- Fill the waiting frames with write_missing_actions, then write the list with "
    "build_prompts.\n"
    "- This step waits for no approval. Go on to Step 6 in the same turn.\n"
    "\n"
    "Step 6 -- the checks\n" + THE_CHECKS
```

- [ ] **Adım 4:** `START_A_SCENARIO`'nun altına:

```python
IMPROVE = (
    "You are an expert SDXL prompt reviewer. The scenario you work on is already written and its "
    "prompts are built, one per frame. You run the checks below on it, fix the frames that fail, "
    "and the user approves each check before the next.\n"
    "\n" + THE_IMAGE_MODEL + "\n"
    "\n"
    "Step 1 -- the scenario\n"
    "- Read the scenario file the request names. If more than one could be it, ask which.\n"
    "- If the project holds a plan for it, carry on from the check the plan names. If it holds "
    "none, write one with create_file.\n"
    "- This step waits for no approval. Go on to Step 2 in the same turn.\n"
    "\n"
    "Step 2 -- the checks\n" + THE_CHECKS
)
```

### Görev 2: kayıtlar

**Dosyalar:** Değişir: `queen-agent/backend/features/workspace/domain/skills.py`,
`queen-agent/frontend/src/features/workspace/skills.js`, `queen-agent/backend/tests/test_skills.py`
*(yalnız bir yorum)*

- [ ] `INSTRUCTIONS`'a `"improve": prompt.IMPROVE`; docstring üç metin.
- [ ] `SKILLS`'in sonuna:

```js
  {
    id: "improve",
    name: "Improve",
    detail: "Run four checks on a scenario's frames and prompts, and say yes after each one.",
  },
```

  ve baştaki yorum üç satırı söyler.
- [ ] `test_the_menu_and_the_instructions_carry_the_same_names`'in yorumu üçüncüyü söyler.

### Görev 3: Yeşil

- [ ] Dört satır, paralel, olduğu gibi; hepsi yeşil.
- [ ] Commit: `feat: Madde 370 -- Improve opens with its first check, one moment`
