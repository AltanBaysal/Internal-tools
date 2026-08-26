from dataclasses import fields, replace

from backend.features.workspace.domain.chat import Chat, Message


def test_a_chat_carries_no_model():
    # Madde 82 took the field out rather than leaving it unread. A field nothing writes and nothing
    # reads is a question every later reader has to answer for themselves, and the answer is never
    # in the code -- so the field goes and this line says it went on purpose.
    assert "model" not in [field.name for field in fields(Chat)]


def test_a_chat_carries_no_skill():
    # Madde 86: the selection lives in the session, not in the record. The answer path never read
    # this field -- what governs a turn is the skill written onto the message when it is sent.
    assert "skill" not in [field.name for field in fields(Chat)]


def test_a_message_still_carries_the_skill_it_was_sent_with():
    # The half that stays, and the reason the one above is not an accident: what governed a turn is
    # written on the turn, so an older message cannot be made to look like a newer choice.
    assert "skill" in [field.name for field in fields(Message)]


def test_a_chat_is_owed_an_answer_when_the_last_word_is_the_users():
    # Madde 88 moved this question out of the browser. It used to live in useChat, where it ran on
    # a reload and on a reconnection -- moments nobody had asked for an answer in.
    #
    # Imported here rather than at the top: a name that does not exist yet fails the whole file's
    # collection, and then none of this turn's reds are visible.
    from backend.features.workspace.domain.chat import is_owed_an_answer

    at = "2026-08-09T11:04:00.000+00:00"
    asked = Chat(
        id="c1", title="hi", created_at=at, messages=(Message(role="user", at=at, text="hi"),)
    )
    answered = replace(asked, messages=asked.messages + (Message(role="ai", at=at, text="Done."),))
    assert is_owed_an_answer(asked)
    assert not is_owed_an_answer(answered)
    # An empty chat cannot exist through the door, but the rule must not read past the end of a
    # list to say so.
    assert not is_owed_an_answer(Chat(id="c1", title="hi", created_at=at))
