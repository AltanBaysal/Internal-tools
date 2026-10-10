"""Advance a chat: a message, an edit or a Try again, and the turn that answers it (Madde 461).

One turn at a time in a chat: the chat is held before it is read, so a request refused for that has
read and written nothing, and one let through reads what the turn before it wrote. Then the chat is
read once, the question written once, and the turn starts on that record on a thread of its own --
holding the chat until its end. Every refusal and every fault before the start lets the chat go.

Refusals are the domain's errors, as everywhere here; the routes turn them into status codes.
"""
from dataclasses import dataclass

from backend.features.workspace.domain.chat import Chat, is_full
from backend.features.workspace.domain.ports import LiveTurn
from backend.features.workspace.domain.errors import (
    ChatFull,
    ChatHeld,
    ChatNotFound,
    NothingToAnswer,
    ProjectNotFound,
    UnknownMode,
)
from backend.features.workspace.domain.modes import MODES
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.features.workspace.domain.usecases.retry_turn import retry_turn
from backend.features.workspace.domain.usecases.run_turn import run_turn


NO_TEXT = object()
"""What `text` is for Try again: no sentence at all. Only the retry door passes it (Madde 462) -- a
message with no text is a blank one, refused as blank."""


@dataclass(frozen=True)
class Started:
    """A turn is running on this chat: the record it was handed, and the turn to listen to."""

    turn: LiveTurn
    chat: Chat


@dataclass(frozen=True)
class Nothing:
    """Try again found nothing to try again -- an answer written while nobody was looking, or a
    stopped one. The chat as it was read, so whoever asked shows it without reading it again."""

    chat: Chat


def advance_chat(
    turns,
    chat_store,
    project_store,
    file_store,
    engine,
    project_id,
    wanted,
    text,
    clock,
    new_id,
    line_id,
    skill="",
    branch_at=None,
    mode="",
):
    """Started or Nothing. `wanted` is the chat, empty for a draft, which is held by the id it is
    about to be born as (`new_id`) -- nobody else can be holding that. `text` NO_TEXT is Try again.

    `clock` is asked for the question's moment here and for the answer's when the turn writes it.

    `mode` is a draft's alone (Madde 463): the mode picked before the chat existed, put on the
    newborn's row before its turn starts, or Edit when none was. A chat that exists has its mode
    picked on its own door, so one sent here is not read -- an older tab still sends one with every
    message, and must not move the chat with it."""
    drafting = not wanted
    # Before the hold: a refusal holds nothing and writes nothing.
    if drafting and mode and mode not in MODES:
        raise UnknownMode(mode)
    held = wanted or new_id
    turn = turns.reserve(project_id, held)
    if turn is None:
        raise ChatHeld(held)
    try:
        read, chat = _to_answer(
            chat_store, project_store, project_id, wanted, text, clock, new_id, line_id, skill, branch_at
        )
        if chat is None:
            turns.release(project_id, held, turn)
            return Nothing(read)
        # Once the row exists -- the birth wrote it -- and before the turn that reads it starts.
        if drafting and mode:
            chat_store.set_mode(project_id, chat.id, mode)
        turns.start(
            project_id,
            turn,
            chat,
            run_turn(chat_store, file_store, engine, project_id, chat, clock, turn),
        )
    except BaseException:
        turns.release(project_id, held, turn)
        raise
    return Started(turn, chat)


def _to_answer(chat_store, project_store, project_id, wanted, text, clock, new_id, line_id, skill, branch_at):
    """The chat as read, and the one whose question a turn is to answer -- None when there is
    nothing to try. Read once."""
    existing = chat_store.get(project_id, wanted) if wanted else None
    # Asked before anything else that could refuse. A full chat that is also already answered is
    # both, and what the user needs to hear is the one that stops them.
    if existing is not None and is_full(existing):
        raise ChatFull(wanted)
    # Absent is not blank. A blank sentence is somebody leaning on the space bar and is refused by
    # append_message; no sentence at all means they are asking for the answer, not sending one.
    if text is not NO_TEXT:
        # A name that is simply wrong is not "no chat yet": made here, a typo would become a second
        # chat nobody asked for.
        if wanted and existing is None:
            raise ChatNotFound(wanted)
        return existing, append_message(
            chat_store,
            project_id,
            existing,
            text,
            clock(),
            skill=skill,
            project_store=project_store,
            new_id=new_id,
            # Which message this one is replacing, when it is an edit (Madde 195): the turn that
            # follows is the same turn, with the same refusals in front of it.
            branch_at=branch_at,
            line_id=line_id,
        )
    if existing is None:
        # Which is missing, the project or its chat: the list says, off no disk (Madde 447).
        if project_store.get(project_id) is None:
            raise ProjectNotFound(project_id)
        raise NothingToAnswer(wanted)
    # Try again: after the ceiling, so a full chat refuses before anything is taken out.
    return existing, retry_turn(chat_store, project_id, existing)
