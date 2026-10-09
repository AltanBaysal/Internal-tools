"""/api/projects/<project>/chats -- request/response translation only (madde 417, 420).

There is no door to delete a chat: a chat is never deleted, so a DELETE is Flask's own 405.
"""
from flask import Blueprint, jsonify, request

from backend.features.agent.domain.usecases.chats import (
    AgentBusy,
    ChatMissing,
    EmptyQuestion,
    ProjectMissing,
)


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


def make_agent_blueprint(ask_question, stop_agent, working_chats):
    """The agent's doors (madde 420). Every argument is a use case already bound (see main.py).

    `/chats/working` stands beside `/chats/<int:chat_id>` without a clash: the int converter does not
    take a word.
    """
    bp = Blueprint("agent", __name__)

    @bp.post("/api/projects/<project>/chats/<int:chat_id>/questions")
    def post_question(project, chat_id):
        body = request.get_json(silent=True)
        text = body.get("text") if isinstance(body, dict) else None
        return _answer(lambda: ask_question(project, chat_id, text))

    @bp.post("/api/projects/<project>/chats/<int:chat_id>/stop")
    def post_stop(project, chat_id):
        return _answer(lambda: stop_agent(project, chat_id))

    @bp.get("/api/projects/<project>/chats/working")
    def get_working(project):
        return _answer(lambda: {"working": working_chats(project)})

    return bp


def _answer(ask):
    try:
        return jsonify(ask())
    except (ProjectMissing, ChatMissing) as exc:
        return jsonify({"error": str(exc)}), 404
    except EmptyQuestion as exc:
        return jsonify({"error": str(exc)}), 400
    except AgentBusy as exc:
        return jsonify({"error": str(exc)}), 409
    except OSError as exc:
        # The operating system's own words -- never a guessed cause.
        return jsonify({"error": str(exc)}), 500
