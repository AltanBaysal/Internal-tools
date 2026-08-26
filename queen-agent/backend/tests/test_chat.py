from dataclasses import fields

from backend.features.workspace.domain.chat import Chat


def test_a_chat_carries_no_model():
    # Madde 82 took the field out rather than leaving it unread. A field nothing writes and nothing
    # reads is a question every later reader has to answer for themselves, and the answer is never
    # in the code -- so the field goes and this line says it went on purpose.
    assert "model" not in [field.name for field in fields(Chat)]


def test_a_chat_still_carries_its_skill():
    # The other half of the pair, and the reason the one above is not an accident: a skill really is
    # chosen per chat, and pressing the selected one again clears it.
    assert "skill" in [field.name for field in fields(Chat)]
