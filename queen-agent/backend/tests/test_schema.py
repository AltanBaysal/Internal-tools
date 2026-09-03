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
    ["characters", "outfits", "locations", "frames", "action", "camera"],
)
def test_the_schema_shows_every_field_rather_than_describing_it(field):
    assert f'"{field}"' in _schema()


def test_the_schema_never_shows_a_people_field():
    # Madde 156: the count is worked out from each character's kind, so there is nothing here for
    # the model to write. The nail is on the quoted field name rather than the word -- "two people
    # dressed differently" is an outfit rule and has nothing to do with counting.
    assert '"people"' not in _schema()


def test_the_schema_shows_a_frames_characters_as_a_map():
    # The shape is the whole decision: a frame names who is in it and what each of them wears.
    assert '"characters": { "aylin": [' in _schema()


def test_the_schema_says_what_belongs_where():
    said = _schema().lower()
    # The rule that makes the split make sense, rather than two maps and no reason.
    assert "changes" in said and "outfits" in said


def test_the_schema_never_mentions_quality():
    # Madde 150: there is one chain, it lives in code, and no file can change it -- so there is
    # nothing here for the model to decide. A paragraph explaining a field it cannot write would
    # only invite it to try, which is how Madde 110's mixed chain reached real files.
    assert "quality" not in _schema().lower()


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
    assert '"aylin": ["gunluk"], "deniz": ["ceket"]' in said
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


def test_no_example_value_carries_an_article():
    # Madde 114: rule 7 banned articles and Madde 109 slipped one into the example a week later.
    # What guards the next one is a sweep, not a memory -- the example is what gets copied.
    import re

    said = _schema()
    example = said[said.index("{") : said.index("\n}\n") + 2]
    for value in re.findall(r': "([^"]+)"', example):
        assert not re.search(r"\b(the|a|an)\b", value), value


def test_the_example_writes_a_camera_in_the_models_own_words():
    # A camera value goes into the prompt as written, so the example's spelling is the output's
    # spelling. "from slightly above" is English; "from above" is the tag.
    said = _schema()
    assert '"camera": "medium shot, from above"' in said
    assert '"camera": "upper body, from side"' in said


def test_the_camera_vocabulary_is_written_as_tags():
    # The prose lists the angles a camera can take. A vocabulary spelled wrong leaves the example
    # standing alone against it.
    said = _schema()
    assert "from side, from above, from behind" in said
    assert "from the side" not in said


def test_the_schema_says_an_article_is_not_a_tag():
    # Rule 7 names articles among the marks of a sentence, but the paragraph that teaches the form
    # says "brief phrases" -- and a weak model reads that as "sitting on the couch".
    assert "an article is not a tag" in _schema().lower()


def test_the_schema_keeps_the_story_out_of_an_action():
    # Madde 115: the run wrote "facing each other after argument, reconciling". The argument is
    # not in the picture -- it came over from the Turkish scene sentence, which is where it
    # belongs. Saying what an action carries was not enough; the ban has to be said.
    said = _schema().lower()
    assert "only what the camera sees" in said
    assert "what came before" in said


def test_the_schema_turns_a_cause_into_what_it_looks_like():
    # A ban on its own empties the frame. The cause is kept -- written as the thing a camera can
    # actually see.
    assert "downcast eyes" in _schema()


def test_the_rulebook_calls_clothing_in_the_wrong_place_a_violation():
    said = _rulebook().lower()
    assert "clothing" in said
    # Both wrong homes, because both are how it comes back as a copy.
    assert "action" in said


def test_the_rulebook_calls_an_unused_name_a_note_rather_than_a_violation():
    assert "note, not a violation" in _rulebook()


def test_the_rulebook_has_no_quality_rule():
    # The third rule went with the field (Madde 150). A rulebook entry forbidding quality tags in a
    # frame would be the only place the word survives, and one mention is enough to teach it.
    assert "quality" not in _rulebook().lower()


def test_the_rulebook_has_no_count_rule():
    # The sixth rule went with the field it policed (Madde 156), the way the third went with quality.
    # It pointed at the frame's people as where a count belongs, and there is no such field any more
    # -- a rule sending the model to a field that is gone teaches it the field is there.
    said = _rulebook()
    assert "6." not in said
    assert "solo" not in said.lower()


def test_the_rulebook_calls_a_sentence_a_violation():
    said = _rulebook()
    assert "7." in said and "fragments" in said.lower()


def test_the_rulebook_catches_one_entry_dressing_two_people():
    said = _rulebook()
    assert "8." in said and "for the man" in said.lower()


def test_the_rulebook_catches_a_cause_written_into_an_action():
    said = _rulebook()
    assert "9." in said and "cause" in said.lower()


def test_what_the_tool_hands_back_carries_both():
    # One call, both halves: whoever writes the file needs the shape and the rules together.
    assert _rulebook() in _schema()


def test_the_schema_never_calls_a_frame_a_shot():
    # The same sweep the instructions get: the word survives only as camera language.
    assert "shot" not in _schema().lower().replace("medium shot", "")


def test_the_schema_names_its_reader():
    # 28 Aug: the file carried stage direction -- head moving back and forth -- because nothing
    # the model reads says who the prompts are for. The fact lived in the roadmap and the
    # decision notebook, two documents the model never sees.
    said = _schema()
    assert "SDXL-family" in said
    assert "tags, never sentences" in said


def test_the_schema_says_a_frame_is_one_frozen_instant():
    # "The camera sees" alone also describes a video camera, and the model wrote for one.
    said = _schema().lower()
    assert "one single still picture" in said
    assert "frozen instant" in said
    assert "no motion" in said


def test_a_movement_is_written_as_the_pose_it_passes_through():
    # The ban alone would empty the frame -- the movement is kept, written as what a still
    # camera can hold, the way the cause became downcast eyes.
    assert "the pose it passes through" in _schema().lower()


def test_a_camera_half_comes_from_the_lists():
    # "from side profile" three times in one file: the vocabulary read as examples, not as the
    # set to choose from.
    assert "come from the lists" in _schema().lower()


def test_the_rulebook_catches_a_movement_in_an_action():
    # 28 Aug: head moving back and forth -- stage direction for a video that will never exist.
    said = _rulebook()
    assert "10." in said and "frozen instant" in said


def test_the_rulebook_catches_camera_language_in_an_action():
    # full body view in the action while the camera field said medium shot: two framings fight.
    said = _rulebook()
    assert "11." in said and "full body view" in said


def test_the_rulebook_catches_a_story_role_in_an_action():
    # stepson thrusting: the camera sees a person, not a relationship, and who is in the frame
    # is the characters map's word.
    said = _rulebook()
    assert "12." in said and "stepson" in said.lower()


def test_the_rulebook_catches_an_or_in_any_value():
    # Rule 8 banned it in outfits; hands gripping wall or body walked around the fence.
    said = _rulebook()
    assert "13." in said and "any value" in said


def test_the_rulebook_catches_an_outfit_named_after_its_wearer():
    # milf_pink, male_nude: the prose said garments name outfits, and prose was not enough --
    # the rulebook is the list the writer is told to check against.
    said = _rulebook()
    assert "14." in said and "named after its wearer" in said
