from dataclasses import fields, replace

from backend.features.workspace.domain.chat import Chat, Message, ToolCall, Usage


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


# --- the ceiling on a chat's context (Madde 92; the messages alone since Madde 337) -------------

AT = "2026-08-09T11:04:00.000+00:00"


def _answered(question, answer, **rest):
    """A chat of one question and its answer; the answer carries whatever else it is given."""
    return Chat(
        id="c1",
        title="hi",
        created_at=AT,
        messages=(
            Message(role="user", at=AT, text=question),
            Message(role="ai", at=AT, text=answer, **rest),
        ),
    )


def test_a_chats_size_is_the_text_of_its_messages():
    # Madde 337. What a chat sends the model of itself is each message's text and nothing else, so
    # that is what fills it. An estimate rather than a count, by DeepSeek's own rough measure: an
    # English character is about 0.3 of a token.
    from backend.features.workspace.domain.chat import chat_size

    assert chat_size(_answered("a" * 600, "a" * 400)) == 300


def test_an_empty_chat_has_no_size():
    from backend.features.workspace.domain.chat import chat_size

    assert chat_size(Chat(id="c1", title="hi", created_at=AT)) == 0


def test_what_a_turn_spent_and_did_is_not_the_chats_size():
    # Madde 337, the row's own words: a turn that calls many tools or opens a big file does not grow
    # the gauge. The steps, the files and the bill ride on the message but never reach the model as
    # the chat -- and the opened-files box is not a message at all.
    from backend.features.workspace.domain.chat import chat_size, is_full

    busy = _answered(
        "a" * 600,
        "a" * 400,
        usage=Usage(120_000, 0, 5),
        calls=tuple(ToolCall("read_file", "scene.json", "900 lines") for _ in range(16)),
        files=("scene.json",),
    )
    assert chat_size(busy) == 300
    assert not is_full(busy)


def test_the_ceiling_is_fifty_thousand():
    # The reason is quality rather than capacity: the window is 256k, so this is a fifth of it.
    # Models get worse as the input grows and what sits in the middle goes unread -- fitting is not
    # the same as being read.
    from backend.features.workspace.domain.chat import CONTEXT_CEILING

    assert CONTEXT_CEILING == 50_000


def test_a_chat_is_full_when_its_messages_reach_the_ceiling_and_not_before():
    from backend.features.workspace.domain.chat import CONTEXT_CEILING, chat_size, is_full

    reached = _answered("", "a" * 166_667)
    below = _answered("", "a" * 166_666)
    assert chat_size(reached) == CONTEXT_CEILING
    assert is_full(reached)
    assert not is_full(below)


def test_a_usage_carries_no_context():
    # Madde 337 took the ceiling off the engine's numbers, and the ceiling was the only reader of the
    # last round's size. A field written every turn and read by nothing is a question every later
    # reader has to answer for themselves.
    assert "context" not in [field.name for field in fields(Usage)]


# --- versions: the lines one chat can hold (Madde 195) -------------------------------------------


def _said(role, text):
    return Message(role=role, at=AT, text=text)


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
    from backend.features.workspace.domain.chat import is_full

    chat = Chat(
        id="c1",
        title="hi",
        created_at=AT,
        messages=(_said("user", "hi"), _said("ai", "a" * 200_000)),
        versions=(_version("l2", "", 1),),
        active="l2",
    )
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


# --- the trim: the oldest turns stop going to the model (Madde 345) -----------------------------


def _marked(chat, count):
    """The chat with its first line's last message carrying a trim of this many messages."""
    last = replace(chat.messages[-1], trimmed=count)
    return replace(chat, messages=chat.messages[:-1] + (last,))


def _turns(*pairs):
    """A chat whose first line is these (question, answer) turns, in order."""
    return _trunk(*[text for pair in pairs for text in pair])


def test_a_chat_nobody_trimmed_sends_its_whole_open_line():
    from backend.features.workspace.domain.chat import active_messages, sent_from, sent_messages

    chat = _trunk("hi", "Done.", "again", "Done twice.")
    assert sent_from(chat) == 0
    assert sent_messages(chat) == active_messages(chat)


def test_a_trimmed_line_sends_and_measures_only_what_follows_the_cut():
    # Madde 345, the row's own words: the oldest messages stop going to the model, and the ring
    # reads what is still sent. They stay in the record -- only what is sent moves.
    from backend.features.workspace.domain.chat import (
        active_messages,
        chat_size,
        sent_from,
        sent_messages,
    )

    chat = _marked(_trunk("a" * 600, "a" * 400, "b" * 60, "b" * 40), 2)
    assert sent_from(chat) == 2
    assert [m.text for m in sent_messages(chat)] == ["b" * 60, "b" * 40]
    assert len(active_messages(chat)) == 4
    assert chat_size(chat) == 30


def test_the_newest_trim_on_the_line_is_the_one_that_holds():
    # A trimmed chat fills again and is trimmed again; the second cut is further on, and it is the
    # one the line reads from.
    from backend.features.workspace.domain.chat import sent_from

    first = _marked(_trunk("hi", "Done.", "again", "Done twice."), 2)
    grown = replace(first, messages=first.messages + (_said("user", "more"), _said("ai", "More.")))
    assert sent_from(_marked(grown, 4)) == 4


def test_a_version_split_before_the_trim_is_not_trimmed_and_one_after_it_is():
    # The mark sits on the message that was last when the chat was trimmed -- the answer that filled
    # it. A version cut before that answer never filled, so nothing on it is trimmed; one opened
    # after it carries the mark in front of it and stays trimmed (the design's BEHAVIOUR.md).
    from backend.features.workspace.domain.chat import sent_from

    chat = _marked(_trunk("hi", "Done.", "again", "Done twice."), 2)
    before = replace(chat, versions=(_version("l2", "", 2, "again, shorter"),), active="l2")
    after = replace(chat, versions=(_version("l2", "", 4, "and more"),), active="l2")
    assert sent_from(before) == 0
    assert sent_from(after) == 2


def test_a_trimmed_chat_that_grows_back_to_the_ceiling_is_full_again():
    # 29 September: a trimmed chat that fills again shows the notice again. The measure counts from
    # the cut, so what is past it is what fills the chat.
    from backend.features.workspace.domain.chat import is_full

    trimmed = _marked(_trunk("a" * 200_000, "Done.", "hi", "Done."), 2)
    assert not is_full(trimmed)
    grown = replace(
        trimmed,
        messages=trimmed.messages + (_said("user", "go on"), _said("ai", "a" * 166_667)),
    )
    assert is_full(grown)


def test_a_trim_keeps_ten_thousand():
    # The owner's number, 28 September: "10k contexte kadar".
    from backend.features.workspace.domain.chat import TRIM_KEEPS

    assert TRIM_KEEPS == 10_000


def test_a_trim_drops_whole_turns_from_the_start_until_ten_thousand_is_left():
    # Seventeen turns of 3,000 each: 51,000, full. Three of them are 9,000 and four are 12,000, so
    # the cut stands before the fifteenth question -- message 28.
    from backend.features.workspace.domain.chat import chat_size, trim_point

    chat = _turns(*[("a" * 1000, "a" * 9000)] * 17)
    assert trim_point(chat) == 28
    assert chat_size(_marked(chat, 28)) == 9000


def test_a_trim_never_cuts_between_a_question_and_its_answer():
    # The last turn weighs 10,800 -- more than a trim keeps -- and its answer alone would fit. The
    # cut still stands before the question: the model is never handed an answer to nothing, and the
    # last turn stays whatever it weighs.
    from backend.features.workspace.domain.chat import trim_point

    chat = _turns(("a" * 100, "a" * 100), ("a" * 30_000, "a" * 6_000))
    assert trim_point(chat) == 2
