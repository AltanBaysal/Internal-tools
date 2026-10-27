# Madde 96 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m96-sema-aractan-testler-design.md](../specs/2026-08-27-queenagent-m96-sema-aractan-testler-design.md)
**Bu turda kod yazılmaz.** Şema modülü henüz yok; testler onu adıyla çağırıyor.
**Komut:** `python -m pytest queen-agent -q`

---

## Bu turun biçimi: taşınan testler de bu turda taşınıyor

`test_skills.py`'de duran sekiz iddia yeni dosyaya geçiyor. İddiaları değişmiyor — yalnız
baktıkları yer skill metni değil şema oluyor. Madde 94'ün test turu da böyle yapmıştı: bir testin
konusu taşınıyorsa test de aynı turda taşınır, yoksa tur 2 hem kodu hem testi değiştirmek zorunda
kalır.

## 1 · Yeni dosya: `backend/tests/test_schema.py`

```python
"""What read_schema hands back: the shape of a structure file, and the rules it has to hold.

The module is imported inside each test rather than at the top -- a module that does not exist yet
fails this whole file's collection, and then none of the turn's other reds are visible anywhere in
the suite. modes.py's tests do the same, for the same reason.
"""
import pytest


def _schema():
    from backend.features.workspace.domain.schema import SCHEMA

    return SCHEMA


def _rulebook():
    from backend.features.workspace.domain.schema import RULEBOOK

    return RULEBOOK


@pytest.mark.parametrize(
    "field",
    ["quality", "characters", "outfits", "locations", "frames", "people", "action", "camera"],
)
def test_the_schema_shows_every_field_rather_than_describing_it(field):
    assert f'"{field}"' in _schema()


def test_the_schema_shows_a_frames_characters_as_a_map():
    # The shape is the whole decision: a frame names who is in it and what each of them wears.
    assert '"characters": { "aylin": [' in _schema()


def test_the_schema_says_what_belongs_where():
    said = _schema().lower()
    # The rule that makes the split make sense, rather than two maps and no reason.
    assert "changes" in said and "outfits" in said


def test_the_schema_names_the_structure_file_after_frames():
    assert "intro-frames.json" in _schema()


def test_the_schema_says_a_frame_carries_the_name_not_the_text():
    said = _schema()
    assert "names it" in said and "never carries the text" in said


def test_the_schema_says_the_first_name_leads_the_prompt():
    # Madde 95 put this in the code. Here is the only place a model learns that the order it writes
    # the map in is a decision rather than an accident.
    said = _schema().lower()
    assert "first name" in said and "leads the prompt" in said


def test_the_schema_keeps_the_count_out_of_a_character():
    said = _schema().lower()
    assert "never inside a character" in said


def test_the_rulebook_calls_clothing_in_the_wrong_place_a_violation():
    said = _rulebook().lower()
    assert "clothing" in said
    # Both wrong homes, because both are how it comes back as a copy.
    assert "action" in said


def test_the_rulebook_calls_an_unused_name_a_note_rather_than_a_violation():
    assert "note, not a violation" in _rulebook()


def test_the_rulebook_names_the_quality_field_that_actually_exists():
    said = _rulebook().lower()
    assert "quality" in said and "style" not in said


def test_the_rulebook_has_a_sixth_rule_about_the_count():
    # K27: a count or a solo tag inside a character's own entry is in the wrong place. The code does
    # not strip it -- guessing which tag is a count needs a list of names that is never complete.
    said = _rulebook()
    assert "6." in said and "solo" in said.lower()


def test_what_the_tool_hands_back_carries_both():
    # One call, both halves: whoever writes the file needs the shape and the rules together.
    assert _rulebook() in _schema()


def test_the_schema_never_calls_a_frame_a_shot():
    # The same sweep the instructions get: the word survives only as camera language.
    assert "shot" not in _schema().lower().replace("medium shot", "")
```

## 2 · `backend/tests/test_modes.py` — tek satır

```python
READS = {"list_files", "read_file", "read_schema"}
```

Yorumu da bir cümle alıyor:

```python
# read_schema joined them in Madde 96: it opens no file and changes nothing, so no mode has a
# reason to withhold it.
```

Bu tek satır üç testi birden kırmızıya döndürüyor — `ask`, `plan` ve `edit`.

## 3 · `backend/tests/test_tools.py` — bir güncelleme, üç yeni

Küme testine yedinci ad giriyor:

```python
def test_every_tool_is_declared_to_the_model():
    assert {spec["function"]["name"] for spec in TOOL_SPECS} == {
        "list_files",
        "read_file",
        "create_file",
        "edit_file",
        "build_prompts",
        # Sixth since Madde 91, and declared here with the rest: which modes offer it is a separate
        # question, asked in modes.py.
        "write_plan",
        # Seventh since Madde 96. The shape of a structure file stopped being a paragraph in a
        # skill's text; it is fetched when a file is about to be written.
        "read_schema",
    }
```

Ve `test_the_build_tool_tells_the_model_it_assembles_frames`'in altına:

```python
def test_the_schema_tool_hands_back_the_shape_and_the_rules(tmp_path):
    from backend.features.workspace.domain.schema import SCHEMA

    # No arguments at all: there is one shape, and asking which one would be a question with a
    # single answer.
    assert _call(_files(tmp_path), "read_schema") == SCHEMA


def test_the_schema_tool_brings_no_file_into_being(tmp_path):
    assert run_tool(_files(tmp_path), "p1", "read_schema", "{}").created is None


def test_the_schema_tool_says_what_it_answered_with(tmp_path):
    # A reader's line rather than the answer itself, like every other outcome.
    assert run_tool(_files(tmp_path), "p1", "read_schema", "{}").outcome == "Schema"
```

## 4 · `backend/tests/test_skills.py` — sekiz taşınıyor, üç yeni

**Silinenler** *(iddiaları `test_schema.py`'de yaşıyor)*:

- `test_the_structured_instruction_shows_the_schema_rather_than_describing_it`
- `test_the_structured_instruction_shows_the_frames_characters_as_a_map`
- `test_the_structured_instruction_says_what_belongs_where`
- `test_the_structured_instruction_names_the_structure_file_after_frames`
- `test_the_structured_instruction_says_a_frame_carries_the_name_not_the_text`
- `test_the_rulebook_calls_clothing_in_the_wrong_place_a_violation`
- `test_the_rulebook_calls_an_unused_name_a_note_rather_than_a_violation`
- `test_the_rulebook_names_the_quality_field_that_actually_exists`

**Değişen ikisi:**

`test_the_structured_instruction_checks_itself_before_it_builds` ve
`test_the_rulebook_has_one_reader_now` yerlerini şu üçe bırakıyor:

```python
def test_the_instruction_no_longer_carries_the_schema():
    # It went to read_schema. Left here it would be paid for every turn, and copied again the day a
    # second skill writes the same file.
    said = instruction_for("generate-prompts-plus")
    assert '"frames"' not in said and '"outfits"' not in said


def test_the_instruction_no_longer_carries_the_rulebook():
    from backend.features.workspace.domain.schema import RULEBOOK

    assert RULEBOOK not in instruction_for("generate-prompts-plus")


def test_the_instruction_reads_the_schema_before_it_builds():
    # The order is part of the instruction: the shape is fetched, the file is written, and only then
    # is anything built from it.
    said = instruction_for("generate-prompts-plus")
    assert said.index("read_schema") < said.index("build_prompts with")
```

Dosyanın başındaki `RULEBOOK` importu düşüyor.

## 5 · Koş

```
python -m pytest queen-agent -q
```

Beklenen kırmızılar:

- `test_schema.py`'nin tamamı — modül yok, `ImportError`.
- `test_modes.py` — üç kip.
- `test_tools.py` — küme testi ve üç yeni.
- `test_skills.py` — üç yeni.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

**Bir tanesi bugün de yeşil:** `test_the_schema_tool_brings_no_file_into_being`. Tanınmayan bir araç
da dosya doğurmuyor, yani iddia bugün başka bir sebeple doğru. Yarın da yeşil kalması gereken şey
gerçek: okuyan bir aracın sohbete kart düşürmemesi.

## 6 · Commit

```
test(queen-agent): red for a schema that is fetched rather than recited
```
