"""Ports the workspace domain depends on. Implementations live in data/."""
from typing import Callable, Protocol

from backend.features.workspace.domain.chat import Chat, ChatSummary
from backend.features.workspace.domain.file import File, FileBody
from backend.features.workspace.domain.permission import Decision
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.turn import Snapshot


class ProjectStore(Protocol):
    def add(self, project: Project) -> None:
        """Persist a new project. Raises if its id is already taken."""

    def list_all(self) -> list[Project]:
        """Every project, in no particular order."""

    def get(self, project_id: str) -> Project | None:
        """The project carrying this id, or None."""

    def update(self, project_id: str, change: Callable[[Project], Project]) -> Project | None:
        """Apply `change` to the project and answer with it as it now stands, or None if there is
        no such project.

        What is kept of the changed project is its name, pinned_at and archived: the counts and
        the last use are not the project's to set -- they come from its chats and files.
        """

    def delete(self, project_id: str) -> str | None:
        """Move the whole project to the trash and answer with the name it took, or None."""


class ChatStore(Protocol):
    def add(self, project_id: str, chat: Chat) -> None:
        """Persist a chat under its project."""

    def get(self, project_id: str, chat_id: str) -> Chat | None:
        """The chat carrying this id inside that project, or None."""

    def replace(self, project_id: str, chat: Chat) -> None:
        """Overwrite an existing chat."""

    def list_for(self, project_id: str) -> list[ChatSummary]:
        """What a list shows of every chat of the project, in no particular order -- read without
        opening any chat (Madde 447)."""


class Engine(Protocol):
    """Something that answers a conversation, or one text on its own.

    Which model it answers with is settled when it is built, not asked per turn (Madde 358): there
    is one, config.py names it, and nothing on the screen does.
    """

    def stream(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        on_open=None,
    ):
        """Answer a conversation piece by piece.

        One request, one try: the black box (black_box.py) reads the stream to its end and is what
        sends it again (Madde 440). Raising is how a try fails.

        Yields {"text": str} as words arrive and {"tool_calls": [...]} when the model asks for one.

        `on_open` is handed a callable that cuts the connection this answer is reading, as soon as
        there is one to cut. An engine with no connection to cut never calls it.

        Also yields {"usage": {"sent": int, "cached": int, "answered": int}} when the engine says
        what the answer cost -- once, as the stream closes. Should it ever say so more than once,
        each figure is the total for this one call rather than the share since the last, so the
        newest replaces the one before it. An engine that never mentions spending never yields
        this, and every fake in the tests is such an engine.
        """

    def stream_alone(self, system: str, text: str, on_open=None):
        """One instruction and one text in a request of their own, answered like `stream`.

        No conversation, no tools, and none of the fixed head -- QueenAgent's system prompt and the
        SDXL document (Madde 453): `system` is the whole of what the model is told and `text` the
        whole of what it reads. The black box's check asks
        this (Madde 445) -- QueenAgent's page is about tools, files and chats, in front of a model
        whose whole job is one word. A stream rather than one piece so that a stop cuts it like any
        other request: `on_open` is the same as `stream`'s.
        """


class TurnControl(Protocol):
    """What a running turn's loop asks of the turn it belongs to (Madde 461): its stop and its
    question. One per turn, so nothing a turn leaves behind reaches the next one."""

    def stopped(self) -> bool:
        """Was this turn stopped. The only thing that tells a cut connection from a fault."""

    def hold(self, cut) -> None:
        """Take the way to cut the request this turn is reading. Cuts at once if already stopped."""

    def decision(self) -> Decision | None:
        """Wait, with no limit, for the answer to the question this turn just asked; None if the
        turn is stopped instead."""


class LiveTurn(TurnControl, Protocol):
    """A turn as the requests reach it while it runs: what it holds, what it shows, and the two
    things a person can tell it. A stop and a decision name the turn and the question they mean,
    so one meant for another does nothing."""

    id: str

    def record(self) -> Chat | None:
        """The chat as this turn holds it, or None before one is handed -- then the disk has it."""

    def snapshot(self) -> Snapshot:
        """The turn as it stands now."""

    def changed_since(self, version: int, timeout: float) -> Snapshot:
        """The snapshot once it has moved past `version`, or as it is after `timeout` seconds."""

    def stop(self, turn_id: str) -> None:
        """Stop this turn, if it is the one named: cut its request and end a wait on a question."""

    def decide(self, turn_id: str, wait: int, allowed: bool, reason: str) -> None:
        """Answer the question standing, if turn and question are the ones named."""


class Turns(Protocol):
    """The turns running now, at most one per chat, each holding its chat while it runs. In memory:
    a turn lives as long as the process running it."""

    def reserve(self, project_id: str, chat_id: str) -> LiveTurn | None:
        """A new turn holding this chat, or None if one already does -- in one step."""

    def release(self, project_id: str, chat_id: str, turn: LiveTurn, error: str = "") -> None:
        """Let go of the chat, if that turn is still the one holding it, and end the turn -- with
        these words when its own code broke. Every hold ends, so nobody listens to one for ever."""

    def get(self, project_id: str, chat_id: str) -> LiveTurn | None:
        """The turn holding this chat, or None."""

    def any_in(self, project_id: str) -> bool:
        """Whether any chat of the project is held."""

    def start(self, project_id: str, turn: LiveTurn, chat: Chat, pieces) -> None:
        """Run the turn's loop on its own thread, handed this record; let go of the chat at its end."""


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
