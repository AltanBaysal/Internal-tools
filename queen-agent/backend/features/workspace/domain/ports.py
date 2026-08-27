"""Ports the workspace domain depends on. Implementations live in data/."""
from typing import Protocol

from backend.features.workspace.domain.chat import Chat
from backend.features.workspace.domain.file import File, FileBody
from backend.features.workspace.domain.permission import Decision
from backend.features.workspace.domain.project import Project


class ProjectStore(Protocol):
    def add(self, project: Project) -> None:
        """Persist a new project. Raises if its id is already taken."""

    def list_all(self) -> list[Project]:
        """Every project, in no particular order."""

    def get(self, project_id: str) -> Project | None:
        """The project carrying this id, or None."""

    def replace(self, project: Project) -> None:
        """Overwrite an existing project's stored fields."""

    def delete(self, project_id: str) -> str | None:
        """Move the whole project to the trash and answer with the name it took, or None."""


class ChatStore(Protocol):
    def add(self, project_id: str, chat: Chat) -> None:
        """Persist a chat under its project."""

    def get(self, project_id: str, chat_id: str) -> Chat | None:
        """The chat carrying this id inside that project, or None."""

    def replace(self, project_id: str, chat: Chat) -> None:
        """Overwrite an existing chat."""

    def list_for(self, project_id: str) -> list[Chat]:
        """Every chat of the project, in no particular order."""

    def delete(self, project_id: str, chat_id: str) -> None:
        """Remove a chat for good. The files it produced are not touched."""


class Engine(Protocol):
    """Something that answers a conversation.

    Which model it answers with is not asked here: there is one, and config.py names it once. That
    belongs to whatever the engine was built with, not to the call.
    """

    def complete(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Answer a conversation. Messages carry the domain's own roles: user and ai."""

    def stream(self, messages: list[dict], tools: list[dict] | None = None, on_open=None):
        """Answer a conversation piece by piece.

        Yields {"text": str} as words arrive and {"tool_calls": [...]} when the model asks for one.

        `on_open` is handed a callable that cuts the connection this answer is reading, as soon as
        there is one to cut. An engine with no connection to cut never calls it.

        Also yields {"usage": {"sent": int, "cached": int, "answered": int}} when the engine says
        what the answer cost -- once, as the stream closes. Should it ever say so more than once,
        each figure is the total for this one call rather than the share since the last, so the
        newest replaces the one before it. An engine that never mentions spending never yields
        this, and every fake in the tests is such an engine.
        """


class Stops(Protocol):
    """The one cancel. What is held is the running answer's connection, never a note on disk."""

    def hold(self, project_id: str, chat_id: str, cut) -> None:
        """Take the way to cut this answer's connection. Cuts at once if a stop is already waiting."""

    def want(self, project_id: str, chat_id: str) -> None:
        """Stop the answer running for this chat, by cutting the connection it is reading."""

    def wanted(self, project_id: str, chat_id: str) -> bool:
        """Was this answer's connection cut by us. The only thing that tells a stop from a fault."""

    def clear(self, project_id: str, chat_id: str) -> None:
        """Forget the request and the connection both. Left standing, either would reach the
        next answer -- one by cutting it as it is born, the other by naming a stranger's socket."""


class Permissions(Protocol):
    """The answer a paused turn is waiting for. Held in memory, exactly like a stop.

    What has to survive a restart is the message, and it does. A question lives as long as the turn
    that asked it: if the process dies the turn dies with it, and there is nothing left to answer.
    """

    def answer(self, project_id: str, chat_id: str, allowed: bool, reason: str) -> None:
        """Leave the user's decision. Wakes the turn if one is waiting, and keeps it if not."""

    def wait(self, project_id: str, chat_id: str, tick: float) -> Decision | None:
        """Block until the decision arrives or `tick` seconds pass, and spend what is found.

        None means nothing was decided -- the tick ran out, or somebody woke the wait. Spending is
        what keeps a second question in the same turn a question.
        """

    def wake(self, project_id: str, chat_id: str) -> None:
        """End the wait without a decision. What a stop reaches for: there is no socket to cut
        while a turn is paused here."""

    def clear(self, project_id: str, chat_id: str) -> None:
        """Forget the question and the answer. Left standing, an answer would settle the next
        turn's question before anybody was asked."""


class FileStore(Protocol):
    def list_names(self, project_id: str) -> list[str]:
        """The names of the files a project holds."""

    def list_files(self, project_id: str) -> list[File]:
        """The project's files with the chip and the time the screens show."""

    def read(self, project_id: str, name: str) -> str | None:
        """A file's contents, or None if there is no such file."""

    def read_body(self, project_id: str, name: str) -> FileBody | None:
        """A file with its contents, or None if there is no such file."""

    def write(self, project_id: str, name: str, content: str) -> str:
        """Write a file and answer with the name actually used."""

    def delete(self, project_id: str, name: str) -> str | None:
        """Move a file to the trash and answer with the name it took there, or None if it is gone."""
