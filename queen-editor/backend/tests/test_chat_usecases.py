"""What the agent's chat doors decide (madde 417): a new chat, the list, one chat opened.

The record is faked (CODE-STANDARD, Tests). Its chats have the shape the real one folds them into:
{"id", "questions": [{"text", "askedAt", "steps", "outcome"}]}.

The module under test is imported inside the tests: it is written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
import pytest

AT_10 = "2026-10-06T10:00:00+00:00"
AT_11 = "2026-10-06T11:00:00+00:00"
AT_12 = "2026-10-06T12:00:00+00:00"


def usecases():
    from backend.features.agent.domain.usecases import chats
    return chats


def question(text, at):
    return {"text": text, "askedAt": at, "steps": [], "outcome": None}


def chat(chat_id, *questions):
    return {"id": chat_id, "questions": list(questions)}


class FakeChatRecord:
    """The project düğün and the chats it holds. What is added is written down."""

    def __init__(self, *chats):
        self.held = list(chats)
        self.added = []

    def project_exists(self, project):
        return project == "düğün"

    def chats(self, project):
        return list(self.held)

    def add_chat(self, project, chat_id):
        self.added.append((project, chat_id))
        self.held.append(chat(chat_id))


def test_a_new_chat_is_made_when_none_is_waiting():
    record = FakeChatRecord()

    assert usecases().new_chat(record, "düğün") == {"id": 1, "questions": []}
    assert record.added == [("düğün", 1)]


def test_a_new_chat_takes_the_number_after_the_highest():
    record = FakeChatRecord(chat(1, question("a", AT_10)), chat(2, question("b", AT_11)))

    assert usecases().new_chat(record, "düğün") == {"id": 3, "questions": []}
    assert record.added == [("düğün", 3)]


def test_a_waiting_empty_chat_is_returned_instead_of_a_new_one():
    """Yeni sohbet opens the empty chat if one is waiting (BEHAVIOUR.md, Agent panel)."""
    record = FakeChatRecord(chat(1, question("a", AT_10)), chat(2))

    assert usecases().new_chat(record, "düğün") == {"id": 2, "questions": []}
    assert record.added == []


def test_the_list_holds_only_chats_with_a_question_newest_last_question_first():
    first = "Projeyi özetler misin?\nHer kareyi ayrı anlat"
    record = FakeChatRecord(chat(1, question(first, AT_10), question("Peki 7?", AT_12)),
                            chat(2, question("Kaç kare var?", AT_11)),
                            chat(3))

    assert usecases().list_chats(record, "düğün") == [
        # The whole first question: cutting it to one line is the screen's.
        {"id": 1, "firstQuestion": first, "lastAskedAt": AT_12},
        {"id": 2, "firstQuestion": "Kaç kare var?", "lastAskedAt": AT_11},
    ]


def test_a_project_where_nothing_was_asked_lists_nothing():
    assert usecases().list_chats(FakeChatRecord(chat(1)), "düğün") == []


def test_a_chat_opens_with_everything_in_it():
    held = chat(2, {"text": "Kaç kare var?", "askedAt": AT_10,
                    "steps": [{"running": "3 numaralı kareyi okuyor…",
                               "done": "3 numaralı kareyi okudu", "finished": True}],
                    "outcome": {"kind": "answer", "text": "12 kare."}})
    record = FakeChatRecord(chat(1, question("a", AT_11)), held)

    assert usecases().open_chat(record, "düğün", 2) == held


def test_a_chat_that_is_not_there_is_refused():
    module = usecases()

    with pytest.raises(module.ChatMissing) as exc:
        module.open_chat(FakeChatRecord(chat(1)), "düğün", 7)

    assert str(exc.value) == "Sohbet yok: 7"


@pytest.mark.parametrize("door", ["new", "list", "open"])
def test_every_door_refuses_a_project_that_is_not_there_and_writes_nothing(door):
    module, record = usecases(), FakeChatRecord()
    ask = {"new": lambda: module.new_chat(record, "yok"),
           "list": lambda: module.list_chats(record, "yok"),
           "open": lambda: module.open_chat(record, "yok", 1)}[door]

    with pytest.raises(module.ProjectMissing) as exc:
        ask()

    assert str(exc.value) == "Proje yok: yok"
    assert record.added == []
