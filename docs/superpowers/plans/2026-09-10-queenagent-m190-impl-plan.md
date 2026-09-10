# Madde 190 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-10-queenagent-m190-kod-gecisi-uygulama-design.md](../specs/2026-09-10-queenagent-m190-kod-gecisi-uygulama-design.md)
**Hedef metinler:** [okuma kopyası](../../2026-09-09-queenagent-modele-giden-metinler.md) — §1, §3, §4, §5, §6.
**Gerekçeler:** [düzeltme log'u](../../2026-09-09-queenagent-metin-duzeltmeleri.md), 35 kayıt.
**Test turu:** `1a4cbf3`.

**Amaç:** `prompt.py` okuma kopyasının söylediğini desin, ve test turunun 34 kırmızısı kapansın.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Yürüten:** bu oturum, tek başına.

---

## Bağlayıcı kurallar

- **Metin belgeden kopyalanır, yeniden yazılmaz.** Her cümle kullanıcıyla karara bağlandı; bu turun
  işi onu koda indirmek. Belge ile kod arasında **fark bırakılmaz** — fark bırakmak bu maddenin
  kapatmaya çalıştığı şeydir.
- **Yorumlar kodla birlikte doğrulanır.** CLAUDE.md: *bir yorum NEDEN'i söyler, ve yalnız bugün
  doğru olanı.* 34 numara ortak metinden kural indirdiği için onu anlatan blok yorumu da değişir.
- **Test dosyaları yalnız Görev 0'da açılır**, ve orada yeni iddia yazılmaz.
- Commit mesajında çift tırnak yok; amend yok.

## Değişen dosyalar

| Dosya | Sorumluluğu | Görev |
|---|---|---|
| `queen-agent/backend/tests/test_skills.py` | akış ve editör metninin iddiaları | 0 |
| `queen-agent/backend/features/workspace/domain/prompt.py` | modele giden her metin | 1–6 |
| `queen-agent/backend/features/workspace/domain/tools.py` | üç `tags` alanının teli | 6 |

---

## Görev 0 · Test turunun kaçırdığı üç test *(kırmızı commit)*

**Dosya:** `queen-agent/backend/tests/test_skills.py`

Üçü de bugün kırmızı, ve kod inmeden kırmızı. Yeni iddia yok: biri dizgeyi `STEPS`'e bağlıyor, biri
iddiasını kuralın indiği yere taşıyor, biri karşılaştırmayı düzeltiyor.

- [ ] **0.1 — `pov_` girdisi karakter adımında açılır**

`test_the_flow_opens_a_pov_entry_beside_each_character`, bugün `"2. The characters"` dizgesini elle
tutuyor. `STEPS`'i okuyan yedinci test — altısı test turunda çevrildi, bu geride kaldı.

```python
def test_the_flow_opens_a_pov_entry_beside_each_character():
    # Opened with the character, not when a frame needs one: needing one happens in the middle of a
    # correction turn, which is the worst moment to send the model back to the maps.
    said = _flow()
    assert "pov_" in said
    assert said.index("pov_") > said.index(STEPS[1])
```

*(`STEPS` bu dosyada 359. satırda tanımlı ve modül seviyesinde okunuyor; testin gövdesi çalışırken
sabit hazır.)*

- [ ] **0.2 — sayısız ve kıyafetsiz girdi, artık alanının kuralı**

`test_a_pov_entry_carries_neither_a_count_nor_an_outfit` iddiasını taşır: 34 numara sayıyı ve
kıyafeti `ADD_CHARACTER_TAGS`'e indirdi, 12 numara da akıştan sildi *(akış kuralı değil zamanlamayı
söyler)*. Test bakacağı yeri değiştirir.

```python
def test_a_pov_entry_carries_neither_a_count_nor_an_outfit():
    # Both are the leak. A count makes the picture claim a person it does not show, and an outfit
    # dresses the frame with clothes nobody in it is wearing.
    #
    # Read off the field rather than off the flow: correction 34 moved both rules to the tool that
    # writes an entry, and correction 12 took the copy out of the flow -- a flow says when a thing
    # is written, and the rule for what goes in it belongs beside the parameter.
    from backend.features.workspace.domain.prompt import ADD_CHARACTER_TAGS

    said = ADD_CHARACTER_TAGS.lower()
    assert "no count" in said
    assert "those are outfits" in said
```

- [ ] **0.3 — küçük harfli cümle, küçültülmüş metinde aranır**

`test_where_the_work_stopped_is_read_off_the_files` aradığı cümleyi küçük harfle yazıyor ama
`_flow()`'u küçültmüyor. Hedef metinde cümle *"The project's files…"* diye başlıyor: bu hâliyle test
kod insin ya da inmesin kırmızı kalır.

```python
def test_where_the_work_stopped_is_read_off_the_files():
    # Correction 11. The boxes were the only thing the flow looked at, and a box is filled by a tool
    # nobody is obliged to call -- so a chat that stopped mid-step read its own plan as finished.
    # What the work produced is on disk either way, and that is what says how far it got.
    said = _flow().lower()
    assert "the project's files are what say how far it got" in said
    assert "the first step whose box is empty" not in said
```

- [ ] **0.4 — süit**

```bash
python -m pytest queen-agent -q
```

Beklenen: **36 kırmızı** — test turunun 34'ü, üstüne 0.1 ile 0.2. Üçü değil ikisi, çünkü 0.3 zaten
kırmızı olan bir testi düzeltiyor: karşılaştırma yanlıştı ve cümle de metinde yoktu, yani test
turunun 34'ü içinde sayılı.

- [ ] **0.5 — commit**

```
test(m190): the three the red missed, on the pov_ block and one comparison
```

---

## Görev 1 · Blok A — `SYSTEM_PROMPT`

**Dosya:** `queen-agent/backend/features/workspace/domain/prompt.py:31-70`

İki paragraf değişir: 2. *(okuma ve tazelik)* ve 4. *(değişiklik hangi araçtan geçer)*. Kalan beş
paragraf **birebir** durur — 6. paragrafın `create_file writes it.` cümlesi 207'de indi, orada.

- [ ] **1.1 — 2. paragraf** *(log'da 1, 2, 3, 4)*

```python
    "You are inside one project. It holds files: you can see all of them, and so can every "
    "other chat in it. Their names are listed for you in every request, so nothing has to be "
    "called to find out what exists; when the answer depends on a file, read it first with "
    "read_file. Read only what the answer needs. A read opens a file rather than printing it: "
    "what comes back is a receipt, and the file itself is listed among your opened files, where "
    "it is read from disk again every round -- what stands there is always current. A fresh read "
    "is only for a file that is not among your opened files: one you have never opened, or one "
    "the five have pushed out. Never read a file again to check your own writing or to see "
    "somebody else's change.\n"
```

- [ ] **1.2 — 4. paragraf** *(log'da 5, 6)*

```python
    "What exists is edited, never reborn: a change goes through edit_file, or through the tool "
    "that owns that kind of file, and a new file is for a new thing -- not a second version of "
    "an old one, because two copies of one thing is how the next step reads the wrong one. When "
    "the user asks you to change something that is in a file, make the change in the file.\n"
```

**Kapanan beş test:** `test_a_fresh_read_is_for_a_file_that_is_not_already_open`,
`test_the_base_reads_only_what_the_answer_needs`, `test_the_base_says_where_a_read_file_appears`,
`test_the_base_edits_what_exists_rather_than_rebirthing_it`,
`test_the_base_puts_a_change_on_disk_rather_than_in_the_chat`.

**Bozulmayacaklar:** `test_the_base_names_no_task` yedi kelimeyi arıyor — `scenario`, `frame`,
`character`, `prompt`, `sdxl`, `outfit`, `structure file`; ikisi de hiçbirini taşımıyor.
`test_the_app_forces_no_language_of_its_own` `English` arıyor, yok.

---

## Görev 2 · Blok B — `START_A_SCENARIO`

**Dosya:** `queen-agent/backend/features/workspace/domain/prompt.py:195-236`

Metnin tamamı. §3'ün bloğu, satır satır.

- [ ] **2.1 — metni indir**

```python
START_A_SCENARIO = (
    "You are an expert scenario writer, and everything here serves one end: prompts for an "
    "SDXL-family image model, one frozen frame at a time. You lay the ground and then build the "
    "prompts, in one flow, walking the user through five steps in order, by asking.\n"
    "\n"
    "How a step runs:\n"
    "- Ask, write it into the file, show what you wrote, and wait for their yes. A step ends "
    "when they approve it, never before.\n"
    "- Never write a placeholder, and never stop the flow to wait for a description: ask for "
    "what is missing, and carry on when it is answered.\n"
    '- "You decide" covers that step only. Choose, show it, and still wait for the yes. Ask the '
    'next step\'s question as usual -- one "you decide" is not permission for the rest.\n'
    "- Close an approved step with mark_step_done. It fills that step's box and touches nothing "
    "else.\n"
    "\n"
    "Step 1 -- the plan\n"
    "- Do this on the chat's first turn only. Later turns carry on from where the chat already "
    "is.\n"
    "- If the project holds no plan for this work, write one with create_file: one line per "
    "step, each written as - [ ] 1. and what that step is.\n"
    "- If a plan is already there, read it and carry on from where the work stopped. The "
    "project's files are what say how far it got; the plan's boxes are only a note. If there is "
    "more than one plan, ask which.\n"
    "- This step waits for no approval. Ask Step 2's question in the same turn.\n"
    "\n"
    "Step 2 -- the characters\n"
    "- Ask who is in this scenario, then open the file with start_scenario, once, named after "
    "what is being built: every step after it writes into a file that exists.\n"
    "- Write each character in with add_character, named as the user named them or, where they "
    "did not, in English for what they are.\n"
    "- Write each outfit as one entry with add_outfit the moment it is described: everything "
    "worn in that look, together.\n"
    "- Give each character a pov_ entry as well, again with add_character: what a frame through "
    "their own eyes holds of them.\n"
    "\n"
    "Step 3 -- the places\n"
    "- Ask where this scenario happens, and write each place in with add_location.\n"
    "\n"
    "Step 4 -- the scenes\n"
    "- Ask how many scenes and which moments matter.\n"
    "- Write them with add_scene: one sentence each, in the language the user is writing in.\n"
    "- Write no actions here. A frame is born without one, and the model kept for writing them "
    "fills it in Step 5.\n"
    "\n"
    "Step 5 -- the prompts\n"
    "- Fill the waiting frames with write_missing_actions, then write the list with "
    "build_prompts.\n"
    "- Close by naming the file and saying it is ready. Do not print the prompts back, offer "
    "nothing, and ask nothing: this is the last word."
)
```

**Tırnak notu:** `"You decide"` ile `"you decide"` metnin kendi tırnakları. O iki satır tek tırnaklı
Python dizgesi olarak yazılır *(yukarıdaki gibi)*, kaçış yalnız `step's` için.

**Kapanan on dokuz test:** altı indeks testi *(`STEPS`)*, döngünün beş cümlesi, 1. adımın üç
iddiası, `named as the user named them`, sahne adımının dili, kadronun aracı, ve Görev 0'ın üç
düzeltmesinden ikisi.

- [ ] **2.2 — kelime tavanı, Görev 7'de ölçülür**

Bu metin elle sayınca ~480 kelime, tavan 450. Kesim **ölçüden sonra** yapılır ve kuralı 9 numara
yazdı; sırası Görev 7'de.

---

## Görev 3 · Blok C — `EDIT_PROMPTS`

**Dosya:** `queen-agent/backend/features/workspace/domain/prompt.py:170-193`

- [ ] **3.1 — metni indir**

```python
EDIT_PROMPTS = (
    "You are an expert SDXL prompt writer. The prompts you work on are already written: one per "
    "frame. The user wants something in them changed. The code builds every prompt from the "
    "structure file -- its characters, outfits, locations and frames -- so make your change "
    "there.\n"
    "\n"
    "Step 1 -- what the request is about\n"
    "- Read the scenario file the request names. If more than one could be it, ask which.\n"
    "- Find what the user means: the frames, the person, the place or the outfit they are "
    "unhappy with. If nothing matches, say so; where something close is there, ask whether that "
    "is the one.\n"
    "\n"
    "Step 2 -- the fix\n"
    "- A frame's action reads wrong, or wants writing afresh from its scene: write it yourself "
    "with update_frame.\n"
    "- Somebody looks wrong, or a place does, wherever they appear: change their entry with "
    "update_character, update_outfit or update_location -- one change reaches every frame "
    "naming it.\n"
    "- Who is in a frame, what they wear, or where it happens: update_frame, once for each frame "
    "the request reaches.\n"
    "- A frame seen through somebody's own eyes names their pov_ entry instead of them, because "
    "their whole entry would be drawn onto whoever the picture holds.\n"
    "\n"
    "Step 3 -- the answer\n"
    "- Call build_prompts again: the prompt file is rebuilt rather than patched.\n"
    "- Say what you changed and which frames it reached. The built file is the answer: its "
    "prompts are never printed back."
)
```

**Kapanan test:** `test_the_editor_changes_the_structure_rather_than_the_prompt_by_hand` —
*"the code builds every prompt from the structure file"* artık metinde.

**Bekçiler yeşil kalır:** metin elle sayınca ~247 kelime, tavan 260 *(20 numara)*. Açılış hâlâ
`You are an expert SDXL prompt writer` ile başlıyor ve `SDXL` taşıyor.

---

## Görev 4 · Blok D — `WRITE_FRAME_SYSTEM_PROMPT`

**Dosya:** `queen-agent/backend/features/workspace/domain/prompt.py:294-320`

Bu blokta **kırmızı yok**: 33 numara metnin tamamını yeniden yazdı ve testlerin tuttuğu her dizgeyi
korudu. İş, metni sözleşmeye uydurmak.

- [ ] **4.1 — metni indir**

```python
WRITE_FRAME_SYSTEM_PROMPT = (
    "You write the action line for one frozen frame. An SDXL-family image model draws it. You "
    "are given three things: the scene in one sentence, who is in the frame, and where it "
    "happens.\n"
    "\n"
    "- Output the action line and nothing else. Your whole answer is written into the frame "
    "exactly as you send it, so a preamble, a quotation mark, or a comment about having written "
    "it ends up inside the image prompt.\n"
    "- Write one single moment. The model draws one picture, so a line that moves through "
    "several moments cannot be drawn at all.\n"
    "- Choose the shot yourself. There is no camera field, so write the framing and angle into "
    "your line, as tags, the same way you write everything else.\n"
    "- Write what the body is doing in this instant, and the expression on the face. You are the "
    "only one who writes these two: nothing else in the prompt says what this person is doing or "
    "feeling in this frame.\n"
    "- Name what is visible of them directly: erect penis, penis penetrating vagina, mouth on "
    "penis. Never use a euphemism. The model draws what you name and invents what you leave "
    "out, and that is how a frame comes back with a melted body.\n"
    "- Do not describe how anybody looks, what they wear, or what the place looks like. Other "
    "text already puts all three into the prompt. A second description here contradicts the "
    "first.\n"
    "- Do not write that anybody is naked. Clothes are decided elsewhere: someone with no outfit "
    "is already bare, so you never have to say it.\n"
    "- Use what you are shown only to make your line fit it. If somebody wears a long coat, do "
    "not write that they take it off.\n"
    "\n" + SDXL_PROMPT_RULES
)
```

**Yerinde kalan dizgeler** *(dokuz test)*: `framing and angle`, `action`, `camera`,
`name what is visible`, `penis`, `vagina`, `euphemism`, `expression`, `already bare`,
`do not describe` + `clothes`.

**Docstring'e dokunulmaz:** altındaki üç paragraf bugün de doğru — 172'nin böldüğü ikinci yarı,
ve `SYSTEM_PROMPT`'un neden dışarıda kaldığı.

---

## Görev 5 · Blok E — `SDXL_PROMPT_RULES`

**Dosya:** `queen-agent/backend/features/workspace/domain/prompt.py:239-292`

- [ ] **5.1 — metni indir**

```python
SDXL_PROMPT_RULES = (
    "An SDXL-family image model reads these tags, and it was trained on Danbooru's own tags.\n"
    "\n"
    "- Write tags, never sentences. An article is not a tag either.\n"
    "- Use a tag that the Danbooru vocabulary already has, rather than a description of the same "
    "thing. The model has seen a real tag many times, and has never seen a paraphrase of it.\n"
    "- Write the tags in English, with spaces where the site writes underscores.\n"
    "- Put one thing in each tag, split the way the vocabulary splits it. Do not join two tags "
    "into one longer phrase.\n"
    "- When the vocabulary has no tag for it, write a few plain words in the same short form.\n"
    "- Never write quality tags. The code already puts them at the front of every prompt, so "
    "yours would be printed twice.\n"
    "- Never write the word or inside a tag. The model draws one picture and cannot toss a coin "
    "between two choices, so pick one and write only that."
)
```

- [ ] **5.2 — blok yorumunun iki cümlesi** *(`prompt.py:256-265`)*

Yorum bugün *"what goes into a map entry is Queen's and is written here"* diyor. 34 numaradan sonra
bu yarım doğru: **ortak** olan burada, girdiye özgü olan alanına indi. Yorumun o parçası şöyle olur:

```python
# The other half split again, by author. What goes into a map entry is Queen's and is written here;
# what goes into a frame's action is the prompt writer's, and lives in WRITE_FRAME_SYSTEM_PROMPT.
# Carried together they would ride on six tools that never write an action.
#
# Correction 34 split this half once more, by reader. What is left here is what all six tools share;
# a rule that ruled on one field -- the count, solo, a pov_ entry, naming an outfit, nobody in a
# location -- went down to that field's own description, where it is read while the value is being
# written rather than five times over by tools it does not concern.
```

Ve maliyet cümlesi *(bugün "six copies is roughly a thousand tokens on every request")* metin
küçüldüğü için ölçüsünü kaybetti; kalan cümle sayı vermez:

```python
# Not in SYSTEM_PROMPT, where every chat would carry it including the ones writing no tags -- Madde
# 94 pruned the skill texts for exactly that. Its cost is paid all the same, because a tool's
# description travels every turn as well: six copies of it ride in every request. What is bought is
# where the attention falls -- the rule sits beside the parameter it governs and is read while the
# tool is being chosen -- and a round, since nothing is fetched.
```

**Kapanan test:** `test_the_rules_put_one_thing_in_each_tag`, ve
`test_the_rules_carry_nothing_that_belongs_to_one_field` *(`solo`, `pov_`, `outfit`, `location`
artık ortak metinde yok)*.

**Bozulmayacaklar:** `danbooru`, `rather than a description`, `underscores`, `no tag for it`,
`quality` + `twice`, ` or ` + `coin`, `tags` + `sentence` + `article`; ve `action` ile `camera`
**yokluğu**.

---

## Görev 6 · Blok F — 18 araç tarifi

**Dosyalar:** `queen-agent/backend/features/workspace/domain/prompt.py:355-585`,
`queen-agent/backend/features/workspace/domain/tools.py:172,220,268`

35 numaranın sözleşmesi: emir başa, sebep arkaya ayrı cümle, bir madde bir kural, örnek yok, ret
cümlesi kendi maddesine. Tarifler madde madde; **parametre metinleri düz kalır**.

- [ ] **6.1 — ortak kuyruk ve üç yeni sabit**

```python
AN_ENTRYS_NEW_TAGS = (
    "Give the whole entry as it should now read: this replaces the text rather than adding to it. "
    "Leave it out to change only the name."
)
"""The tail every update_ tool's tags field ends with (Madde 189, rewritten by correction 35).

Not a field's whole description since correction 34: each of the three now carries its own map's
categories first and this sentence last. Written once because it is the same sentence in all three
-- and because the broken half of it, a phrase with no verb hanging off the end of the categories,
is what 35 was written to fix.
"""
```

Üç birleşim, her birinin `ADD_*_TAGS`'inden hemen sonra:

```python
UPDATE_CHARACTER_TAGS = f"{ADD_CHARACTER_TAGS} {AN_ENTRYS_NEW_TAGS}"
UPDATE_OUTFIT_TAGS = f"{ADD_OUTFIT_TAGS} {AN_ENTRYS_NEW_TAGS}"
UPDATE_LOCATION_TAGS = f"{ADD_LOCATION_TAGS} {AN_ENTRYS_NEW_TAGS}"
```

`tools.py`'de üç satır bunları gösterir:

```python
"tags": {"type": "string", "description": prompt.UPDATE_CHARACTER_TAGS},
"tags": {"type": "string", "description": prompt.UPDATE_OUTFIT_TAGS},
"tags": {"type": "string", "description": prompt.UPDATE_LOCATION_TAGS},
```

Birleştirme çağrı yerinde yapılamaz: `test_every_text_a_tool_carries_comes_from_the_prompt_module`
bir aracın taşıdığı her dizgenin `prompt.py`'de büyük harfli bir adla **yazılı** olmasını istiyor.

- [ ] **6.2 — dosya ve doküman araçları**

```python
READ_FILE = "Read one of this project's files."

CREATE_FILE = (
    "Save a document into this project.\n"
    "- Call this only when the user asked for something worth keeping: a draft, a report, a "
    "summary they will come back to.\n"
    "- To change a file that already exists, use edit_file. This tool refuses a name that is "
    "already taken.\n"
    "- This tool does not write scenarios. start_scenario opens those."
)
CREATE_FILE_NAME = "A short file name, as in notes.md."
CREATE_FILE_CONTENT = "The document itself."

START_SCENARIO = (
    "Open a new scenario: the structure file that prompts are built from.\n"
    "- The file is born empty: no characters, no outfits, no locations, no frames. The tools "
    "that add each of those are what fill it.\n"
    "- Give a name and nothing else. The shape belongs to the code, and the file is always "
    ".json.\n"
    "- This tool refuses a name that is already taken. A scenario is opened once and added to, "
    "never started a second time."
)
START_SCENARIO_NAME = "What the scenario is called, as in bar-scene."

EDIT_FILE = (
    "Change part of a document that already exists.\n"
    "- This is for documents, not scenarios. A structure file is changed by the tools that know "
    "its shape.\n"
    "- The text you give as old must appear exactly once, and must match what is on disk now, "
    "without the line numbers a read shows it with.\n"
    "- Read the file first if this turn has not seen it. What this turn read or wrote is already "
    "in front of you.\n"
    "- Include enough of the surrounding text to be sure you have the right place.\n"
    "- Pass replace_all when you mean every occurrence rather than one, instead of growing the "
    "text. Renaming an entry through all the frames that name it is the usual case."
)
EDIT_FILE_OLD = "The exact text to replace."
EDIT_FILE_NEW = "What takes its place. Empty takes the text out."
EDIT_FILE_REPLACE_ALL = (
    "Change every occurrence. Left out, text that appears more than once "
    "is refused rather than guessed at."
)
```

**Tutulan dizgeler:** `start_scenario opens those`, `structure file`,
`if this turn has not seen it`, `already in front of you`, `without the line numbers`,
`replace_all`; ve `.json`'ın `CREATE_FILE_NAME`'de **olmaması**.

- [ ] **6.3 — karakter**

```python
ADD_CHARACTER = (
    "Write a new character into a scenario: the tags an image model draws them from.\n"
    "- The entry is written once here, and every frame that holds this character names it.\n"
    "- This tool refuses a name that is already there. To change a character that exists, use "
    "update_character.\n"
    "\n" + SDXL_PROMPT_RULES
)
ADD_CHARACTER_NAME = (
    "What this character is called in this scenario, as in young man. Frames name them by it."
)
ADD_CHARACTER_TAGS = (
    "Write the character as tags: how many people this entry draws, their age, body, hair and "
    "face. The count goes here and nowhere else, because this is the one place a count sits next "
    "to the person it counts. Do not write solo: the same character stands alone in one frame "
    "and next to somebody in the next, so an entry claiming solo is wrong in half of them. A "
    "pov_ entry shows only hands and arms and no face, so it carries no count at all. Do not "
    "write clothes here -- those are outfits."
)

UPDATE_CHARACTER = (
    "Change a character that is already in a scenario: its tags, its name, or both.\n"
    "- Only what you give changes.\n"
    "- Renaming reaches every frame that names this character, so the scenario still builds "
    "afterwards.\n"
    "- This tool refuses a name that is not there.\n"
    "\n" + SDXL_PROMPT_RULES
)
UPDATE_CHARACTER_NAME = "Which character to change."

REMOVE_CHARACTER = (
    "Take a character out of a scenario.\n"
    "- This tool refuses while any frame still names the character, and the answer says which "
    "frames. Take the character out of those frames first, or remove the frames.\n"
    "- Nothing here can be undone by calling it again."
)
REMOVE_CHARACTER_NAME = "Which character to remove."
```

**Kapanan altı test:** `the count goes here and nowhere else` + `1girl` yokluğu, `do not write solo`,
`pov_` + `carries no count`, `those are outfits`, dört kategori + iki örneğin yokluğu, ve Görev
0.2'nin taşıdığı iddia.

- [ ] **6.4 — kıyafet**

```python
ADD_OUTFIT = (
    "Write a new outfit into a scenario: a set of clothes with a name, worn by whoever a frame "
    "puts it on.\n"
    "- An outfit is kept apart from the character because the same person wears different things "
    "across the frames, and the same clothes can be worn by more than one person.\n"
    "- Name an outfit after the clothes, not after the person wearing them, because two "
    "characters can wear the same outfit.\n"
    "- This tool refuses a name that is already there.\n"
    "\n" + SDXL_PROMPT_RULES
)
ADD_OUTFIT_NAME = "What this outfit is called, as in nightgown."
ADD_OUTFIT_TAGS = (
    "Write the clothes as tags and nothing else: the garments, their colour, their material, and "
    "what they leave bare. Do not write a person here: no count, no body, no hair. One entry "
    "dresses one person. Its text is handed whole to whoever wears it, so an entry covering two "
    "people would put the man in the dress."
)

UPDATE_OUTFIT = (
    "Change an outfit that is already in a scenario: its tags, its name, or both.\n"
    "- Only what you give changes.\n"
    "- Renaming reaches every frame wearing this outfit.\n"
    "- Name an outfit after the clothes, not after the person wearing them, because two "
    "characters can wear the same outfit.\n"
    "- This tool refuses a name that is not there.\n"
    "\n" + SDXL_PROMPT_RULES
)
UPDATE_OUTFIT_NAME = "Which outfit to change."

REMOVE_OUTFIT = (
    "Take an outfit out of a scenario.\n"
    "- This tool refuses while any frame still has somebody wearing the outfit, and the answer "
    "says which frames. Change what those frames wear first, or remove them."
)
REMOVE_OUTFIT_NAME = "Which outfit to remove."
```

**Kapanan test:** `test_an_outfit_is_named_after_the_clothes`, iki araçta birden —
`name an outfit after the clothes` ve `not after the person wearing them`.

- [ ] **6.5 — mekân**

```python
ADD_LOCATION = (
    "Write a new location into a scenario: a place a frame can be set in.\n"
    "- This tool refuses a name that is already there.\n"
    "\n" + SDXL_PROMPT_RULES
)
ADD_LOCATION_NAME = "What this place is called, as in bedroom."
ADD_LOCATION_TAGS = (
    "Write the place as tags: what kind of place it is, whether it is indoors or out, what "
    "stands in it, and the light. Nobody is in it and it carries no count. Who is in the frame "
    "is decided elsewhere, and a person written here would be drawn into every frame set in this "
    "place."
)

UPDATE_LOCATION = (
    "Change a location that is already in a scenario: its tags, its name, or both.\n"
    "- Only what you give changes.\n"
    "- Renaming reaches every frame set in this place.\n"
    "- This tool refuses a name that is not there.\n"
    "\n" + SDXL_PROMPT_RULES
)
UPDATE_LOCATION_NAME = "Which location to change."

REMOVE_LOCATION = (
    "Take a location out of a scenario.\n"
    "- This tool refuses while any frame is still set there, and the answer says which frames. A "
    "frame has one place, so give those frames another one first, or remove them."
)
REMOVE_LOCATION_NAME = "Which location to remove."
```

**Kapanan iki test:** `nobody is in it` + `it carries no count`, ve `indoors` + `the light` +
örneğin yokluğu.

- [ ] **6.6 — sahne ve kare**

```python
ADD_SCENE = (
    "Add scenes to a structure file, one frame each, in the order they happen.\n"
    "- The frames go at the end, unless before names a frame to go in front of.\n"
    "- A frame's number is not yours to give. It is the frame's place in the list, and every "
    "frame after an insertion moves up.\n"
    "- Every name a scene uses must already be in the file. A name nobody knows is refused, and "
    "the whole call is refused with it: nothing is written unless every scene in the call is "
    "good.\n"
    "- The answer names the frames it made, which is how you say which frame you mean next.\n"
    "- A frame is born without its action. write_missing_actions writes every frame that is "
    "still without one."
)
ADD_SCENE_BEFORE = (
    "Go in front of this frame, by its number, rather than at the end. The "
    "frames from there on move up and keep everything they carry, their "
    "actions included. This is how a scene goes into the middle of a "
    "scenario; taking the tail out and adding it again is not. One past the "
    "last frame means the end."
)
ADD_SCENE_SCENES = "The scenes to add. A list even when there is one of them."
ADD_SCENE_SCENE = (
    "What happens, in one sentence and in the language the "
    "work is being done in. The brief this frame is built "
    "from, never the tags themselves."
)
ADD_SCENE_CHARACTERS = (
    "Who is in the frame: each name from the file's "
    "characters, with the list of outfits they wear. Whoever "
    "is written first leads the frame's prompt. Left out for a "
    "frame with nobody in it."
)
ADD_SCENE_LOCATION = (
    "Where it happens, named as the file's locations name it. "
    "Left out for a frame that shows no place of its own."
)

UPDATE_FRAME = (
    "Change a frame that is already in a structure file, naming it by its number.\n"
    "- Only what you give is changed. The rest of the frame stays as it is, so correcting a "
    "place leaves the cast alone.\n"
    "- Giving a field empty clears it: a frame with nobody in it, or one that shows no place of "
    "its own. The scene is the exception, because a frame is never without one.\n"
    "- Names come from the file here as they do when the frame is written.\n"
    "- The action is among these fields. A line that reads wrong is corrected here, in your own "
    "words."
)

REMOVE_FRAME = (
    "Take one frame out of a structure file, naming it by its number.\n"
    "- Every frame after it moves up a place and the numbers follow, so the answer says how many "
    "are left. A number you were told before this call may not mean the same frame after it.\n"
    "- Nothing else is touched. A character or a place left in no frame at all stays where it "
    "is, and taking it out is the user's to ask for."
)
```

`UPDATE_FRAME_SCENE`, `UPDATE_FRAME_CHARACTERS`, `UPDATE_FRAME_LOCATION` ve `UPDATE_FRAME_ACTION`
**değişmiyor** — §6 onları bugünkü hâliyle yazıyor.

**Tutulan dizgeler:** `before`, `write_missing_actions` *(add_scene'de)*, `action` +
`is not among these` yokluğu *(update_frame)*, ve `write_missing_actions`'ın `update_frame`'de
**olmaması**.

- [ ] **6.7 — kalan iki araç**

```python
WRITE_MISSING_ACTIONS = (
    "Write the action of every frame in a structure file that is still without one, in one "
    "call.\n"
    "- Each frame is asked of a model kept for writing those and nothing else, at the same time "
    "as the others, and each is shown only its own scene, cast and place.\n"
    "- Frames that already have an action are left exactly as they are. A line that is there is "
    "changed with update_frame, in your own words.\n"
    "- There is no range and nothing to say twice: what is waiting is what is empty.\n"
    "- One request failing does not undo the rest. The answer names the frames it wrote and, for "
    "any it could not, says why."
)

BUILD_PROMPTS = (
    "Build the prompt list from a structure file.\n"
    "- The code assembles every frame in a fixed order, so a character reads the same in all of "
    "them.\n"
    "- This tool writes a Python file named after the structure, replacing what it wrote last "
    "time."
)
```

`MARK_STEP_DONE` ile iki parametresi **elden geçmez** *(203 aracı kaldırıyor)*.

**Tutulan dizgeler:** `update_frame` + `write_frame_prompt` yokluğu, ve `build_prompts`'ta `frame`
var / `shot` yok.

---

## Görev 7 · Süit, kelime tavanı, yeşil commit

- [ ] **7.1 — arka uç**

```bash
python -m pytest queen-agent -q
```

- [ ] **7.2 — akış tavanı kırmızıysa: 9 numaranın kuralı**

`test_the_texts_stay_short_enough_to_be_read` kırmızı verirse **tavan yükselmez**; iki yerde aynı
şeyi söyleyen cümleler sırayla silinir, ve süit tekrar koşulur:

1. **1. adım, 3. madde:** `If there is more than one plan, ask which.` *(8 kelime; 10 numaranın
   kendi nominasyonu — taban metin zaten "iki okuması olan şeyi sor" diyor.)*
2. **4. adım, 3. madde:** `A frame is born without one, and the model kept for writing them fills
   it in Step 5.` *(16 kelime; `ADD_SCENE`'in tarifi aynısını söylüyor ve o metin her istekte
   gidiyor. `Write no actions here.` durur — `test_the_flow_never_writes_an_action_by_hand` onu
   tutuyor.)*
3. **2. adım, 1. madde:** `: every step after it writes into a file that exists` *(9 kelime;
   `START_SCENARIO` "opened once and added to, never started a second time" diyor. `once` durur.)*

11 numaranın nominasyonu **uygulanmaz**: `Later turns carry on from where the chat already is.`
cümlesi `test_the_opening_moves_belong_to_the_first_turn`'ün tuttuğu dizge, ve Madde 107'nin dersi
başka hiçbir metinde yazmıyor — iki yerde söylenen bir cümle değil.

- [ ] **7.3 — kesim olduysa belge ve log**

Kod ile okuma kopyası arasında fark bırakılmaz:

- `docs/2026-09-09-queenagent-modele-giden-metinler.md` §3 — akış metni kesilmiş hâliyle.
- `docs/2026-09-09-queenagent-metin-duzeltmeleri.md` — **36** numaralı kayıt: ölçü, 9 numaranın
  kuralı, hangi cümleler neden düştü, ve her birinin nerede duruyor olduğu.

- [ ] **7.4 — ön uç**

```bash
npm test --prefix queen-agent/frontend
```

Beklenen: 648 yeşil. Bu madde ön uca dokunmuyor; kırmızı çıkarsa sebebi başka yerde.

- [ ] **7.5 — commit**

```
feat(m190): the code says what the reading decided
```

---

## Kendi kontrolü

- **Spec'in her maddesi bir göreve düşüyor mu?** Altı blok → 1–6; üç test düzeltmesi → 0; üç yeni
  sabit ve `tools.py` teli → 6.1; kelime tavanı → 7.2; belge kapanışı → 7.3.
- **Yer tutucu var mı?** Yok: her görev inecek metnin tamamını taşıyor.
- **Ad tutarlılığı:** `UPDATE_CHARACTER_TAGS`, `UPDATE_OUTFIT_TAGS`, `UPDATE_LOCATION_TAGS` 6.1'de
  tanımlanıyor ve yalnız `tools.py`'nin üç satırında kullanılıyor. `ADD_CHARACTER_TAGS`,
  `ADD_OUTFIT_TAGS`, `ADD_LOCATION_TAGS` 6.3–6.5'te, birleşimlerden **önce** yazılı olmalı: üçü de
  kendi `update_` sabitinin üstünde durur.
- **`SDXL_PROMPT_RULES` sırası:** Görev 5 onu Görev 6'nın altı aracından önce tanımlar; dosyadaki
  yeri değişmiyor, yalnız içeriği.
- **Kaçırılan test var mı?** Görev 0 üçünü kapatıyor. Kalanı süit söyler; beklenmeyen bir kırmızı
  çıkarsa commit atılmaz.
