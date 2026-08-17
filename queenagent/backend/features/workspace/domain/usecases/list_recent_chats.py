"""Every chat in the workspace, newest first -- what the sidebar's Recent chats shows."""


def list_recent_chats(chat_store):
    # Each entry is (project_id, chat): the sidebar needs the project to know where to navigate.
    return sorted(
        chat_store.list_all(),
        key=lambda pair: (pair[1].last_activity, pair[1].id),
        reverse=True,
    )
