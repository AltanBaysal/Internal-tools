"""Ports this feature needs. Implemented in data/, faked in tests -- domain stays pure."""
from typing import Protocol


class ChatRecord(Protocol):
    """A project's chats with the agent, kept with the project for good (madde 417).

    A chat is {"id": int, "questions": [question]}. A question is {"text", "askedAt", "steps",
    "outcome"}; a step is {"running", "done", "finished"} -- its sentence while it goes on, its
    sentence once done, and whether it is. The outcome is None while the agent still works on the
    question, else {"kind": "answer" | "failure", "text"} or {"kind": "stopped"}. A failure's text is
    a refusal's sentence or a technical error's own words.

    A step, its end and an outcome are written to the chat's latest question.
    """

    def project_exists(self, project: str) -> bool:
        ...

    def chats(self, project: str) -> list[dict]:
        """Every chat of the project, in the order they were opened."""
        ...

    def add_chat(self, project: str, chat_id: int) -> None:
        """A chat with nothing asked yet."""
        ...

    def add_question(self, project: str, chat_id: int, text: str, at: str) -> None:
        ...

    def add_step(self, project: str, chat_id: int, running: str, done: str) -> None:
        """A step begins, with both of its sentences; it is not finished yet."""
        ...

    def finish_step(self, project: str, chat_id: int) -> None:
        """The latest step is finished."""
        ...

    def answer(self, project: str, chat_id: int, text: str) -> None:
        ...

    def fail(self, project: str, chat_id: int, text: str) -> None:
        ...

    def stop(self, project: str, chat_id: int) -> None:
        ...
