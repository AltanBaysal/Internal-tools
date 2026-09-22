"""/api/projects/<project>/references · …/references/order · /references/<project>/<file>

The project's reference pool, over HTTP: the browser cannot reach Drive, so every byte in and out
goes through here (FOUNDATION 4).

A blueprint of its own rather than four more arguments on the cards' factory: the surface is
separate, and the two are registered side by side in main.py.

Translation only: no rules here. The use case's exception messages go out verbatim, so the wording
lives in exactly one place (the domain).
"""
from flask import Blueprint, jsonify, request, send_from_directory

from backend.features.photo_generation.domain.references import LIMITS, PoolLimit
from backend.features.photo_generation.domain.usecases.add_references import UnknownReference
from backend.features.photo_generation.domain.usecases.save_reference_order import (
    InvalidReferenceOrder,
)
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def make_reference_blueprint(add_references, list_references, remove_reference,
                             save_reference_order, reference_dir):
    """The callables are already bound to a store and a pool (see main.py)."""
    bp = Blueprint("references", __name__)

    def pool(rows):
        """The pool, and how much of it may be filled.

        The limits ride down with it so the screen can head each row with 4/9 without keeping its
        own copy of the numbers -- a copy would go on being right about the old ones.
        """
        return jsonify({"references": rows, "limits": LIMITS})

    @bp.post("/api/projects/<project>/references")
    def post_references(project):
        # A request with no file at all gives the pool back unchanged: nothing asked for and
        # nothing done is a result, not a failure.
        files = [(file.filename or "", file.read()) for file in request.files.getlist("files")]
        try:
            return pool(add_references(project, files))
        except (UnknownReference, PoolLimit) as exc:
            # Two refusals, one answer: the user asked for a file to go in and it cannot, and the
            # sentence is the whole difference between them.
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.get("/api/projects/<project>/references")
    def get_references(project):
        try:
            return pool(list_references(project))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.post("/api/projects/<project>/references/<name>/delete")
    def delete_reference(project, name):
        try:
            return pool(remove_reference(project, name))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.put("/api/projects/<project>/references/order")
    def put_reference_order(project):
        body = request.get_json(silent=True) or {}
        try:
            return pool(save_reference_order(project, body.get("order")))
        except InvalidReferenceOrder as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.get("/references/<project>/<filename>")
    def serve_reference(project, filename):
        # send_from_directory rejects paths that escape the folder.
        resp = send_from_directory(reference_dir(project), filename)
        # Unlike a photo, whose number is never reused: a deleted reference's name can be given to
        # another file, and bytes left in the browser would be the wrong picture.
        resp.headers["Cache-Control"] = "no-store"
        return resp

    return bp
