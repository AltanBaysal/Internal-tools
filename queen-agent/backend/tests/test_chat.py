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


# --- versions: the lines one chat can hold (Madde 195) -------------------------------------------


def _said(role, text, context=0):
    return Message(role=role, at=AT, text=text, usage=Usage(context, 0, 5, context))


def _trunk(*texts):
    """A chat whose first line is these messages, user and ai in turn."""
    return Chat(
        id="c1",
        title=texts[0],
        created_at=AT,
        messages=tuple(
            _said("user" if index % 2 == 0 else "ai", text) for index, text in enumerate(texts)
        ),
    )


def _version(id, parent, at, *texts):
    from backend.features.workspace.domain.chat import Version

    return Version(
        id=id,
        parent=parent,
        at=at,
        messages=tuple(
            _said("user" if index % 2 == 0 else "ai", text) for index, text in enumerate(texts)
        ),
    )


def test_a_chat_with_no_versions_reads_its_own_messages():
    # The floor under everything below: nothing about a chat that never branched changes, and the
    # empty active is what says "the first line" rather than a name nobody wrote.
    from backend.features.workspace.domain.chat import active_messages

    chat = _trunk("hi", "Done.")
    assert [m.text for m in active_messages(chat)] == ["hi", "Done."]


def test_a_version_is_the_prefix_it_kept_plus_its_own():
    # What the whole madde rests on: the messages before the split are not copied into the version,
    # so the two lines share one copy of them and neither can drift from the other.
    from backend.features.workspace.domain.chat import active_messages

    chat = replace(
        _trunk("hi", "Done.", "again", "Done twice."),
        versions=(_version("l2", "", 2, "again, shorter", "Shorter."),),
        active="l2",
    )
    assert [m.text for m in active_messages(chat)] == ["hi", "Done.", "again, shorter", "Shorter."]


def test_a_version_of_a_version_walks_the_whole_chain():
    from backend.features.workspace.domain.chat import active_messages

    chat = replace(
        _trunk("hi", "Done.", "again", "Done twice."),
        versions=(
            _version("l2", "", 2, "again, shorter", "Shorter."),
            _version("l3", "l2", 3, "Shorter still."),
        ),
        active="l3",
    )
    assert [m.text for m in active_messages(chat)] == ["hi", "Done.", "again, shorter", "Shorter still."]


def test_an_active_naming_nothing_falls_back_to_the_first_line():
    # A chat on disk can be edited by hand, and the store reads field by field for the same reason.
    # A name nobody wrote is not worth a crash: the first line is the one that always exists.
    from backend.features.workspace.domain.chat import active_messages

    chat = replace(_trunk("hi", "Done."), active="gone")
    assert [m.text for m in active_messages(chat)] == ["hi", "Done."]


def test_whether_an_answer_is_owed_is_asked_of_the_open_line():
    # The closed line was answered and the open one was not. Reading the first line here would send
    # the user's newest question nowhere.
    from backend.features.workspace.domain.chat import is_owed_an_answer

    chat = replace(
        _trunk("hi", "Done."),
        versions=(_version("l2", "", 1, "hi again"),),
        active="l2",
    )
    assert is_owed_an_answer(chat)
    assert not is_owed_an_answer(replace(chat, active=""))


def test_the_ceiling_is_measured_on_the_open_line():
    # A turn that only exists on a line nobody is on is not sent any more, and what is not sent
    # cannot fill the chat. Measuring it would close a conversation over work it has walked away
    # from.
    from backend.features.workspace.domain.chat import is_full, last_context

    chat = Chat(
        id="c1",
        title="hi",
        created_at=AT,
        messages=(_said("user", "hi"), _said("ai", "Done.", context=60_000)),
        versions=(_version("l2", "", 1),),
        active="l2",
    )
    assert last_context(chat) == 0
    assert not is_full(chat)
    assert is_full(replace(chat, active=""))


def test_the_last_activity_is_the_open_lines_last_message():
    # The sidebar orders chats by this. A chat left on a version was last touched there, and reading
    # the first line would sort it by a conversation the user walked away from.
    from backend.features.workspace.domain.chat import Version

    later = "2026-08-09T12:00:00.000+00:00"
    chat = replace(
        _trunk("hi", "Done."),
        versions=(
            Version(
                id="l2", parent="", at=1, messages=(Message(role="user", at=later, text="again"),)
            ),
        ),
        active="l2",
    )
    assert chat.last_activity == later


def test_the_options_at_a_split_are_the_base_line_and_the_versions_of_it():
    # What the arrows step through, and the order they step in: the base line first because its
    # message was there first, then the versions in the order they were made. Nothing else decides
    # which way `1/2` points.
    from backend.features.workspace.domain.chat import variants_of

    chat = replace(
        _trunk("hi", "Done.", "again", "Done twice."),
        versions=(_version("l2", "", 2, "again, shorter"),),
        active="l2",
    )
    assert [(v["index"], v["of"], v["versions"]) for v in variants_of(chat)] == [
        (0, 1, [""]),
        (0, 1, [""]),
        (1, 2, ["", "l2"]),
    ]


def test_the_same_message_edited_twice_has_three_options():
    from backend.features.workspace.domain.chat import variants_of

    chat = replace(
        _trunk("hi", "Done."),
        versions=(_version("l2", "", 0, "hello"), _version("l3", "", 0, "hey")),
        active="l3",
    )
    assert [(v["index"], v["of"], v["versions"]) for v in variants_of(chat)] == [
        (2, 3, ["", "l2", "l3"])
    ]
