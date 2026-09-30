# Madde 391 — Senaryonun geliştirilmesi · test turu planı

> **30 Eylül güncellemesi.** Bu plan ilk taslağın testlerini yazdı; kullanıcı metni değiştirince testler
> de değişti. Değişenler [test spec'inin](../specs/2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-testler-design.md)
> başında, bugünkü testler `test_skills.py`'de.

> **Ajanlar için:** bu plan satır satır, bu oturumda yürütülür (superpowers:executing-plans'ın
> biçimiyle); adımlar `- [ ]` kutularıyla.

**Amaç:** Start a scenario'nun 5. adımdan sonra gelen üç kontrol adımını — tek an, görünen parçalar,
çizilebilir mi —, onay beklememelerini ve kapanışın 8. adıma taşınmasını tutan testleri yazmak, ve
bugünkü metinde kırmızı olduklarını görmek.

**Yapı:** Yalnız `test_skills.py` değişir. `STEPS` sekiz başlık olur; bir adımın dilimini okuyan
`_step(number)` yardımcısı yeni testlerin ortak zemini. Metne (`prompt.py`) bu turda dokunulmaz.

**Araçlar:** pytest.

**Spec:** [2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-testler-design.md](../specs/2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-testler-design.md)

## Genel kısıtlar

- Dört test satırı, yazıldığı gibi, paralel: `python -m pytest queen-agent -q` ·
  `npm test --prefix queen-agent/frontend` · `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend`. Borulanmaz, süzülmez, daraltılmaz.
- `skip`, `xfail`, `.skip`, `.todo` yok.
- **Commit yok:** kullanıcı değişikliği Changes'ten okur; onaydan sonra commit'lenir.
- Test adları ve yorumları İngilizce; yorum neden'i ve yalnız bugün doğru olanı söyler.

---

### Görev 1: Testler

**Dosya:**
- Değişir: `queen-agent/backend/tests/test_skills.py`

**Arayüz:**
- Üretir: `STEPS` (sekiz başlık), `_step(number) -> str` (1'den sayan adım numarası; başlıktan sonraki
  başlığa ya da metnin sonuna), `CLOSING` (kapanışın iki cümlesi).

- [ ] **Adım 1: `test_the_flow_never_writes_an_action_by_hand`'i yeniden adlandır**

İddialar aynı kalır; ad ve yorum 8. adımın bir aksiyonu kendisi sadeleştirmesini karşılar:

```python
def test_the_flow_writes_no_new_action_by_hand():
    # It writes the frames, which it never did before Madde 173 -- but not their sentences. That
    # is the whole reason this run has two models, and a flow writing one itself would be the way
    # round the model kept for writing them.
    #
    # Madde 391's last step does change an action in its own words, and that is not the way round:
    # the line is already written, the flow has read it in the built prompt, and what it writes is
    # the same line made simpler -- Madde 201's reason for the editor. A frame whose scene changes
    # is emptied instead, and goes back to the model kept for writing it.
    said = _flow()
    assert "no action" in said
    assert "write_missing_actions" in said
```

- [ ] **Adım 2: `STEPS` sekiz başlık, docstring'i ve adım sayısı testi**

```python
STEPS = (
    "Step 1 -- the plan",
    "Step 2 -- the characters",
    "Step 3 -- the places",
    "Step 4 -- the scenes",
    "Step 5 -- the prompts",
    "Step 6 -- one moment",
    "Step 7 -- visible parts",
    "Step 8 -- can it be drawn",
)
"""The flow's steps, in the order they run (Madde 198, written this way by correction 9).

Read by the tests below and by the ones that place create_file, start_scenario and the build.
Madde 186 had six of these and the first was the context; that question is gone, and the numbers
moved with it. Numbered headings became named ones so that every step reads the same way -- a
heading, then its rules as lines -- and so the loop above them is not read as one more step. Madde
391 adds the last three: the checks the flow runs on the prompts it has just built.
"""


def test_the_flow_runs_eight_numbered_steps():
    # Madde 108: a stage outside the numbered list is a stage a weak model walks past, because it
    # stops when the list ends. Five since Madde 198 -- the context question in front of them was
    # the one thing a user had to answer before any work could start -- and eight since Madde 391,
    # whose checks follow the build.
    said = _flow().lower()
    assert "eight steps" in said
    assert "five steps" not in said
    for step in STEPS:
        assert step.lower() in said, step
```

- [ ] **Adım 3: Madde 391'in bölümü** — `test_the_closing_message_offers_nothing_and_asks_nothing`'in
  hemen arkasına:

```python
# --- the checks the flow ends with (Madde 391) ----------------------------------------------------
#
# 30 September, the owner: the questions they used to put to the model by hand once the prompts were
# built -- does a frame hold one moment, does its prompt name only what the angle shows, can the
# image model draw it -- are the flow's own last three steps. Each is written in its own step of
# Start a scenario's text: the first try kept them in a block several skills shared, and the owner
# took it back. None waits for a yes (the owner: update directly, and just say what changed).

CLOSING = (
    "Close by naming the file and saying it is ready. Do not print the prompts back, offer "
    "nothing, and ask nothing: this is the last word."
)


def _step(number):
    """One step of the flow by its own number: from its heading to the next one, or to the end."""
    said = _flow()
    start = said.index(STEPS[number - 1])
    if number == len(STEPS):
        return said[start:]
    return said[start : said.index(STEPS[number])]


def test_a_frame_telling_more_than_one_moment_is_brought_down_or_split():
    # The owner's fourth question. A frame is one picture, and a scene or action holding two moments
    # is a picture the model has to choose between.
    said = _step(6)
    assert "more than one moment" in said
    assert "split" in said
    assert "one frame per moment" in said


def test_a_changed_frame_gets_its_action_written_again():
    # A frame whose scene changed but whose action stayed would build into the old picture, and a
    # frame split off is born with no action at all. Emptied, both go to write_missing_actions, which
    # already writes whatever is waiting.
    said = _step(6)
    assert "update_frame" in said
    assert "empty action" in said
    assert "add_scene" in said
    assert said.index("update_frame") < said.index("write_missing_actions")
    assert said.index("add_scene") < said.index("write_missing_actions")


def test_a_part_the_angle_hides_stays_out_of_the_frames_prompt():
    # The owner's second question: a weak model draws what it is given, and a part it cannot place
    # on the one who owns it goes onto somebody else.
    said = _step(7)
    assert "camera angle" in said
    assert "draws it anyway" in said
    assert "somebody else" in said


def test_what_the_angle_shows_is_an_entry_of_its_own():
    # The owner's chosen way. A frame names whole entries and build_prompts writes each one whole, so
    # "only this much of them here" can only be another entry. The whole one is left alone: the other
    # frames still show that person whole.
    said = _step(7)
    for tool in ("add_character", "add_outfit", "update_frame"):
        assert tool in said, tool
    assert "man body no face" in said
    assert "dress from behind" in said
    assert "already there" in said
    assert "in place of the whole one" in said
    assert "leaves that frame's cast" in said
    assert "whole entries stay as they are" in said
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "update_character" not in said
    assert "update_outfit" not in said


def test_the_last_check_asks_the_owners_question_of_the_built_prompts():
    # The owner's first question, asked as they ask it: of the prompts as build_prompts wrote them,
    # since what the model is handed is the parts joined, and too much often shows only in the sum.
    said = _step(8)
    assert "build_prompts wrote" in said
    assert "very weak" in said
    assert "as it is written?" in said


def test_what_cannot_be_drawn_is_simplified_where_it_comes_from():
    # The prompt file is rebuilt rather than patched, so a part is made simpler in the frame's action
    # or in the entry it comes from, and the frame keeps its moment.
    said = _step(8)
    assert "simplify it where it comes from" in said
    assert "keep the moment" in said
    for tool in ("update_frame", "update_character", "update_outfit", "update_location"):
        assert tool in said, tool


def test_no_instruction_says_what_the_model_cannot_draw():
    # The owner, 30 September: told it cannot draw anything complex, the model really does go and
    # ask for only the simplest things. The last check asks the owner's question instead of making
    # the claim.
    assert "very weak" in _step(8)
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    for skill, said in INSTRUCTIONS.items():
        said = said.lower()
        assert "complex" not in said, skill
        assert "what is simple" not in said, skill
        assert "cannot draw" not in said, skill


@pytest.mark.parametrize("number", [6, 7, 8])
def test_every_check_rebuilds_and_says_what_it_changed(number):
    # The owner: I want to see what was done. The list is rebuilt after a change so the file matches
    # the structure, and a check that found nothing says so, since silence reads the same as never
    # having looked.
    said = _step(number)
    assert "build_prompts again if you changed anything" in said
    assert "which frames you changed and what" in said
    assert "say so in a line" in said


@pytest.mark.parametrize("number", [5, 6, 7, 8])
def test_the_build_and_the_checks_wait_for_no_approval(number):
    # How a step runs says every step waits for a yes, and Step 1 already says it does not. These
    # four say it the same way, and each goes on in the same turn -- the owner: update directly.
    said = _step(number)
    assert "This step waits for no approval." in said
    if number < len(STEPS):
        assert f"Go on to Step {number + 1} in the same turn." in said


def test_the_closing_word_comes_at_the_end_of_the_last_check():
    # Moved from the build, unchanged: the build is no longer the end, and a closing left there would
    # be the last word said before three steps still to come.
    said = _flow()
    assert said.endswith(CLOSING)
    assert CLOSING in _step(8)
    assert said.count("last word") == 1


def test_the_checks_are_written_in_the_flow_itself():
    # The owner, 30 September: no separate fields. A line of these steps found in another of the
    # module's texts is a line kept somewhere else and joined in -- the shape that was taken back.
    from backend.features.workspace.domain import prompt

    lines = [line for number in (6, 7, 8) for line in _step(number).splitlines() if line]
    assert lines
    for name, value in vars(prompt).items():
        if isinstance(value, str) and name != "START_A_SCENARIO":
            for line in lines:
                assert line not in value, (name, line)
```

- [ ] **Adım 4: Kelime tavanı 450'den 800'e, gerekçesi yorumda**

`test_the_texts_stay_short_enough_to_be_read`'in yorumuna, Correction 20'nin paragrafından sonra:

```python
    # Madde 391 raises the flow's to 800, on the owner's decision of 28 September that the cap rises
    # only in a written one. The questions the owner used to ask by hand once the prompts were built
    # are three steps after the build now, and each says the whole of itself -- what it fixes, that it
    # rebuilds and says what changed, that it waits for no yes -- since the owner wants them in the
    # flow's own text rather than in a block the steps would share.
    assert len(_flow().split()) <= 800
```

- [ ] **Adım 5: Dört satırı paralel koş, kırmızıyı gör**

`npm test --prefix queen-agent/frontend` arka planda; özeti kendi çıktı dosyasından okunur.

Beklenen: `python -m pytest queen-agent -q`'da tam 18 test kırmızı — `test_the_flow_runs_eight_numbered_steps`,
`test_the_steps_are_written_in_the_order_they_run`, Adım 3'ün 16'sı (parametreliler dahil) —, geri
kalanı yeşil. Öteki üç süit yeşil. `test_the_flow_writes_no_new_action_by_hand` ve kelime tavanı yeşil.

- [ ] **Adım 6: Commit yok.** Değişiklik çalışma ağacında kalır; uygulama turu buradan sürer.
