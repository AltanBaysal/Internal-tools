import pytest

from backend.features.workspace.domain.skills import INSTRUCTIONS, instruction_for

# Written out rather than imported: the picker's ids live in the frontend's skills.js and Python
# cannot read it. If the two ever drift apart, a skill answers with no instruction at all -- so the
# match is pinned here, in words.
ALL_SKILLS = ["generate-prompts-plus", "start-a-scenario"]

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


def test_the_menu_and_the_instructions_carry_the_same_names():
    # Two since Madde 101: the one that builds from a file that exists, and the one that walks the
    # user through making one. A name in the menu with no instruction here is a turn that quietly
    # runs on the base text alone.
    assert sorted(INSTRUCTIONS) == sorted(ALL_SKILLS)


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


def test_the_instruction_no_longer_carries_the_schema():
    # It went to the schema tool. Left here it would be paid for every turn, and copied again the
    # day a second skill writes the same file.
    said = instruction_for("generate-prompts-plus")
    assert '"frames"' not in said and '"outfits"' not in said


def test_the_instruction_no_longer_carries_the_rulebook():
    from backend.features.workspace.domain.schema import RULEBOOK

    assert RULEBOOK not in instruction_for("generate-prompts-plus")


def test_the_instruction_reads_the_schema_before_it_builds():
    # The order is part of the instruction: the shape is fetched, the file is written, and only then
    # is anything built from it.
    said = instruction_for("generate-prompts-plus")
    assert said.index("read_prompt_structure_schema") < said.index("build_prompts with")


def test_the_structured_instruction_writes_the_skeleton_then_batches_of_five():
    said = instruction_for("generate-prompts-plus")
    assert "skeleton" in said and "batches of five" in said
    assert "create_file" in said and "edit_file" in said


def test_the_structured_instruction_forbids_assembling_a_prompt_by_hand():
    said = instruction_for("generate-prompts-plus")
    # Without this the skill loses the only thing that makes it different.
    assert "do not assemble" in said.lower()
    assert "build_prompts" in said


def test_no_instruction_carries_the_rulebook_any_more():
    # It was one text with two readers until Madde 94 took the checking skill away, and one reader
    # until Madde 96 moved it out of the texts entirely. Whoever writes a file fetches it.
    from backend.features.workspace.domain.schema import RULEBOOK

    assert not [skill for skill in INSTRUCTIONS if RULEBOOK in INSTRUCTIONS[skill]]


# --- the flow that walks the user through it (Madde 101) -----------------------------------------


def _flow():
    return instruction_for("start-a-scenario")


def test_the_flow_writes_the_plan_before_it_asks_anything():
    # Step one whatever the user's opening sentence was. Without it the flow starts somewhere
    # different every time, and has nowhere to keep its place.
    said = _flow()
    assert "write_plan" in said
    assert said.index("write_plan") < said.index("read_prompt_structure_schema")


def test_the_flow_carries_on_from_a_plan_that_is_already_there():
    # How a conversation that grew too long is continued: files belong to the project rather than
    # the chat, so a new chat finds the plan and picks up the step it left open.
    assert "carry on from the step it left open" in _flow()


def test_a_step_ends_when_the_user_approves_it():
    # Not when an answer is written. One of the flow's two rules, and the one that keeps a step
    # from running away with the work.
    assert "approves" in _flow()


def test_what_nobody_described_becomes_a_placeholder():
    # K34. A flow that stops to ask for a description is a flow that never reaches the prompts.
    said = _flow()
    assert "placeholder" in said
    assert "never stop the flow" in said.lower()


def test_the_scenes_step_writes_a_readable_list_too():
    # K33 turned around by K40: the list is no longer a copy of the frames, it is their source --
    # and it follows the reader, because every neighbouring text is English and without a word the
    # list would drift there too.
    said = _flow()
    assert "one sentence" in said
    assert "their own language" in said


def test_a_finished_step_reaches_the_plan():
    # The flow promises a fresh chat can carry on from the step left open. A plan nobody updates
    # shows no step as open, so the promise stands only if ending a step writes into the plan.
    assert "marked done" in _flow()


def test_the_structure_file_is_born_once():
    # The observed failure wears two masks here: everything gathered in chat and written at the
    # end, or a new file per step. One birth at the characters step rules out both -- and the
    # schema is read before the birth, the same order the other skill keeps.
    said = _flow()
    assert "born once" in said
    assert "never a second file" in said
    assert said.index("read_prompt_structure_schema") < said.index("born once")


def test_the_flow_hands_the_frames_to_the_builder():
    # K40 overturned K32 (28 Aug): writing action and camera detail is heavy work, and the flow's
    # asking rhythm is not where it belongs. The flow leaves the foundation and names its heir --
    # the frames stay out of the structure file on purpose.
    said = _flow()
    assert "Generate prompts+" in said
    assert "frames stay empty" in said


def test_the_scene_list_is_named_after_the_structure_file():
    # The discovery mechanism: prompt+ finds the pair by name with list_files, so the convention
    # has to be pinned or the handoff rests on a guess.
    assert "bar-scene-scenes.md" in _flow()


def test_the_builder_picks_up_where_the_flow_stops():
    # The other half of K40: the flow leaves a scene list, and this skill reads it, writes the
    # frames in its order, and resumes by shortfall -- fewer frames than sentences is work left.
    said = instruction_for("generate-prompts-plus")
    assert "Start a scenario" in said
    assert "scene list" in said
    assert "first sentence with no frame" in said


def test_the_sentence_is_a_brief_never_the_frames_text():
    # The observed failure: scene sentences retold as the action, word for word. The brief line
    # holds the door: the sentence briefs the frame, the frame's text is this skill's own.
    said = instruction_for("generate-prompts-plus")
    assert "never text to copy into the frame" in said
