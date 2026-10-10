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
from backend.features.workspace.domain.turn import status_of
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
from backend.features.workspace.domain.usecases.read_chat import read_chat
from backend.features.workspace.domain.usecases.read_file import read_file
from backend.features.workspace.domain.usecases.trim_chat import trim_chat

# What a request that would write a chat hears while that chat's turn is running (Madde 461, the
# user's "İkinci istek reddedilir"): a message, an edit, a Try again, a version, Continue here.
BUSY = "this chat is still answering -- try again once it has finished"
# And deleting its project: the folder would move from under the turn writing into it.
PROJECT_BUSY = "a chat in this project is still answering -- try again once it has finished"

BEAT_SECONDS = 15
"""How long the events stream may stay quiet before it says something (Madde 461, 462).

Not a timeout: neither the turn nor its question has an end of its own. What this number says is
how often the browser hears from us while nothing happens -- the model thinking as well as a
question waiting: a stream gone quiet inside a tunnel is a stream the tunnel closes (about 100
seconds on trycloudflare), and a browser that went away is only discovered by writing to it. Since
the turn runs on its own, that discovery ends only the listening, never the turn.
"""

# What keeps a proxy from holding the frames back: nothing here may be cached, and nginx-style
# buffers are told to pass each frame on as it is written.
EVENT_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}


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
        # With its status and its running turn (Madde 462): a reload draws the turn, its Stop and
        # its question from here. While a turn runs, off no disk (Madde 461).
        chat, snapshot = read_chat(turns, chat_store, project_id, chat_id)
        if chat is None:
            return jsonify({"error": "chat not found"}), 404
        return jsonify(_chat_state(chat, snapshot))

    @workspace_bp.get("/api/projects/<project_id>/chats/<chat_id>/events")
    def get_events(project_id, chat_id):
        # The running turn as it moves (Madde 462). Found here rather than inside the stream, so the
        # turn listened to is the one running as the request arrives. No chat is read: a name that
        # holds no turn hears that none runs, which is all this door says.
        live = turns.get(project_id, chat_id)
        return Response(_listened(live), mimetype="text/event-stream", headers=EVENT_HEADERS)

    def advanced_json(advanced):
        """A started turn's answer, or Try again's when it found nothing: the chat as reading it
        gives it -- the screen draws the transcript at once, with no read after the door's answer
        (Madde 462). The turn is looked at before the record it holds, as read_chat does."""
        if isinstance(advanced, Started):
            snapshot = advanced.turn.snapshot()
            return jsonify(_chat_state(advanced.turn.record(), snapshot)), 202
        return jsonify(_chat_state(advanced.chat, None)), 200

    def busy(project_id, chat_id):
        # With the chat as the turn holds it, off no disk: a tab that was out of date draws the turn
        # it ran into over the question that started it, and its box keeps the sentence. A name
        # with no chat behind it -- two requests for one wrong id at once -- has only the turn.
        chat, snapshot = read_chat(turns, chat_store, project_id, chat_id)
        if chat is None:
            return jsonify({"error": BUSY, "turn": _turn_json(snapshot)}), 409
        return jsonify({"error": BUSY, **_chat_state(chat, snapshot)}), 409

    def advance(project_id, wanted, text, payload):
        return advance_chat(
            turns,
            chat_store,
            project_store,
            file_store,
            engine,
            project_id,
            wanted,
            text,
            _now,
            # Minted whether or not they are used: the alternative is a second branch inside the
            # rule, asking the route for an id only once it knows it needs one.
            new_id=_new_id("c"),
            line_id=_new_id("l"),
            skill=payload.get("skill", ""),
            branch_at=payload.get("from"),
            # The request says it until Madde 463 gives the chat one.
            mode=payload.get("mode", ""),
        )

    # One door, and one meaning: say something in this chat. Which chat is a field in the body
    # rather than a piece of the address, because it is allowed to be empty -- and an empty piece of
    # a path is a different address, not an empty value. Try again has a door of its own since
    # Madde 462, so absent text here is blank text, refused as blank.
    @workspace_bp.post("/api/projects/<project_id>/messages")
    def post_message(project_id):
        payload = request.get_json(silent=True) or {}
        wanted = payload.get("chat", "")
        try:
            advanced = advance(project_id, wanted, payload.get("text", ""), payload)
        except ChatHeld as held:
            return busy(project_id, held.args[0])
        except ChatFull:
            return full()
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        except EmptyMessage:
            return jsonify({"error": "a message needs text"}), 400
        return advanced_json(advanced)

    # Try again (Madde 462): what it means is the chat's status, and the server's to decide. A
    # running turn is handed back, so the screen reconnects; an unanswered question or a failed
    # answer starts the loop; anything else is answered as it is. The question is never written.
    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/retry")
    def post_retry(project_id, chat_id):
        payload = request.get_json(silent=True) or {}
        try:
            advanced = advance(project_id, chat_id, NO_TEXT, payload)
        except ChatHeld:
            # Reconnecting writes nothing and reads the chat where the turn holds it.
            chat, snapshot = read_chat(turns, chat_store, project_id, chat_id)
            return jsonify(_chat_state(chat, snapshot))
        except ChatFull:
            return full()
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except NothingToAnswer:
            return jsonify({"error": "chat not found"}), 404
        return advanced_json(advanced)

    def full():
        return jsonify(
            {"error": "this chat has reached its context ceiling -- start a new chat to keep going"}
        ), 400

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
        return jsonify({"turn": None})

    # Stop and the answer to a question name what they were pressed for (Madde 462): the turn, and
    # the question within it. A press landing late -- after its turn ended, or once another one
    # began -- names something no longer running, and does nothing. Each answers with the turn as it
    # stands after the press, off no disk; what the press amounts to is heard on the events door.
    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/stop")
    def post_stop(project_id, chat_id):
        live = turns.get(project_id, chat_id)
        if live is None:
            return nothing_running(project_id, chat_id)
        live.stop((request.get_json(silent=True) or {}).get("turn"))
        # Asked for, not done: the answer stops at its next chance, which has not come yet.
        return jsonify({"turn": _turn_json(live.snapshot())})

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/permission")
    def post_permission(project_id, chat_id):
        live = turns.get(project_id, chat_id)
        if live is None:
            return nothing_running(project_id, chat_id)
        payload = request.get_json(silent=True) or {}
        live.decide(
            payload.get("turn"), payload.get("wait"), payload.get("allowed"), payload.get("reason", "")
        )
        return jsonify({"turn": _turn_json(live.snapshot())})

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


def _listened(live):
    """The running turn, told to one listener (Madde 462): the snapshot as it stands first, then a
    snapshot on every change, a beat while nothing moves, and the stream ends after the turn does.

    Whole snapshots, small (a few hundred bytes a step): a listener that wakes after several changes
    lands where the turn is, and one that reconnects needs nothing but the first frame -- no event
    log, no event ids. It listens rather than drives: a browser that goes away ends this stream at
    its next write, and the turn runs on.
    """
    if live is None:
        yield _frame({"turn": None})
        return
    seen = live.snapshot()
    yield _frame(_told(seen))
    while not seen.ended:
        now = live.changed_since(seen.version, BEAT_SECONDS)
        if now.version == seen.version:
            # A comment line, which EventSource drops -- and dropping it is the whole job. This
            # frame exists to be bytes on a connection that has gone quiet.
            yield ": beat\n\n"
            continue
        seen = now
        yield _frame(_told(seen))


def _told(snapshot):
    # The last frame says no turn runs; the browser then reads the record the turn wrote. A turn
    # whose own code broke wrote nothing, and its words travel here: no record will say them.
    if snapshot.ended and snapshot.error:
        return {"turn": None, "error": snapshot.error}
    return {"turn": _turn_json(snapshot)}


def _frame(data):
    # No event name: every frame is a snapshot, and EventSource hands an unnamed one to onmessage.
    return f"data: {json.dumps(data)}\n\n"


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


def _turn_json(snapshot):
    """A running turn as the screen draws it, or None when none runs (Madde 462). The same object in
    every answer that carries one -- reading a chat, its events, a refused message, Stop."""
    if snapshot is None or snapshot.ended:
        return None
    progress, asked = snapshot.progress, snapshot.permission
    return {
        "id": snapshot.id,
        "status": status_of(None, snapshot),
        "calls": [{"tool": step.tool, "target": step.target, "outcome": step.outcome} for step in snapshot.calls],
        "files": list(snapshot.files),
        # A file being written this moment: the dashed card.
        "creating": snapshot.creating,
        # Where the turn has got to (Madde 194), or None before its first round has begun.
        "progress": progress and {"round": progress.round, "of": progress.of, "tokens": progress.tokens},
        # The question it waits on. `wait` names it, so the answer cannot settle a later one.
        "permission": asked and {"wait": asked.wait, "tool": asked.tool, "arguments": asked.arguments},
    }


def _chat_state(chat, snapshot):
    """The chat, with what it is doing (Madde 462): its status, the server's to say, and its turn."""
    return {**_chat_json(chat), "status": status_of(chat, snapshot), "turn": _turn_json(snapshot)}


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
