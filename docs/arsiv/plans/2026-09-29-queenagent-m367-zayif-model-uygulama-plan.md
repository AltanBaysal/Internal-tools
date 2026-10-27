# Madde 367 — Bütün skill'ler zayıf modeli bilir, ve `pov_` kalkar: uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** `5c013526`'daki yedi kırmızı testi, yalnız `prompt.py`'nin metinlerini değiştirerek yeşile getirmek.

**Mimari:** Tek yeni sabit `THE_IMAGE_MODEL`, iki skill metninin açılışının arkasına eklenir; kare yazarının ilk cümlesi değişir; `pov_` üç metinden çıkar.

**Teknoloji:** Python string sabitleri.

**Spec:** [2026-09-29-queenagent-m367-zayif-model-uygulama-design.md](../specs/2026-09-29-queenagent-m367-zayif-model-uygulama-design.md)

## Genel kısıtlar

- Modele giden metin sade, kısa İngilizce; her kural bir kez.
- 368–374'ün kuralı yazılmaz.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşar. dist yok, tarayıcı yok.
- Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: `prompt.py`

**Dosyalar:** Değişir: `queen-agent/backend/features/workspace/domain/prompt.py`

- [ ] **Adım 1: Skill bloğunun tavan yorumu** — son paragraf:

```python
# Since Madde 123 each opens as a persona, and a word cap in test_skills.py keeps it short; Madde
# 367 raised the cap, and the test says why. From here a sentence enters only by deleting one.
```

- [ ] **Adım 2: `THE_IMAGE_MODEL`**, `EDIT_PROMPTS`'un önüne:

```python
THE_IMAGE_MODEL = (
    "The prompts go to a weak text-to-image model of the SDXL family. It cannot draw anything "
    "complex, so ask it only for what is simple to draw. Each frame is one moment, drawn as one "
    "still picture, and that picture becomes a 4-second video."
)
"""What every skill knows about the model at the far end (Madde 367).

Written once and carried by each skill text right after its opening, because it is one fact and two
copies of it is how one of them goes stale. Not in SYSTEM_PROMPT: that text names no task.
"""
```

- [ ] **Adım 3: `EDIT_PROMPTS`** — açılış paragrafından sonra `"\n\n" + THE_IMAGE_MODEL + "\n\n"`,
  ve 2. adımın `pov_` maddesi silinir:

```python
    "- Who is in a frame, what they wear, or where it happens: update_frame, once for each frame "
    "the request reaches.\n"
    "\n"
    "Step 3 -- the answer\n"
```

- [ ] **Adım 4: `START_A_SCENARIO`** — açılış:

```python
    "You are an expert scenario writer, and everything here serves one end: image prompts, one "
    "per frame. You lay the ground and then build the prompts, in one flow, walking the user "
    "through five steps in order, by asking.\n"
    "\n" + THE_IMAGE_MODEL + "\n"
    "\n"
    "How a step runs:\n"
```

  ve 2. adımın `pov_` maddesi silinir; adım `add_outfit` maddesiyle biter.

- [ ] **Adım 5: `ADD_CHARACTER_TAGS`** — *"A pov_ entry shows only hands and arms and no face, so it
  carries no count at all."* cümlesi silinir.

- [ ] **Adım 6: 34. düzeltmenin yorumu** — *"the count, solo, a pov_ entry, naming an outfit"* →
  *"the count, solo, naming an outfit"*.

- [ ] **Adım 7: `WRITE_FRAME_SYSTEM_PROMPT`** — *"An SDXL-family image model draws it."* →
  *"A weak SDXL-family image model draws it, and it cannot draw anything complex."*

### Görev 2: Yeşil

- [ ] Dört satır, paralel, olduğu gibi; queen-agent frontend arka planda, özeti görev çıktısından.
  Beklenen: hepsi yeşil.
- [ ] Commit: `feat: Madde 367 -- every skill knows the weak image model, and pov_ goes`
