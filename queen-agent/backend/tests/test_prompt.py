import pytest

from backend.features.workspace.domain.prompt import SYSTEM_PROMPT


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


def test_the_base_looks_before_it_writes():
    # Having read it earlier in the chat is not having read it: the file on disk is what the next
    # step reads, and it may have moved on since.
    assert "read it first" in SYSTEM_PROMPT.lower()


def test_the_base_asks_rather_than_inventing():
    # Sat in three skill texts, each in its own words. A guess is either more than the user wanted
    # or less, and nothing on the screen says which one happened. Since 28 Aug the same rule covers
    # the request itself: what was not understood is asked about, not worked around.
    said = SYSTEM_PROMPT.lower()
    assert "ask" in said
    assert "invent" in said
    assert "not sure" in said


def test_the_base_works_in_pieces_and_lands_each_one():
    # The reason was written out three times, identically: quality falls away towards the end of a
    # long stretch. And each piece reaching disk is what makes an interruption cost one piece.
    said = SYSTEM_PROMPT.lower()
    assert "one long" in said or "in pieces" in said
    assert "before the next" in said


def test_the_base_edits_what_exists_rather_than_rebirthing_it():
    # The observed failure: the model reaches for creation because creation is the only writing it
    # was told about, and code can only refuse the same name -- a file reborn under a second name
    # walks right past the wall. The preference has to live where the name is picked.
    assert "edit_file" in SYSTEM_PROMPT
    assert "never reborn" in SYSTEM_PROMPT.lower()


def test_the_base_puts_a_correction_on_disk_too():
    # A correction that only lands in the chat leaves the file saying the older thing, and the file
    # is what the next step reads.
    said = SYSTEM_PROMPT.lower()
    assert "correction" in said
    assert "chat" in said and "file" in said


def test_the_base_starts_a_long_job_with_the_plan():
    # Skill-less chats had no reason to plan; the flow got one in its own text and the base got
    # nothing. The plan file is where a job keeps its place -- which is also how a chat that grew
    # too long is survived.
    assert "write_plan" in SYSTEM_PROMPT
    assert "keeps its place" in SYSTEM_PROMPT.lower()


def test_the_base_says_what_it_did_even_when_it_did_nothing():
    # Silence is not an answer: a turn that found nothing to change and a turn that never looked
    # read exactly the same.
    assert "nothing" in SYSTEM_PROMPT.lower()


def test_a_turn_does_not_end_with_a_menu_of_options():
    # 28 Aug: every answer closed with five things the user could ask for next. A turn ends with
    # the one question that decides what happens, or with nothing -- a list is the work handed
    # back rather than an ending.
    said = SYSTEM_PROMPT.lower()
    assert "list of things you could do next" in said
    assert "ask the one question" in said


# --- the ritual reads (Madde 107) -----------------------------------------------------------------
#
# One trial: a one-line message cost eight tool calls. The base text said a file seen earlier is
# not a file read now, and the model heard a rule to re-read everything every turn -- its own
# writing included. The fresh read belongs to the file somebody else may have moved.


def test_a_fresh_read_is_for_what_someone_else_may_have_changed():
    said = SYSTEM_PROMPT.lower()
    assert "somebody else may have changed" in said
    assert "never to check your own writing" in said
    assert "not the same as reading it now" not in said


def test_the_base_is_handed_the_names_rather_than_asking_for_them():
    # Madde 127. Asking for what exists was a whole round, every turn -- and the turn that did not
    # ask invented a name instead. The names are true every turn, so they ride in every request.
    assert "listed for you in every request" in SYSTEM_PROMPT
    assert "list_files" not in SYSTEM_PROMPT


def test_the_base_reads_nothing_the_answer_does_not_need():
    # The other half of the same trial: files the question never touched were read anyway,
    # because nothing said the reading has a boundary.
    assert "nothing the answer does not need" in SYSTEM_PROMPT.lower()


# --- what the turn's last round is told (Madde 137) -----------------------------------------------
#
# Imported inside each test rather than at the top of the file: until the constant exists a module
# level import would stop this file being collected at all, and the fourteen guards above would read
# as errors of this item's making. The same shape allowed() and refused() use in test_stream_answer.
#
# The text is only half the item -- the round really is handed no tools, and test_stream_answer
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
