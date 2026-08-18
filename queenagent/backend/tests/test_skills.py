import pytest

from backend.features.workspace.domain.skills import RULEBOOK, instruction_for

# Written out rather than imported: the picker's ids live in the frontend's skills.js and Python
# cannot read it. If the two ever drift apart, a skill answers with no instruction at all -- so the
# match is pinned here, in words.
ALL_SKILLS = [
    "create-scenario",
    "create-character-prompt",
    "split-into-shots",
    "generate-prompts",
    "generate-prompts-plus",
    "verify-shots",
]


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_in_the_menu_carries_an_instruction(skill):
    assert instruction_for(skill).strip()


def test_a_skill_nobody_knows_carries_nothing():
    # An older record can name a skill that has since been renamed; that turn simply runs without
    # an instruction.
    assert instruction_for("web-search") == ""
    assert instruction_for("") == ""


def test_the_scenario_instruction_says_how_long_where_it_goes_and_in_what_language():
    said = instruction_for("create-scenario")
    assert "10 to 15" in said
    assert "scenario.md" in said
    # The app's own prompt says English; silence here would make that the scenario's language too.
    assert "language" in said


def test_the_scenario_instruction_keeps_out_of_the_shot_lists_territory():
    said = instruction_for("create-scenario").lower()
    assert "camera" in said and "shot" in said


@pytest.mark.parametrize("skill", ["create-character-prompt", "split-into-shots"])
def test_the_two_chat_only_skills_say_they_write_no_file(skill):
    assert "Do not create a file" in instruction_for(skill)


def test_the_character_instruction_asks_for_candidates_and_leaves_quality_out():
    said = instruction_for("create-character-prompt")
    assert "candidates" in said
    # build_prompts puts the quality tags in once, so a character carrying them would double them.
    assert "quality" in said.lower()


def test_the_character_instruction_keeps_the_shots_own_fields_out():
    said = instruction_for("create-character-prompt").lower()
    assert "pose" in said and "camera" in said


def test_the_shot_instruction_settles_the_count_with_the_user_and_works_in_batches():
    said = instruction_for("split-into-shots").lower()
    assert "how many" in said and "together with the user" in said
    assert "batches" in said


def test_the_plain_instruction_asks_for_the_python_list_and_its_own_name():
    said = instruction_for("generate-prompts")
    assert "PROMPTS = [" in said
    # -plain keeps the control group's file from colliding with the structured one's.
    assert "-plain" in said
    assert "English" in said


def test_the_plain_instruction_is_the_control_group():
    said = instruction_for("generate-prompts")
    # It has to say what it is NOT doing: both skills answer the same request.
    assert "no structure file" in said.lower()
    assert "build_prompts" in said


def test_the_plain_instruction_writes_in_batches_too():
    # The rule is every skill's, not the structured one's alone.
    assert "edit_file" in instruction_for("generate-prompts")


@pytest.mark.parametrize(
    "field", ["quality", "characters", "locations", "shots", "action", "camera"]
)
def test_the_structured_instruction_shows_the_schema_rather_than_describing_it(field):
    assert f'"{field}"' in instruction_for("generate-prompts-plus")


def test_the_structured_instruction_says_a_shot_carries_the_name_not_the_text():
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


def test_the_rulebook_is_one_text_with_two_readers():
    assert RULEBOOK in instruction_for("generate-prompts-plus")
    assert RULEBOOK in instruction_for("verify-shots")


def test_the_rulebook_calls_an_unused_name_a_note_rather_than_a_violation():
    assert "note, not a violation" in RULEBOOK


def test_the_rulebook_names_the_quality_field_that_actually_exists():
    # The decisions document called this rule style; the field was settled as quality.
    assert "quality" in RULEBOOK.lower()
    assert "style" not in RULEBOOK.lower()


def test_verify_reports_and_never_fixes():
    said = instruction_for("verify-shots")
    assert "Do not fix" in said
    assert "Do not create a file" in said or "do not write" in said.lower()


def test_verify_leaves_the_drifted_copy_to_the_user():
    said = instruction_for("verify-shots")
    assert "user" in said and "which of the two" in said.lower()
