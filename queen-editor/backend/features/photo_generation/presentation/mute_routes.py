"""/api/projects/<project>/muted and …/frames/<frame>/muted -- the turned-off sounds (madde 510).

A blueprint of its own, the way the project's switches have one. Translation only; the use case's
sentences go out verbatim. The frame in the address is never a path: it is looked up in the record
and written into the list.
"""
from flask import Blueprint, jsonify, request

from backend.features.photo_generation.domain.mute import InvalidMute, NoSound
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def make_mute_blueprint(get_muted, set_muted):
    """Both arguments are use cases already bound to their stores (see main.py)."""
    bp = Blueprint("mute", __name__)

    @bp.get("/api/projects/<project>/muted")
    def get_list(project):
        try:
            return jsonify({"frames": get_muted(project)})
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    # PUT and a state rather than a toggle: the same press arriving twice leaves the same answer.
    @bp.put("/api/projects/<project>/frames/<frame>/muted")
    def put_one(project, frame):
        body = request.get_json(silent=True) or {}
        try:
            return jsonify({"frames": set_muted(project, frame, body.get("muted"))})
        except (InvalidMute, NoSound) as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    return bp
