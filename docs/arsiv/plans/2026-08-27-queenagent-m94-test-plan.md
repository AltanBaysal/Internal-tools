# Madde 94 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m94-tek-skill-testler-design.md](../specs/2026-08-27-queenagent-m94-tek-skill-testler-design.md)
**Bu turda kod yazılmaz.** Sekiz test kırmızıya döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Bu turun biçimi: test dosyası son hâli tarif eder

Silinen beş metnin testleri **bu turda** gidiyor, kırmızılarla birlikte. Sebebi: bir testin konusu
yoksa test de yoktur, ve tur 1'in işi kodun ne olacağını yazmaktır. Tur 2 yalnız kodu siler.

Ölçü değişen ama iddiası değişmeyen testler de bu turda taşınıyor — bugün de yarın da yeşiller,
çünkü değişen tek şey kullandıkları skill adı.

## 1 · `backend/tests/test_skills.py`

### `ALL_SKILLS` ve iki yeni test

Baştaki liste ve ilk iki test bu hâle geliyor:

```python
# Written out rather than imported: the picker's ids live in the frontend's skills.js and Python
# cannot read it. If the two ever drift apart, a skill answers with no instruction at all -- so the
# match is pinned here, in words.
ALL_SKILLS = ["generate-prompts-plus"]

# Madde 94 silmesi. Adları burada, çünkü bir silmenin kanıtı yokluk ve yokluğu ancak onu arayan bir
# test görür -- yeniden eklenmesi de bu satırdan geçmek zorunda kalır.
DELETED = [
    "create-scenario",
    "create-character-prompt",
    "split-into-frames",
    "generate-prompts",
    "verify-prompts",
]


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_in_the_menu_carries_an_instruction(skill):
    assert instruction_for(skill).strip()


def test_only_one_skill_is_offered():
    # The path runs on the base instruction plus one text now, and only the last leg has a text.
    assert list(INSTRUCTIONS) == ALL_SKILLS


@pytest.mark.parametrize("skill", DELETED)
def test_a_deleted_skill_carries_nothing(skill):
    # A record written before the deletion still names one of these, and that turn simply runs on
    # the base instruction -- the same road an unknown name has always taken.
    assert instruction_for(skill) == ""
```

`DELETED` yorumu Türkçe yazılmayacak — dosya İngilizce. Yukarıdaki iki Türkçe satır bu planın
açıklaması; teste giren metin şu:

```python
# Madde 94's deletion. The names live here because the proof of a deletion is an absence, and only a
# test that looks for it sees one -- putting any of them back has to come past this line.
```

### Kural kitabının tek okuyucusu

`test_the_rulebook_is_one_text_with_two_readers` gidiyor, yerine:

```python
def test_the_rulebook_has_one_reader_now():
    # It was one text with two readers until Madde 94 took the checking skill away. It is still one
    # text, and it is still applied -- before every build, by the skill that builds.
    holders = [skill for skill in INSTRUCTIONS if RULEBOOK in INSTRUCTIONS[skill]]
    assert holders == ["generate-prompts-plus"]
```

### Silinen testler

| Konusu | Testler |
|---|---|
| `create-scenario` | `..._no_longer_counts_sentences`, `..._asks_for_a_list`, `..._says_why_it_stays_short`, `test_the_scenario_file_is_named_after_its_subject`, `test_a_correction_reaches_the_scenario_file_too`, `test_the_scenario_still_goes_into_the_chat_as_well`, `..._no_longer_argues_about_language`, `..._keeps_out_of_the_frame_lists_territory` |
| `split-into-frames` | `test_the_frame_list_comes_in_the_users_own_language`, `..._leaves_the_translating_to_the_prompt_skills`, `test_the_frame_list_reaches_a_file_too`, `test_the_frame_file_is_named_after_the_subject`, `test_the_frame_split_no_longer_stays_in_the_chat`, `test_a_frame_is_one_or_two_sentences`, `test_the_frame_instruction_no_longer_says_one_line`, `test_a_frame_is_still_not_a_paragraph`, `..._settles_the_count_with_the_user_and_works_in_batches` |
| `create-character-prompt` | `..._asks_for_candidates_and_leaves_quality_out`, `test_the_character_count_comes_from_the_user`, `test_the_character_candidates_go_into_a_file`, `test_the_character_file_is_named_after_the_character`, `test_the_character_file_has_the_shape_of_the_structure`, `test_a_pasted_prompt_is_read_as_a_format_example`, `..._keeps_the_frames_own_fields_out`, `..._leaves_clothing_out_of_the_identity` |
| `generate-prompts` | `..._asks_for_the_python_list_and_its_own_name`, `test_the_plain_instruction_is_the_control_group`, `test_the_plain_instruction_writes_in_batches_too` |
| `verify-prompts` | `test_verify_talks_about_prompts_rather_than_frames`, `test_verify_reports_and_never_fixes`, `test_verify_leaves_the_drifted_copy_to_the_user`, `test_verify_is_the_one_skill_that_writes_nothing` |

### Duran testler

`test_a_skill_nobody_knows_carries_nothing`, `test_the_names_from_before_the_rename_carry_nothing`,
`test_no_instruction_calls_a_frame_a_shot`, ve `generate-prompts-plus` ile `RULEBOOK`'un bütün
testleri. Tek kelimesi değişmiyor.

## 2 · `backend/tests/test_stream_answer.py` — dört ölçü taşınıyor

`test_the_instruction_is_the_last_thing_in_the_request`:

```python
    _, conversation = _said_with(tmp_path, ("write me the prompts", "generate-prompts-plus"))
    assert conversation[-1] == {
        "role": "system",
        "content": instruction_for("generate-prompts-plus"),
    }
    assert conversation[-2]["content"] == "write me the prompts"
```

`test_only_the_current_skill_is_sent_whatever_came_before` — iki değeri artık **skill'li ve
skill'siz** olarak alıyor, çünkü menüde tek ad var. İddia aynı: en sonuncusu karar veriyor.

```python
    _, conversation = _said_with(
        tmp_path,
        ("one", "generate-prompts-plus"),
        ("and again", "generate-prompts-plus"),
        ("never mind", ""),
    )
    assert _instructions(conversation) == []
```

Yorumun son cümlesi de doğrusuna dönüyor: *"Before Madde 93 a chat that had changed skill four times
carried four texts"* duruyor, ama örnek artık seçimi bırakan bir sohbet.

`test_no_instruction_stands_among_the_messages`:

```python
    _, conversation = _said_with(
        tmp_path, ("one", "generate-prompts-plus"), ("and the rest", "generate-prompts-plus")
    )
```

`test_the_instruction_moves_to_the_end_of_every_round` — `"verify-prompts"` yerine
`"generate-prompts-plus"`, cümle `"build me the prompts"`.

`test_the_instruction_is_never_written_to_the_chat` — `("write me the prompts",
"generate-prompts-plus")`.

## 3 · `backend/tests/test_chats_api.py` — bir ölçü taşınıyor

`test_a_message_carries_the_skill_it_was_sent_with` içindeki iki `"create-scenario"`
*(gövdedeki ve `instruction_for` çağrısındaki)* `"generate-prompts-plus"` oluyor.

**Dokunulmayan:** aynı dosyanın 577/582 satırlarındaki `"create-scenario"`. Orası kaydın alanını
sınıyor ve adı opak dizge olarak kullanıyor — `instruction_for` çağırmıyor. Aynısı
`test_append_message.py` ve `test_file_chat_store.py` için de geçerli.

## 4 · `frontend/src/features/workspace/skills.test.js`

Dosya bu hâle iniyor:

```javascript
import { expect, test } from "vitest";

import { SKILLS, skillName } from "./skills.js";

// Madde 94: five of the six were deleted. What is left is the one that builds a prompt from parts,
// and the menu is one row -- not none, because having no skill selected is an ordinary state and
// more rows will come.
test("the one skill left is the one that builds", () => {
  expect(SKILLS.map((skill) => skill.id)).toEqual(["generate-prompts-plus"]);
});

test("each row says what it does", () => {
  for (const skill of SKILLS) {
    expect(skill.name.length).toBeGreaterThan(0);
    expect(skill.detail.length).toBeGreaterThan(0);
  }
});

test("no row promises to stay in the chat any more", () => {
  expect(SKILLS.filter((skill) => /stays in the chat/i.test(skill.detail))).toEqual([]);
});

test("a name is the label, not the id", () => {
  expect(skillName("generate-prompts-plus")).toBe("Generate prompts+");
});

test("a deleted skill keeps its id on the screen rather than vanishing", () => {
  // An old record can still name one. The button says something rather than going blank.
  expect(skillName("verify-prompts")).toBe("verify-prompts");
});

test("nothing selected is the button's own word", () => {
  expect(skillName("")).toBe("Skills");
});
```

**Silinen:** `the six skills are the ones that were agreed`, `the skill that checks carries no frame
in its name`, `the skill that splits says frames`, `the scenario row says what a scenario is now`,
`the rows that write a file say so`.

`a deleted skill keeps its id on the screen` yeni ve **bugün kırmızı** — ilk yazımı yeşil olacağını
söylüyordu, oysa `verify-prompts` hâlâ listede, yani `skillName` onun etiketini buluyor. Silmeden
sonra `?? id` koluna düşecek, ve testi olmayan bir kol sessizce kaybolur.

## 5 · `frontend/src/features/workspace/SkillPicker.test.jsx`

Beş yerde ölçü taşınıyor; hepsi bugün de yarın da yeşil.

| Satır | Bugün | Yarın |
|---|---|---|
| `a selected skill gives the button its name...` | `skill="verify-prompts"` · `/Verify prompts/` | `skill="generate-prompts-plus"` · `/Generate prompts/` |
| `choosing one hands the id over` | `"Split into frames"` → `"split-into-frames"` | `"Generate prompts+"` → `"generate-prompts-plus"` |
| `pressing the selected one clears it` | `skill="verify-prompts"`, `"Verify prompts"` | `skill="generate-prompts-plus"`, `"Generate prompts+"` |
| `the selected row is the marked one` | `skill="verify-prompts"`, `"Verify prompts"` | `skill="generate-prompts-plus"`, `"Generate prompts+"` |

`open, it lists every skill under a label` `SKILLS` üzerinde döndüğü için hiç değişmiyor.

Düğme adı aranırken `/Generate prompts/` kullanılıyor, `+` regex'te kaçış isterdi ve tek satırlık
menüde bu kadarı zaten tek.

## 6 · `frontend/src/features/workspace/ChatScreen.test.jsx`

`the picker shows the skill it is handed, not the chat's` — iki farklı değere ihtiyacı var ve tek
skill kalınca ikisini **kayıtta olan** ile **hiçbiri** olarak alıyor. İddia aynı: canlı seçim
kaydın alanını yener.

```jsx
  render(
    <ChatScreen project={PROJECT} chat={{ ...CHAT, skill: "generate-prompts-plus" }} skill="" />,
  );
  expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Generate prompts/ })).toBeNull();
```

`picking a skill is passed up rather than kept here` — `"Split into frames"` yerine
`"Generate prompts+"`, beklenen `"generate-prompts-plus"`.

## 7 · `frontend/src/features/workspace/ProjectScreen.test.jsx`

İki yerde `"Create scenario"` → `"Generate prompts+"`, biri beklenen id ile birlikte
`"generate-prompts-plus"`.

## 8 · `frontend/src/App.test.jsx`

Dokuz yerde ölçü taşınıyor; hiçbirinin iddiası değişmiyor.

| Satır | Bugün | Yarın |
|---|---|---|
| 173, 178 | `"Create scenario"` | `"Generate prompts+"` |
| 207, 218 | `"Create scenario"` / `"create-scenario"` | `"Generate prompts+"` / `"generate-prompts-plus"` |
| 1315 | `withStoredSkill(stored = "verify-prompts")` | `stored = "generate-prompts-plus"` |
| 1391, 1393, 1404, 1424 | `"Verify prompts"` / `/Verify prompts/` | `"Generate prompts+"` / `/Generate prompts/` |
| 1692 | `skill: "verify-prompts"` | `skill: "generate-prompts-plus"` |
| 1718, 1725 | `"Split into frames"` / `/Split into frames/` | `"Generate prompts+"` / `/Generate prompts/` |
| 1734, 1735, 1749 | `"Split into frames"` / `/…/` / `"split-into-frames"` | `"Generate prompts+"` / `/Generate prompts/` / `"generate-prompts-plus"` |
| 1764, 1776 | `"Create scenario"` | `"Generate prompts+"` |

1725'te düğme aranırken `/Generate prompts/` — o anda seçim yapılmış ve menü kapalı, yani tek.
1393'te de öyle.

## Beklenen kırmızı

| Nerede | Kaç | Neden |
|---|---|---|
| `test_a_deleted_skill_carries_nothing` | 5 | beşi de bugün metin taşıyor |
| `test_only_one_skill_is_offered` | 1 | `INSTRUCTIONS` altı satır |
| `test_the_rulebook_has_one_reader_now` | 1 | `verify-prompts` de taşıyor |
| `the one skill left is the one that builds` | 1 | `SKILLS` altı satır |
| `a deleted skill keeps its id on the screen` | 1 | `verify-prompts` hâlâ listede, etiketi bulunuyor |

**Toplam dokuz.** Sayı bugünkü `skills.py` ve `skills.js`'ten türetildi: altı yönerge, altı menü
satırı, ve kural kitabı iki metnin içinde. Son satır koşulduktan sonra eklendi — türetme onu yeşil
sanmıştı.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `skills.py` ve `skills.js` bu turda açılmaz.
- **`dist` derlenmez** — ön yüz kaynağı yalnız testte değişiyor.
- **`SkillPicker.jsx`, `ChatScreen.jsx`, `ProjectScreen.jsx`, `App.jsx` açılmaz** — seçici olduğu
  gibi kalıyor, değişen yalnız beslendiği liste ve o tur 2'de değişiyor.
- **Eski spec'ler ve planlar düzeltilmez.**
