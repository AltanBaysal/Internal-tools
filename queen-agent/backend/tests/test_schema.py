"""What read_prompt_structure_schema hands back: the shape of a structure file, and its rules.

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
    ["characters", "outfits", "locations", "frames", "people", "action", "camera"],
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


def test_the_example_carries_no_quality_field():
    # Madde 110: what the example shows is what gets copied, and this one was copying a chain that
    # mixed two model families into every scenario.
    assert '"quality"' not in _schema()


def test_the_schema_says_where_the_quality_chain_comes_from():
    said = _schema().lower()
    assert "quality chain is not in this file" in said
    assert "code puts it at the front" in said


def test_an_outfit_entry_dresses_one_person():
    # 28 Aug: one entry said "dark pants for man, black dress for woman" and the code handed the
    # whole text to both -- the man came out in the dress. The schema pushed sharing and never
    # said that two people dressed differently are two entries.
    said = _schema().lower()
    assert "dresses one person" in said
    assert "two entries" in said


def test_the_example_shows_two_people_in_different_clothes():
    # The example is the teacher: the failure it has to rule out is one entry covering both, so
    # the second frame stands two characters side by side, each with their own outfit.
    said = _schema()
    assert '"people": "1boy, 1girl"' in said
    assert "deniz" in said


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


def test_the_schema_teaches_the_form_of_a_value():
    # 28 Aug: the observed failure -- values written as narrated sentences. The form was only
    # ever shown by the example; a weak model needs it said.
    said = _schema().lower()
    assert "comma-separated fragments" in said
    assert "never a sentence" in said


def test_the_schema_says_what_a_camera_is_made_of():
    # Madde 111: seven of ten frames came out as a plain medium shot. The field existed and the
    # example showed one value; nothing said the value is two decisions.
    said = _schema().lower()
    assert "how much of the body" in said
    assert "where it is looking from" in said


def test_the_example_reads_at_working_density():
    # The example gets copied, so the example is the teacher: expression and gaze in the action,
    # and no placeholder left to copy.
    said = _schema()
    assert "pensive expression" in said
    assert "..." not in said


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


def test_the_rulebook_calls_a_sentence_a_violation():
    said = _rulebook()
    assert "7." in said and "fragments" in said.lower()


def test_the_rulebook_catches_one_entry_dressing_two_people():
    said = _rulebook()
    assert "8." in said and "for the man" in said.lower()


def test_what_the_tool_hands_back_carries_both():
    # One call, both halves: whoever writes the file needs the shape and the rules together.
    assert _rulebook() in _schema()


def test_the_schema_never_calls_a_frame_a_shot():
    # The same sweep the instructions get: the word survives only as camera language.
    assert "shot" not in _schema().lower().replace("medium shot", "")
