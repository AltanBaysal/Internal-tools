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


def test_the_builder_changes_what_exists_too():
    # Madde 94's record gave prompt+ the job of updating what exists; the sentence never reached
    # the text, so the skill read as a one-way builder -- and Madde 108 now sends people here.
    said = instruction_for("generate-prompts-plus")
    assert "or changed" in said
    assert "build_prompts again" in said


def test_a_change_goes_through_the_file_rather_than_the_prompt_list():
    # The prompt file is derived: patched by hand it stops matching the structure it came from.
    assert "rebuilt rather than patched" in instruction_for("generate-prompts-plus")


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


def test_the_handoff_is_a_step_of_its_own():
    # Madde 108: the handoff sat outside the numbered list, and a weak model stops when the list
    # ends -- so the flow went on to write frames instead of naming its heir.
    said = _flow()
    assert "Five steps" in said
    assert "5. The handoff" in said
    assert said.index("5. The handoff") < said.rindex("Generate prompts+")


def test_the_flow_never_writes_a_frame_even_when_asked():
    # What happened: asked for the frames, the flow wrote all ten in one edit. The batching rule
    # and the craft licence live in the other skill, so the ask is answered by pointing there.
    said = _flow()
    assert "never written here" in said
    assert "not even when the user asks" in said


def test_the_sentence_is_a_brief_never_the_frames_text():
    # The observed failure: scene sentences retold as the action, word for word. The brief line
    # holds the door: the sentence briefs the frame, the frame's text is this skill's own.
    said = instruction_for("generate-prompts-plus")
    assert "never text to copy into the frame" in said


def test_the_builder_varies_the_camera_between_frames():
    # Ten scenes came back as one framing. The craft licence was there; the reason to use it was
    # not.
    said = instruction_for("generate-prompts-plus")
    assert "the same framing and angle" in said
    assert "differ in at least one" in said


def test_a_delegation_answers_only_the_question_that_was_asked():
    # 28 Aug: "you decide" arrived with the places answer and the flow read it as authority over
    # everything left -- the scenes question was never asked. A delegation is an answer, and an
    # answer belongs to its question.
    said = _flow()
    assert "answers only the question that was asked" in said
    assert "asked as ever" in said


def test_a_delegated_step_still_ends_on_approval():
    # The flow choosing for the user is not the user approving the choice: the step shows what
    # was chosen and waits, like every other step.
    assert "still ends when the user approves" in _flow()


def test_the_plan_records_a_delegation_with_the_step_it_closed():
    # The plan wrote "user said you decide" with no step name, and the fresh chat that read it
    # inherited an authority the user never gave.
    assert "never as a standing authority" in _flow()


def test_the_flow_never_calls_the_builder():
    # 28 Aug: told never to write a frame, the flow offered to run build_prompts instead -- a ban
    # that names the deed invites the road around it. The builder is the other skill's too, and
    # the file this flow leaves holds no frames for it to build from.
    assert "build_prompts is never called here" in _flow()


def test_the_handoff_offers_nothing_and_asks_nothing():
    # The closing message came back as an offer wearing a question mark. "It is the last word"
    # was already pinned; this pins that no offer and no question ride on it.
    assert "offers nothing and asks nothing" in _flow()


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_opens_with_what_the_work_is_for(skill):
    # 29 Aug, the user's own sentence: if we never give the model the context of what we are
    # doing, where would it know it from? Neither text said what the prompts are for.
    assert "prompts for an SDXL-family image model" in instruction_for(skill)


def test_the_plan_carries_the_context_too():
    # The plan is the fresh chat's memory; a plan that holds only steps hands over the steps
    # and not the work.
    said = _flow()
    assert "opens with one line of context" in said
    assert "inherits the work" in said


def test_the_flow_opens_as_a_persona():
    # Madde 123, the user's own framing: you are an expert scenario writer laying the ground,
    # and an expert prompt writer takes over. A role holds a weak model better than a rule list.
    assert _flow().startswith("You are an expert scenario writer")


def test_the_builder_opens_as_a_persona():
    assert instruction_for("generate-prompts-plus").startswith("You are an expert SDXL prompt writer")


# --- the ritual openings (Madde 107) --------------------------------------------------------------
#
# The same trial from the skills' side: every turn opened with list_files and write_plan, and the
# schema was fetched again for every edit. The opening moves belong to a chat's first turn, and
# the schema to the one turn that gives the file its shape.


def test_the_opening_moves_belong_to_the_first_turn():
    said = _flow()
    assert "A chat's first turn" in said
    assert "carry on from what the chat already knows" in said


def test_the_flow_fetches_the_schema_once():
    said = _flow()
    assert "once, before the birth" in said
    assert "do not fetch it again" in said


def test_the_builder_fetches_the_schema_once():
    assert "once, before the first write" in instruction_for("generate-prompts-plus")


def test_the_texts_stay_short_enough_to_be_read():
    # Five runs of patches doubled the texts, and a weak model stops reading the middle. The cap
    # is the guard against swelling back: from here a sentence enters only by deleting one.
    assert len(_flow().split()) <= 450
    assert len(instruction_for("generate-prompts-plus").split()) <= 300
