"""Referanstan's record over HTTP (madde 317).

A blueprint of its own rather than two more rows in the projects one, the way the reference pool has
its own: the photo panel's settings door, and everything wired to it, stays exactly as it was.
"""
from flask import Blueprint, jsonify, request

from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def make_reference_settings_blueprint(get_reference_settings, save_reference_settings):
    """Both arguments are use cases already bound to a store (see main.py)."""
    bp = Blueprint("reference_settings", __name__)

    @bp.get("/api/projects/<project>/reference-settings")
    def get_reference_record(project):
        try:
            return jsonify(get_reference_settings(project))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500

    @bp.put("/api/projects/<project>/reference-settings")
    def put_reference_record(project):
        body = request.get_json(silent=True) or {}
        prompts, variants = body.get("prompts"), body.get("variants")
        try:
            save_reference_settings(
                project,
                prompts if isinstance(prompts, str) else "",
                # bool is an int in Python, and True would silently mean "1 variant".
                variants if isinstance(variants, int) and not isinstance(variants, bool) else None,
            )
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        # 204: the client already has what it sent; there is nothing to send back.
        return "", 204

    return bp
