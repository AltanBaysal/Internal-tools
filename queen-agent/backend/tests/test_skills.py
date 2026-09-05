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


def test_no_instruction_names_a_tool_that_is_gone():
    # Madde 172, and the guard m127 cost a trial for the want of. A skill text naming a tool that
    # does not exist tells the model to make a call that comes back "there is no tool called that",
    # and the model has no way to find that out except by spending a round on it.
    #
    # Asked of every underscored word rather than of a list written here: a tool deleted later has
    # to be caught by this test existing, not by somebody remembering to add its name.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    known = {spec["function"]["name"] for spec in TOOL_SPECS}
    for skill, said in INSTRUCTIONS.items():
        named = {word.strip(".,;:") for word in said.split() if "_" in word}
        assert named <= known, (skill, named - known)


def test_the_builder_writes_each_frames_action_then_builds():
    # Madde 178. The skeleton and the batches of five went with the tools that made them: a
    # scenario is opened by start_scenario and its frames are written by the flow, so what is left
    # for this skill is the sentence each frame turns on, and then the list.
    said = instruction_for("generate-prompts-plus")
    assert "write_frame_prompt" in said
    assert said.index("write_frame_prompt") < said.rindex("build_prompts")


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


def test_no_instruction_carries_the_prompt_rules():
    # It was one text with two readers until Madde 94 took the checking skill away, and one reader
    # until Madde 96 moved it out of the texts entirely. Madde 172 moved it once more -- to the six
    # tools that take tags, where it sits beside the parameter it governs and is read while the tool
    # is being chosen. A copy back here would be paid for by every turn, including the ones writing
    # no tags at all.
    from backend.features.workspace.domain.tools import SDXL_PROMPT_RULES

    assert not [skill for skill in INSTRUCTIONS if SDXL_PROMPT_RULES in INSTRUCTIONS[skill]]


# --- the flow that walks the user through it (Madde 101) -----------------------------------------


def _flow():
    return instruction_for("start-a-scenario")


def test_the_flow_writes_the_plan_before_it_asks_anything():
    # Step one whatever the user's opening sentence was. Without it the flow starts somewhere
    # different every time, and has nowhere to keep its place.
    said = _flow()
    assert "write_plan" in said
    # Ordered against the next step rather than against the schema fetch, which Madde 172 retired.
    assert said.index("write_plan") < said.index("2. The characters")


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


def test_the_scenario_is_opened_by_the_tool_that_opens_one():
    # The observed failure wears two masks: everything gathered in chat and written at the end, or
    # a new file per step. One birth rules out both, and since Madde 167 the tool enforces it --
    # start_scenario refuses a name that is taken, so the text only has to say which step opens it.
    said = _flow()
    assert "start_scenario" in said
    assert said.index("start_scenario") < said.index("3. The places")


def test_the_flow_fills_the_maps_with_the_tools_that_own_them():
    # Madde 168 to 170. Three maps, three tools, and the text names them rather than describing a
    # shape: the model knows a tool's signature and never the file's.
    said = _flow()
    assert "add_character" in said
    assert "add_outfit" in said
    assert "add_location" in said


def test_the_flow_hands_the_frames_to_the_builder():
    # The handoff, and what it now hands over. The flow writes the frames -- Madde 173 gave it a
    # tool that takes a scene whole -- and leaves their actions to the model that writes those.
    said = _flow()
    assert "Generate prompts+" in said
    assert "add_scene" in said


def test_the_scenes_step_writes_the_cast_into_the_frame():
    # The frame is born with its cast (Madde 173), so the step that writes one has to ask who is in
    # it. A scene written without its cast builds into a prompt with nobody in the picture.
    said = _flow()
    assert "who is in it" in said


def test_no_instruction_writes_a_scene_list_file():
    # It existed because a frame had nowhere to keep its brief. Since Madde 173 the scene sentence
    # is a field of the frame, and a second copy in a .md would be the same sentence in two places
    # -- which is the shape every staleness bug in this app has had.
    for skill, said in INSTRUCTIONS.items():
        assert "-scenes.md" not in said, skill
        assert "scene list" not in said, skill


def test_the_builder_picks_up_where_the_flow_stops():
    # The other half of the handoff. What the flow leaves is frames with a scene and no action, so
    # that is what this skill looks for -- and it is how the work resumes after a chat that ran out
    # of room: the file itself says which frames are still waiting.
    said = instruction_for("generate-prompts-plus")
    assert "Start a scenario" in said
    assert "no action" in said


def test_the_handoff_is_a_step_of_its_own():
    # Madde 108: the handoff sat outside the numbered list, and a weak model stops when the list
    # ends -- so the flow went on to write frames instead of naming its heir.
    said = _flow()
    assert "Five steps" in said
    assert "5. The handoff" in said
    assert said.index("5. The handoff") < said.rindex("Generate prompts+")


def test_the_flow_leaves_the_action_to_the_other_skill():
    # It writes the frames now, which it never did before Madde 173 -- but not their actions. That
    # sentence is the whole reason this run has two models, and a flow writing one by hand would be
    # the way round the model kept for writing them.
    said = _flow()
    assert "no action" in said
    assert "write_frame_prompt" not in said


def test_the_craft_rules_left_the_texts_with_the_work(_=None):
    # Two rules used to live in prompt+: a scene sentence is a brief and not text to copy, and
    # neighbouring frames must differ in framing. Both were about writing an action, and since
    # Madde 176 the main model does not write one -- so they moved to the prompt writer's own
    # system prompt, where they are read once by the model they are for.
    from backend.features.workspace.domain.tools import WRITE_FRAME_SYSTEM_PROMPT

    assert "framing and angle" in WRITE_FRAME_SYSTEM_PROMPT
    for skill, said in INSTRUCTIONS.items():
        assert "framing" not in said, skill


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


def test_a_finished_step_is_marked_with_one_edit():
    # Madde 126: closing one step cost three plan writes in the trial -- write_plan, edit_file,
    # write_plan -- because "marked done" never said which of the two it meant, and write_plan
    # rewrites the whole file. The birth of the plan stays write_plan's; marking is one line.
    said = _flow()
    assert "marked done with one edit_file" in said
    assert "never a rewrite" in said


# --- the ritual openings (Madde 107) --------------------------------------------------------------
#
# The same trial from the skills' side: every turn opened with list_files and write_plan, and the
# schema was fetched again for every edit. The opening moves belong to a chat's first turn, and
# the schema to the one turn that gives the file its shape.


def test_the_opening_moves_belong_to_the_first_turn():
    said = _flow()
    assert "A chat's first turn" in said
    assert "carry on from what the chat already knows" in said


def test_no_instruction_reaches_for_the_listing_tool():
    # Madde 127: the tool is gone, and a text still naming it would send the model after something
    # that cannot answer. The flow's first turn keeps write_plan; the listing that stood before it
    # is what the request now carries on its own.
    for skill, said in INSTRUCTIONS.items():
        assert "list_files" not in said, skill
    assert "first turn opens with write_plan" in _flow()


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_no_instruction_sends_the_model_to_fetch_a_shape(skill):
    # Madde 172. Both texts opened by fetching the schema, because for a while the model really did
    # write the file's shape. It does not any more -- it calls a function -- so a sentence sending
    # it to read the shape first spends a round on a tool that is gone.
    assert "schema" not in instruction_for(skill).lower()


def test_the_builder_no_longer_writes_frames_at_all():
    # Madde 128 put add_frames in this text; Madde 173 replaced the tool and Madde 178 moved the
    # job. The frames arrive written -- what this skill does to a file is fill in the sentences and
    # build. A text still naming the adding tools would have two skills writing frames into one
    # file, each from a different idea of what is already there.
    said = instruction_for("generate-prompts-plus")
    assert "add_scene" not in said
    assert "add_frames" not in said


def test_a_complaint_is_written_again_rather_than_edited():
    # Two roads and the text names both, because they answer different complaints. One frame's
    # sentence is wrong: call the writer again with a note. Somebody looks wrong in every frame
    # they are in: that is the map entry, and one update reaches all of them.
    said = instruction_for("generate-prompts-plus")
    assert "note" in said
    assert "update_" in said


def test_no_instruction_touches_a_structure_file_as_text():
    # Madde 171 shut that door in the code; a text still telling the model to walk through it would
    # spend a round being refused. edit_file is not gone -- it writes documents -- so this asks
    # about the pairing rather than about the name.
    for skill, said in INSTRUCTIONS.items():
        assert "edit_file on the frame" not in said, skill
        assert "structure file's maps" not in said, skill


def test_the_flow_reads_a_plan_it_found_rather_than_one_it_just_wrote():
    # Madde 134. Step 1 says the first turn opens with write_plan, and two sentences later that a
    # plan already there is the memory to read. The model did both: it wrote one, and then a plan
    # really was already there -- its own. The sentence means a plan from before this chat and
    # never said so, and the eighth trial paid a whole round for the gap.
    said = _flow()
    assert "already there when the chat opened" in said
    assert "A plan already there is that memory" not in said


def test_prompt_plus_closes_with_the_file_rather_than_a_menu():
    # Madde 130. The base already forbids the closing menu (112), but the skill text is the last
    # thing in the request (93) and said nothing about closing -- so the trial's build turn read
    # its own output back, printed 25 prompts into the chat, and offered three choices over a file
    # already sitting in the project. A text that goes quiet is a text a weak model writes over.
    said = instruction_for("generate-prompts-plus")
    assert "The built file is the answer" in said
    assert "never printed back" in said


def test_the_texts_stay_short_enough_to_be_read():
    # Five runs of patches doubled the texts, and a weak model stops reading the middle. The cap
    # is the guard against swelling back: from here a sentence enters only by deleting one.
    assert len(_flow().split()) <= 450
    assert len(instruction_for("generate-prompts-plus").split()) <= 300
