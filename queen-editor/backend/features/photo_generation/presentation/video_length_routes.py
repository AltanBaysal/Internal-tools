"""/api/projects/<project>/video-length -- how long the project's H3 videos run (madde 422).

A blueprint of its own, the way Referanstan's record has one: the cards' factory, and everything
wired to it, stays as it was. Translation only; the use case's sentences go out verbatim.
"""
from flask import Blueprint, jsonify, request

from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing
from backend.features.photo_generation.domain.video_length import InvalidLength


def make_video_length_blueprint(get_video_length, save_video_length):
    """Both arguments are use cases already bound to a store (see main.py)."""
    bp = Blueprint("video_length", __name__)

    @bp.get("/api/projects/<project>/video-length")
    def get_length(project):
        try:
            return jsonify({"seconds": get_video_length(project)})
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.put("/api/projects/<project>/video-length")
    def put_length(project):
        body = request.get_json(silent=True) or {}
        try:
            save_video_length(project, body.get("seconds"))
        except InvalidLength as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        # 204: the client already has what it sent; there is nothing to send back.
        return "", 204

    return bp
