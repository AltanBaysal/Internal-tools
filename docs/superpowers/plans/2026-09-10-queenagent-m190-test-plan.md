# Madde 190 · Tur 1 (testler) — Plan

**Tasarım:** [2026-09-10-queenagent-m190-kod-gecisi-testler-design.md](../specs/2026-09-10-queenagent-m190-kod-gecisi-testler-design.md)
**Hedef metinler:** [okuma kopyası](../../2026-09-09-queenagent-modele-giden-metinler.md) — §1, §3, §4, §5, §6.
**Gerekçeler:** [düzeltme log'u](../../2026-09-09-queenagent-metin-duzeltmeleri.md), 35 kayıt.

**Bu turda kod yazılmaz.** Otuz dört test kırmızıya döner; iki bekçi bugün yeşil geçer.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Yürüten:** bu oturum, tek başına.

---

## Bağlayıcı kurallar

- **Hiçbir test silinmiyor.** Kaydın kendi cümlesi: *"kuralı tutacak şekilde gevşetilecek —
  silinmeyecek, çünkü her biri bir denemenin dersi."* Bir testin yorumu, geldiği denemenin
  hikâyesidir; iddiası taşınırken yorum da **taşınır**, atılmaz.
- **Ad, iddia değişince değişir.** `test_the_character_example_is_written_in_that_vocabulary` artık
  örnek tutmuyor; adı da öyle demeyecek.
- **Kod bu turda açılmaz.**
- Commit mesajında çift tırnak yok; amend yok.

---

## Blok A · `test_prompt.py` — taban metin *(5 kırmızı)*

- [ ] **A1 — taze okuma kimin için**

`test_a_fresh_read_is_for_what_someone_else_may_have_changed` → adı ve iddiası değişir. Yeni metin
tazeliği **açık dosyalar listesine** bağlıyor: orası her raunt diskten okunuyor, yani oradaki bir
dosyayı yeniden okumak hiçbir şey satın almıyor.

```python
def test_a_fresh_read_is_for_a_file_that_is_not_already_open():
    # Madde 107's lesson, and correction 2 sharpened what it is about. The opened files are read
    # from disk every round, so what stands there is current and a second read of one buys nothing.
    # What is worth a read is a file that is not among them.
    #
    # Correction 3: the old sentence gave the wrong reason -- somebody else may have changed it --
    # and a wrong reason is a rule the model applies in the wrong places.
    said = SYSTEM_PROMPT.lower()
    assert "not among your opened files" in said
    assert "check your own writing" in said
    assert "somebody else may have changed" not in said
    assert "not the same as reading it now" not in said
```

- [ ] **A2 — okumanın sınırı**

`test_the_base_reads_nothing_the_answer_does_not_need` → aynı kural, olumlu cümle *(2)*.

```python
    assert "read only what the answer needs" in SYSTEM_PROMPT.lower()
```

- [ ] **A3 — açık dosyalar hep güncel** *(4)*

`test_the_base_says_where_a_read_file_appears`'a bir satır eklenir:

```python
    assert "opened files" in SYSTEM_PROMPT
    # Correction 4. Saying only where the file appears left open whether what stands there is the
    # file as it was read; it is read from disk every round, and a model that does not know that
    # reads it again to be sure.
    assert "always current" in SYSTEM_PROMPT
```

- [ ] **A4 — her değişiklik `edit_file`'dan geçmiyor** *(5)*

`test_the_base_edits_what_exists_rather_than_rebirthing_it`'e bir satır eklenir:

```python
    # Correction 5. A scenario is not changed with edit_file at all -- Madde 171 shut that door --
    # so a sentence naming only that tool tells the model to make a call that comes back refused.
    assert "the tool that owns that kind of file" in SYSTEM_PROMPT
```

- [ ] **A5 — düzeltme dosyaya yazılır** *(6)*

`test_the_base_puts_a_correction_on_disk_too` → adı ve iddiası değişir: eski cümle bir **tespitti**
*("a correction that lands only in the chat leaves the file saying the older thing")*, yenisi bir
**emir**.

```python
def test_the_base_puts_a_change_on_disk_rather_than_in_the_chat():
    # A change that only lands in the chat leaves the file saying the older thing, and the file is
    # what the next step reads. Correction 6: the old sentence described that failure instead of
    # asking for anything, and it covered only corrections -- the same is true of any change.
    assert "make the change in the file" in SYSTEM_PROMPT.lower()
```

---

## Blok B · `test_skills.py` — akış *(19 kırmızı)*

- [ ] **B1 — adım başlıkları**

`STEPS` sabiti yeniden yazılır. Altı test bunu okuyor.

```python
STEPS = (
    "Step 1 -- the plan",
    "Step 2 -- the characters",
    "Step 3 -- the places",
    "Step 4 -- the scenes",
    "Step 5 -- the prompts",
)
"""The flow's steps, in the order they run (Madde 198, rewritten by correction 9).

Read by the tests below and by the one that places start_scenario. Numbered headings became named
ones so that every step reads the same way -- a heading, then its rules as lines -- and so the loop
above them is not one more numbered item.
"""
```

Bunu okuyan altı testin iddiası değişmiyor, yalnız hangi dizgeyi aradıkları:

```python
# test_the_flow_writes_the_plan_before_it_asks_anything
    assert said.index("create_file") < said.index(STEPS[1])

# test_the_scenario_is_opened_by_the_tool_that_opens_one
    assert said.index(STEPS[1]) < said.index("start_scenario") < said.index(STEPS[2])

# test_the_flow_hands_off_to_nobody
    assert STEPS[4] in said

# test_the_flow_finishes_with_the_build
    assert said.rindex("build_prompts") > said.index(STEPS[4])

# test_the_flow_runs_five_numbered_steps
    assert "five steps" in said.lower()
    assert "six steps" not in said.lower()
    for step in STEPS:
        assert step in said, step
```

*(`test_the_steps_are_written_in_the_order_they_run` `STEPS`'i olduğu gibi kullanıyor, kendi kodu
değişmiyor — yeni sabitle kırmızıdan yeşile döner.)*

- [ ] **B2 — döngünün beş cümlesi** *(7, 8)*

```python
# test_a_step_ends_when_the_user_approves_it
    assert "a step ends when they approve it" in _flow().lower()

# test_a_delegation_answers_only_the_question_that_was_asked
    said = _flow()
    assert "covers that step only" in said
    assert "as usual" in said

# test_a_delegated_step_still_ends_on_approval
    assert "still wait for the yes" in _flow()

# test_the_plan_records_a_delegation_with_the_step_it_closed
    assert "not permission for the rest" in _flow()

# test_the_closing_message_offers_nothing_and_asks_nothing
    assert "offer nothing, and ask nothing" in _flow()
```

- [ ] **B3 — 1. adım: ilk tur, ve nerede kalındığı** *(10, 11)*

```python
# test_the_opening_moves_belong_to_the_first_turn
    said = _flow()
    assert "the chat's first turn only" in said
    assert "later turns carry on" in said.lower()

# test_the_flow_carries_on_from_a_plan_that_is_already_there
    assert "carry on from where the work stopped" in _flow()

# test_the_flow_reads_a_plan_it_found_rather_than_one_it_just_wrote
    said = _flow()
    assert "if a plan is already there" in said.lower()
    assert "A plan already there is that memory" not in said

# test_no_instruction_reaches_for_the_listing_tool -- son satırı
    assert "first turn" in _flow()
```

**Yeni test** *(11 numaranın kendi iddiası)*:

```python
def test_where_the_work_stopped_is_read_off_the_files():
    # Correction 11. The boxes were the only thing the flow looked at, and a box is filled by a
    # tool nobody is obliged to call -- so a chat that stopped mid-step read its plan as finished.
    # What the work produced is on disk either way, and that is what says how far it got.
    said = _flow()
    assert "the project's files are what say how far it got" in said
    assert "the first step whose box is empty" not in said
```

- [ ] **B4 — 2. adım: ad uydurulmaz** *(17)*

**Yeni test:**

```python
def test_a_character_is_named_as_the_user_named_them():
    # Correction 17. Asked for a name, a model invents one -- and the user's own scenario comes back
    # holding somebody they never named. What the user said is the name; where they said nothing,
    # the name is English for what the person is, so it reads as a description rather than a person.
    said = _flow()
    assert "named as the user named them" in said
    assert "in English for what they are" in said
```

- [ ] **B5 — 4. adım: dil, ve kadronun sorulduğu yer** *(14, 15)*

```python
# test_the_scenes_step_writes_a_readable_list_too
    said = _flow()
    assert "one sentence" in said
    assert "in the language the user is writing in" in said
```

`test_the_scenes_step_writes_the_cast_into_the_frame` → iddia araca taşınır:

```python
def test_the_frames_cast_is_asked_for_by_the_tool_that_writes_one():
    # The frame is born with its cast (Madde 173), so somebody has to ask who is in it. Correction
    # 14: the step used to repeat all three fields -- who, what they wear, where -- and add_scene's
    # own signature already asks for them. Two texts describing one call is the shape every drift in
    # this app has had, so the repetition goes and the signature keeps the claim.
    from backend.features.workspace.domain.prompt import ADD_SCENE_CHARACTERS

    assert "who is in the frame" in ADD_SCENE_CHARACTERS.lower()
    assert "who is in it" not in _flow()
```

---

## Blok C · `test_skills.py` — editör *(1 kırmızı, 2 bekçi)*

- [ ] **C1 — yasak tarife döner** *(24)*

```python
def test_the_editor_changes_the_structure_rather_than_the_prompt_by_hand():
    # Without this the skill loses the only thing that makes it different. Correction 24: it was a
    # prohibition -- do not assemble a prompt by hand -- and a prohibition says what not to do
    # without saying what to do instead. Written as what is true, it carries the rule and answers
    # the next question with it.
    said = _edit()
    assert "the code builds every prompt from the structure file" in said.lower()
    assert "build_prompts" in said
```

- [ ] **C2 — bekçi: kelime tavanı 260** *(20)*

```python
    # The flow's stays where it was through Madde 186, which was the roadmap's own condition -- it
    # gains a step and loses one, so the two cancel. The editor's came down from 300 when building
    # went to the flow, and correction 20 gives 60 back: the step format costs lines, and the text
    # it buys is one a weak model can follow. A cap that moves on the record is not a cap that
    # quietly took the old work back.
    assert len(_flow().split()) <= 450
    assert len(_edit().split()) <= 260
```

- [ ] **C3 — bekçi: her skill ne için yazdığını söyler** *(22)*

```python
@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_says_what_the_prompts_are_for(skill):
    # 29 Aug, the user's own sentence: if we never give the model the context of what we are doing,
    # where would it know it from? Correction 22 shortened the editor's opening paragraph, so what
    # is held here is the fact rather than one wording of it -- both texts still say, in their first
    # two sentences, that these are SDXL prompts and what they are for.
    assert "SDXL" in instruction_for(skill)
```

---

## Blok E · `test_tools.py` — kurallar alanlarına iner *(9 kırmızı)*

34 numara ortak metni böldü: yalnız gerçekten ortak olan altı araçta kaldı, girdiye özgü olan
kendi alanına indi. Testler bakacakları yeri değiştiriyor, iddialarını değil.

- [ ] **E1 — sayı, `solo`, `pov_`, kıyafet: `ADD_CHARACTER_TAGS`**

```python
def test_the_count_lands_in_the_characters_own_entry():
    # Madde 166 inverted the schema's sixth rule: the count used to belong to the frame's people
    # field, and that field is gone. Correction 34 moved the rule out of the shared text and into
    # the field it governs -- it was riding on six tools while ruling on one.
    from backend.features.workspace.domain.prompt import ADD_CHARACTER_TAGS

    said = ADD_CHARACTER_TAGS.lower()
    assert "the count goes here and nowhere else" in said
    assert "1girl" not in said


def test_solo_is_kept_out_of_a_character():
    # The count travels with the person; solo does not. The same character stands alone in one frame
    # and beside somebody in the next, so an entry claiming solo is wrong in half of them.
    from backend.features.workspace.domain.prompt import ADD_CHARACTER_TAGS

    assert "do not write solo" in ADD_CHARACTER_TAGS.lower()


def test_an_entry_for_somebody_half_in_shot_carries_no_count():
    # Madde 182. The count is the sharpest way the leak shows: a POV frame holds one person and the
    # prompt asks for two, because every character entry carries its own count and both are in the
    # cast. The exception is written where the count rule is, or it is a replacement rather than an
    # exception.
    from backend.features.workspace.domain.prompt import ADD_CHARACTER_TAGS

    said = ADD_CHARACTER_TAGS
    assert "pov_" in said
    assert "carries no count" in said.lower()


def test_clothes_are_kept_out_of_a_character():
    from backend.features.workspace.domain.prompt import ADD_CHARACTER_TAGS

    assert "those are outfits" in ADD_CHARACTER_TAGS.lower()
```

- [ ] **E2 — kıyafetin adlandırılması: `ADD_OUTFIT` ve `UPDATE_OUTFIT`** *(16, 34)*

```python
@pytest.mark.parametrize("name", ["ADD_OUTFIT", "UPDATE_OUTFIT"])
def test_an_outfit_is_named_after_the_clothes(name):
    # Correction 16 and 34. Two characters can wear the same outfit, so a name taken from whoever
    # wore it first is a name that lies in the second frame. Written on both tools rather than in
    # the shared rules: it governs a name, and the name is asked for by these two.
    from backend.features.workspace.domain import prompt

    said = getattr(prompt, name).lower()
    assert "name an outfit after the clothes" in said
    assert "not after the person wearing them" in said
```

- [ ] **E3 — mekânda kimse yok: `ADD_LOCATION_TAGS`**

```python
def test_people_are_kept_out_of_a_location():
    from backend.features.workspace.domain.prompt import ADD_LOCATION_TAGS

    said = ADD_LOCATION_TAGS.lower()
    assert "nobody is in it" in said
    assert "it carries no count" in said
```

- [ ] **E4 — örnekler kalkar, kategoriler kalır** *(30, 35)*

```python
def test_the_character_field_says_which_categories_to_write():
    # Correction 30 took the examples out of every text and 35 put the detail back the way the rest
    # of this file carries it: by naming categories. An example is read as the whole of what may be
    # written -- Deneme 4 came back with entries that were the example with two words changed.
    from backend.features.workspace.domain.prompt import ADD_CHARACTER_TAGS

    said = ADD_CHARACTER_TAGS.lower()
    for category in ("age", "body", "hair", "face"):
        assert category in said, category
    assert "long hair, black" not in said
    assert "woman in her mid 20s" not in said


def test_the_place_field_says_which_categories_to_write():
    from backend.features.workspace.domain.prompt import ADD_LOCATION_TAGS

    said = ADD_LOCATION_TAGS.lower()
    assert "indoors" in said
    assert "the light" in said
    assert "bedroom, indoors, curtains" not in said
```

- [ ] **E5 — ortak metnin kendi maddesi** *(34)*

`test_the_rules_split_a_tag_into_the_tags_the_vocabulary_has` → örnek gider, kural kalır:

```python
def test_the_rules_put_one_thing_in_each_tag():
    # Two tags rather than one phrase reading like both: the vocabulary has long hair and it has
    # black hair, and nothing that is the two written together -- so the joined-up version falls
    # outside it exactly as a description does. The example went with correction 30; the rule says
    # the same thing without offering a sentence to copy.
    said = _rules().lower()
    assert "put one thing in each tag" in said
    assert "do not join two tags" in said
    assert "long black hair" not in said
```

- [ ] **E6 — ortak metinden çıkanların yokluğu**

`test_the_rules_keep_people_out_of_a_location` **silinmez**, E3'e taşındığı için adı ve gövdesi
E3'ün testi olur. Yerine ortak metnin ne **taşımadığını** tutan tek satır, `_rules()`'un kendi
testlerinin arasına:

```python
def test_the_rules_carry_nothing_that_belongs_to_one_field():
    # Correction 34's whole point. A rule riding on six tools while ruling on one is read six times
    # per request by five readers it does not concern -- and it sits away from the parameter it
    # governs, which is where a rule is actually applied.
    said = _rules().lower()
    for moved in ("solo", "pov_", "outfit", "location"):
        assert moved not in said, moved
```

---

## Görev · Süit ve kırmızı commit

- [ ] **Arka uç:** `python -m pytest queen-agent -q`

Beklenen: **34 kırmızı**.

| Blok | Kırmızı |
|---|---|
| A · `test_prompt.py` | 5 |
| B · `test_skills.py` — akış | 19 |
| C · `test_skills.py` — editör | 1 |
| E · `test_tools.py` — kurallar ve alanlar | 9 |

D bloğunda kırmızı yok, ve iki bekçi *(C2, C3)* yeşil geçer. Beklenmeyen bir kırmızı çıkarsa
uygulama turuna geçilmez.

- [ ] **Ön uç:** `npm test --prefix queen-agent/frontend` → 648 yeşil.
- [ ] **Commit.**

---

## Kendi kontrolü

- **Her blok bir göreve düşüyor mu?** A → A1–A5; B → B1–B5; C → C1–C3; E → E1–E6. D'nin kırmızısı
  yok, ve bu spec'te yazılı.
- **Yer tutucu var mı?** Yok: her adımın iddiası tam.
- **Silinen test var mı?** Yok. Taşınan var, adı değişen var.
- **Ad tutarlılığı:** `_flow`, `_edit`, `_rules`, `_said_by`, `instruction_for`, `ALL_SKILLS`,
  `STEPS` — hepsi bugünkü adlar. `ADD_SCENE_CHARACTERS`, `ADD_CHARACTER_TAGS`, `ADD_LOCATION_TAGS`,
  `ADD_OUTFIT`, `UPDATE_OUTFIT` — hepsi `prompt.py`'de bugün var.
