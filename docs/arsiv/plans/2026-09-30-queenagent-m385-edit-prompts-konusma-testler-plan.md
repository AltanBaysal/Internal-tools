# Madde 385 — Edit prompts da konuşmayı sahne cümlesine yazar — test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** 385'in davranışını tutan testleri yazmak, suite'i koşup yeni testlerin kırmızı olduğunu görmek,
kırmızı commit'lemek. Kod yazılmaz.

**Mimari:** Yalnız `queen-agent/backend/tests/test_skills.py` değişir. Yeni iki test Edit prompts'un
2. adımını ve paylaşılan sabiti (`SPEECH_IN_THE_SCENE`) sorar; 369'un testindeki Edit prompts yokluk
satırı kalkar; tavan testi Edit prompts'a 856 verir.

**Teknoloji:** pytest.

**Spec:** [2026-09-30-queenagent-m385-edit-prompts-konusma-testler-design.md](../specs/2026-09-30-queenagent-m385-edit-prompts-konusma-testler-design.md)

## Genel kısıtlar

- Tavanlar: akış 1025, Edit prompts 856 (830'dan), Improve 700.
- Test isimleri ve yorumlar İngilizce; `skip`/`xfail` yok.
- Suite yalnız CLAUDE.md'deki dört satırla, olduğu gibi, paralel koşar.

---

### Görev 1: Testler

**Dosyalar:**
- Değişir: `queen-agent/backend/tests/test_skills.py`

**Arayüzler:**
- Kullanır: `_flow()`, `_edit()`, `_improve()`, `STEPS`, `EDIT_STEPS` (dosyada var).
- Üretir: uygulamanın vermesi gereken ad — `prompt.SPEECH_IN_THE_SCENE` (str).

- [ ] **Adım 1: 369'un testinden Edit prompts yokluğu kalkar.** `test_the_scenes_step_writes_wanted_speech_into_the_frames_scene_sentence`
  içinde şu satır silinir:

```python
    assert "speak" not in _edit().lower()
```

- [ ] **Adım 2: Yeni bölüm**, 374'ün bölümünün son testinden
  (`test_after_an_edit_the_negative_is_written_again_only_if_the_cast_changed`) sonra:

```python
# --- Edit prompts writes speech where the flow does (Madde 385) -----------------------------------
#
# 30 Sep, the user: "olur eklensin". 369's rule stood in the flow alone, so speech asked for while
# editing went into the photo prompt or nowhere. The same sentence goes into the editor's fix step,
# where it makes its change -- one constant, so the two cannot drift apart.


def _edits_fix_step():
    said = _edit()
    return said[said.index(EDIT_STEPS[1]) : said.index(EDIT_STEPS[2])]


def test_edit_prompts_writes_wanted_speech_into_the_frames_scene_sentence():
    step = _edits_fix_step()
    assert "speak" in step
    assert "quotation marks" in step
    assert "that frame's scene sentence" in step
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "speak" not in _edit().replace(step, "").lower()


def test_the_speech_sentence_is_written_once_and_both_skills_carry_it():
    from backend.features.workspace.domain.prompt import SPEECH_IN_THE_SCENE

    assert "speak" in SPEECH_IN_THE_SCENE
    assert "that frame's scene sentence" in SPEECH_IN_THE_SCENE
    flow = _flow()
    scenes = flow[flow.index(STEPS[3]) : flow.index(STEPS[4])]
    assert scenes.count(SPEECH_IN_THE_SCENE) == 1
    assert flow.count(SPEECH_IN_THE_SCENE) == 1
    assert _edits_fix_step().count(SPEECH_IN_THE_SCENE) == 1
    assert _edit().count(SPEECH_IN_THE_SCENE) == 1
    # Improve writes no scene the user asks for, so it carries no speech.
    assert "speak" not in _improve().lower()
```

- [ ] **Adım 3: Tavan.** `test_the_texts_stay_short_enough_to_be_read` yorumunun sonuna 385'in
  gerekçesi, Edit prompts'un satırı `<= 856`:

```python
    # Madde 385 raises the editor's to 856. Its fix step carries 369's sentence about speech, the one
    # the flow's scenes step carries, written once for both; the flow's own count does not move.
    assert len(_flow().split()) <= 1025
    assert len(_edit().split()) <= 856
    assert len(_improve().split()) <= 700
```

- [ ] **Adım 4: Suite.** Dört satır, olduğu gibi, paralel:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent pytest'te yalnız iki yeni test kırmızı — ilki `"speak" in step` satırında,
ikincisi `ImportError` (sabit yok). Öteki üç suite yeşil.

- [ ] **Adım 5: Kırmızı commit** — spec, plan ve test dosyası:

```
test(queen-agent): Madde 385 red -- Edit prompts writes wanted speech into the frame's scene sentence
```
