"""Workspace HTTP routes -- request/response translation only, no business rules."""
import json
import uuid
from datetime import datetime, timezone

from flask import Blueprint, Response, jsonify, request

from backend.features.workspace.domain.errors import (
    ChatNotFound,
    EmptyMessage,
    EngineFailed,
    InvalidProjectName,
    ProjectNotFound,
)
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.list_chats import list_chats
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.features.workspace.domain.usecases.list_recent_chats import list_recent_chats
from backend.features.workspace.domain.usecases.start_chat import start_chat
from backend.features.workspace.domain.usecases.start_chat_in_new_project import (
    start_chat_in_new_project,
)
from backend.features.workspace.domain.usecases.stream_answer import stream_answer


def make_workspace_bp(project_store, chat_store, engine):
    workspace_bp = Blueprint("workspace", __name__)

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
            edit_project(
                project_store,
                project_id,
                name=payload.get("name"),
                desc=payload.get("desc"),
            )
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except InvalidProjectName:
            return jsonify({"error": "a project needs a name"}), 400
        # Re-read so the counts in the answer come from the directories, exactly like the list does.
        return jsonify(_project_json(project_store.get(project_id)))

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
            )
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except EmptyMessage:
            return jsonify({"error": "a message needs text"}), 400
        return jsonify(_chat_json(chat)), 201

    @workspace_bp.get("/api/projects/<project_id>/chats")
    def get_chats(project_id):
        return jsonify([_chat_summary(chat) for chat in list_chats(chat_store, project_id)])

    @workspace_bp.get("/api/projects/<project_id>/chats/<chat_id>")
    def get_chat(project_id, chat_id):
        chat = chat_store.get(project_id, chat_id)
        if chat is None:
            return jsonify({"error": "chat not found"}), 404
        return jsonify(_chat_json(chat))

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/messages")
    def post_message(project_id, chat_id):
        payload = request.get_json(silent=True) or {}
        try:
            chat = append_message(
                chat_store, project_id, chat_id, payload.get("text", ""), now=_now()
            )
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        except EmptyMessage:
            return jsonify({"error": "a message needs text"}), 400
        return jsonify(_chat_json(chat))

    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/answer")
    def post_answer(project_id, chat_id):
        # No body: the chat as it stands is the question. Both a first message and a follow-up
        # arrive here, so there is one answering path rather than two.
        if chat_store.get(project_id, chat_id) is None:
            # The only failure that can still be a status code: nothing has gone out yet.
            return jsonify({"error": "chat not found"}), 404
        return Response(
            _sse(stream_answer(chat_store, engine, project_id, chat_id, now=_now())),
            mimetype="text/event-stream",
        )

    @workspace_bp.post("/api/chats")
    def post_chat_anywhere():
        # A message from home has no target, so the rule that opens a project and a chat together
        # lives here rather than in two browser calls that could stop half-way.
        payload = request.get_json(silent=True) or {}
        try:
            project, chat = start_chat_in_new_project(
                project_store,
                chat_store,
                payload.get("text", ""),
                new_project_id=_new_id("p"),
                new_chat_id=_new_id("c"),
                now=_now(),
            )
        except EmptyMessage:
            return jsonify({"error": "a message needs text"}), 400
        return jsonify({"project": _project_json(project), "chat": _chat_json(chat)}), 201

    @workspace_bp.get("/api/chats")
    def get_recent_chats():
        return jsonify(
            [
                {**_chat_summary(chat), "projectId": project_id}
                for project_id, chat in list_recent_chats(chat_store)
            ]
        )

    return workspace_bp


def _sse(pieces):
    """Wrap the use case's output as events. A Chat means the answer is complete."""
    try:
        for piece in pieces:
            if isinstance(piece, str):
                yield _frame("chunk", {"text": piece})
            else:
                yield _frame("done", _chat_json(piece))
    except EngineFailed as failure:
        # The status code was settled the moment the first byte left, so a fault after that can
        # only travel inside the stream.
        yield _frame("error", {"error": str(failure)})


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
        "desc": project.desc,
        "hue": project.hue,
        "createdAt": project.created_at,
        "chats": project.chat_count,
        "files": project.file_count,
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
        "messages": [
            {"role": message.role, "at": message.at, "text": message.text}
            for message in chat.messages
        ],
    }
