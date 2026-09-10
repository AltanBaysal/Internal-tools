import pytest

from backend.features.workspace.domain.skills import INSTRUCTIONS, instruction_for

# Written out rather than imported: the picker's ids live in the frontend's skills.js and Python
# cannot read it. If the two ever drift apart, a skill answers with no instruction at all -- so the
# match is pinned here, in words.
ALL_SKILLS = ["edit-prompts", "start-a-scenario"]

# Madde 94's deletion. The names live here because the proof of a deletion is an absence, and only a
# test that looks for it sees one -- putting any of them back has to come past this line.
DELETED = [
    "create-scenario",
    "create-character-prompt",
    "split-into-frames",
    "generate-prompts",
    "verify-prompts",
    # Madde 186. Its building half went into the flow, which can finish the job in one turn since
    # Madde 185 made the actions one call; what was left of it is Edit prompts, under a name of its
    # own. A record written before today still names this one, and that turn runs on the base text.
    "generate-prompts-plus",
]


def _flow():
    return instruction_for("start-a-scenario")


def _edit():
    """Madde 186's skill: what is wrong with prompts that already exist."""
    return instruction_for("edit-prompts")


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_in_the_menu_carries_an_instruction(skill):
    assert instruction_for(skill).strip()


def test_the_menu_and_the_instructions_carry_the_same_names():
    # Two since Madde 101, and since Madde 186 they are the two halves of the work rather than two
    # ways into it: one makes a scenario and finishes it, the other fixes what is already made. A
    # name in the menu with no instruction here is a turn that quietly runs on the base text alone.
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
    said = _edit()
    assert '"frames"' not in said and '"outfits"' not in said


def test_no_instruction_names_a_tool_that_is_gone():
    # Madde 172, and the guard m127 cost a trial for the want of. A skill text naming a tool that
    # does not exist tells the model to make a call that comes back "there is no tool called that",
    # and the model has no way to find that out except by spending a round on it.
    #
    # Asked of every underscored word rather than of a list written here: a tool deleted later has
    # to be caught by this test existing, not by somebody remembering to add its name.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    # pov_ is not a tool, it is the prefix Madde 182 names a half-seen character by, and it is
    # written as the bare prefix rather than pov_kyle so that what is exempt here is a naming rule
    # and not somebody's name. The reason above survives it: a tool deleted later still has nowhere
    # to hide, because this exemption is one word and it is not a tool's.
    known = {spec["function"]["name"] for spec in TOOL_SPECS} | {"pov_"}
    for skill, said in INSTRUCTIONS.items():
        named = {word.strip(".,;:") for word in said.split() if "_" in word}
        assert named <= known, (skill, named - known)


def test_the_flow_fills_every_waiting_frame_then_builds():
    # Madde 185 made the actions one call, and Madde 186 gave that call to the flow: the job it
    # used to hand over is now its last step. Twenty-one frames were twenty-one rounds, and a text
    # saying "one at a time" is what sent the model round that loop.
    said = _flow()
    assert "write_missing_actions" in said
    assert said.index("write_missing_actions") < said.rindex("build_prompts")


def test_the_flow_no_longer_offers_a_look_at_one_character():
    # Madde 206, and the reading's 18th correction before it: the second step offered a preview of
    # one character and carried on if it was declined, which is a side door written into a flow --
    # a line the model reads on every scenario for a tool the scenario is not built from.
    #
    # Its own test rather than left to test_no_instruction_names_a_tool_that_is_gone: that one would
    # force the sentence out as a consequence of the tool going, and say nothing about why the
    # sentence itself was not wanted.
    assert "build_character_prompts" not in _flow()


def test_no_instruction_walks_the_frames_one_at_a_time():
    # The old sentence goes rather than standing beside the new one: two ways of doing one job in
    # one text is the model choosing, and the expensive one reads as the careful one.
    for skill, said in INSTRUCTIONS.items():
        assert "one at a time" not in said, skill


def test_a_wrong_line_is_corrected_in_the_editors_own_turn():
    # Madde 201. The skill's reader has read the line and heard what the user said about it, and
    # the road it used to take squeezed both of those into a note for somebody else to work from.
    said = _edit()
    assert "update_frame" in said
    assert "yourself" in said


def test_the_editor_sends_a_wrong_line_to_the_agent_itself():
    # Madde 208. Both roads out of a wrong line lead to the same place now: correcting one, and
    # wanting one afresh from the scene, are the agent's own writing. Neither goes back to a model
    # that has not read the line -- which is the road 201 argued against and this madde closes.
    said = _edit()
    assert "write_frame_prompt" not in said
    assert "update_frame" in said


def test_the_editor_forbids_assembling_a_prompt_by_hand():
    said = _edit()
    # Without this the skill loses the only thing that makes it different.
    assert "do not assemble" in said.lower()
    assert "build_prompts" in said


def test_the_editor_is_about_what_already_exists():
    # Madde 186 split the work in two. This half never makes a scenario -- it is reached when one
    # is already built and something in it is wrong -- and the text has to say so, or it reads as
    # a second road into the same job.
    said = _edit()
    assert "already" in said
    assert "build_prompts again" in said


def test_a_change_goes_through_the_file_rather_than_the_prompt_list():
    # The prompt file is derived: patched by hand it stops matching the structure it came from.
    assert "rebuilt rather than patched" in _edit()


# --- somebody the camera is standing in (Madde 182) -----------------------------------------------
#
# Being in a frame's cast is all or nothing, and the builder writes the whole of an entry. In a POV
# frame none of that person is in shot, and an SDXL-family model with no body to hang those tags on
# hangs them on the one that is there -- the woman comes back with the man's hair, and a picture
# holding one person is asked for 1girl and 1boy at once.
#
# The user's decision of 5 Sep is a rule rather than a field: a second character, pov_ and their
# name, short and countless and wearing nothing, opened when the character is opened rather than
# when a POV frame turns up. Nothing in the code moves -- add_character already takes that name and
# a cast already names whoever it likes.


def test_the_flow_opens_a_pov_entry_beside_each_character():
    # Opened with the character, not when a frame needs one: needing one happens in the middle of a
    # correction turn, which is the worst moment to send the model back to the maps.
    said = _flow()
    assert "pov_" in said
    assert said.index("pov_") > said.index("2. The characters")


def test_a_pov_entry_carries_neither_a_count_nor_an_outfit():
    # Both are the leak. A count makes the picture claim a person it does not show, and an outfit
    # dresses the frame with clothes nobody in it is wearing.
    said = _flow().lower()
    assert "no count" in said
    assert "no outfit" in said


def test_a_pov_frame_names_the_pov_entry_in_its_cast():
    # The other half, and it lives here because "make this one POV" arrives during a correction --
    # this skill's turn, not the flow's.
    assert "pov_" in _edit()


def test_no_instruction_carries_the_prompt_rules():
    # It was one text with two readers until Madde 94 took the checking skill away, and one reader
    # until Madde 96 moved it out of the texts entirely. Madde 172 moved it once more -- to the six
    # tools that take tags, where it sits beside the parameter it governs and is read while the tool
    # is being chosen. A copy back here would be paid for by every turn, including the ones writing
    # no tags at all.
    from backend.features.workspace.domain.prompt import SDXL_PROMPT_RULES

    assert not [skill for skill in INSTRUCTIONS if SDXL_PROMPT_RULES in INSTRUCTIONS[skill]]


# --- the flow that walks the user through it (Madde 101) -----------------------------------------


def test_the_flow_writes_the_plan_before_it_asks_anything():
    # Step one whatever the user's opening sentence was. Without it the flow starts somewhere
    # different every time, and has nowhere to keep its place.
    #
    # Madde 207: the tool is create_file, and the step's own sentence is what says a plan is boxes.
    said = _flow()
    assert "create_file" in said
    # Ordered against the next step rather than against the schema fetch, which Madde 172 retired.
    assert said.index("create_file") < said.index("2. The characters")


def test_the_flow_carries_on_from_a_plan_that_is_already_there():
    # How a conversation that grew too long is continued: files belong to the project rather than
    # the chat, so a new chat finds the plan and picks up where it stopped. Since Madde 198 that
    # place is readable rather than described: the first box nobody filled.
    assert "the first step whose box is empty" in _flow()


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
    # The flow promises a fresh chat can carry on from where the work stopped. A plan nobody updates
    # shows no step as open, so the promise stands only if ending a step writes into the plan.
    assert "mark_step_done" in _flow()


def test_the_scenario_is_opened_by_the_tool_that_opens_one():
    # The observed failure wears two masks: everything gathered in chat and written at the end, or
    # a new file per step. One birth rules out both, and since Madde 167 the tool enforces it --
    # start_scenario refuses a name that is taken, so the text only has to say which step opens it.
    #
    # Madde 186 moved that step from the characters to the plan, because what named the file was
    # the context. Madde 198 takes the context away, so the birth goes back where it was: the first
    # character is what the file can be named after.
    said = _flow()
    assert "start_scenario" in said
    assert said.index("2. The characters") < said.index("start_scenario") < said.index("3. The places")


def test_an_approved_step_is_ticked_by_the_tool_that_ticks_one():
    # The rule was already written and asked for edit_file, which is a free edit -- so what a ticked
    # step looks like was the model's to invent, and the next turn did not recognise it. A plan
    # nobody can read the progress off is a plan that has lost its one job (Madde 198).
    said = _flow()
    assert "mark_step_done" in said
    assert "edit_file" not in said


def test_the_flow_fills_the_maps_with_the_tools_that_own_them():
    # Madde 168 to 170. Three maps, three tools, and the text names them rather than describing a
    # shape: the model knows a tool's signature and never the file's.
    said = _flow()
    assert "add_character" in said
    assert "add_outfit" in said
    assert "add_location" in said


def test_the_flow_writes_the_frames_itself():
    # Madde 173 gave it a tool that takes a scene whole, and since Madde 186 the frames it writes
    # are finished in the same flow rather than handed to somebody else.
    said = _flow()
    assert "add_scene" in said


def test_the_flow_hands_off_to_nobody():
    # Madde 186. Deneme 3 broke the actions across two turns because the stage would not fit in
    # one; Madde 185 made it one call, and with that the reason for a second skill went with it.
    said = _flow()
    # Asserted first, and not for company: a test looking for the absence of a name passes on a
    # text that was never read at all, which is how eleven tests in this run went green while red.
    assert "5. The prompts" in said
    assert "Generate prompts+" not in said
    assert "skills menu" not in said


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


def test_the_editor_starts_from_a_complaint_rather_than_a_blank_page():
    # What reaches this skill is a prompt file somebody has looked at and does not like. It never
    # opens a scenario -- that road is the flow's, end to end, since Madde 186.
    said = _edit()
    assert "start_scenario" not in said
    assert "wrong" in said


STEPS = ("1. The plan", "2. The characters", "3. The places", "4. The scenes", "5. The prompts")
"""The flow's steps, in the order they run (Madde 198).

Read by the two tests below and by the one that places start_scenario. Madde 186 had six of these
and the first was the context; that question is gone, and the numbers moved with it.
"""


def test_the_flow_runs_five_numbered_steps():
    # Madde 108: a stage outside the numbered list is a stage a weak model walks past, because it
    # stops when the list ends. Five since Madde 198 -- the context question in front of them was
    # the one thing a user had to answer before any work could start.
    said = _flow()
    assert "Five steps" in said
    assert "Six steps" not in said
    for step in STEPS:
        assert step in said, step


def test_the_steps_are_written_in_the_order_they_run():
    # The order is the whole of what the text is: a model reading them out of order would ask for
    # the cast before there is a plan to put it in.
    said = _flow()
    places = [said.index(step) for step in STEPS]
    assert places == sorted(places)


def test_the_flow_asks_for_no_context_before_it_starts():
    # Madde 186 added that question so the plan's opening line would carry an answer rather than a
    # guess. Madde 198 takes it back out (user, 8 September): the cost was a question standing in
    # front of every scenario. What goes with it is the promise -- a plan that opened by saying what
    # the work was for would be back to guessing.
    said = _flow()
    assert "what it is for" not in said
    assert "The context" not in said


def test_the_flow_never_writes_an_action_by_hand():
    # It writes the frames, which it never did before Madde 173 -- but not their sentences. That
    # is the whole reason this run has two models, and a flow writing one itself would be the way
    # round the model kept for writing them.
    said = _flow()
    assert "no action" in said
    assert "write_missing_actions" in said


def test_the_craft_rules_left_the_texts_with_the_work(_=None):
    # Two rules used to live in prompt+: a scene sentence is a brief and not text to copy, and
    # neighbouring frames must differ in framing. Both were about writing an action, and since
    # Madde 176 the main model does not write one -- so they moved to the prompt writer's own
    # system prompt, where they are read once by the model they are for.
    from backend.features.workspace.domain.prompt import WRITE_FRAME_SYSTEM_PROMPT

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


def test_the_flow_finishes_with_the_build():
    # Turned around by Madde 186. The text used to say build_prompts is never called here, because
    # the file the flow left held no action to build from; now the step before it writes them all,
    # and stopping short would leave the user one manual call from what they asked for.
    said = _flow()
    assert "build_prompts is never called here" not in said
    assert said.rindex("build_prompts") > said.index("5. The prompts")


def test_the_closing_message_offers_nothing_and_asks_nothing():
    # The closing message came back as an offer wearing a question mark. "It is the last word"
    # was already pinned; this pins that no offer and no question ride on it.
    assert "offers nothing and asks nothing" in _flow()


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_opens_with_what_the_work_is_for(skill):
    # 29 Aug, the user's own sentence: if we never give the model the context of what we are
    # doing, where would it know it from? Neither text said what the prompts are for.
    assert "prompts for an SDXL-family image model" in instruction_for(skill)


def test_the_plan_no_longer_opens_with_a_line_of_context():
    # Madde 186 asked for that line and Madde 198 takes it back, with the question that fed it. The
    # claim is not dropped, it is turned around: with nobody asked what the work is for, a plan
    # opening with it would be back to guessing -- which is the thing 186 was written against.
    said = _flow()
    assert "opens with one line of context" not in said
    assert "inherits the work" not in said


def test_the_flow_opens_as_a_persona():
    # Madde 123, the user's own framing: you are an expert scenario writer laying the ground,
    # and an expert prompt writer takes over. A role holds a weak model better than a rule list.
    assert _flow().startswith("You are an expert scenario writer")


def test_the_editor_opens_as_a_persona():
    assert _edit().startswith("You are an expert SDXL prompt writer")


def test_a_finished_step_is_closed_without_rewriting_the_plan():
    # Madde 126's finding, and it still holds: closing one step cost three plan writes in the trial,
    # because "marked done" did not say which tool it meant and the plan tool of the day rewrote the
    # whole file.
    # 126 answered it with edit_file, 198 with a tool that fills one box -- the same rule, now kept
    # by the code rather than by a sentence asking the model to be careful.
    said = _flow()
    assert "mark_step_done" in said
    assert "touches nothing else" in said


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
    # that cannot answer. The flow's first turn still writes the plan; the listing that stood before
    # it is what the request now carries on its own.
    for skill, said in INSTRUCTIONS.items():
        assert "list_files" not in said, skill
    assert "A chat's first turn" in _flow()


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_no_instruction_sends_the_model_to_fetch_a_shape(skill):
    # Madde 172. Both texts opened by fetching the schema, because for a while the model really did
    # write the file's shape. It does not any more -- it calls a function -- so a sentence sending
    # it to read the shape first spends a round on a tool that is gone.
    assert "schema" not in instruction_for(skill).lower()


def test_the_editor_writes_no_frames_at_all():
    # Madde 128 put add_frames in this text; Madde 173 replaced the tool and Madde 178 moved the
    # job. The frames arrive written -- what this skill does to a file is correct it. A text still
    # naming the adding tools would have two skills writing frames into one file, each from a
    # different idea of what is already there.
    said = _edit()
    assert "add_scene" not in said
    assert "add_frames" not in said


def test_a_complaint_is_written_again_rather_than_edited():
    # Two roads and the text names both, because they answer different complaints. One frame's
    # sentence is wrong: call the writer again with a note. Somebody looks wrong in every frame
    # they are in: that is the map entry, and one update reaches all of them.
    said = _edit()
    assert "note" in said
    assert "update_" in said


def test_a_complaint_is_told_apart_by_where_the_fault_lives():
    # Two roads and the text names both, because they answer different complaints. One frame's
    # sentence is wrong: that is the frame's own line. Somebody looks wrong in every frame they are
    # in: that is their entry, and one update reaches all of them.
    said = _edit()
    assert "update_frame" in said
    assert "update_character" in said


def test_no_instruction_touches_a_structure_file_as_text():
    # Madde 171 shut that door in the code; a text still telling the model to walk through it would
    # spend a round being refused. edit_file is not gone -- it writes documents -- so this asks
    # about the pairing rather than about the name.
    for skill, said in INSTRUCTIONS.items():
        assert "edit_file on the frame" not in said, skill
        assert "structure file's maps" not in said, skill


def test_the_flow_reads_a_plan_it_found_rather_than_one_it_just_wrote():
    # Madde 134. Step 1 says the first turn writes the plan, and two sentences later that a
    # plan already there is the memory to read. The model did both: it wrote one, and then a plan
    # really was already there -- its own. The sentence means a plan from before this chat and
    # never said so, and the eighth trial paid a whole round for the gap.
    said = _flow()
    assert "already there when the chat opened" in said
    assert "A plan already there is that memory" not in said


def test_the_editor_closes_with_the_file_rather_than_a_menu():
    # Madde 130. The base already forbids the closing menu (112), but the skill text is the last
    # thing in the request (93) and said nothing about closing -- so the trial's build turn read
    # its own output back, printed 25 prompts into the chat, and offered three choices over a file
    # already sitting in the project. A text that goes quiet is a text a weak model writes over.
    said = _edit()
    assert "The built file is the answer" in said
    assert "never printed back" in said


def test_the_texts_stay_short_enough_to_be_read():
    # Five runs of patches doubled the texts, and a weak model stops reading the middle. The cap
    # is the guard against swelling back: from here a sentence enters only by deleting one.
    #
    # The flow's stays where it was through Madde 186, which was the roadmap's own condition -- it
    # gains a step and loses one, so the two cancel. The other comes down from 300, because that
    # text gave half its job away: building went to the flow, and what is left is the correction.
    # A cap that comes down is a cap that cannot quietly take the old work back.
    assert len(_flow().split()) <= 450
    assert len(_edit().split()) <= 200
