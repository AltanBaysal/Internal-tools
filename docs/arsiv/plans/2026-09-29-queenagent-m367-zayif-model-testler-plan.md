# Madde 367 — Bütün skill'ler zayıf modeli bilir, ve `pov_` kalkar: test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Her skill metninin zayıf modeli, tek anı ve 4 saniyelik videoyu söylediğini, kare yazarının zayıf modeli bildiğini ve modele söylenen hiçbir metnin `pov` içermediğini isteyen testler; tavanın yeni sayıları kararıyla. Yalnız testler, kod yok.

**Mimari:** Testler olguyu tutar: skill metinleri `INSTRUCTIONS` üstünden (`ALL_SKILLS` ile parametreli), `pov` süpürmesi `prompt.py`'nin büyük harfli metinleri ve `TOOL_SPECS` üstünden.

**Teknoloji:** pytest.

**Spec:** [2026-09-29-queenagent-m367-zayif-model-testler-design.md](../specs/2026-09-29-queenagent-m367-zayif-model-testler-design.md)

## Genel kısıtlar

- Testler İngilizce; yorum NEDEN'i söyler.
- `skip`/`xfail` yok; kalkan davranışın testi davranışla birlikte kalkar.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşar.
- Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: `test_skills.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_skills.py`

- [ ] **Adım 1: `pov_` istisnası kalkar.** `test_no_instruction_names_a_tool_that_is_gone`'da istisnanın
  dört satırlık yorumu silinir ve satır şu olur:

```python
    known = {spec["function"]["name"] for spec in TOOL_SPECS}
```

- [ ] **Adım 2: Madde 182'nin bölümü kalkar** — `# --- somebody the camera is standing in (Madde 182)`
  başlığı ve yorumu, ve üç test: `test_the_flow_opens_a_pov_entry_beside_each_character`,
  `test_a_pov_entry_carries_neither_a_count_nor_an_outfit`, `test_a_pov_frame_names_the_pov_entry_in_its_cast`.

- [ ] **Adım 3: Yeni bölüm**, `test_every_skill_says_what_the_prompts_are_for`'un altına:

```python
# --- the image model at the far end (Madde 367) ---------------------------------------------------
#
# 28 Sep, the user: the model does not know its prompts go to a weak SDXL model, so it writes things
# too complex for it to draw -- and fixes them the moment it is told. Parametrised by ALL_SKILLS,
# which a test above holds equal to INSTRUCTIONS, so the next skill cannot arrive without this.


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_knows_the_image_model_is_weak(skill):
    assert "weak" in instruction_for(skill).lower()


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_knows_a_frame_is_one_moment_and_a_4_second_video(skill):
    # The user again: every video is four seconds. A frame is one picture, and the picture is where
    # the video starts, so a scene holding two moments can be neither.
    said = instruction_for(skill)
    assert "one moment" in said
    assert "4-second video" in said
```

- [ ] **Adım 4: Tavan testi** — `test_the_texts_stay_short_enough_to_be_read`'in yorumunun sonuna karar
  eklenir ve sayılar değişir:

```python
    #
    # Madde 367 raises both, on the user's decision of 28 September. Madde 123 set them for the
    # model of that day, which stopped reading the middle of a long text; the texts are read by a
    # stronger model now. The new numbers leave room for what comes next: the four checks (370 to
    # 373) are written once and the flow ends with them, Edit prompts ends with them too (374), and
    # 368 and 369 each add a sentence to the scenes step -- so both texts can roughly double. The
    # cap still guards: a text at its cap takes a sentence only by deleting one.
    assert len(_flow().split()) <= 1000
    assert len(_edit().split()) <= 700
```

### Görev 2: `test_prompt.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_prompt.py`

- [ ] **Adım 1:** Başa `import json`.
- [ ] **Adım 2:** `test_the_prompt_module_holds_the_texts_the_others_gave_up`'ın altına:

```python
def test_no_text_the_model_is_told_asks_for_a_pov_entry():
    # Madde 367 (user, 28 Sep): the pov_ entry goes. It was a naming rule rather than a field (Madde
    # 182), so no code ever knew it -- only texts told the model to write one, and every text is
    # here. The tool schemas are swept whole as well, for their parameter names.
    from backend.features.workspace.domain import prompt
    from backend.features.workspace.domain.tools import TOOL_SPECS

    texts = _texts_named_by(prompt) | {json.dumps(TOOL_SPECS)}
    assert len(texts) > 10
    for said in texts:
        assert "pov" not in said.lower(), said[:80]
```

### Görev 3: `test_tools.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_tools.py`

- [ ] **Adım 1:** `test_the_rules_carry_nothing_that_belongs_to_one_field`'de
  `for moved in ("solo", "outfit", "location"):`.
- [ ] **Adım 2:** `test_an_entry_for_somebody_half_in_shot_carries_no_count` silinir; yerine:

```python
def test_the_frame_writer_knows_the_image_model_is_weak():
    # Madde 367. Not a skill, but the text that writes the action line of every photo prompt -- which
    # is where a frame grows more complex than the model at the far end can draw.
    from backend.features.workspace.domain.prompt import WRITE_FRAME_SYSTEM_PROMPT

    assert "weak" in WRITE_FRAME_SYSTEM_PROMPT.lower()
```

### Görev 4: Kırmızı

- [ ] Dört satır, paralel, olduğu gibi. Beklenen kırmızı: `test_every_skill_knows_the_image_model_is_weak`
  (2), `test_every_skill_knows_a_frame_is_one_moment_and_a_4_second_video` (2),
  `test_no_text_the_model_is_told_asks_for_a_pov_entry`, `test_the_frame_writer_knows_the_image_model_is_weak`,
  ve istisnası kalkan `test_no_instruction_names_a_tool_that_is_gone` — yedi. Geri kalan her şey yeşil; queen-editor ve frontend'ler değişmez.
- [ ] Commit: `test(queen-agent): Madde 367 red -- every skill knows the weak image model, and pov_ goes`
