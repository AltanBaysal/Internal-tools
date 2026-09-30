# Madde 385 — Edit prompts da konuşmayı sahne cümlesine yazar — uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** 369'un konuşma cümlesini tek sabite çıkarıp Edit prompts'un düzeltme adımına da koymak, ki
kırmızı commit'teki iki test yeşile dönsün.

**Mimari:** `prompt.py`'de yeni `SPEECH_IN_THE_SCENE`; Start a scenario ve Edit prompts onu taşır.
Başka dosya değişmez.

**Teknoloji:** Python (metin sabitleri), pytest.

**Spec:** [2026-09-30-queenagent-m385-edit-prompts-konusma-uygulama-design.md](../specs/2026-09-30-queenagent-m385-edit-prompts-konusma-uygulama-design.md)

## Genel kısıtlar

- Tavanlar: akış 1025, Edit prompts 856, Improve 700.
- Start a scenario'nun metni bayt bayt aynı kalır.
- Modele giden metin İngilizce; testlere dokunulmaz.

---

### Görev 1: Paylaşılan konuşma cümlesi

**Dosyalar:**
- Değişir: `queen-agent/backend/features/workspace/domain/prompt.py`
- Test: `queen-agent/backend/tests/test_skills.py` (kırmızı commit `06ecc37b`, değişmez)

**Arayüzler:**
- Üretir: `SPEECH_IN_THE_SCENE: str` — `prompt.py` modül düzeyinde.

- [ ] **Adım 1: Sabit**, `THE_IMAGE_MODEL`'in docstring'inin arkasına:

```python
SPEECH_IN_THE_SCENE = (
    "- If the user wants someone to speak in a frame, write their words, in quotation marks, "
    "into that frame's scene sentence: the video's prompt is written from it."
)
"""Where speech the user asks for is written (Madde 369), in both skills that write a scene (385).

queen-editor's model reads each frame's scene sentence beside its photo and writes the video's
prompt from it, so the words have to be in that sentence. The photo prompt is kept clear of them by
the frame writer, which leaves speech out of the action line: the image model draws quoted words as
text. Start a scenario says it while it writes the scenes and Edit prompts while it makes its fix --
one sentence, so the two skills cannot come to disagree about where the words go.
"""
```

- [ ] **Adım 2: Start a scenario**, `Step 4 -- the scenes` içinde:

```python
    "- Write them with add_scene: one sentence each, in the language the user is writing in.\n"
    + SPEECH_IN_THE_SCENE + "\n"
    "- What someone wears can change from one scene to the next. The moment clothes are taken "
```

(eski iki satırlık `"- If the user wants someone to speak ..."` maddesinin yerine).

- [ ] **Adım 3: Edit prompts**, `Step 2 -- the fix`'in sonuna:

```python
    "- Who is in a frame, what they wear, or where it happens: update_frame, once for each frame "
    "the request reaches.\n" + SPEECH_IN_THE_SCENE + "\n"
    "\n"
    "Step 3 -- the prompts\n"
```

- [ ] **Adım 4: Suite.** Dört satır, olduğu gibi, paralel:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; tavan testi Edit prompts'u 856'nın içinde, akışı 1025'in içinde bulur.

- [ ] **Adım 5: Commit** — `prompt.py`, uygulama spec'i ve planı:

```
feat: Madde 385 -- Edit prompts writes wanted speech into the frame's scene sentence
```
