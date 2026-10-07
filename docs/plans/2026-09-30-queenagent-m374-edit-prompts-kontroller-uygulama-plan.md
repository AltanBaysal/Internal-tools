# Madde 374 — Edit prompts kontrollerle biter — uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Edit prompts `THE_CHECKS` ile biter; kontroller yalnız değişikliğin ulaştığı karelere bakar,
Check 4 yalnız senaryonun kadrosu değiştiyse koşar. Kırmızı commit `a2c13521`'in altı testi yeşile döner.

**Mimari:** Yalnız `prompt.py`'nin metinleri. `THE_CHECKS`'in ilk satırı adımın daraltmasına yer açar;
`EDIT_PROMPTS`'un 3. adımı cevap olmaktan çıkar ve 4. adım kapsamı ve Check 4'ün koşulunu söyleyip
`THE_CHECKS`'i ekler.

**Teknoloji:** Python sabitleri, pytest.

**Spec:** [uygulama spec'i](../specs/2026-09-30-queenagent-m374-edit-prompts-kontroller-uygulama-design.md)

## Genel kısıtlar

- Kontroller tek yerde: `THE_CHECKS` kopyalanmaz.
- Tavanlar: akış 1025, Edit prompts 830, Improve 700.
- Dört test satırı, yazıldığı gibi, paralel.
- Modele giden metin sade, kısa İngilizce.

---

### Görev 1: Metinler

**Dosyalar:**
- Değişir: `queen-agent/backend/features/workspace/domain/prompt.py` — `THE_CHECKS` (ilk satır ve
  docstring), `EDIT_PROMPTS` (3. adım, yeni 4. adım).

- [ ] **Adım 1: `THE_CHECKS`'in ilk satırı**

```python
    "- Run the checks in order, each over every frame of the scenario unless this step limits "
    "them.\n"
```

Akış tavanı için iki kelime düşer: bu satırdaki *below*, ve Check 2'de *"a face seen from behind"* →
*"a face from behind"*.

- [ ] **Adım 2: `EDIT_PROMPTS`'un sonu**

```python
    "Step 3 -- the prompts\n"
    "- Call build_prompts again: the prompt file is rebuilt rather than patched.\n"
    "- Say what you changed and which frames it reached.\n"
    "- This step waits for no approval. Go on to Step 4 in the same turn.\n"
    "\n"
    "Step 4 -- the checks\n"
    "- This step limits the checks to the frames your change reached.\n"
    "- Check 4 runs only if your change touched the scenario's cast: a character added, changed or "
    "taken out. Otherwise skip it.\n" + THE_CHECKS
```

`EDIT_PROMPTS` `THE_CHECKS`'ten sonra tanımlı olduğu için ad hazır.

- [ ] **Adım 3: `THE_CHECKS`'in docstring'i** — ilk paragraf:

```
Start a scenario and Edit prompts end with them, and Improve runs them alone. A skill cannot call
another, so all three texts carry this part -- as one constant, because the same rule written twice
is how one copy drifts. No heading of its own: each skill puts its own step heading in front, since
the step's number differs. The closing belongs to whatever check comes last, so a new check goes in
front of it.
```

ve son paragraftan sonra yeni paragraf:

```
Edit prompts runs them after its change (Madde 374), on the frames that change reached and not on
the whole scenario: the first line reads every frame unless the step in front limits them, so the
limit is the editor's own sentence and the block stays one. Check 4's condition is the editor's for
the same reason -- the flow and Improve always write the list, and after an edit it is written again
only when the scenario's cast changed, since the list is written from it.
```

- [ ] **Adım 4: Dört satırı paralel çalıştır** — `python -m pytest queen-agent -q`,
  `npm test --prefix queen-agent/frontend`, `python -m pytest queen-editor -q`,
  `npm test --prefix queen-editor/frontend`. Beklenen: hepsi yeşil. Tavan testi kırmızıysa sayım
  yanlıştır; metin kısaltılır, tavan değil.

- [ ] **Adım 5: Commit** — spec ve plan aynı commit'te.

```
feat: Madde 374 -- Edit prompts ends with the checks, on the frames it changed
```
