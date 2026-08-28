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


@pytest.mark.parametrize(
    "task",
    ["scenario", "frame", "character", "prompt", "sdxl", "outfit", "structure file"],
)
def test_the_base_names_no_task(task):
    # The item's own boundary, and the one worth guarding: what goes into the base is how to work,
    # never what the work is. A task word here would make every chat carry knowledge that belongs
    # to one skill -- and would quietly answer a question Madde 94 has not asked yet.
    assert task not in SYSTEM_PROMPT.lower()
