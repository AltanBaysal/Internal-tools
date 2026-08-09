"""FileChatStore -- the only place that knows the chats/<id>.json schema."""
import json

from backend.features.workspace.domain.chat import Chat, Message

CHATS_DIR = "chats"
SUFFIX = ".json"


class FileChatStore:
    def __init__(self, store):
        self._store = store

    def add(self, project_id, chat):
        self._write(project_id, chat)

    def get(self, project_id, chat_id):
        path = self._path(project_id, chat_id)
        if not self._store.exists(path):
            return None
        return _as_chat(chat_id, json.loads(self._store.read_text(path)))

    def list_for(self, project_id):
        chats = []
        for entry in self._store.list_dir(f"{project_id}/{CHATS_DIR}"):
            if not entry.endswith(SUFFIX):
                continue  # anything else in the folder is not ours to read
            chats.append(self.get(project_id, entry[: -len(SUFFIX)]))
        return chats

    def _write(self, project_id, chat):
        # The id is the file name, so it is not written inside: no artifact repeats an answer
        # another one already gives.
        self._store.write_text(
            self._path(project_id, chat.id),
            json.dumps(
                {
                    "title": chat.title,
                    "createdAt": chat.created_at,
                    "messages": [
                        {"role": message.role, "at": message.at, "text": message.text}
                        for message in chat.messages
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
        )

    @staticmethod
    def _path(project_id, chat_id):
        return f"{project_id}/{CHATS_DIR}/{chat_id}{SUFFIX}"


def _as_chat(chat_id, raw):
    return Chat(
        id=chat_id,
        title=raw["title"],
        created_at=raw["createdAt"],
        messages=tuple(
            Message(role=message["role"], at=message["at"], text=message["text"])
            for message in raw["messages"]
        ),
    )
