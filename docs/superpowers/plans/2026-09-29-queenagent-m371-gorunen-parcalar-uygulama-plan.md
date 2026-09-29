# Madde 371 — Kontrol: yalnız görünen parçalar: uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** `THE_CHECKS`'e ikinci kontrolü yazmak, ve kırmızı commit'in (`5cda0452`) üç testini yeşile
çevirmek.

**Mimari:** Yalnız metin: `prompt.THE_CHECKS`'e bir blok ve docstring'in bugüne getirilmesi. Kod yok.

**Teknoloji:** Python sabitleri; pytest.

**Spec:** [2026-09-29-queenagent-m371-gorunen-parcalar-uygulama-design.md](../specs/2026-09-29-queenagent-m371-gorunen-parcalar-uygulama-design.md)

## Genel kısıtlar

- Modele giden metin sade, kısa İngilizce; `pov`, `shot`, `framing`, `video`, `h3`, `taken off`,
  `speak` geçmez.
- Tavanlar: akış ≤ 1000, Improve ≤ 700 kelime.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi.
- Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: `THE_CHECKS`

**Dosyalar:** Değişir: `queen-agent/backend/features/workspace/domain/prompt.py` (`THE_CHECKS` ve
docstring'i)

- [ ] **Adım 1:** `Check 1`'in son satırından sonra, kapanıştan önce:

```python
    "- Then write_missing_actions writes the emptied and the new frames, so each gets its own "
    "action.\n"
    "\n"
    "Check 2 -- visible parts\n"
    "- Read the camera angle in each frame's action. A frame fails when its prompt names a part of "
    "somebody that the angle hides, such as a face seen from behind: the model draws it anyway, "
    "or gives it to somebody else.\n"
    "- Write a second entry of only what shows, with add_character or add_outfit, named for it: "
    "man body no face, dress from behind. Use it if it is already there.\n"
    "- Give update_frame the frame's cast with those entries in place of the whole ones, and "
    "without anybody the angle does not show. The whole entries stay as they are: other frames "
    "show them whole.\n"
    "\n"
    "When the checks are done, ..."
```

- [ ] **Adım 2:** Docstring: *"The next checks (371 to 373) go in after Check 1"* → *"The next checks
  (372 and 373) go in after Check 2"*; sonuna bir paragraf:

```
Check 2 leaves a hidden part out through an entry of its own (Madde 371). A frame names whole
entries and build_prompts puts each in whole, so nothing else can say "only this much of them
here". The angle is the action's and stays: what the check corrects is what the frame names.
```

### Görev 2: Yeşil

- [ ] Dört satır, paralel, olduğu gibi; hepsi yeşil.
- [ ] Commit: `feat: Madde 371 -- the second check keeps only what the angle shows`
