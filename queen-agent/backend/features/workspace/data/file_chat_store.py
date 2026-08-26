"""FileChatStore -- the only place that knows the chats/<id>.json schema."""
import json

from backend.features.workspace.domain.chat import Chat, Message, ToolCall, Usage
from backend.features.workspace.domain.naming import unique_name

CHATS_DIR = "chats"
# The same trash the files go to: one directory answers "what did the user just delete".
TRASH_DIR = "trash"
SUFFIX = ".json"


class FileChatStore:
    def __init__(self, store):
        self._store = store

    def add(self, project_id, chat):
        self._write(project_id, chat)

    def replace(self, project_id, chat):
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

    def delete(self, project_id, chat_id):
        # Moved, not destroyed, and into the same trash a deleted file goes to: a chat is the user's
        # own writing, and nothing in this app removes work from the disk.
        name = f"{chat_id}{SUFFIX}"
        trashed = unique_name(self._store.list_dir(f"{project_id}/{TRASH_DIR}"), name)
        self._store.move(self._path(project_id, chat_id), f"{project_id}/{TRASH_DIR}/{trashed}")

    def _write(self, project_id, chat):
        # The id is the file name, so it is not written inside: no artifact repeats an answer
        # another one already gives.
        stored = {
            "title": chat.title,
            "createdAt": chat.created_at,
            "messages": [_message_json(message) for message in chat.messages],
        }
        # A chat that picked no model writes no field, exactly as a message with no files does.
        if chat.model:
            stored["model"] = chat.model
        if chat.skill:
            stored["skill"] = chat.skill
        self._store.write_text(
            self._path(project_id, chat.id),
            json.dumps(stored, ensure_ascii=False, indent=2),
        )

    @staticmethod
    def _path(project_id, chat_id):
        return f"{project_id}/{CHATS_DIR}/{chat_id}{SUFFIX}"


def _message_json(message):
    stored = {"role": message.role, "at": message.at, "text": message.text}
    # An empty list is noise on disk: the field appears only when there is something in it.
    if message.files:
        stored["files"] = list(message.files)
    if message.skill:
        stored["skill"] = message.skill
    if message.calls:
        stored["calls"] = [_call_json(call) for call in message.calls]
    # Only the true one is written: almost no answer is stopped, and a false everywhere is noise.
    if message.stopped:
        stored["stopped"] = True
    # An all-zero object is noise too, and it is what a message nobody measured carries -- the
    # user's own sentences included, since spending is what an answer does.
    if message.usage != Usage():
        stored["usage"] = {
            "sent": message.usage.sent,
            "cached": message.usage.cached,
            "answered": message.usage.answered,
        }
    return stored


def _call_json(call):
    # The same rule one level down: a call about no file in particular writes no target.
    stored = {"tool": call.tool}
    if call.target:
        stored["target"] = call.target
    return stored


def _as_usage(raw):
    # Field by field rather than **raw: a chat on disk can be edited by hand, and a key this app
    # does not know would turn a stray edit into a crash instead of something ignored.
    if not raw:
        return Usage()
    return Usage(raw.get("sent", 0), raw.get("cached", 0), raw.get("answered", 0))


def _as_chat(chat_id, raw):
    return Chat(
        id=chat_id,
        title=raw["title"],
        created_at=raw["createdAt"],
        # Chats written before these fields existed picked nothing, which is what empty means.
        model=raw.get("model", ""),
        skill=raw.get("skill", ""),
        messages=tuple(
            Message(
                role=message["role"],
                at=message["at"],
                text=message["text"],
                # Chats written before these fields existed simply have neither.
                files=tuple(message.get("files", ())),
                skill=message.get("skill", ""),
                calls=tuple(
                    ToolCall(call["tool"], call.get("target", ""))
                    for call in message.get("calls", ())
                ),
                stopped=message.get("stopped", False),
                usage=_as_usage(message.get("usage")),
            )
            for message in raw["messages"]
        ),
    )
