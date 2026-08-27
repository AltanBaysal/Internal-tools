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
