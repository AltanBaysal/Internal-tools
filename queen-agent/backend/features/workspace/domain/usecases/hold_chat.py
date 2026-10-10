"""Hold a chat while something writes it, so no turn starts between the read and the write (Madde 461).

What a version and Continue here do: each reads the chat and writes it back, and a turn that began
in between would build its answer on the record from before. Held, the turn waits; and while a turn
already holds the chat they are refused, having read and written nothing.
"""
from backend.features.workspace.domain.errors import ChatHeld


def hold_chat(turns, project_id, chat_id, act):
    """What act() answers, done with the chat held. Raises ChatHeld while a turn holds it."""
    holding = turns.reserve(project_id, chat_id)
    if holding is None:
        raise ChatHeld(chat_id)
    try:
        return act()
    finally:
        turns.release(project_id, chat_id, holding)
