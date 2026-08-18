import pytest

from backend.features.workspace.domain.skills import instruction_for

# Written out rather than imported: the picker's ids live in the frontend's skills.js and Python
# cannot read it. If the two ever drift apart, a skill answers with no instruction at all -- so the
# match is pinned here, in words.
PRODUCING = ["create-scenario", "create-character-prompt", "split-into-shots"]


@pytest.mark.parametrize("skill", PRODUCING)
def test_every_producing_skill_carries_an_instruction(skill):
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
