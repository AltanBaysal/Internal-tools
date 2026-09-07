from dataclasses import fields, replace

from backend.features.workspace.domain.chat import Chat, Message, Usage


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


def test_a_message_carries_the_model_it_was_sent_with():
    # Madde 146, and the field sits beside skill for the very same reason: changing the selection
    # later must not make an older turn look as though the new model answered it. The chat's own
    # root stays clear of it -- test_a_chat_carries_no_model above is the other half of this pair.
    assert "model" in [field.name for field in fields(Message)]


def test_a_message_written_before_the_field_carries_the_empty_model():
    # Every message on disk today. Answering one has to go on working, and it does by resolving to
    # the default -- the rule config.engine_for keeps.
    assert Message(role="user", at="2026-09-02T10:00:00+00:00", text="hi").model == ""


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


# --- the ceiling on a chat's context (Madde 92) --------------------------------------------------

AT = "2026-08-09T11:04:00.000+00:00"


def _answered(sent, context=None):
    """A chat whose one answer spent this much, and left the conversation this big.

    Two numbers since Madde 133: what the turn spent across all its rounds, and what its last round
    carried. They are equal only when the turn took a single round, which is why they default that
    way -- a caller who does not care about the difference is describing a one-round turn.
    """
    return Chat(
        id="c1",
        title="hi",
        created_at=AT,
        messages=(
            Message(role="user", at=AT, text="hi"),
            Message(
                role="ai",
                at=AT,
                text="Done.",
                usage=Usage(sent, 0, 5, sent if context is None else context),
            ),
        ),
    )


def test_the_ceiling_is_read_off_the_last_answer():
    # A turn's size is only known once the answer comes back, so the ceiling reads the previous one
    # -- one turn stale on purpose. Which means the record does not always end with the answer it
    # has to read: a question whose answer never came can be sitting on the end, and a question has
    # no number of its own.
    from backend.features.workspace.domain.chat import last_context

    chat = _answered(41_000)
    asked_again = replace(
        chat, messages=chat.messages + (Message(role="user", at=AT, text="more"),)
    )
    assert last_context(chat) == 41_000
    assert last_context(asked_again) == 41_000


def test_a_chat_with_no_answer_yet_has_sent_nothing():
    # Zero is what unknown looks like here, and Madde 76 settled that already: an answer from
    # before the counting existed reads back as zero too, and nothing is drawn for either.
    from backend.features.workspace.domain.chat import last_context

    assert last_context(Chat(id="c1", title="hi", created_at=AT)) == 0
    asked = Chat(
        id="c1", title="hi", created_at=AT, messages=(Message(role="user", at=AT, text="hi"),)
    )
    assert last_context(asked) == 0


def test_the_ceiling_ignores_what_the_rounds_added_up_to():
    # Madde 133, and the whole of it. A turn of six rounds spends six requests' worth, and the
    # eighth trial closed a chat at 51.4k whose conversation was nowhere near it. What fills a
    # chat is how big the request got, not how many of them it took.
    from backend.features.workspace.domain.chat import is_full, last_context

    six_rounds = _answered(120_000, context=12_000)
    assert last_context(six_rounds) == 12_000
    assert not is_full(six_rounds)


def test_an_answer_from_before_the_field_never_fills_the_chat():
    # No migration is written, so every chat on disk today reads zero here. Zero has meant
    # unmeasured since Madde 76, and an unmeasured chat is not a full one -- the permissive side
    # is the right side, since the cost of being wrong is closing a chat that had room.
    from backend.features.workspace.domain.chat import is_full

    older = Chat(
        id="c1",
        title="hi",
        created_at=AT,
        messages=(
            Message(role="user", at=AT, text="hi"),
            Message(role="ai", at=AT, text="Done.", usage=Usage(90_000, 0, 5)),
        ),
    )
    assert not is_full(older)


def test_the_ceiling_is_fifty_thousand():
    # The reason is quality rather than capacity: the window is 256k, so this is a fifth of it.
    # Models get worse as the input grows and what sits in the middle goes unread -- fitting is not
    # the same as being read.
    from backend.features.workspace.domain.chat import CONTEXT_CEILING

    assert CONTEXT_CEILING == 50_000


def test_a_chat_is_full_at_the_ceiling_and_not_before():
    from backend.features.workspace.domain.chat import CONTEXT_CEILING, is_full

    assert not is_full(_answered(CONTEXT_CEILING - 1))
    assert is_full(_answered(CONTEXT_CEILING))
