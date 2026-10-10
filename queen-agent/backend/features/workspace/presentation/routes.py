"""Workspace HTTP routes -- request/response translation only, no business rules."""
import json
import uuid
from datetime import datetime, timezone

from flask import Blueprint, Response, jsonify, request

from backend.features.workspace.domain.errors import (
    ChatFull,
    ChatHeld,
    ChatNotFound,
    ChatNotFull,
    EmptyMessage,
    FileNotFound,
    InvalidProjectName,
    NothingToAnswer,
    ProjectAnswering,
    ProjectNotFound,
    VersionNotFound,
)
from backend.features.workspace.domain.chat import (
    CONTEXT_CEILING,
    active_messages,
    chat_size,
    is_full,
    sent_from,
    variants_of,
)
from backend.features.workspace.domain.turn import Snapshot
from backend.features.workspace.domain.usecases.advance_chat import (
    NO_TEXT,
    Started,
    advance_chat,
)
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.delete_file import delete_file
from backend.features.workspace.domain.usecases.delete_project import delete_project
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.list_chats import list_chats
from backend.features.workspace.domain.usecases.list_files import list_files
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.features.workspace.domain.usecases.open_version import open_version
from backend.features.workspace.domain.usecases.read_file import read_file
from backend.features.workspace.domain.usecases.trim_chat import trim_chat

# What a request that would write a chat hears while that chat's turn is running (Madde 461, the
# user's "İkinci istek reddedilir"): a message, an edit, a Try again, a version, Continue here.
BUSY = "this chat is still answering -- try again once it has finished"
# And deleting its project: the folder would move from under the turn writing into it.
PROJECT_BUSY = "a chat in this project is still answering -- try again once it has finished"

BEAT_SECONDS = 15
"""How long the POST's stream may stay quiet before it says something (Madde 461).

Not a timeout: neither the turn nor its question has an end of its own. What this number says is
how often the browser hears from us while nothing happens -- the model thinking as well as a
question waiting: a stream gone quiet inside a tunnel is a stream the tunnel closes (about 100
seconds on trycloudflare), and a browser that went away is only discovered by writing to it. Since
the turn runs on its own, that discovery ends only the listening, never the turn.
"""


def make_workspace_bp(project_store, chat_store, file_store, engine, turns):
    workspace_bp = Blueprint("workspace", __name__)

    @workspace_bp.get("/api/projects")
    def get_projects():
        return jsonify([_project_json(project) for project in list_projects(project_store)])

    @workspace_bp.post("/api/projects")
    def post_project():
        payload = request.get_json(silent=True) or {}
        try:
            project = create_project(
                project_store, new_id=_new_id("p"), name=payload.get("name"), now=_now()
            )
        except InvalidProjectName:
            return jsonify({"error": "a project needs a name"}), 400
        return jsonify(_project_json(project)), 201

    @workspace_bp.patch("/api/projects/<project_id>")
    def patch_project(project_id):
        payload = request.get_json(silent=True) or {}
        try:
            project = edit_project(
                project_store,
                project_id,
                # What a pin is stamped with: the pinned are listed in the order they were pinned.
                now=_now(),
                name=payload.get("name"),
                pinned=payload.get("pinned"),
                archived=payload.get("archived"),
            )
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except InvalidProjectName:
            return jsonify({"error": "a project needs a name"}), 400
        return jsonify(_project_json(project))

    @workspace_bp.delete("/api/projects/<project_id>")
    def delete_project_route(project_id):
        try:
            trashed = delete_project(project_store, turns, project_id)
        except ProjectAnswering:
            return jsonify({"error": PROJECT_BUSY}), 409
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        # There is no way back, so the name is only a record of what happened on disk.
        return jsonify({"trashed": trashed})

    # There is no PATCH here. What a chat has said never changes: the skill is the session's and
    # rides on each message, and a chat is never renamed (Madde 86). Two things about it do move --
    # which version is open (Madde 195) and where the model starts reading it (Madde 345) -- and
    # each has a door of its own below, next to the other two that act on a chat rather than
    # describe it.
    @workspace_bp.get("/api/projects/<project_id>/chats")
    def get_chats(project_id):
        return jsonify([_chat_summary(chat) for chat in list_chats(chat_store, project_id)])

    @workspace_bp.get("/api/projects/<project_id>/chats/<chat_id>")
    def get_chat(project_id, chat_id):
        # While a turn runs it holds the chat as it stands -- nothing else writes it then -- so a
        # reload reads it there, off no disk (Madde 461).
        live = turns.get(project_id, chat_id)
        chat = (live and live.record()) or chat_store.get(project_id, chat_id)
        if chat is None:
            return jsonify({"error": "chat not found"}), 404
        return jsonify(_chat_json(chat))

    # One door, and one meaning: advance this chat. Which chat is a field in the body rather than a
    # piece of the address, because it is allowed to be empty -- and an empty piece of a path is a
    # different address, not an empty value.
    #
    # Text writes a message first; no text is Try again. The turn runs on a thread of its own since
    # Madde 461, whoever is listening; what leaves down this connection is the bridge's telling of
    # it, so the screen is what it was.
    @workspace_bp.post("/api/projects/<project_id>/messages")
    def post_message(project_id):
        payload = request.get_json(silent=True) or {}
        try:
            advanced = advance_chat(
                turns,
                chat_store,
                project_store,
                file_store,
                engine,
                project_id,
                payload.get("chat", ""),
                # Absent is neither blank nor null: no sentence at all is Try again.
                payload.get("text", NO_TEXT),
                _now(),
                # Minted whether or not they are used: the alternative is a second branch inside
                # the rule, asking the route for an id only once it knows it needs one.
                new_id=_new_id("c"),
                line_id=_new_id("l"),
                skill=payload.get("skill", ""),
                branch_at=payload.get("from"),
                mode=payload.get("mode", ""),
            )
        except ChatHeld:
            return jsonify({"error": BUSY}), 409
        except ChatFull:
            return jsonify(
                {"error": "this chat has reached its context ceiling -- start a new chat to keep going"}
            ), 400
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        except EmptyMessage:
            return jsonify({"error": "a message needs text"}), 400
        except NothingToAnswer:
            return jsonify({"error": "there is nothing here to answer"}), 400
        # Every refusal is settled by here, which is why they can still be status codes. A started
        # turn has its question written, and the first frame is `chat`: the browser reads it as
        # "the question is written" and asks again without it (Madde 449). Nothing to try again
        # ends the stream at once, and the screen reads the record and shows the answer.
        if isinstance(advanced, Started):
            return Response(_sse(advanced.chat.id, advanced.turn), mimetype="text/event-stream")
        return Response(_sse(advanced.chat_id, None), mimetype="text/event-stream")

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/version")
    def post_version(project_id, chat_id):
        # Which line the chat is open on (Madde 195).
        try:
            open_version(
                chat_store,
                turns,
                project_id,
                chat_id,
                (request.get_json(silent=True) or {}).get("version", ""),
            )
        except ChatHeld:
            return jsonify({"error": BUSY}), 409
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        except VersionNotFound:
            return jsonify({"error": "version not found"}), 404
        # The transcript is not sent back: the browser reads the chat the same way it does after a
        # turn, and a second shape for one record is a second thing to keep true.
        return jsonify({})

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/trim")
    def post_trim(project_id, chat_id):
        # Continue here (Madde 345). Answered like the version door, for the same reason: the
        # browser reads the chat again, and its `trimmed` says where the part no longer sent ends.
        try:
            trim_chat(chat_store, turns, project_id, chat_id)
        except ChatHeld:
            return jsonify({"error": BUSY}), 409
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        except ChatNotFull:
            return jsonify({"error": "this chat is not full"}), 400
        return jsonify({})

    def nothing_running(project_id, chat_id):
        # No turn to stop or answer, so nothing is done. Whether the chat exists at all is the row's
        # to say, off no disk.
        if not any(chat.id == chat_id for chat in chat_store.list_for(project_id)):
            return jsonify({"error": "chat not found"}), 404
        return jsonify({})

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/stop")
    def post_stop(project_id, chat_id):
        # Bound to the turn running now: a press landing after it ended reaches nothing. The browser
        # carries no turn id until Madde 462, so the turn holding the chat is the one it means.
        live = turns.get(project_id, chat_id)
        if live is None:
            return nothing_running(project_id, chat_id)
        live.stop(live.id)
        # Asked for, not done: the answer stops at its next chance, which has not come yet.
        return jsonify({})

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/permission")
    def post_permission(project_id, chat_id):
        # The stop's sibling, bound the same way: to the question standing now. One left before it
        # was asked is nobody's answer and is dropped.
        live = turns.get(project_id, chat_id)
        if live is None:
            return nothing_running(project_id, chat_id)
        asked = live.snapshot().permission
        if asked is not None:
            payload = request.get_json(silent=True) or {}
            live.decide(live.id, asked.wait, payload.get("allowed"), payload.get("reason", ""))
        # Left, not acted on: what the decision amounts to is seen in the stream it unblocks.
        return jsonify({})

    @workspace_bp.get("/api/projects/<project_id>/files")
    def get_files(project_id):
        return jsonify(
            [
                {"name": file.name, "ext": file.ext, "modifiedAt": file.modified_at}
                for file in list_files(file_store, project_id)
            ]
        )

    @workspace_bp.get("/api/projects/<project_id>/files/<name>")
    def get_file(project_id, name):
        # A name cannot carry a slash -- Flask's default converter stops at one, and the store's
        # root is the second lock.
        try:
            body = read_file(file_store, project_id, name)
        except FileNotFound:
            return jsonify({"error": "file not found"}), 404
        return jsonify(
            {
                "name": body.file.name,
                "ext": body.file.ext,
                "modifiedAt": body.file.modified_at,
                "size": body.size,
                "text": body.text,
            }
        )

    @workspace_bp.delete("/api/projects/<project_id>/files/<name>")
    def delete_project_file(project_id, name):
        try:
            trashed = delete_file(file_store, project_id, name)
        except FileNotFound:
            return jsonify({"error": "file not found"}), 404
        # Nobody reads this name any more, but it is the one sentence that says what happened on
        # disk, and deleting a project answers the same way.
        return jsonify({"trashed": trashed})

    return workspace_bp


def _sse(chat_id, turn):
    """Today's frames, told from the running turn: the bridge that keeps the screen as it was while
    the turn runs on its own (Madde 461), until the browser listens to the turn itself (462).

    It listens rather than drives: a browser that goes away ends this stream at its next write, and
    the turn runs on. Each wake tells what changed since the last one, so changes that came quicker
    than a wake arrive together -- the screen draws state, so it lands where the turn is.
    """
    # First, before the model has said a word: the id cannot come back as a field any more, and the
    # browser needs it to change the address. Sent every time rather than only when it is news --
    # no condition here, and the browser acts only if it differs from what it holds.
    yield _frame("chat", {"chat": chat_id})
    if turn is None:
        # Nothing to run: the stream ends, and the browser reads the record as after any turn.
        yield _frame("done", {})
        return
    seen = Snapshot(id=turn.id)
    while not seen.ended:
        now = turn.changed_since(seen.version, BEAT_SECONDS)
        if now.version == seen.version:
            # No event line, which is why the browser's parser drops it -- and dropping it is the
            # whole job. This frame exists to be bytes on a connection that has gone quiet.
            yield ": waiting\n\n"
            continue
        yield from _told(seen, now)
        seen = now


def _told(before, after):
    """The frames that say how the turn moved from one snapshot to the next, in the order a turn
    does those things. No words among them since Madde 440: the answer comes back whole and the
    screen reads it off the record once the turn is over."""
    if after.progress is not None and after.progress != before.progress:
        # Where the turn has got to (Madde 194): the round and the count, as they are now.
        progress = after.progress
        yield _frame("progress", {"round": progress.round, "of": progress.of, "tokens": progress.tokens})
    files = after.files[len(before.files) :]
    calls = after.calls[len(before.calls) :]
    for name in files:
        yield _frame("file", {"name": name})
    for step in calls:
        yield _frame("call", {"tool": step.tool, "target": step.target, "outcome": step.outcome})
    # After them: a file or a step takes the card down on screen, so a write that began in the same
    # wake as the last one ended -- no disk between them -- needs its card told again behind them.
    if after.creating and (not before.creating or files or calls):
        yield _frame("file-start", {})
    if after.permission is not None and after.permission != before.permission:
        asked = after.permission
        yield _frame("permission", {"tool": asked.tool, "arguments": asked.arguments})
    if after.ended:
        if after.error:
            # The turn's own fault: nothing was written. The status code was settled the moment
            # the first byte left, so it can only travel inside the stream.
            yield _frame("error", {"error": after.error})
        else:
            # The record has one home since Madde 89, and it is get_chat. This frame says the turn
            # is over; what it wrote is a question asked separately.
            yield _frame("done", {})


def _frame(event, data):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _new_id(prefix):
    # Opaque and immutable: renaming must not move anything on disk or break a link.
    return prefix + uuid.uuid4().hex[:12]


def _now():
    # Milliseconds, not seconds: the stamp is what orders projects and chats, and two things made
    # within the same second would otherwise fall back to a random id and come back in any order.
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _project_json(project):
    return {
        "id": project.id,
        "name": project.name,
        "createdAt": project.created_at,
        "chats": project.chat_count,
        "files": project.file_count,
        "pinned": project.pinned,
        "archived": project.archived,
        "lastActivity": project.last_activity,
    }


def _chat_summary(chat):
    return {
        "id": chat.id,
        "title": chat.title,
        "createdAt": chat.created_at,
        "lastActivity": chat.last_activity,
    }


def _chat_json(chat):
    return {
        **_chat_summary(chat),
        # The ceiling travels with the number: the gauge draws a share, and a share needs its
        # denominator. A second copy of the ceiling living in the browser is what would go stale.
        #
        # The key stays `sent` while the number behind it became the chat's messages (Madde 337):
        # it is still what the chat sends of itself, and renaming it would rebuild the frontend to
        # say the same thing. The gauge is handed the number the ceiling actually stops on -- a
        # gauge measuring something else cannot warn about the wall it is not watching.
        "context": {"sent": chat_size(chat), "ceiling": CONTEXT_CEILING},
        # How many messages at the start of the open line no longer go to the model (Madde 345).
        # Always present, 0 when nothing was trimmed, for the same reason `calls` is below.
        "trimmed": sent_from(chat),
        # Whether the chat takes another turn (Madde 352). The screen stands its notice on this
        # alone rather than counting against the ceiling itself -- the rule has one home.
        "full": is_full(chat),
        # The open line since Madde 195, and the key stays `messages`: what the browser is handed is
        # the conversation as it stands, which is what it always was.
        "messages": [
            {
                "role": message.role,
                "at": message.at,
                "text": message.text,
                # Which of the versions standing in this place is showing, and what the arrows can
                # reach. Always present, like calls below: a field that comes and goes makes every
                # reader check for it first.
                "variants": standing,
                "files": list(message.files),
                "skill": message.skill,
                # Always present, unlike on disk: the browser draws from what it is handed, and an
                # absent field would make every reader check for it.
                "calls": [
                    {"tool": call.tool, "target": call.target, "outcome": call.outcome}
                    for call in message.calls
                ],
                "stopped": message.stopped,
                # "" or the kind of failure, "technical" or "refused" (Madde 440, Madde 445).
                # Always present, like `stopped`; the text is then what the chat says of it.
                "failed": message.failed,
                # The breakdown travels whole: the screen draws `sent` and `cached` under an
                # answer, and `answered` stays for the context work to read.
                "usage": {
                    "sent": message.usage.sent,
                    "cached": message.usage.cached,
                    "answered": message.usage.answered,
                },
            }
            for message, standing in zip(active_messages(chat), variants_of(chat))
        ],
    }
