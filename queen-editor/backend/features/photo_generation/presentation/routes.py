"""/api/projects/<project>/generate · /api/status · /photos/<project>/<file>

Translation only: no rules here. The use case's exception messages go out verbatim, so the wording
lives in exactly one place (the domain).
"""
from flask import Blueprint, jsonify, request, send_from_directory

from backend.features.photo_generation.domain.usecases.start_generation import (
    Busy,
    InvalidPrompt,
    ProjectMissing,
)


def make_photo_generation_blueprint(start_generation, get_status, photo_dir):
    """The callables are already bound to a runner/store/generator (see main.py)."""
    bp = Blueprint("photo_generation", __name__)

    @bp.post("/api/projects/<project>/generate")
    def post_generate(project):
        prompt = (request.get_json(silent=True) or {}).get("prompt", "")
        if not isinstance(prompt, str):
            prompt = ""   # anything but a string is treated as empty -> "Prompt boş olamaz."
        try:
            start_generation(project, prompt)
        except InvalidPrompt as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        # 202: the photo takes 30-90s, so the request only reports that the job was accepted.
        return jsonify({"job": "running"}), 202

    @bp.get("/api/status")
    def status():
        return jsonify(get_status())

    @bp.get("/photos/<project>/<filename>")
    def serve_photo(project, filename):
        # send_from_directory rejects paths that escape the folder.
        return send_from_directory(photo_dir(project), filename)

    return bp
