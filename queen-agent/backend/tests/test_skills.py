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
    # It went to the schema tool in Madde 96, and the shape half of that died in 159 as the tools
    # took the shape over. Either way it is not here: carried in a skill's text it would be paid
    # for every turn, and copied again the day a second skill writes the same file.
    said = instruction_for("generate-prompts-plus")
    assert '"frames"' not in said and '"outfits"' not in said


def test_no_instruction_fetches_a_schema_any_more():
    # Madde 159. The tool is gone, and a text still naming it would spend the model's first round
    # on a refusal.
    assert not [skill for skill in INSTRUCTIONS if "schema" in INSTRUCTIONS[skill].lower()]


def test_the_structured_instruction_hands_the_frames_to_the_writer():
    # Batches of five, then one call per frame, and from Madde 155 no calls of its own at all: the
    # frames are already there carrying their scenes, and write_frame_prompt fills them from a
    # request each. What is left for this skill is deciding, not typing.
    said = instruction_for("generate-prompts-plus")
    assert "write_frame_prompt" in said
    # It used to name create_file and edit_file, back when a structure file was written as text.
    # Madde 151 shut both on one, so naming them here would walk the model into a refusal.
    assert "create_file" not in said and "edit_file" not in said


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
    # until Madde 96 moved it out of the texts entirely. Madde 159 scattered what was left of it
    # into the tools each rule is about, so the nail is on the rules rather than on the list: a
    # numbered rulebook anywhere in a skill's text is the thing that must not come back.
    for skill, said in INSTRUCTIONS.items():
        assert "1. " not in said or "step" in said.lower(), skill


# --- the flow that walks the user through it (Madde 101) -----------------------------------------


def _flow():
    return instruction_for("start-a-scenario")


def test_the_flow_writes_the_plan_before_it_asks_anything():
    # Step one whatever the user's opening sentence was. Without it the flow starts somewhere
    # different every time, and has nowhere to keep its place.
    said = _flow()
    assert "write_plan" in said
    # Before the characters, which is where the work actually starts. It used to be measured against
    # the schema fetch that opened step 2; Madde 159 took that away and the step itself is the mark.
    assert said.index("write_plan") < said.index("The characters")


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


def test_the_scenes_step_calls_the_tool_rather_than_writing_a_file():
    # Madde 155. The list used to be a second file matched to the frames by position, and the
    # matching took a paragraph of instruction nobody could see go wrong. A sentence written into
    # the frame it is for has nothing left to match.
    said = _flow()
    assert "add_scene" in said
    assert "one sentence" in said
    assert "their own language" in said  # the brief follows the reader; it never reaches a prompt


def test_no_step_writes_a_separate_scene_list(tmp_path):
    # Both texts, because a file only one of them stopped writing is a file the other still looks
    # for.
    assert "-scenes" not in _flow()
    assert "-scenes" not in instruction_for("generate-prompts-plus")


def test_a_finished_step_reaches_the_plan():
    # The flow promises a fresh chat can carry on from the step left open. A plan nobody updates
    # shows no step as open, so the promise stands only if ending a step writes into the plan.
    assert "marked done" in _flow()


def test_the_structure_file_is_born_once():
    # The observed failure wears two masks here: everything gathered in chat and written at the
    # end, or a new file per step. One birth at the characters step rules out both.
    said = _flow()
    assert "born once" in said
    assert "never a second file" in said


def test_the_flow_hands_the_frames_to_the_builder():
    # K40 overturned K32 (28 Aug): writing action and camera detail is heavy work, and the flow's
    # asking rhythm is not where it belongs. Since Madde 155 the flow does open the frames -- but
    # only as far as their sentences, and what the picture holds is still its heir's.
    said = _flow()
    assert "Generate prompts+" in said
    assert "no prompt to build from" in said


def test_the_handoff_names_one_file():
    # There used to be a pair, found by name, and the convention had to be pinned or the handoff
    # rested on a guess. One file since Madde 155, so there is nothing to pair.
    said = _flow()
    assert "bar-scene.json" in said
    assert "bar-scene-scenes" not in said


def test_the_builder_picks_up_where_the_flow_stops():
    # The other half of K40. The handover used to be a second file read by name and matched to the
    # frames by position, and resuming meant counting the shortfall. Since Madde 155 the frames are
    # already there with their sentences in them, so there is nothing to find and nothing to count:
    # what is left over is what has no prompt yet, and the writer answers that by itself.
    said = instruction_for("generate-prompts-plus")
    assert "Start a scenario" in said
    assert "carry a scene each" in said
    assert "picks up exactly those" in said


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
    # The observed failure: scene sentences retold as the action, word for word. The line that
    # holds that door moved with the work (Madde 155) -- the skill no longer writes a frame, so it
    # is told to the model that does.
    from backend.features.workspace.domain.tools import WRITING

    assert "never text to copy" in WRITING


def test_the_writer_is_not_asked_for_what_it_cannot_see():
    # Ten scenes came back as one framing, and the rule against it said neighbouring frames must
    # differ. Madde 155 gave each frame a request that carries only its own scene, so the writer has
    # no neighbour to differ from -- and a rule written to be broken teaches that rules can be. The
    # file's whole shape is the main model's to see, and its to fix.
    from backend.features.workspace.domain.tools import WRITING

    assert "neighbour" not in WRITING.lower()
    assert "the same framing and angle" not in instruction_for("generate-prompts-plus")


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
# schema was fetched again for every edit. The opening moves belong to a chat's first turn. The
# second ritual answered itself in Madde 159 -- there is nothing left to fetch.


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


def test_no_instruction_opens_with_a_fetch():
    # The pair that told each skill to fetch the schema once, and where. Madde 159 left neither of
    # them anything to fetch, and a text still sending the model after it would spend the first
    # round of every run on a refusal.
    for skill, said in INSTRUCTIONS.items():
        assert "fetch" not in said.lower(), skill


def test_prompt_plus_adds_frames_with_the_tool_rather_than_an_edit():
    # Madde 128. The text was the whole reason the model reached for edit_file to append: it said
    # so in as many words, and a weak model follows what it is shown.
    said = instruction_for("generate-prompts-plus")
    assert "write_frame_prompt" in said
    assert "Add frames with edit_file" not in said
    # The rhythm outlived the batches and then outlived the calls. What it was for -- quality
    # falling away at the end of a long answer -- is the shape of the tool now: one request per
    # frame, none of them carrying the others (Madde 155).
    assert "five" not in said
    assert "add_frames" not in said


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
