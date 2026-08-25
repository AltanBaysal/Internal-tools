"""Workspace HTTP routes -- request/response translation only, no business rules."""
import json
import uuid
from datetime import datetime, timezone

from flask import Blueprint, Response, jsonify, request

from backend.features.workspace.domain.errors import (
    ChatNotFound,
    EmptyMessage,
    EngineFailed,
    FileNotFound,
    InvalidProjectName,
    ProjectNotFound,
)
from backend.features.workspace.domain.chat import ToolCall
from backend.features.workspace.domain.tools import FileStarted, FileWritten
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.delete_chat import delete_chat
from backend.features.workspace.domain.usecases.delete_file import delete_file
from backend.features.workspace.domain.usecases.delete_project import delete_project
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.list_chats import list_chats
from backend.features.workspace.domain.usecases.list_files import list_files
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.features.workspace.domain.usecases.read_file import read_file
from backend.features.workspace.domain.usecases.set_chat_choices import (
    UNCHANGED,
    set_chat_choices,
)
from backend.features.workspace.domain.usecases.start_chat import start_chat
from backend.features.workspace.domain.usecases.stream_answer import stream_answer


def make_workspace_bp(project_store, chat_store, file_store, engine, default_model, stops):
    workspace_bp = Blueprint("workspace", __name__)

    @workspace_bp.get("/api/model")
    def get_model():
        # The one thing about the model menu that only the server knows. The names and the prices
        # are text, and text belongs to the interface.
        return jsonify({"default": default_model})

    @workspace_bp.get("/api/projects")
    def get_projects():
        return jsonify([_project_json(project) for project in list_projects(project_store)])

    @workspace_bp.post("/api/projects")
    def post_project():
        # Creating takes no input: the design never asks for a name up front.
        project = create_project(project_store, new_id=_new_id("p"), now=_now())
        return jsonify(_project_json(project)), 201

    @workspace_bp.patch("/api/projects/<project_id>")
    def patch_project(project_id):
        payload = request.get_json(silent=True) or {}
        try:
            edit_project(project_store, project_id, name=payload.get("name"))
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except InvalidProjectName:
            return jsonify({"error": "a project needs a name"}), 400
        # Re-read so the counts in the answer come from the directories, exactly like the list does.
        return jsonify(_project_json(project_store.get(project_id)))

    @workspace_bp.delete("/api/projects/<project_id>")
    def delete_project_route(project_id):
        try:
            trashed = delete_project(project_store, project_id)
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        # There is no way back, so the name is only a record of what happened on disk.
        return jsonify({"trashed": trashed})

    @workspace_bp.post("/api/projects/<project_id>/chats")
    def post_chat(project_id):
        payload = request.get_json(silent=True) or {}
        try:
            chat = start_chat(
                chat_store,
                project_store,
                project_id,
                payload.get("text", ""),
                new_id=_new_id("c"),
                now=_now(),
                model=payload.get("model", ""),
                skill=payload.get("skill", ""),
            )
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except EmptyMessage:
            return jsonify({"error": "a message needs text"}), 400
        return jsonify(_chat_json(chat, default_model)), 201

    @workspace_bp.patch("/api/projects/<project_id>/chats/<chat_id>")
    def patch_chat(project_id, chat_id):
        payload = request.get_json(silent=True) or {}
        # The model and the skill are the only things about a chat that change. A title arriving
        # here is not a rename that failed quietly -- it is a request this route does not
        # understand.
        if "model" not in payload and "skill" not in payload:
            return jsonify({"error": "a chat only carries a model and a skill"}), 400
        try:
            chat = set_chat_choices(
                chat_store,
                project_id,
                chat_id,
                model=payload.get("model", UNCHANGED),
                skill=payload.get("skill", UNCHANGED),
            )
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        return jsonify(_chat_json(chat, default_model))

    @workspace_bp.get("/api/projects/<project_id>/chats")
    def get_chats(project_id):
        return jsonify(
            [_chat_summary(chat, default_model) for chat in list_chats(chat_store, project_id)]
        )

    @workspace_bp.get("/api/projects/<project_id>/chats/<chat_id>")
    def get_chat(project_id, chat_id):
        chat = chat_store.get(project_id, chat_id)
        if chat is None:
            return jsonify({"error": "chat not found"}), 404
        return jsonify(_chat_json(chat, default_model))

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/messages")
    def post_message(project_id, chat_id):
        payload = request.get_json(silent=True) or {}
        try:
            chat = append_message(
                chat_store,
                project_id,
                chat_id,
                payload.get("text", ""),
                now=_now(),
                skill=payload.get("skill", ""),
            )
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        except EmptyMessage:
            return jsonify({"error": "a message needs text"}), 400
        return jsonify(_chat_json(chat, default_model))

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/answer")
    def post_answer(project_id, chat_id):
        # No body: the chat as it stands is the question. Both a first message and a follow-up
        # arrive here, so there is one answering path rather than two.
        if chat_store.get(project_id, chat_id) is None:
            # The only failure that can still be a status code: nothing has gone out yet.
            return jsonify({"error": "chat not found"}), 404
        return Response(
            _sse(
                stream_answer(
                    chat_store, file_store, engine, project_id, chat_id, _now(), stops
                ),
                default_model,
            ),
            mimetype="text/event-stream",
        )

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/stop")
    def post_stop(project_id, chat_id):
        # Its own request on its own connection: the answer it stops is still streaming down
        # another one, and the server serves the two at the same time.
        if chat_store.get(project_id, chat_id) is None:
            return jsonify({"error": "chat not found"}), 404
        stops.want(project_id, chat_id)
        # Asked for, not done: the answer stops at its next chance, which has not come yet.
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

    @workspace_bp.delete("/api/projects/<project_id>/chats/<chat_id>")
    def delete_project_chat(project_id, chat_id):
        try:
            delete_chat(chat_store, project_id, chat_id)
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        return jsonify({})

    return workspace_bp


def _sse(pieces, default_model):
    """Wrap the use case's output as events, telling them apart by type."""
    try:
        for piece in pieces:
            if isinstance(piece, str):
                yield _frame("chunk", {"text": piece})
            elif isinstance(piece, FileStarted):
                yield _frame("file-start", {})
            elif isinstance(piece, FileWritten):
                yield _frame("file", {"name": piece.name})
            elif isinstance(piece, ToolCall):
                yield _frame("call", {"tool": piece.tool, "target": piece.target})
            else:
                yield _frame("done", _chat_json(piece, default_model))
    except EngineFailed as failure:
        # The status code was settled the moment the first byte left, so a fault after that can
        # only travel inside the stream.
        yield _frame("error", {"error": str(failure)})
    except EmptyMessage:
        # Neither a word nor a file, so there is no answer to keep. It travels as an event for the
        # same reason: escaping here would break the connection, and a broken connection is read
        # by the browser as a network fault, which is not what happened.
        yield _frame("error", {"error": "The model returned nothing."})


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
    }


def _chat_summary(chat, default_model):
    return {
        "id": chat.id,
        "title": chat.title,
        "createdAt": chat.created_at,
        "lastActivity": chat.last_activity,
        # Resolved on the way out, so the client always has a name to draw. The record on disk
        # stays empty and keeps following the setting.
        "model": chat.model or default_model,
        # Not resolved: no skill is an ordinary state, and there is no default to stand in for it.
        "skill": chat.skill,
    }


def _chat_json(chat, default_model):
    return {
        **_chat_summary(chat, default_model),
        "messages": [
            {
                "role": message.role,
                "at": message.at,
                "text": message.text,
                "files": list(message.files),
                "skill": message.skill,
                # Always present, unlike on disk: the browser draws from what it is handed, and an
                # absent field would make every reader check for it.
                "calls": [{"tool": call.tool, "target": call.target} for call in message.calls],
                "stopped": message.stopped,
            }
            for message in chat.messages
        ],
    }
