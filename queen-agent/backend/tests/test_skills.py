import pytest

from backend.features.workspace.domain.skills import INSTRUCTIONS, instruction_for

# Written out rather than imported: the picker's ids live in the frontend's skills.js and Python
# cannot read it. If the two ever drift apart, a skill answers with no instruction at all -- so the
# match is pinned here, in words.
ALL_SKILLS = ["edit-prompts", "krea-edit", "krea-start-scenario", "start-a-scenario"]
# Madde 492: two skills a model, and each opens by sending the model to its own guide (the user, 22
# October: "bizim skillimizin başında söyleriz git ve şu skili oku önce").
SDXL_SKILLS = ["start-a-scenario", "edit-prompts"]
KREA_SKILLS = ["krea-start-scenario", "krea-edit"]
FIRST_LINE = {
    "start-a-scenario": "Read sdxl-prompt-writing.md first.\n\n",
    "edit-prompts": "Read sdxl-prompt-writing.md first.\n\n",
    "krea-start-scenario": "Read krea-prompt-writing.md first.\n\n",
    "krea-edit": "Read krea-prompt-writing.md first.\n\n",
}

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
    # Madde 492, the user's decision of 22 October: "improve skilinin kendisi kalksın". Its checks
    # stay in the SDXL flow's Steps 7 - 11 (6 - 10 until Madde 493), for a new scenario.
    "improve",
]


def _flow():
    return instruction_for("start-a-scenario")


def _edit():
    """Madde 186's skill: what is wrong with prompts that already exist."""
    return instruction_for("edit-prompts")


def _krea_flow():
    """Madde 492's Krea start scenario."""
    return instruction_for("krea-start-scenario")


def _krea_edit():
    """Madde 492's Krea edit."""
    return instruction_for("krea-edit")


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_in_the_menu_carries_an_instruction(skill):
    assert instruction_for(skill).strip()


def test_the_menu_and_the_instructions_carry_the_same_names():
    # Four since Madde 492: a start and an edit for each image model. Madde 186 made a start and an
    # edit the halves of the work rather than two ways into it. A name in the menu with no
    # instruction here is a turn that quietly runs on the base text alone.
    assert sorted(INSTRUCTIONS) == sorted(ALL_SKILLS)


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_opens_by_sending_the_model_to_its_guide(skill):
    # The guides ride in no request on their own (the user, 22 October: "hiçbiri gitmez"), so the
    # skill is what says to read one, and says it first.
    assert instruction_for(skill).startswith(FIRST_LINE[skill])


@pytest.mark.parametrize("skill", KREA_SKILLS)
def test_a_krea_skill_says_nothing_about_sdxl(skill):
    # Each model's rules in its own place (the user, 22 October).
    said = instruction_for(skill)
    assert "krea-prompt-writing.md" in said
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "sdxl" not in said.lower()
    assert "Danbooru" not in said
    assert "The image model is weak" not in said


@pytest.mark.parametrize("skill", SDXL_SKILLS)
def test_an_sdxl_skill_says_nothing_about_krea(skill):
    said = instruction_for(skill)
    assert "sdxl-prompt-writing.md" in said
    assert "krea" not in said.lower()


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


def test_no_instruction_names_a_tool():
    # Madde 393, the owner's decision of 30 September: a skill text says what to do, and the model
    # is strong enough to pick the tool. A text naming no tool also cannot name one that is gone --
    # Madde 172's guard, which m127 cost a trial for the want of, holds by this one.
    #
    # Asked of every underscored word rather than of a list written here: a tool added later has to
    # be caught by this test existing, not by somebody remembering to add its name. pov_ went in the
    # same item, so nothing is exempt.
    for skill, said in INSTRUCTIONS.items():
        assert "Build the prompts" in said, skill
        # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
        assert not [word for word in said.split() if "_" in word], skill


def test_no_instruction_names_the_bulk_writer():
    # Madde 395, the owner's decision of 30 September: the main model writes each frame's action
    # itself, and the tool that handed them to a second model is gone.
    for skill, said in INSTRUCTIONS.items():
        assert "write_missing_actions" not in said, skill


def test_the_frames_are_updated_one_at_a_time_from_the_scene():
    # Madde 393 turns Madde 124's sentence around. One frame at a time was dropped as the expensive
    # road; the owner, 30 September, takes the cost on purpose -- the frame step has to get each
    # frame right before any check sees it. Each frame starts from its scene, whose first moment the
    # photo is. Step 6 since Madde 493 put the orientation question in front.
    said = _step(6)
    assert "- Update the frames one at a time.\n" in said
    assert "first read the scene of the frame" in said
    assert "the first moment of the scene" in said


def test_the_frame_step_says_what_is_true_before_what_to_do():
    # The owner: the rules are context, and the work sits under a heading of its own.
    said = _step(6)
    places = [said.index(part) for part in ("Context", "Rule 1:", "Rule 7:", "Work")]
    assert places == sorted(places)
    assert said.index("Work") < said.index("Update the frames")


def test_the_frame_step_carries_the_rules_of_the_checks():
    # Madde 393, the owner: the checks catch what slipped, and Step 6 writes the frame right in the
    # first place -- one photo, simple enough for the image model, and every visible part of an NSFW
    # scene named directly.
    said = _step(6)
    assert "The whole prompt of the frame must describe only one photo." in said
    assert "must be simple enough for the weak image model" in said
    assert "as in penis or vagina. Never use a euphemism." in said


def test_the_frame_step_frames_the_photo_for_the_orientation():
    # Madde 493, the user's decision of 22 October: the prompts frame the photo for the orientation
    # the user chose. A rule of the SDXL guide, kept in the frame step beside the six it copies.
    said = _step(6)
    assert "Rule 7: The photo has the orientation of the video, landscape or portrait." in said
    assert "to fit the orientation" in said


def test_the_flow_no_longer_offers_a_look_at_one_character():
    # Madde 206, and the reading's 18th correction before it: the second step offered a preview of
    # one character and carried on if it was declined, which is a side door written into a flow --
    # a line the model reads on every scenario for a tool the scenario is not built from.
    #
    # Its own test rather than left to test_no_instruction_names_a_tool_that_is_gone: that one would
    # force the sentence out as a consequence of the tool going, and say nothing about why the
    # sentence itself was not wanted.
    assert "build_character_prompts" not in _flow()


def test_the_editor_makes_the_change_itself():
    # Madde 201 and 208: the editor has read the line and heard what the user said about it, so the
    # change is its own writing rather than a note for a model that has read neither. Since Madde
    # 393 the text says so without naming the tool.
    assert "- Make the change in the scenario file.\n" in _edit()


def test_the_editor_changes_the_structure_rather_than_the_prompt_by_hand():
    # Without this the skill loses the only thing that makes it different: the prompt file is
    # derived, and patched by hand it stops matching the structure it came from. The owner, 30
    # September: say the file is auto-generated, and that it is not edited by hand.
    said = _edit()
    assert (
        "The prompt file is auto-generated from the scenario file. Do not edit the prompt file."
        in said
    )
    assert "Build the prompts again." in said


def test_the_editor_is_about_what_already_exists():
    # Madde 186 split the work in two. This half never makes a scenario -- it is reached when one
    # is already built and something in it is wrong -- and the text has to say so, or it reads as
    # a second road into the same job.
    assert "You change an existing scenario JSON." in _edit()


# --- what the camera shows only part of (Madde 182, widened by Madde 393) ------------------------
#
# Being in a frame's cast is all or nothing, and the builder writes the whole of an entry. A tag the
# camera angle hides has no body to hang on, and an SDXL-family model hangs it on the one that is
# there -- the woman comes back with the man's hair. Madde 182 answered the POV frame alone, with a
# pov_ entry opened beside each character. The owner, 30 September: every entry -- a character, an
# outfit, a place -- can have a version for a camera angle that shows only part of it, and one made
# for an earlier frame is used again. So pov_ is gone, and the rule sits in the frame step, Step 6.


def test_the_frame_step_names_the_most_common_mistake():
    # The owner: the biggest problem there is, so the reason stands in front of the rules.
    said = _step(6)
    assert "The most common mistake: a tag hidden by the camera angle goes onto another" in said
    assert said.index("The most common mistake") < said.index("Rule 1:")


@pytest.mark.parametrize("kind", ["character", "outfit", "place"])
def test_an_entry_is_used_only_when_the_camera_angle_shows_all_of_it(kind):
    said = _step(6)
    assert f"If one of the {kind}'s entries fits the camera angle, use the entry." in said
    assert "An entry fits when every tag of the entry is meant to be in the photo." in said
    assert "If no entry fits, add a new entry with only the tags meant to be in the photo." in said


def test_no_instruction_opens_a_pov_entry():
    assert "can have more than one entry, for different camera angles" in _step(6)
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    for skill, said in INSTRUCTIONS.items():
        assert "pov_" not in said, skill


def test_no_instruction_carries_a_whole_guide():
    # Madde 453 gathered the rules into one document, and Madde 492 made it one of two guides the
    # skill sends the model to read. The guide carries a copy of the flow's image-model rules, and
    # the skills keep theirs on purpose -- the model is weak (the user, 10 October: "Evet, kopyası
    # belgeye de girsin"). A whole guide copied into a skill would be a second one in the same turn.
    from backend.features.workspace.domain.prompt import GUIDES

    for name, guide in GUIDES.items():
        assert not [skill for skill in INSTRUCTIONS if guide in INSTRUCTIONS[skill]], name


def test_a_place_gets_a_mirror_only_when_the_user_asks():
    # Madde 453 gives the places step (Step 4 since Madde 493) the same exception the SDXL document
    # has, so the two texts agree (the
    # user, 29 September: a mirror goes in only when the user asks for one).
    said = _step(4).lower()
    assert "mirror" in said
    assert "user asks" in said


# --- the flow that walks the user through it (Madde 101) -----------------------------------------


def test_the_flow_takes_them_from_the_notes_when_the_work_carries_on():
    # A fresh chat carries on from the plan (Step 2), and would ask again what the notes file
    # already holds.
    assert "take the orientation and the video length from the notes file instead" in _step(1)


def test_the_flow_writes_them_into_a_notes_file_with_the_scenario():
    # The user, 22 October: "SDXL start scenario da <senaryo>-notes.md açsın, yönü ve süreyi oraya
    # yazsın". The notes file is named after the scenario, so it opens in the step that names one.
    said = _step(3)
    assert "Write the orientation and the video length into a notes file." in said
    assert NOTES_EXAMPLE["start-a-scenario"] in said


def test_the_flow_writes_the_plan_before_the_work_starts():
    # The plan opened the flow whatever the user's opening sentence was. Without it the flow starts
    # somewhere different every time, and has nowhere to keep its place. Madde 493 puts the user's
    # two questions in front of it (the user, 22 October), which writes nothing the plan would keep.
    #
    # Madde 207: the step's own sentence is what says a plan is boxes. Since Madde 393 it names no
    # tool, only the file to write.
    assert "write a plan file" in _step(2)


def test_the_plan_gives_both_the_empty_and_the_done_shape():
    # Madde 466. Madde 198 found the model inventing its own mark when only the empty box was
    # written down, and the next turn did not recognise it. Now that the marks say how far the
    # work got, the plan step gives the done shape beside the empty one.
    said = _step(2)
    assert "- [ ] 2." in said
    assert "- [x] 2." in said


def test_the_flow_carries_on_from_a_plan_that_is_already_there():
    # How a conversation that grew too long is continued: files belong to the project rather than
    # the chat, so a new chat finds the plan and picks up where it stopped. Since Madde 198 that
    # place is readable rather than described. Correction 11 says where it is read from: the files.
    assert "carry on from where the work stopped" in _flow()


def test_where_the_work_stopped_is_read_off_the_plans_marks():
    # Correction 11 moved this to the files: a box was filled by a step the model could skip, and a
    # skipped mark sent a fresh chat back to the start. Madde 203 then withdrew the marking. Madde
    # 466 reverses both (the user, 10 October: "işaretlesin model sıkıntı yok, şu an model daha
    # güçlü"): the base tells the model to mark a plan file's done step, so the marks say how far
    # the work got. The files stay as the check -- what the work produced is on disk either way, and
    # a mark can still be skipped.
    said = _step(2)
    assert any(
        all(word in line for word in ("marked", "how far the work got", "files of the project"))
        for line in said.splitlines()
    )
    assert "The files of the project show how far the work got." not in said


def test_a_step_ends_when_the_user_approves_it():
    # Not when an answer is written. One of the flow's rules, and the one that keeps a step from
    # running away with the work.
    assert "and wait for a yes." in _flow()


def test_what_nobody_described_is_asked_for():
    # K34 turned around by Madde 393, the owner: a placeholder is a guess the user never made, and
    # the flow asks for what is missing instead.
    said = _flow()
    assert "Never write a placeholder. If something is missing, ask." in said
    assert "never stop the flow" not in said.lower()


def test_the_scenes_are_written_in_english_with_the_words_in_quotes():
    # K33 and K40 wrote a scene as one sentence in the user's language. The owner, 30 September: the
    # video prompt is written from the scene, so the scene is English, and it can carry what a
    # character says -- in quotes, translated into good English -- which one sentence could not.
    from backend.features.workspace.domain.prompt import ADD_FRAME_SCENE

    said = _step(5)
    assert "- Write each scene in English.\n" in said
    assert "inside quotes, in natural, well-written English" in said
    assert "one sentence" not in said
    # Madde 492: the field's "Never tags" left the tool, and the flow's own step says it instead
    # (the user, 22 October). The field says what a scene is, and no rule about writing one.
    assert "- Write each scene in sentences, never as tags.\n" in said
    assert "in English" not in ADD_FRAME_SCENE
    assert "tags" not in ADD_FRAME_SCENE.lower()


def test_the_scenario_is_opened_once_with_the_characters():
    # The observed failure wears two masks: everything gathered in chat and written at the end, or
    # a new file per step. One birth rules out both, and since Madde 167 the tool enforces it by
    # refusing a name that is taken, so the text only has to say which step opens it.
    #
    # Madde 186 moved that step from the characters to the plan, because what named the file was
    # the context. Madde 198 takes the context away, so the birth goes back where it was: the first
    # character is what the file can be named after. Since Madde 393 without the tool's name.
    assert "Open the scenario file once" in _step(3)


def test_the_flow_names_no_tool_to_mark_a_step():
    # Madde 198 gave the flow a tool that fills one box. The rule before it asked for edit_file,
    # which is a free edit -- so what a ticked step looks like was the model's to invent, and the
    # next turn did not recognise it; closing one step cost three plan writes in the trial, because
    # the plan tool of the day rewrote the whole file (Madde 126). What answered both was the box
    # format, and the format stays. Madde 203 withdrew the tool, and it stays gone.
    said = _flow()
    assert "mark_step_done" not in said
    assert "edit_file" not in said


def test_the_flow_hands_off_to_nobody():
    # Madde 186. Deneme 3 broke the actions across two turns because the stage would not fit in
    # one; Madde 185 made it one call, and with that the reason for a second skill went with it.
    said = _flow()
    # Asserted first, and not for company: a test looking for the absence of a name passes on a
    # text that was never read at all, which is how eleven tests in this run went green while red.
    assert STEPS[5] in said
    assert "Generate prompts+" not in said
    assert "skills menu" not in said


def test_the_frames_cast_is_asked_for_by_the_tool_that_writes_one():
    # The frame is born with its cast (Madde 173), so somebody has to ask who is in it: a scene
    # written without one builds into a prompt with nobody in the picture. Correction 14: the step
    # used to repeat all three fields -- who, what they wear, where -- and add_frame's own signature
    # already asks for them. Two texts describing one call is the shape every drift in this app has
    # had, so the repetition goes and the signature keeps the claim.
    from backend.features.workspace.domain.prompt import ADD_FRAME_CHARACTERS

    assert "who is in the frame" in ADD_FRAME_CHARACTERS.lower()
    assert "who is in it" not in _flow()


def test_a_character_is_named_as_the_user_named_them():
    # Correction 17. Asked for a name, a model invents one -- and the user's own scenario comes back
    # holding somebody they never named. What the user said is the name; where they said nothing,
    # the name is English for what the person is, so it reads as a description rather than a person.
    said = _step(3)
    assert "Use the name from the user. Without a name, use short English words" in said


def test_no_instruction_writes_a_scene_list_file():
    # It existed because a frame had nowhere to keep its brief. Since Madde 173 the scene sentence
    # is a field of the frame, and a second copy in a .md would be the same sentence in two places
    # -- which is the shape every staleness bug in this app has had.
    for skill, said in INSTRUCTIONS.items():
        assert "-scenes.md" not in said, skill
        assert "scene list" not in said, skill


STEPS = (
    "Step 1 -- ask the orientation and the video length",
    "Step 2 -- write the plan",
    "Step 3 -- write the characters and outfits",
    "Step 4 -- write the places",
    "Step 5 -- write the scenes",
    "Step 6 -- update the frames and build the prompts",
    "Step 7 -- fit each scene into the video length",
    "Step 8 -- fit each prompt into one photo",
    "Step 9 -- remove tags hidden by the camera angle",
    "Step 10 -- simplify prompts too hard to draw",
    "Step 11 -- write the negative list",
)
"""The flow's steps, in the order they run (Madde 198, written this way by correction 9).

Read by the tests below and by the ones that place the plan, the scenario file and the build.
Madde 186 had six of these and the first was the context; that question is gone, and the numbers
moved with it. Numbered headings became named ones so that every step reads the same way -- a
heading, then its rules as lines -- and so the loop above them is not read as one more step. Madde
391 adds four: the checks the flow runs on the prompts it has just built. Madde 392 adds the last
one: the negative list, written once the prompts are final. Madde 493 puts one in front: the
orientation and the video length, which every scene and every prompt after it depends on.
"""


def test_the_flow_runs_eleven_numbered_steps():
    # Madde 108: a stage outside the numbered list is a stage a weak model walks past, because it
    # stops when the list ends. Five since Madde 198 -- the context question in front of them was
    # the one thing a user had to answer before any work could start -- nine since Madde 391, whose
    # checks follow the build, ten since Madde 392, whose negative list closes the flow, and eleven
    # since Madde 493, whose question opens it.
    said = _flow().lower()
    assert "eleven steps" in said
    assert "ten steps" not in said
    assert "five steps" not in said
    for step in STEPS:
        assert step.lower() in said, step


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


def test_a_delegation_answers_only_the_question_that_was_asked():
    # 28 Aug: "you decide" arrived with the places answer and the flow read it as authority over
    # everything left -- the scenes question was never asked. A delegation is an answer, and an
    # answer belongs to its question.
    #
    # Madde 393, the owner: one line says it. A delegated step still waits for the yes because every
    # step does, and the plan needs no note of it: its mark says only that the step is done.
    assert '"You decide" is only for the current step.' in _flow()


def test_the_flow_builds_the_prompts_once_the_frames_are_written():
    # Turned around by Madde 186. The text used to say the build is never done here, because the
    # file the flow left held no action to build from; now the same step writes them all, and
    # stopping short would leave the user one manual call from what they asked for. Madde 393: the
    # build comes after the last frame, not after each.
    assert "- After the last frame, build the prompts.\n" in _step(6)
    assert "build_prompts is never called here" not in _flow()


# --- the checks the flow ends with (Madde 391) ----------------------------------------------------
#
# 30 September, the owner: the questions they used to put to the model by hand once the prompts were
# built -- does a scene fit its video, does a prompt hold one photo, does it name only
# what the angle shows, can the image model draw it -- are the flow's own last four steps. Each is
# written in its own step of Start a scenario's text: the first try kept them in a block several
# skills shared, and the owner took it back. Each says why it runs, reviews the built prompt file
# and writes the failing frames down, then fixes only those; none waits for a yes.
#
# Written with the owner line by line: plain sentences, no pronouns, no tool names and no list of
# the file's fields -- the model is strong enough to pick the tool, and a list of fields goes stale
# the day a field is added.

CHECKS = [7, 8, 9, 10]
LAST_WORD = "- Tell the user the prompts and the negative list are complete."


def _step(number):
    """One step of the flow by its own number: from its heading to the next one, or to the end."""
    said = _flow()
    start = said.index(STEPS[number - 1])
    if number == len(STEPS):
        return said[start:]
    return said[start : said.index(STEPS[number])]


@pytest.mark.parametrize("number", CHECKS)
def test_every_check_says_why_then_reviews_then_fixes(number):
    # The owner, 30 September: the reason comes first, under a heading of its own, so the review
    # says only what to do. The model reviews every frame and writes the list down before it fixes
    # anything, and the fix touches the listed frames and nothing else.
    said = _step(number)
    places = [said.index(part) for part in ("Context", "Part 1 -- review", "Part 2 -- fix")]
    assert places == sorted(places)
    assert "Fix only the frames in the review file." in said


@pytest.mark.parametrize("number", CHECKS)
def test_every_check_tells_the_user_what_it_improves(number):
    # The owner: at each check, one very short line saying what is being improved now -- and no
    # report of every change at the end.
    assert "Tell the user in one short line what the step improves." in _step(number)


@pytest.mark.parametrize("number", CHECKS)
def test_every_check_reads_the_built_prompt_file(number):
    # The owner's question is asked of the prompts as build_prompts wrote them: what the image model
    # is handed is the parts joined, and too much often shows only in the sum.
    assert "in the built prompt file" in _step(number).lower()


@pytest.mark.parametrize("number", CHECKS)
def test_every_review_is_written_to_a_file_of_its_own(number):
    # The list is on disk before the fix starts, so a turn that runs out loses nothing. A file for
    # each check rather than one file added to: adding means edit_file, the hand-built anchor Madde
    # 126 was written against, and the flow names no edit_file (only the base does, to mark a plan's
    # steps, since Madde 466). A check that finds nothing writes no file at all (the owner, 30
    # September).
    said = _step(number)
    assert "the frame numbers and the reason for each frame in a review file" in said
    assert f"-review-{number}.md" in said
    assert "write no review file" in said


def test_a_scene_longer_than_its_video_is_shortened_or_split():
    # The owner: a scene becomes a video of exactly the video length -- four seconds until Madde
    # 493 let the user choose it (22 October). A scene that can be written to fit with every event
    # kept is written again; one that cannot is split in two. The model does not choose which events
    # matter -- the owner took that reading out.
    said = _step(7)
    assert "video of exactly the video length" in said
    assert "with every event kept" in said
    assert "split the scene into two scenes of the video length each" in said
    assert "right after the first scene" in said
    # Madde 393: a changed or new frame is written again whole, by the frame step's rules, not only
    # its action -- a split scene's second frame needs its entries chosen for its own camera angle.
    assert "Update each changed frame and each new frame by the rules of Step 6." in said
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "important" not in said
    assert "main event" not in said


def test_a_prompt_is_cut_to_one_photo_without_touching_the_scene():
    # The owner's fourth question: the image model draws one photo, and a prompt describing more
    # breaks the image. The scene stays as Step 7 left it, and no scene is added here.
    said = _step(8)
    assert "more than one photo can hold" in said
    assert "Do not change the scene, and do not add a new scene." in said


def test_a_tag_the_angle_hides_is_taken_out():
    # The owner's second question, widened by the owner: not only a part of a character -- a hidden
    # part of the room or of an outfit is drawn anyway too, and a tag with nowhere to go lands on
    # somebody else. The hair is the owner's example.
    said = _step(9)
    assert "hidden by the camera angle" in said
    assert "draws every tag in the prompt, hidden or not" in said
    assert "another character" in said
    assert "hair" in said


def test_the_last_check_asks_the_owners_question():
    # The owner's first question, asked as they ask it.
    assert "can a weak image model draw the prompt as written?" in _step(10)


@pytest.mark.parametrize("number", [8, 9, 10])
def test_the_image_checks_say_the_model_is_weak(number):
    # The owner: say at the head of each image check that the model is weak and draws every tag. Not
    # in Step 7, which is about the length of the video rather than the image.
    context = _step(number).split("Part 1 -- review")[0]
    assert "The image model is weak and draws every tag in the prompt" in context


def test_the_video_check_says_nothing_of_the_image_model():
    assert "image model" not in _step(7)


@pytest.mark.parametrize("number", [8, 9, 10])
def test_a_fix_is_made_where_the_part_comes_from(number):
    # The prompt file is rebuilt rather than patched, so a part is fixed in the scenario file where
    # it comes from. An entry is shared by every frame naming it, so a change one frame needs alone
    # goes into a new entry.
    said = _step(number)
    assert "comes from in the scenario file" in said
    assert "If other frames use the same entry, add a new entry for the frame instead." in said


@pytest.mark.parametrize("number", CHECKS)
def test_the_checks_name_no_tool_and_no_field(number):
    # The owner, 30 September: do not say which tool -- the model is strong enough to choose -- and do
    # not list the file's fields one by one, or the list breaks the day a field is added.
    said = _step(number)
    assert "Build the prompts again" in said
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert not [word for word in said.split() if "_" in word]
    assert "outfit" not in said
    assert "location" not in said


def test_the_checks_use_no_pronouns():
    # The owner, 30 September: simple English, and no it, that and the like -- the noun is said
    # again instead.
    words = set()
    for number in CHECKS:
        words |= {word.strip('.,:;?"').lower() for word in _step(number).split()}
    assert "frame" in words
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    for pronoun in ("it", "its", "that", "these", "those", "they", "them", "their", "which",
                    "whose"):
        assert pronoun not in words, pronoun


def test_no_instruction_says_what_the_model_cannot_draw():
    # The owner, 30 September: told it cannot draw anything complex, the model really does go and
    # ask for only the simplest things. The last check asks the owner's question instead of making
    # the claim, and Step 6 says what a complex prompt does -- breaks the image -- rather than what
    # the model cannot do (the owner's own line).
    assert "can a weak image model draw" in _step(10)
    assert "A complex prompt breaks the image." in _step(6)
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    for skill, said in INSTRUCTIONS.items():
        said = said.lower()
        assert "what is simple" not in said, skill
        assert "cannot draw" not in said, skill


def test_no_check_reports_every_change():
    # The owner took the per-check report out: the short line at the start of each check is what the
    # user is told.
    assert "Say the changed frames" not in _flow()


@pytest.mark.parametrize("number", [6, 7, 8, 9, 10])
def test_the_build_and_the_checks_wait_for_no_approval(number):
    # How a step runs says every step waits for a yes, and the plan step, Step 2, already says it
    # does not. These
    # say it the same way, and each goes on in the same turn -- the owner: update directly.
    said = _step(number)
    assert "This step waits for no approval." in said
    assert f"Go on to Step {number + 1} in the same turn." in said


def test_the_flow_ends_by_saying_the_prompts_are_complete():
    # The owner: no closing section and no approval line at the end -- tell the user the work is
    # complete, and that is all. Since Madde 392 the negative list is the last thing written, so
    # the closing line names the prompts and the negative list both.
    said = _flow()
    assert said.endswith(LAST_WORD)
    assert "Closing" not in said
    assert "approval" not in _step(11)


# --- the negative list the flow ends with (Madde 392) ---------------------------------------------
#
# 30 September, the owner: the last step of Start a scenario writes one negative list for the whole
# scenario, into a file of its own holding only the tags, separated by commas -- the user copies it
# into queen-editor by hand. The lessons are the owner's of 28 September: a negative tag works on
# the whole photo, so a character's own feature written there is taken off that character too, and
# what keeps a feature is the opposite tags.


def test_the_negative_list_is_for_the_image_model():
    # The owner: say so, it matters -- the scenes go to the video model, the negative to the photo.
    assert "The negative list is for the image model, not the video model." in _step(11)


def test_the_negative_list_keeps_the_characters_apart():
    # The owner: characters' features mixing is the biggest problem, and the list is written for
    # it, from every tag of every entry.
    said = _step(11)
    assert "The biggest problem is the features of the characters mixing" in said
    assert "Read every tag of every entry of the scenario." in said
    assert "Never write a feature of a character into the negative list." in said
    assert "write the opposite tags instead" in said


def test_the_negative_list_is_a_file_of_tags_alone():
    said = _step(11)
    assert "-negative.md" in said
    assert "Write only the tags into the file, separated by commas." in said
    assert "Nothing else goes into the file." in said


def test_the_checks_are_written_in_the_flow_itself():
    # The owner, 30 September: no separate fields. A line of these steps found in another of the
    # module's texts is a line kept somewhere else and joined in -- the shape that was taken back.
    #
    # The editors' texts are left out: each is a skill of its own and joined into nothing, and since
    # Madde 393 every editor closes a change with the same plain line, build the prompts again. The
    # Krea flow is a skill of its own as well (Madde 492). The two guides are no constants since
    # Madde 495, only GUIDES' values, so they are walked by their names.
    from backend.features.workspace.domain import prompt

    skills = ("START_A_SCENARIO", "EDIT_PROMPTS", "KREA_START_SCENARIO", "KREA_EDIT")
    lines = [
        line for number in CHECKS for line in _step(number).splitlines() if line.startswith("- ")
    ]
    assert lines
    texts = [(name, value) for name, value in vars(prompt).items() if isinstance(value, str)]
    for name, value in [*texts, *prompt.GUIDES.items()]:
        if name not in skills:
            for line in lines:
                assert line not in value, (name, line)


# --- Krea: a start and an edit of its own (Madde 492) ---------------------------------------------
#
# 22 October, the user: "Krea start scenario olacak, bir de Krea edit olacak". Simple texts in the
# shape of the SDXL two, carrying no SDXL rule; how a character is described is left open ("şu an bu
# kısıtlamalara girmeyelim"). The Krea flow asks the name and the style when it starts ("senaryo
# başlarken sorulsun"), behind the orientation and the video length since Madde 493, and keeps the
# characters' and places' looks in a notes file.

KREA_STEPS = (
    "Step 1 -- ask the orientation and the video length",
    "Step 2 -- open the scenario with its name and style",
    "Step 3 -- write the scenes",
    "Step 4 -- write the notes",
    "Step 5 -- add the frames with their prompts",
    "Step 6 -- build the prompts",
)


def _krea_step(number):
    """One step of the Krea flow by its own number, cut the way _step cuts the SDXL flow's."""
    said = _krea_flow()
    start = said.index(KREA_STEPS[number - 1])
    if number == len(KREA_STEPS):
        return said[start:]
    return said[start : said.index(KREA_STEPS[number])]


def test_the_krea_flow_runs_six_steps_in_order():
    said = _krea_flow()
    assert "six steps" in said
    places = [said.index(step) for step in KREA_STEPS]
    assert places == sorted(places)


def test_the_krea_flow_asks_the_name_and_the_style_when_it_starts():
    said = _krea_step(2)
    assert "the name of the scenario and for the style of the photos" in said
    assert "Open the scenario file once, with the name and the style." in said


def test_the_krea_flow_writes_the_scenes_by_the_scene_rules():
    said = _krea_step(3)
    assert "- Write each scene in English.\n" in said
    assert "- Write each scene in sentences, never as tags.\n" in said
    assert "inside quotes, in natural, well-written English" in said
    assert "short enough for the video length" in said


def test_the_krea_flow_keeps_the_looks_in_the_notes_file():
    # The user, 22 October: the notes go into the scenario's notes file. The file is opened in Step
    # 2, with the orientation and the video length, and the looks are written into the same file.
    said = _krea_step(4)
    assert "how each place looks into the notes file" in said


def test_the_krea_flow_opens_the_notes_file_with_the_scenario():
    # Madde 493: the answers of Step 1 go into the notes file, which is named after the scenario
    # and so opens in the step that names one.
    said = _krea_step(2)
    assert "Write the orientation and the video length into a notes file." in said
    assert NOTES_EXAMPLE["krea-start-scenario"] in said


def test_the_krea_flow_adds_the_frames_from_the_notes_in_one_go():
    # One call writes many frames; a call per frame would spend the turn's rounds.
    said = _krea_step(5)
    assert "from the notes" in said
    assert "many frames in one go" in said
    assert "This step waits for no approval. Go on to Step 6 in the same turn." in said


def test_the_krea_flow_frames_each_photo_for_the_orientation():
    # Madde 493, the user's decision of 22 October: the prompts frame the photo for the
    # orientation the user chose, in Krea as in SDXL -- each in its own model's texts.
    assert "Frame the photo of each frame for the orientation in the notes." in _krea_step(5)


def test_the_krea_flow_ends_by_saying_the_prompts_are_complete():
    said = _krea_flow()
    assert "- Build the prompts.\n" in _krea_step(6)
    assert said.endswith("never print the prompts back.")


def test_the_krea_editor_reads_the_scenario_and_its_notes():
    said = _krea_edit()
    assert "You change an existing Krea scenario JSON." in said
    assert "and the notes file of the scenario" in said
    assert "goes into the notes file too" in said
    assert "Build the prompts again." in said
    assert "The built prompt file is the answer: never print the prompts back." in said


# --- the orientation and the video length (Madde 493) ---------------------------------------------
#
# 22 October, the user: "biz videoları yatay yapma özelliği eklemedik mi, queen agent başta sormalı
# ki ona göre prompt yazsın"; "bir de video süresi var". Both start skills ask first, the answers
# live in the scenario's notes file ("sonra da notes'a not alırlar"), and both edit skills read them
# there -- asking when an older scenario has none ("mantıklı"). No text fixes a length or a size any
# more.

START_SKILLS = {"start-a-scenario": _step, "krea-start-scenario": _krea_step}
EDIT_SKILLS = ["edit-prompts", "krea-edit"]

NOTES_EXAMPLE = {
    "start-a-scenario": "as in beach.sdxl-notes.md for beach.sdxl.json",
    "edit-prompts": "as in beach.sdxl-notes.md for beach.sdxl.json",
    "krea-start-scenario": "as in beach.krea-notes.md for beach.krea.json",
    "krea-edit": "as in beach.krea-notes.md for beach.krea.json",
}
"""How each skill names the notes file: the scenario's file name without .json, kind kept.

The user, 22 October ("evet böyle olsun"): beach.sdxl.json and beach.krea.json in one project would
otherwise share beach-notes.md, and the second start's file would be refused as taken. The kind stays
in the name the way build_prompts keeps it in beach.sdxl.py.
"""


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_names_the_notes_file_with_its_kind(skill):
    said = instruction_for(skill)
    assert NOTES_EXAMPLE[skill] in said
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "beach-notes.md" not in said


@pytest.mark.parametrize("skill", sorted(START_SKILLS))
def test_every_start_skill_asks_the_orientation_and_the_video_length_first(skill):
    said = START_SKILLS[skill](1)
    assert said.startswith("Step 1 -- ask the orientation and the video length\n")
    assert "whether the video is landscape or portrait" in said
    assert "how many seconds the video of each frame is" in said
    assert "Go on to Step 2 in the same turn." in said


@pytest.mark.parametrize("skill", sorted(START_SKILLS))
def test_every_start_skill_says_the_user_chooses_both(skill):
    said = instruction_for(skill)
    assert "The user chooses both in Step 1." in said


@pytest.mark.parametrize("skill", EDIT_SKILLS)
def test_every_edit_skill_reads_the_notes_and_asks_when_they_are_missing(skill):
    # The user, 22 October: "SDXL edit de işe başlarken bu notu okusun"; an older scenario with no
    # notes file is asked about ("mantıklı"), and the answer kept so the next edit need not ask.
    said = instruction_for(skill)
    assert "Read the scenario file named in the request, and the notes file of the scenario." in said
    assert "says whether the video is landscape or portrait" in said
    assert (
        "If the notes file is missing, or does not say the orientation and the video length, ask "
        "the user." in said
    )
    assert "Write the answers into the notes file" in said


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_no_skill_fixes_the_video_length(skill):
    # "four seconds" was the length before the user could choose one (Madde 493).
    said = instruction_for(skill)
    assert "video length" in said
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "four seconds" not in said
    assert "1536" not in said


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_says_what_the_prompts_are_for(skill):
    # 29 Aug, the user's own sentence: if we never give the model the context of what we are doing,
    # where would it know it from? Neither text said what the prompts are for.
    #
    # Madde 393, the owner: what the work is for is a video now. Every text opens with a context
    # that says the prompt makes a photo and the video starts from the photo. The owner took the
    # model's name out -- the context says what the model is like instead.
    said = instruction_for(skill)
    assert "The prompt of the frame makes a photo. The video starts from the photo." in said
    assert "SDXL" not in said


@pytest.mark.parametrize("skill", SDXL_SKILLS)
def test_every_sdxl_skill_says_the_image_model_is_weak(skill):
    # Madde 393's other half, and an SDXL rule: since Madde 492 it stays with the SDXL skills.
    assert "The image model is weak" in instruction_for(skill)


def test_the_plan_no_longer_opens_with_a_line_of_context():
    # Madde 186 asked for that line and Madde 198 takes it back, with the question that fed it. The
    # claim is not dropped, it is turned around: with nobody asked what the work is for, a plan
    # opening with it would be back to guessing -- which is the thing 186 was written against.
    said = _flow()
    assert "opens with one line of context" not in said
    assert "inherits the work" not in said


def _after_the_first_line(skill):
    """The text behind the line that sends the model to its guide (Madde 492)."""
    return instruction_for(skill)[len(FIRST_LINE[skill]) :]


def test_the_flow_opens_as_a_persona():
    # Madde 123, the user's own framing: you are an expert scenario writer laying the ground,
    # and an expert prompt writer takes over. A role holds a weak model better than a rule list.
    # Since Madde 492 behind the line that sends the model to its guide.
    assert _after_the_first_line("start-a-scenario").startswith("You are an expert scenario writer")


@pytest.mark.parametrize("skill", ["edit-prompts", "krea-start-scenario", "krea-edit"])
def test_the_other_skills_open_as_the_same_persona(skill):
    # Madde 393, the owner: the same writer as the flow -- only the context differs. The Krea two
    # are the same writer for another model.
    assert _after_the_first_line(skill).startswith(
        "You are an expert scenario writer and prompt writer."
    )


# --- the ritual openings (Madde 107) --------------------------------------------------------------
#
# The same trial from the skills' side: every turn opened with list_files and write_plan, and the
# schema was fetched again for every edit. The opening moves belong to the start of the work, and
# the schema to the one turn that gives the file its shape.


def test_the_flow_looks_for_a_plan_before_it_writes_one():
    # Madde 107 tied the opening moves to the chat's first turn, and Madde 134 found the model
    # writing a plan and then reading its own new plan as one from before. The owner, 30 September:
    # which turn it is cannot be told reliably, so the plan step looks for a plan first and writes
    # one only when there is none.
    said = _step(2)
    assert said.index("Look for a plan in the project.") < said.index("If there is no plan")
    assert "first turn" not in _flow()


def test_no_instruction_reaches_for_the_listing_tool():
    # Madde 127: the tool is gone, and a text still naming it would send the model after something
    # that cannot answer. The flow still starts by looking for the plan; the listing that stood
    # before it is what the request now carries on its own.
    assert "Look for a plan in the project." in _flow()
    for skill, said in INSTRUCTIONS.items():
        assert "list_files" not in said, skill


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
    # different idea of what is already there. add_frame is the adding tool's name since Madde 454,
    # and looking for it finds add_frames too.
    said = _edit()
    assert "add_frame" not in said


def test_a_complaint_is_told_apart_by_where_the_fault_lives():
    # Two roads and the text names both, because they answer different complaints. One frame's
    # sentence is wrong: that is the frame's own line. Somebody looks wrong in every frame they are
    # in: that is their entry, and one update reaches all of them. Since Madde 393 the text names
    # the two places rather than the two tools.
    assert "Find the frames or the entries the user means." in _edit()


def test_no_instruction_touches_a_structure_file_as_text():
    # Madde 171 shut that door in the code; a text still telling the model to walk through it would
    # spend a round being refused. edit_file is not gone -- it writes documents -- so this asks
    # about the pairing rather than about the name.
    for skill, said in INSTRUCTIONS.items():
        assert "edit_file on the frame" not in said, skill
        assert "structure file's maps" not in said, skill


def test_the_editor_closes_with_the_file_rather_than_a_menu():
    # Madde 130. The base already forbids the closing menu (112), but the skill text is the last
    # thing in the request (93) and said nothing about closing -- so the trial's build turn read
    # its own output back, printed 25 prompts into the chat, and offered three choices over a file
    # already sitting in the project. A text that goes quiet is a text a weak model writes over.
    assert "The built prompt file is the answer: never print the prompts back." in _edit()


def test_the_texts_stay_short_enough_to_be_read():
    # Five runs of patches doubled the texts, and a weak model stops reading the middle. The cap
    # is the guard against swelling back: from here a sentence enters only by deleting one.
    #
    # The flow's stays where it was through Madde 186, which was the roadmap's own condition -- it
    # gains a step and loses one, so the two cancel. The editor's came down from 300 when that text
    # gave half its job away: building went to the flow, and what was left is the correction.
    #
    # Correction 20 gives sixty of them back, on the record: the step format the flow uses costs
    # lines, and what it buys is a text a weak model can follow. A cap that moves in a written
    # decision is not a cap that quietly took the old work back.
    #
    # Madde 391 raises the flow's to 1220, on the owner's decision of 28 September that the cap rises
    # only in a written one. The questions the owner used to ask by hand once the prompts were built
    # are four steps after the build now, each a reason, a review and a fix, each in plain sentences
    # that say the noun again rather than a pronoun (the owner, 30 September), and each says the
    # whole of itself since the owner wants them in the flow's own text rather than in a block they
    # share. Every heading also says what its step does now, rather than naming a topic. The owner
    # wrote the four steps line by line, and the count is what that text came to.
    #
    # Madde 393 raises the flow's again and lowers the editor's, both on the same written decision.
    # The owner wrote the frame step (Step 6 since Madde 493) line by line so each frame comes out
    # right before any check sees it:
    # six rules, one kind of entry to a rule so each stands alone, and the reason in front of them.
    # The editor's came down with the tool names and the rules the owner did not keep.
    #
    # Madde 392 raises the flow's once more, on the owner's word: a tenth step writes the negative
    # list, and its context carries the owner's own lessons -- what the list is for, what it must
    # never hold, and what to write instead.
    #
    # Madde 492 raises the flow's to 1835, on the user's written decision of 22 October: Step 4
    # says a scene is never tags, the sentence that left the scene field, so the scene rules read
    # the same in the flow, the Krea flow and both guides. The line that sends each skill to its
    # guide fits under the old caps. The Krea two get caps of their own, written here as the rule
    # asks: what the texts came to and a few words of room -- not room for the next sentence.
    # Improve's went with it.
    #
    # Madde 493 raises all four, on the user's written decision of 22 October: the cap rises as far
    # as the texts need ("sınır gerektiği kadar yükseltilsin"). Each start skill gains a first step
    # asking the orientation and the video length, a context line saying the user chooses both, and
    # a line opening the notes file that keeps them; each edit reads the notes and asks when they are
    # missing; the SDXL flow's frame step gains Rule 7, framing the photo for the orientation. The
    # texts came to 2012, 263, 531 and 314 words; each cap is that and a few words of room.
    assert len(_flow().split()) <= 2020
    assert len(_edit().split()) <= 275
    assert len(_krea_flow().split()) <= 540
    assert len(_krea_edit().split()) <= 325
