from pathlib import Path

import pytest

from backend.features.workspace.domain.prompt import SYSTEM_PROMPT

# --- one place for every text the model is told (Madde 189) ---------------------------------------
#
# They were spread over four files: this one, skills.py, the nine hundred lines of TOOL_SPECS, and
# stream_answer's heading for the context box. Reading them meant walking four files, and a rule
# said twice in two of them could not be seen at all -- 182 only found such a copy because a word
# cap went red.
#
# The line this madde draws is between what the model is TOLD and what it is TOLD BACK. Instructions
# move: they are written once and read on every call. Answers stay where they are made, because an
# answer is an f-string over values that exist only at that call, and a template pulled into another
# file is a copy of the call's shape -- and a copy is the side that goes stale.


def _texts_named_by(module):
    """Every string this module names in capitals, which is how a text is written down here."""
    return {
        value
        for name, value in vars(module).items()
        if name.isupper() and isinstance(value, str)
    }


def _descriptions_in(properties):
    """Every description under a parameter map, following arrays into their items.

    add_frame's frames is a list of objects and those objects carry descriptions of their own. A
    walk that stopped at the first level would leave the deepest texts unwatched, which is where a
    forgotten one would sit.
    """
    for said in properties.values():
        if "description" in said:
            yield said["description"]
        inner = said.get("items", {}).get("properties")
        if inner:
            yield from _descriptions_in(inner)


def test_every_text_a_tool_carries_comes_from_the_prompt_module():
    from backend.features.workspace.domain import prompt
    from backend.features.workspace.domain.tools import TOOL_SPECS

    known = _texts_named_by(prompt)
    # Before anything else: an empty set would let the loop below pass over an empty TOOL_SPECS too,
    # and this run has already watched seven tests go green because nothing had happened yet.
    assert len(known) > 10

    for spec in TOOL_SPECS:
        function = spec["function"]
        assert function["description"] in known, function["name"]
        for said in _descriptions_in(function["parameters"]["properties"]):
            assert said in known, function["name"]


def test_no_tool_carries_the_sdxl_document():
    # Madde 453. It rides once, behind the system prompt, where its rules used to ride six times --
    # once on each tool that takes tags. A copy back on a tool is paid for on every request.
    #
    # Line by line as well as whole: a copy of one rule, or of the document with a line changed,
    # is the same rule said twice and would slip past a search for the whole text.
    from backend.features.workspace.domain.prompt import SDXL_DOCUMENT
    from backend.features.workspace.domain.tools import TOOL_SPECS

    rules = [line[2:] for line in SDXL_DOCUMENT.splitlines() if line.startswith("- ")]
    # Before the loop: an empty document would let it pass over nothing.
    assert len(rules) > 10
    for spec in TOOL_SPECS:
        function = spec["function"]
        said = [function["description"], *_descriptions_in(function["parameters"]["properties"])]
        for text in said:
            for rule in rules:
                assert rule not in text, (function["name"], rule)


@pytest.mark.parametrize(
    "module,name",
    [
        ("tools", "SDXL_PROMPT_RULES"),
        ("skills", "START_A_SCENARIO"),
        # Madde 186 renamed this one with the skill it belongs to. The guard keeps watching the
        # name it had when it moved as well: a text put back under the old name in skills.py is
        # the same failure as one put back under the new one.
        ("skills", "GENERATE_PROMPTS_PLUS"),
        ("skills", "EDIT_PROMPTS"),
    ],
)
def test_no_text_is_still_written_down_where_it_used_to_live(module, name):
    """The source rather than the module, and that is not fussiness.

    An imported name becomes an attribute of the module that imported it, so hasattr says yes long
    after the text has moved. What this madde forbids is the text being *written* in two places, and
    only the source says where it was written. test_notebook.py watches its notebook the same way.
    """
    from backend.features.workspace.domain import skills, tools

    source = Path({"tools": tools, "skills": skills}[module].__file__).read_text(encoding="utf-8")
    assert f"{name} = " not in source, f"{name} is still assigned in {module}.py"


MUST_BE_FULL = (
    "SYSTEM_PROMPT",
    "LAST_ROUND",
    "SDXL_DOCUMENT",
    "START_A_SCENARIO",
    "EDIT_PROMPTS",
    "IMPROVE",
)
"""The texts this app writes, and every one of them says something.

Read by the test below and by the one about Madde 196's second part, which is deliberately not on
this list -- lifted out of that test so the absence can be asserted rather than only meant.
"""


def test_the_prompt_module_holds_the_texts_the_others_gave_up():
    # The floor under the two above: both of them would pass over an empty module, one with an empty
    # set of texts and one with an empty source.
    from backend.features.workspace.domain import prompt

    for name in MUST_BE_FULL:
        assert getattr(prompt, name, "").strip(), name


def test_the_answer_follows_the_language_it_was_asked_in():
    assert "the language the user writes in" in SYSTEM_PROMPT


def test_the_app_forces_no_language_of_its_own():
    # The interface is English because its design was written in English. That is a rule about
    # labels, and it was never a reason to answer a Turkish question in English.
    assert "English" not in SYSTEM_PROMPT


# --- the behaviour that holds whatever skill is selected (Madde 73) -------------------------------
#
# Four rules that sat in the skill texts one copy each, so a chat with no skill selected had none of
# them -- and the copies drifted. What comes here is the agentic half only: how to work, never what
# the work is.
#
# Since Madde 455 the text is laid out from the research into agent harnesses, and the tests ask
# each rule by its words of substance rather than by the sentence it sits in: the wording is the
# user's to change, and a test that held a sentence would break on every rewording of it.


def _a_line_says(*words):
    """Whether one line of the text holds all these words. A rule is one line since Madde 455, so
    a rule's words are asked of one line rather than of the whole text, where they could come from
    two different rules."""
    return any(all(word in line for word in words) for line in SYSTEM_PROMPT.lower().splitlines())


def test_the_base_looks_before_it_writes():
    # Having read it earlier in the chat is not having read it: the file on disk is what the next
    # step reads, and it may have moved on since.
    assert _a_line_says("read_file", "first")


def test_the_base_says_where_a_read_file_appears():
    # Madde 179. The tool answers with a receipt now, so a model told only to read would get a
    # sentence back, believe it had not seen the file, and read it again -- which is the very thing
    # this item removes.
    assert _a_line_says("receipt", "opened files")
    # Correction 4. Saying only where the file appears left open whether what stands there is the
    # file as it was read; it is read from disk every round, and a model that does not know that
    # reads it again to be sure.
    assert _a_line_says("opened files", "every round")


def test_the_base_says_how_many_files_stay_open():
    # Madde 455: the window explained, in one sentence. The box's own heading gives the number, but
    # only once a file is open; a model that does not know the window holds five goes looking for
    # a sixth it can no longer see. BOX_LIMIT is 5, and test_context_box holds it there.
    assert _a_line_says("opened files", "five")


def test_the_base_asks_rather_than_inventing():
    # Sat in three skill texts, each in its own words. A guess is either more than the user wanted
    # or less, and nothing on the screen says which one happened. Since 28 Aug the same rule covers
    # the request itself: what was not understood is asked about, not worked around.
    assert _a_line_says("invent", "ask")
    assert _a_line_says("not sure", "ask")


def test_the_base_asks_only_what_a_tool_cannot_find_out():
    # Madde 455. What a file says is found out with a read; only what the user alone can decide is
    # a question, and it is one question.
    assert _a_line_says("tool can find out")
    assert _a_line_says("only the user can decide", "one question")


def test_the_base_works_in_pieces_and_lands_each_one():
    # The reason was written out three times, identically: quality falls away towards the end of a
    # long stretch. And each piece reaching disk is what makes an interruption cost one piece.
    assert _a_line_says("pieces", "before the next")


def test_the_base_edits_what_exists_rather_than_rebirthing_it():
    # The observed failure: the model reaches for creation because creation is the only writing it
    # was told about, and code can only refuse the same name -- a file reborn under a second name
    # walks right past the wall. The preference has to live where the name is picked.
    #
    # Correction 5. A scenario is not changed with edit_file at all -- Madde 171 shut that door --
    # so a sentence naming only that tool tells the model to make a call that comes back refused.
    assert _a_line_says("edit_file", "the tool that owns")
    # And the new file is named for what it is not: a second version of an old one.
    assert _a_line_says("new file", "second version")


def test_the_base_puts_a_change_on_disk_rather_than_in_the_chat():
    # A change that only lands in the chat leaves the file saying the older thing, and the file is
    # what the next step reads. Correction 6: the old sentence described that failure instead of
    # asking for anything, and it covered only corrections -- the same is true of any change.
    assert _a_line_says("change", "in the file")


def test_the_base_starts_a_long_job_with_the_plan():
    # Skill-less chats had no reason to plan; the flow got one in its own text and the base got
    # nothing. The plan file is where a job keeps its place -- which is also how a chat that grew
    # too long is survived.
    #
    # Madde 207 changed the tool it names. Asked of the line rather than of the word create_file:
    # that word is already in this text, about when to save a document, so a test looking for it
    # anywhere would pass without holding this rule at all.
    assert _a_line_says("plan file", "create_file")
    assert "write_plan" not in SYSTEM_PROMPT


def test_the_base_says_the_plan_and_carries_on():
    # Madde 455. A plan announced at the end of a turn is a turn that stopped: the Codex guide saw
    # strong models end the turn on "here is my plan". So the plan is said and the work goes on in
    # the same turn, unless a skill says to wait for a yes -- and the plan is only for work of
    # several steps.
    assert _a_line_says("plan", "several steps", "same turn")
    assert _a_line_says("skill", "wait")


def test_a_plans_steps_go_one_at_a_time_each_verified():
    # Madde 465. The model began a plan's second step before the first was done -- the locations
    # before every character existed -- and each step builds on what the one before it made. So a
    # step is its own loop, gather context, take action, verify results (the user's words, from
    # Claude Code's agentic loop), and the next starts only once this one is complete. Asked of the
    # Planning section, where the rule about plans lives.
    # Empty when no section is headed Planning, so a renamed heading fails on the asserts below.
    planning = next(
        (part for part in SYSTEM_PROMPT.split("\n\n") if part.startswith("Planning\n")), ""
    ).lower()
    rules = planning.splitlines()
    assert any("one at a time" in line and "verify" in line for line in rules)
    assert any("next step" in line and "complete" in line for line in rules)


def test_the_base_says_what_it_did_even_when_it_did_nothing():
    # Silence is not an answer: a turn that found nothing to change and a turn that never looked
    # read exactly the same.
    assert _a_line_says("nothing", "say")


def test_a_turn_does_not_end_with_a_menu_of_options():
    # 28 Aug: every answer closed with five things the user could ask for next. A turn ends with
    # the one question that decides what happens, or with nothing -- a list is the work handed
    # back rather than an ending.
    assert _a_line_says("list", "do next")
    assert _a_line_says("one question", "stop")


# --- what a tool's answer is worth (Madde 455) ----------------------------------------------------


def test_a_tools_answer_is_what_happened():
    # Every harness the research read says the same: the environment's answer is the ground truth.
    # A weak model reports what it meant to do; the tool's answer is what it did.
    assert _a_line_says("tool's answer", "truth")
    assert _a_line_says("refused", "failed")
    assert _a_line_says("never", "did not make")


def test_the_same_call_is_not_made_twice_in_a_row():
    # DeepSeek in other agent loops repeats the same action (the research's Roo Code and V3
    # reports). The same call gets the same answer, and two failed tries at one change go to the
    # user.
    assert _a_line_says("same arguments", "twice")
    assert _a_line_says("both fail", "stop")


def test_independent_reads_go_in_one_round():
    # Each round is one more request, and a turn has thirty-two. The loop runs every call of a
    # round (test_run_turn) and the black box collects them (test_black_box).
    assert _a_line_says("one round", "several calls")


# --- how the text is written (Madde 455) ----------------------------------------------------------


def test_the_text_ends_on_its_last_word():
    # system_prompt() puts the owner's part behind a blank line; a blank line of this text's own
    # would make two, and an empty suffix returns this text as it is -- the cached prefix's head.
    assert SYSTEM_PROMPT == SYSTEM_PROMPT.strip()


def test_nothing_is_shouted():
    # The research: newer models overtrigger on capitals and markdown emphasis, and the guides turn
    # it down. AI is a name, not a shout.
    words = [word.strip(".,:;()'") for word in SYSTEM_PROMPT.split()]
    assert [word for word in words if len(word) > 2 and word.isupper()] == []
    assert "**" not in SYSTEM_PROMPT
    assert "#" not in SYSTEM_PROMPT


def test_the_three_core_rules_close_the_text():
    # What a weak model is told at both ends it keeps (GPT-4.1's guide; Gemini's Final Reminder):
    # the last section repeats read first, never claim what a tool did not do, always answer in the
    # chat -- three lines and nothing after them.
    last = SYSTEM_PROMPT.split("\n\n")[-1].splitlines()
    rules = [line.lower() for line in last[1:]]
    assert len(rules) == 3
    assert all(line.startswith("- ") for line in rules)
    assert "read" in rules[0]
    assert "tool" in rules[1]
    assert "chat" in rules[2]


# --- the ritual reads (Madde 107) -----------------------------------------------------------------
#
# One trial: a one-line message cost eight tool calls. The base text said a file seen earlier is
# not a file read now, and the model heard a rule to re-read everything every turn -- its own
# writing included. The fresh read belongs to the file somebody else may have moved.


def test_a_fresh_read_is_for_a_file_that_is_not_already_open():
    # Madde 107's lesson, and correction 2 sharpened what it is about. The opened files are read
    # from disk every round, so what stands there is current and a second read of one buys nothing.
    # What is worth a read is a file that is not among them.
    #
    # Correction 3: the old sentence gave the wrong reason -- somebody else may have changed it --
    # and a wrong reason is a rule the model applies in the wrong places.
    said = SYSTEM_PROMPT.lower()
    assert _a_line_says("not among your opened files")
    assert _a_line_says("never", "own writing")
    assert "somebody else may have changed" not in said
    assert "not the same as reading it now" not in said


def test_the_base_is_handed_the_names_rather_than_asking_for_them():
    # Madde 127. Asking for what exists was a whole round, every turn -- and the turn that did not
    # ask invented a name instead. The names are true every turn, so they ride in every request.
    assert _a_line_says("listed", "every request")
    assert "list_files" not in SYSTEM_PROMPT


def test_the_base_reads_only_what_the_answer_needs():
    # The other half of the same trial: files the question never touched were read anyway,
    # because nothing said the reading has a boundary. Correction 2 turned the boundary the right
    # way up -- what to do rather than what not to do.
    assert _a_line_says("only what the answer needs")


# --- what the turn's last round is told (Madde 137) -----------------------------------------------
#
# Imported inside each test rather than at the top of the file: until the constant exists a module
# level import would stop this file being collected at all, and the fourteen guards above would read
# as errors of this item's making. The same shape allowed() and refused() use in test_run_turn.
#
# The text is only half the item -- the round really is handed no tools, and test_run_turn
# measures that. What is guarded here is that the sentence says the two things the failure asked
# for: that nothing more will run, and what the closing answer owes the reader.


def test_the_last_round_notice_says_no_tool_will_run():
    # Why it says so rather than only asking for a summary: the model is not stopping early, it is
    # being told the road ends here. A sentence that said wrap up would leave it free to spend the
    # round on one more call -- which is the failure this item comes from.
    from backend.features.workspace.domain.prompt import LAST_ROUND

    said = LAST_ROUND.lower()
    assert "last round" in said
    assert "no tool" in said


def test_the_last_round_notice_asks_what_is_left():
    # The user's own two words for what a closing answer owes them. Saying only what was done
    # leaves the reader to work out where it stopped, and the next message is where they pick it up.
    from backend.features.workspace.domain.prompt import LAST_ROUND

    said = LAST_ROUND.lower()
    assert "what is left" in said
    assert "next step" in said


@pytest.mark.parametrize(
    "task",
    ["scenario", "frame", "character", "prompt", "sdxl", "outfit", "structure file"],
)
def test_the_base_names_no_task(task):
    # The item's own boundary, and the one worth guarding: what goes into the base is how to work,
    # never what the work is. A task word here would make every chat carry knowledge that belongs
    # to one skill -- and would quietly answer a question Madde 94 has not asked yet.
    assert task not in SYSTEM_PROMPT.lower()


# --- the second part, which is the user's own (Madde 196) ----------------------------------------


def test_a_plan_is_written_as_boxes_to_tick():
    # Madde 198. The ticking was instructed long before the shape was, and an instruction without a
    # shape is one the model answers differently every turn -- so the plan a fresh chat opens says
    # nothing about where the work stopped.
    #
    # The shape used to live in write_plan's description; Madde 207 takes that tool away, and
    # correction 10 had already decided where the shape goes instead: into the sentence of the step
    # that writes the plan, so that it holds whichever tool writes it.
    from backend.features.workspace.domain import prompt

    assert "- [ ]" in prompt.START_A_SCENARIO


def test_the_system_prompt_has_a_second_part():
    from backend.features.workspace.domain import prompt

    assert isinstance(prompt.SYSTEM_PROMPT_SUFFIX, str)


def test_the_second_part_is_allowed_to_be_empty():
    """The one text in this module the app does not write.

    What goes in it is the user's own, and the item builds the place rather than filling it -- so it
    is born empty and stays legal that way. Asserted as an absence from the list rather than as a
    sentence in a comment: a name added there would fail this madde on the day somebody leaves the
    suffix blank, which is every day until the user writes something.
    """
    assert "SYSTEM_PROMPT_SUFFIX" not in MUST_BE_FULL
