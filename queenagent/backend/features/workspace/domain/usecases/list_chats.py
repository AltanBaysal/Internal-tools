"""List chats newest first -- both the sidebar and the project screen show the latest on top."""


def list_chats(chat_store, project_id):
    # By last activity rather than by creation: a chat answered a minute ago belongs on top even if
    # it started yesterday. The id breaks ties so the order never wobbles.
    return sorted(
        chat_store.list_for(project_id),
        key=lambda chat: (chat.last_activity, chat.id),
        reverse=True,
    )
