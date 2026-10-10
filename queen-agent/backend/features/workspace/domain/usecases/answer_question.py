"""Answer the question a running turn waits on (Madde 462), and what an Allow means (Madde 463).

An Allow puts the chat in Edit: the user said yes to working, and left in Ask or Plan the very next
write would raise the same question again -- and in Plan a plan written from here on would end the
turn the user just told to carry on. The rule is the server's, here and nowhere else; the browser
draws the mode it is answered with.

The order is the point. The chat is put in Edit first, and only then is the turn woken: the turn
reads the chat's mode at every call, and woken first, a second call in the same round could read the
old mode before the new one was set, and ask again.

Only an Allow of the question standing changes the mode. A stale one -- another turn, a question
already answered -- allowed nothing, and leaves the mode as it was. A Stop landing between the look
and the answer leaves the chat in Edit with nothing allowed; Allow meant "go ahead" all the same.
"""
from backend.features.workspace.domain.modes import EDIT


def answer_question(turns, chat_store, project_id, chat_id, turn_id, wait, allowed, reason):
    """The running turn, once answered, or None when none runs in the chat."""
    live = turns.get(project_id, chat_id)
    if live is None:
        return None
    if allowed and live.asks(turn_id, wait):
        chat_store.set_mode(project_id, chat_id, EDIT)
    live.decide(turn_id, wait, allowed, reason)
    return live
