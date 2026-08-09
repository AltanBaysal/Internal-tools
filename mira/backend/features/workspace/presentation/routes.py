"""Workspace HTTP routes -- request/response translation only, no business rules."""
import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from backend.features.workspace.domain.errors import (
    EmptyMessage,
    InvalidProjectName,
    ProjectNotFound,
)
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.list_chats import list_chats
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.features.workspace.domain.usecases.start_chat import start_chat


def make_workspace_bp(project_store, chat_store):
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

    return workspace_bp


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
