# Madde 372 — Kontrol: çizilebilir mi — uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** `THE_CHECKS`'e `Check 3 -- can it be drawn` bloğu; kırmızı commit `2486b0a1`'in dört testi yeşil.

**Mimari:** Yalnız `prompt.py`'nin `THE_CHECKS` sabiti ve docstring'i. Kod, araç, yapı dosyası değişmez.

**Teknoloji:** Python sabitleri, pytest.

**Spec:** [uygulama spec'i](../specs/2026-09-29-queenagent-m372-cizilebilir-mi-uygulama-design.md)

## Genel kısıtlar

- Tavanlar değişmez: akış 1000, Improve 700.
- Blokta yasak: `pov`, `shot`, `framing`, `video`, `h3`, `weak`, `taken off`, `speak`, `one at a time`.
- Alt çizgili her kelime var olan bir araç.

---

### Görev 1: Check 3'ün metni

**Dosyalar:**
- Değişir: `queen-agent/backend/features/workspace/domain/prompt.py` — `THE_CHECKS` ve docstring'i.

- [ ] **Adım 1: Blok, Check 2'nin son satırından sonra, kapanıştan önce**

```python
    "show them whole.\n"
    "\n"
    "Check 3 -- can it be drawn\n"
    "- Read each photo prompt in the file build_prompts wrote, in its final form. A frame fails "
    "when it asks for more than the model can draw: a hard pose, too many things, or what no "
    "picture shows.\n"
    "- Simplify that part where it comes from, and keep the moment: the action with update_frame, "
    "an entry with update_character, update_outfit or update_location, which reaches every frame "
    "naming it.\n"
    "\n"
    "When the checks are done, ..."
```

- [ ] **Adım 2: Docstring**

`The next checks (372 and 373) go in after Check 2, ...` cümlesi şu olur:

```
The next check (373) goes in after Check 3, in front of the closing, which belongs to whatever check
comes last.
```

Sona paragraf:

```
Check 3 reads the built file rather than the structure (Madde 372): what the image model is handed
is the parts joined, and too much often shows only in the sum. The file is rebuilt rather than
patched, so a part is simplified where it comes from. The action is rewritten by the agent, which
has read the line; emptied, it would go back to a model that has not. An entry is changed whole,
since what cannot be drawn in one frame cannot be drawn in any.
```

- [ ] **Adım 3: Dört satırı çalıştır** — `python -m pytest queen-agent -q`,
  `npm test --prefix queen-agent/frontend`, `python -m pytest queen-editor -q`,
  `npm test --prefix queen-editor/frontend`. Beklenen: hepsi yeşil; `test_the_texts_stay_short_enough_to_be_read` dahil.

- [ ] **Adım 4: Commit**

```
feat: Madde 372 -- the third check simplifies what the model cannot draw
```
Spec ve plan aynı commit'te.
