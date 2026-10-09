"""/api/projects/<project>/happy-ending -- the project's Mutlu son switch (madde 426).

A blueprint of its own, the way the length has one: the cards' factory, and everything wired to it,
stays as it was. Translation only; the use case's sentences go out verbatim.
"""
from flask import Blueprint, jsonify, request

from backend.features.photo_generation.domain.happy_ending import InvalidSwitch
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def make_happy_ending_blueprint(get_happy_ending, save_happy_ending):
    """Both arguments are use cases already bound to a store (see main.py)."""
    bp = Blueprint("happy_ending", __name__)

    @bp.get("/api/projects/<project>/happy-ending")
    def get_switch(project):
        try:
            return jsonify({"on": get_happy_ending(project)})
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.put("/api/projects/<project>/happy-ending")
    def put_switch(project):
        body = request.get_json(silent=True) or {}
        try:
            save_happy_ending(project, body.get("on"))
        except InvalidSwitch as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        # 204: the client already has what it sent; there is nothing to send back.
        return "", 204

    return bp
