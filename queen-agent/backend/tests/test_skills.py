import pytest

from backend.features.workspace.domain.skills import INSTRUCTIONS, RULEBOOK, instruction_for

# Written out rather than imported: the picker's ids live in the frontend's skills.js and Python
# cannot read it. If the two ever drift apart, a skill answers with no instruction at all -- so the
# match is pinned here, in words.
ALL_SKILLS = ["generate-prompts-plus"]

# Madde 94's deletion. The names live here because the proof of a deletion is an absence, and only a
# test that looks for it sees one -- putting any of them back has to come past this line.
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


def test_a_skill_nobody_knows_carries_nothing():
    # An older record can name a skill that has since been renamed; that turn simply runs without
    # an instruction.
    assert instruction_for("web-search") == ""
    assert instruction_for("") == ""


@pytest.mark.parametrize("old", ["split-into-shots", "verify-shots"])
def test_the_names_from_before_the_rename_carry_nothing(old):
    # A chat sent under the old name still opens; the turn simply runs without an instruction.
    assert instruction_for(old) == ""


def test_no_instruction_calls_a_frame_a_shot():
    # The sweep: hunting the word one sentence at a time is how one gets left behind.
    # "medium shot" survives on purpose -- it is camera language naming a framing, and an image
    # model reads it. What goes is the word used as the name of a unit in the list.
    for skill, said in INSTRUCTIONS.items():
        assert "shot" not in said.lower().replace("medium shot", ""), skill


@pytest.mark.parametrize(
    "field", ["quality", "characters", "outfits", "locations", "frames", "action", "camera"]
)
def test_the_structured_instruction_shows_the_schema_rather_than_describing_it(field):
    assert f'"{field}"' in instruction_for("generate-prompts-plus")


def test_the_structured_instruction_shows_the_frames_characters_as_a_map():
    # The shape is the whole decision: a frame names who is in it and what each of them wears.
    said = instruction_for("generate-prompts-plus")
    assert '"characters": { "aylin": [' in said


def test_the_structured_instruction_says_what_belongs_where():
    said = instruction_for("generate-prompts-plus").lower()
    # The rule that makes the split make sense, rather than two maps and no reason.
    assert "changes" in said and "outfits" in said


def test_the_rulebook_calls_clothing_in_the_wrong_place_a_violation():
    said = RULEBOOK.lower()
    assert "clothing" in said
    # Both wrong homes, because both are how it comes back as a copy.
    assert "action" in said


def test_the_structured_instruction_names_the_structure_file_after_frames():
    assert "intro-frames.json" in instruction_for("generate-prompts-plus")


def test_the_structured_instruction_says_a_frame_carries_the_name_not_the_text():
    said = instruction_for("generate-prompts-plus")
    assert "names it" in said and "never carries the text" in said


def test_the_structured_instruction_writes_the_skeleton_then_batches_of_five():
    said = instruction_for("generate-prompts-plus")
    assert "skeleton" in said and "batches of five" in said
    assert "create_file" in said and "edit_file" in said


def test_the_structured_instruction_forbids_assembling_a_prompt_by_hand():
    said = instruction_for("generate-prompts-plus")
    # Without this the skill loses the only thing that makes it different.
    assert "do not assemble" in said.lower()
    assert "build_prompts" in said


def test_the_structured_instruction_checks_itself_before_it_builds():
    said = instruction_for("generate-prompts-plus")
    # A dirty structure never produces a list, so the order is part of the instruction.
    assert said.index(RULEBOOK) < said.index("build_prompts with")


def test_the_rulebook_has_one_reader_now():
    # It was one text with two readers until Madde 94 took the checking skill away. It is still one
    # text, and it is still applied -- before every build, by the skill that builds.
    holders = [skill for skill in INSTRUCTIONS if RULEBOOK in INSTRUCTIONS[skill]]
    assert holders == ["generate-prompts-plus"]


def test_the_rulebook_calls_an_unused_name_a_note_rather_than_a_violation():
    assert "note, not a violation" in RULEBOOK


def test_the_rulebook_names_the_quality_field_that_actually_exists():
    # The decisions document called this rule style; the field was settled as quality.
    assert "quality" in RULEBOOK.lower()
    assert "style" not in RULEBOOK.lower()
