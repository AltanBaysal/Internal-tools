# Madde 369 — Konuşma senaryonun içine yazılır: test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** İki test: Start a scenario'nun sahneler adımı kullanıcının istediği konuşmayı o karenin sahne
cümlesine yazar; kare yazarı sahnedeki sözleri aksiyon satırına yazmaz. Yalnız test, metin yok.

**Mimari:** Birinci test `START_A_SCENARIO`'yu `instruction_for("start-a-scenario")` üstünden okur ve
`STEPS[3]` ile `STEPS[4]` başlıkları arasından keser — 368'in şekli. İkinci test
`WRITE_FRAME_SYSTEM_PROMPT` ile `SDXL_PROMPT_RULES`'ı `prompt` modülünden okur.

**Teknoloji:** pytest.

**Spec:** [2026-09-29-queenagent-m369-konusma-senaryoda-testler-design.md](../specs/2026-09-29-queenagent-m369-konusma-senaryoda-testler-design.md)

## Genel kısıtlar

- Testler İngilizce; yorum NEDEN'i söyler.
- `skip`/`xfail` yok.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşar.
- Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: `test_skills.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_skills.py`

**Arayüzler:** Kullanır: `_flow()`, `_edit()`, `STEPS` (aynı dosyada; `STEPS` modül seviyesinde, test
çalışırken tanımlı); `WRITE_FRAME_SYSTEM_PROMPT`, `SDXL_PROMPT_RULES`
(`backend.features.workspace.domain.prompt`).

- [ ] **Adım 1: Yeni bölüm**, `test_the_scenes_step_writes_no_frame_of_clothes_coming_off_unless_asked`'in
  altına:

```python
# --- speech rides in the scene sentence (Madde 369) -----------------------------------------------
#
# 29 Sep, the user: speech wanted in a frame has to be written inside the scenario, so queen-editor's
# model, which reads each frame's scene sentence beside its photo (Queen Editor v8-3b), can put it into
# the video prompt. Only speech. The scenes step is where it is read while the sentence is written.
#
# The same sentence has a second reader: the frame writer turns it into the photo prompt's action line.
# The weak image model cannot draw speech, and quoted words come back drawn as text -- so that reader is
# told to leave the words out, or the first half of this madde would break every frame it touches.


def test_the_scenes_step_writes_wanted_speech_into_the_frames_scene_sentence():
    said = _flow()
    start, end = said.index(STEPS[3]), said.index(STEPS[4])
    step = said[start:end].lower()
    assert "speak" in step
    assert "that frame's scene sentence" in step
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "speak" not in (said[:start] + said[end:]).lower()
    assert "speak" not in _edit().lower()


def test_the_frame_writer_leaves_spoken_words_out_of_the_action_line():
    from backend.features.workspace.domain.prompt import (
        SDXL_PROMPT_RULES,
        WRITE_FRAME_SYSTEM_PROMPT,
    )

    said = WRITE_FRAME_SYSTEM_PROMPT.lower()
    assert "speaks" in said
    assert "leave their words out" in said
    # Not in the rules the six map tools carry too: none of them writes an action.
    assert "speak" not in SDXL_PROMPT_RULES.lower()
```

### Görev 2: Kırmızı

- [ ] Dört satır, paralel, olduğu gibi. Beklenen kırmızı yalnız iki yeni test. Geri kalan her şey yeşil;
  queen-editor ve frontend'ler değişmez.
- [ ] Commit: `test(queen-agent): Madde 369 red -- speech the user wants rides in the frame's scene sentence`
