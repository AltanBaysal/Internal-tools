# Madde 388 — Edit prompts olmayan negatif dosyayı söylemez — uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** Kırmızı testi (`17d41190`) Edit prompts'a bir cümleyle yeşile getirmek.

**Mimari:** Yalnız `prompt.py`: `EDIT_PROMPTS`'un Step 4'ündeki Check 4 maddesi bir cümle alır;
`THE_CHECKS`'in docstring'i kapanışın koşulunun da editörde olduğunu söyler. Paylaşılan metin değişmez.

**Teknoloji:** Python sabitleri, pytest.

**Spec:** [2026-09-30-queenagent-m388-negatif-dosya-uygulama-design.md](../specs/2026-09-30-queenagent-m388-negatif-dosya-uygulama-design.md)

## Genel kısıtlar

- Modele giden metin 390'ın biçiminde: madde içinde tam cümle, kısaltma yok, İngiliz yazımı.
- Tavanlar: akış 1025, Edit prompts 870, Improve 700.
- Suite yalnız CLAUDE.md'deki dört satırla, olduğu gibi, paralel koşar.

---

### Görev 1: Cümle ve docstring

**Dosyalar:**
- Değişir: `queen-agent/backend/features/workspace/domain/prompt.py` (`THE_CHECKS`'in docstring'i,
  `EDIT_PROMPTS`'un Step 4'ü)
- Test: `queen-agent/backend/tests/test_skills.py` (commit'li, dokunulmaz)

**Arayüzler:**
- Kullanır: testin istediği `no negative file` ve `the prompt file alone`, `Otherwise skip it`'ten sonra.

- [ ] **Adım 1: `EDIT_PROMPTS`'un Check 4 maddesi.** Şu:

```python
    "- Check 4 runs only if your change touched the scenario's cast: a character added, changed or "
    "taken out. Otherwise skip it.\n" + THE_CHECKS
```

şu olur:

```python
    "- Check 4 runs only if your change touched the scenario's cast: a character added, changed or "
    "taken out. Otherwise skip it. If the scenario has no negative file, close by naming the "
    "prompt file alone.\n" + THE_CHECKS
```

- [ ] **Adım 2: `THE_CHECKS`'in docstring'i.** Son paragrafın sonuna:

```
So is the closing's: it names the negative file, and an edit that
skipped Check 4 on a scenario written before 373 has none, so the editor's step says to name the
prompt file alone (Madde 388).
```

- [ ] **Adım 3: Suite.** Dört satır, olduğu gibi, paralel:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

- [ ] **Adım 4: Commit** — uygulama spec'i, plan ve `prompt.py`:

```
feat: Madde 388 -- Edit prompts names the negative file only when there is one
```
