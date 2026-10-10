"""Read a chat with the turn running in it, if any (Madde 462).

While a turn runs it holds the chat as it stands -- nothing else writes it then (Madde 461) -- so the
chat is read there, off no disk. The turn is looked at first: one that ends between the two reads
then pairs its last snapshot with its final record, and whoever reads hears the end at once.
"""


def read_chat(turns, chat_store, project_id, chat_id):
    """(chat, snapshot): the chat or None, and its running turn's snapshot or None."""
    live = turns.get(project_id, chat_id)
    snapshot = live.snapshot() if live else None
    chat = (live and live.record()) or chat_store.get(project_id, chat_id)
    return chat, snapshot
