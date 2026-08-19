import pytest

from backend.features.workspace.domain.skills import INSTRUCTIONS, RULEBOOK, instruction_for

# Written out rather than imported: the picker's ids live in the frontend's skills.js and Python
# cannot read it. If the two ever drift apart, a skill answers with no instruction at all -- so the
# match is pinned here, in words.
ALL_SKILLS = [
    "create-scenario",
    "create-character-prompt",
    "split-into-frames",
    "generate-prompts",
    "generate-prompts-plus",
    "verify-prompts",
]


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_in_the_menu_carries_an_instruction(skill):
    assert instruction_for(skill).strip()


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


def test_the_scenario_instruction_no_longer_counts_sentences():
    # A count and a shape that were both wrong for what a scenario is for. Watched rather than
    # simply deleted, so the old rule cannot quietly come back.
    said = instruction_for("create-scenario").lower()
    assert "10 to 15" not in said
    assert "plain prose" not in said


def test_the_scenario_instruction_asks_for_a_list():
    said = instruction_for("create-scenario").lower()
    assert "bullet" in said or "one line each" in said


def test_the_scenario_instruction_says_why_it_stays_short():
    # The reason is the rule: this is here to show what was understood, not to be the finished work.
    said = instruction_for("create-scenario").lower()
    assert "understood" in said
    assert "short" in said


def test_the_scenario_file_is_named_after_its_subject():
    said = instruction_for("create-scenario")
    # One project holds several scenarios, and a fixed name loses which is which.
    assert "scenario.md" not in said
    assert ".md" in said


def test_a_correction_reaches_the_scenario_file_too():
    said = instruction_for("create-scenario")
    assert "create_file" in said and "edit_file" in said


def test_the_scenario_still_goes_into_the_chat_as_well():
    said = instruction_for("create-scenario").lower()
    assert "chat" in said


def test_the_scenario_instruction_no_longer_argues_about_language():
    # It carried one only because the app forced English. The app follows the user now, and a rule
    # repeated in every skill is a rule that drifts.
    # Narrow on purpose: "camera or lighting language" is a different sentence and stays.
    assert "the language the user" not in instruction_for("create-scenario")


def test_the_scenario_instruction_keeps_out_of_the_frame_lists_territory():
    said = instruction_for("create-scenario").lower()
    assert "camera" in said and "frame" in said


def test_only_the_frame_split_still_stays_in_the_chat():
    # The character skill writes a file now, so it left this list.
    assert "Do not create a file" in instruction_for("split-into-frames")
    assert "Do not create a file" not in instruction_for("create-character-prompt")


def test_the_character_instruction_asks_for_candidates_and_leaves_quality_out():
    said = instruction_for("create-character-prompt")
    assert "candidates" in said
    # build_prompts puts the quality tags in once, so a character carrying them would double them.
    assert "quality" in said.lower()


def test_the_character_count_comes_from_the_user():
    # How many is the user's call: a guess is either more than they wanted or fewer.
    said = instruction_for("create-character-prompt").lower()
    assert "two or three" not in said
    assert "ask" in said


def test_the_character_candidates_go_into_a_file():
    said = instruction_for("create-character-prompt")
    assert "create_file" in said
    assert "stays in the chat" not in said.lower()


def test_the_character_file_is_named_after_the_character():
    # A general name loses which file is whose once the tries pile up.
    assert "aylin.json" in instruction_for("create-character-prompt")


def test_the_character_file_has_the_shape_of_the_structure():
    # Pasteable straight into a structure file, which is the whole reason it is a file.
    said = instruction_for("create-character-prompt")
    assert '"characters"' in said and '"outfits"' in said


def test_a_pasted_prompt_is_read_as_a_format_example():
    said = instruction_for("create-character-prompt").lower()
    assert "paste" in said
    # What is taken is the shape; what belongs to a frame is left behind.
    assert "pose" in said and "camera" in said


def test_the_character_instruction_keeps_the_frames_own_fields_out():
    said = instruction_for("create-character-prompt").lower()
    assert "pose" in said and "camera" in said


def test_the_character_instruction_leaves_clothing_out_of_the_identity():
    # An identity that carries clothing cannot be worn twice, which is exactly what outfits is for.
    said = instruction_for("create-character-prompt").lower()
    assert "what they are wearing" not in said
    assert "outfits" in said


def test_a_frame_is_one_or_two_sentences():
    # A countable limit: "keep it short" was already there and the model wrote paragraphs anyway.
    said = instruction_for("split-into-frames").lower()
    assert "one or two sentences" in said


def test_the_frame_instruction_no_longer_says_one_line():
    # It described a shape rather than a length -- three sentences with no line break are still
    # one line -- and two rules side by side let the model pick the loose one.
    assert "one line" not in instruction_for("split-into-frames").lower()


def test_a_frame_is_still_not_a_paragraph():
    assert "paragraph" in instruction_for("split-into-frames").lower()


def test_the_frame_instruction_settles_the_count_with_the_user_and_works_in_batches():
    said = instruction_for("split-into-frames").lower()
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


def test_the_rulebook_is_one_text_with_two_readers():
    assert RULEBOOK in instruction_for("generate-prompts-plus")
    assert RULEBOOK in instruction_for("verify-prompts")


def test_the_rulebook_calls_an_unused_name_a_note_rather_than_a_violation():
    assert "note, not a violation" in RULEBOOK


def test_the_rulebook_names_the_quality_field_that_actually_exists():
    # The decisions document called this rule style; the field was settled as quality.
    assert "quality" in RULEBOOK.lower()
    assert "style" not in RULEBOOK.lower()


def test_verify_talks_about_prompts_rather_than_frames():
    # It reads the material the prompts are made of, so its name carries no frame -- and neither
    # does the sentence that opens it.
    said = instruction_for("verify-prompts").lower()
    assert "prompts" in said


def test_verify_reports_and_never_fixes():
    said = instruction_for("verify-prompts")
    assert "Do not fix" in said
    assert "Do not create a file" in said or "do not write" in said.lower()


def test_verify_leaves_the_drifted_copy_to_the_user():
    said = instruction_for("verify-prompts")
    assert "user" in said and "which of the two" in said.lower()
