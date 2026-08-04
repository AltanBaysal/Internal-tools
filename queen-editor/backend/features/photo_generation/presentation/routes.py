"""/api/projects/<project>/generate · /api/status · /api/stop
/api/projects/<project>/photos · /photos/<project>/<file>

Translation only: no rules here. The use case's exception messages go out verbatim, so the wording
lives in exactly one place (the domain).
"""
import io
import json

from flask import Blueprint, jsonify, request, send_file, send_from_directory

from backend.features.photo_generation.domain.prompt_list import InvalidPrompts
from backend.features.photo_generation.domain.usecases.delete_photos import InvalidFiles
from backend.features.photo_generation.domain.usecases.resume_batch import NothingToResume
from backend.features.photo_generation.domain.usecases.retry_frame import FrameMissing
from backend.features.photo_generation.domain.usecases.save_order import InvalidOrder
from backend.features.photo_generation.domain.usecases.start_batch import (
    Busy,
    InvalidVariants,
    ProjectMissing,
)


def make_photo_generation_blueprint(start_batch, get_status, stop_generation, resume_batch,
                                    cancel_generation, retry_frame, get_queue, list_photos,
                                    save_order, export_project, delete_photos, photo_dir):
    """The callables are already bound to a runner/store/generator (see main.py)."""
    bp = Blueprint("photo_generation", __name__)

    @bp.post("/api/projects/<project>/generate")
    def post_generate(project):
        body = request.get_json(silent=True) or {}
        prompts = body.get("prompts")
        # A non-string body field is treated as empty text -> "Prompt listesi boş."
        prompts = prompts if isinstance(prompts, str) else ""
        negative = body.get("negative")
        # No negative is legitimate (the batch renders without one); a non-string counts as none.
        negative = negative if isinstance(negative, str) else ""
        try:
            start_batch(project, prompts, negative, body.get("variants"))
        # Which box was wrong travels with the message: the screen marks that field instead of
        # guessing from the wording.
        except InvalidPrompts as exc:
            return jsonify({"error": str(exc), "field": "prompts"}), 400
        except InvalidVariants as exc:
            return jsonify({"error": str(exc), "field": "variants"}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        # 202: a batch runs for minutes, so the request only reports that the job was accepted.
        return jsonify({"job": "running"}), 202

    @bp.get("/api/status")
    def status():
        return jsonify(get_status())

    @bp.post("/api/stop")
    def stop():
        return jsonify(stop_generation())

    @bp.post("/api/projects/<project>/resume")
    def resume(project):
        try:
            resume_batch(project)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except (NothingToResume, Busy) as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify({"job": "running"}), 202

    @bp.post("/api/projects/<project>/cancel")
    def cancel(project):
        try:
            cancel_generation(project)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        return "", 204

    @bp.post("/api/projects/<project>/retry")
    def retry(project):
        body = request.get_json(silent=True) or {}
        try:
            retry_frame(project, body.get("file"))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except FrameMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify({"job": "running"}), 202

    @bp.get("/api/projects/<project>/queue")
    def queue(project):
        try:
            return jsonify(get_queue(project))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.get("/api/projects/<project>/photos")
    def photos(project):
        try:
            return jsonify({"photos": list_photos(project)})
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.put("/api/projects/<project>/order")
    def put_order(project):
        body = request.get_json(silent=True) or {}
        try:
            # The stored list goes back so the client sees what was kept, not what it guessed.
            return jsonify({"order": save_order(project, body.get("order"))})
        except InvalidOrder as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.get("/api/projects/<project>/export")
    def export(project):
        try:
            data = export_project(project)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        # Written out here rather than in the domain: turning a value into bytes on the wire is
        # this layer's job. ensure_ascii=False keeps Turkish prompts readable in the file.
        payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        return send_file(io.BytesIO(payload), mimetype="application/json", as_attachment=True,
                         download_name=f"{project}-export.json")

    # POST, not DELETE: the request carries a list of names, and a body on DELETE is a corner of
    # HTTP that proxies and clients disagree about.
    @bp.post("/api/projects/<project>/photos/delete")
    def remove_photos(project):
        body = request.get_json(silent=True) or {}
        try:
            # What was really deleted goes back: names that had already gone are not an error.
            return jsonify({"deleted": delete_photos(project, body.get("files"))})
        except InvalidFiles as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            # The operating system's own words -- never guess the cause.
            return jsonify({"error": str(exc)}), 500

    @bp.get("/photos/<project>/<filename>")
    def serve_photo(project, filename):
        # send_from_directory rejects paths that escape the folder.
        resp = send_from_directory(photo_dir(project), filename)
        # next_number never reuses a number, so a photo URL's bytes can never change.
        resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return resp

    return bp
