"""/api/projects/<project>/chats -- request/response translation only (madde 417).

There is no door to delete a chat: a chat is never deleted, so a DELETE is Flask's own 405.
"""
from flask import Blueprint, jsonify

from backend.features.agent.domain.usecases.chats import ChatMissing, ProjectMissing


def make_chats_blueprint(new_chat, list_chats, open_chat):
    """Every argument is a use case already bound to the record (see main.py)."""
    bp = Blueprint("agent_chats", __name__)

    @bp.post("/api/projects/<project>/chats")
    def post_chat(project):
        return _answer(lambda: new_chat(project))

    @bp.get("/api/projects/<project>/chats")
    def get_chats(project):
        return _answer(lambda: {"chats": list_chats(project)})

    @bp.get("/api/projects/<project>/chats/<int:chat_id>")
    def get_chat(project, chat_id):
        return _answer(lambda: open_chat(project, chat_id))

    return bp


def _answer(ask):
    try:
        return jsonify(ask())
    except (ProjectMissing, ChatMissing) as exc:
        return jsonify({"error": str(exc)}), 404
    except OSError as exc:
        # The operating system's own words -- never a guessed cause.
        return jsonify({"error": str(exc)}), 500
