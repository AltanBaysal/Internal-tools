"""FileChatStore -- the only place that knows the chats/<id>.json schema.

Which chats a project has is projects.json's answer (FileProjectStore, Madde 447): the list is read
from there and opens no chat, and a chat is opened only once its row names it.
"""
import json

from backend.features.workspace.domain.chat import Chat, Message, ToolCall, Usage, Version

CHATS_DIR = "chats"
SUFFIX = ".json"


class FileChatStore:
    def __init__(self, store, projects):
        self._store = store
        self._projects = projects

    def add(self, project_id, chat):
        self._write(project_id, chat)

    def replace(self, project_id, chat):
        self._write(project_id, chat)

    def get(self, project_id, chat_id):
        # The id comes from the address, so it becomes a path only once projects.json names it -- and
        # an id nobody made costs no trip to the disk.
        if not any(chat.id == chat_id for chat in self._projects.chats(project_id)):
            return None
        try:
            text = self._store.read_text(self._path(project_id, chat_id))
        except FileNotFoundError:
            # A row that outlived its chat -- the project's folder moved by hand, or to the trash by a
            # delete a sudden death half finished. Not found rather than a crash on every look.
            return None
        return _as_chat(chat_id, json.loads(text))

    def list_for(self, project_id):
        return self._projects.chats(project_id)

    # A chat's mode is a setting, not something it said, so it lives on its row (Madde 463): picking
    # one opens no chat file.
    def mode_of(self, project_id, chat_id):
        return self._projects.chat_mode(project_id, chat_id)

    def set_mode(self, project_id, chat_id, mode):
        return self._projects.set_chat_mode(project_id, chat_id, mode)

    def _write(self, project_id, chat):
        # The id is the file name, so it is not written inside: no artifact repeats an answer
        # another one already gives.
        stored = {
            "title": chat.title,
            "createdAt": chat.created_at,
            "messages": [_message_json(message) for message in chat.messages],
        }
        # The same rule the fields below keep: a chat that never branched writes neither key, and
        # reads back exactly as it did before Madde 195.
        if chat.versions:
            stored["versions"] = [_version_json(version) for version in chat.versions]
        if chat.active:
            stored["active"] = chat.active
        # A chat carries no skill of its own since Madde 86, and no model since 82. Older records
        # still have those keys here; nothing puts one back, so they drop the first time such a
        # chat is written again.
        self._store.write_text(
            self._path(project_id, chat.id),
            json.dumps(stored, ensure_ascii=False, indent=2),
        )
        # After the chat itself: a row never names a chat that is not on disk.
        self._projects.put_chat(project_id, chat)

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
    # The same rule. Only messages Madde 146 to 357 wrote carry one, and they keep it when the chat
    # is written again; every other message looks exactly as it did, and no migration is owed.
    if message.model:
        stored["model"] = message.model
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
    # Only the message a trim was written on carries one.
    if message.trimmed:
        stored["trimmed"] = message.trimmed
    # Only a failed answer carries one, and almost no answer fails.
    if message.failed:
        stored["failed"] = message.failed
    return stored


def _version_json(version):
    # Where it split and what was said after it. The messages before the split belong to the line it
    # grew out of and are not repeated here (Madde 195).
    return {
        "id": version.id,
        "parent": version.parent,
        "at": version.at,
        "messages": [_message_json(message) for message in version.messages],
    }


def _call_json(call):
    # The same rule one level down: a call about no file in particular writes no target, and one
    # recorded before outcomes existed writes no outcome.
    stored = {"tool": call.tool}
    if call.target:
        stored["target"] = call.target
    if call.outcome:
        stored["outcome"] = call.outcome
    return stored


def _as_usage(raw):
    # Field by field rather than **raw: a chat on disk can be edited by hand, and a key this app
    # does not know would turn a stray edit into a crash instead of something ignored. The chats
    # answered between Madde 133 and 337 carry one such key, `context`, and it drops the next time
    # the chat is written.
    if not raw:
        return Usage()
    return Usage(raw.get("sent", 0), raw.get("cached", 0), raw.get("answered", 0))


def _as_message(message):
    return Message(
        role=message["role"],
        at=message["at"],
        text=message["text"],
        # Chats written before these fields existed simply have neither.
        files=tuple(message.get("files", ())),
        skill=message.get("skill", ""),
        model=message.get("model", ""),
        calls=tuple(
            ToolCall(call["tool"], call.get("target", ""), call.get("outcome", ""))
            for call in message.get("calls", ())
        ),
        stopped=message.get("stopped", False),
        usage=_as_usage(message.get("usage")),
        trimmed=message.get("trimmed", 0),
        failed=message.get("failed", ""),
    )


def _as_version(raw):
    return Version(
        id=raw["id"],
        parent=raw.get("parent", ""),
        at=raw.get("at", 0),
        messages=tuple(_as_message(message) for message in raw.get("messages", ())),
    )


def _as_chat(chat_id, raw):
    return Chat(
        id=chat_id,
        title=raw["title"],
        created_at=raw["createdAt"],
        messages=tuple(_as_message(message) for message in raw["messages"]),
        # A chat written before Madde 195 has neither, and reads back as the one line it is. No
        # migration: the fields fill themselves the first time somebody edits a message.
        versions=tuple(_as_version(version) for version in raw.get("versions", ())),
        active=raw.get("active", ""),
    )
