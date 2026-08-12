"""The Üreticiler panel's endpoints: what is here, and installing what is not."""
from flask import Blueprint, jsonify

from backend.features.producers.domain.usecases.install_producer import Busy


def make_producers_blueprint(list_producers, install_producer, cancel_install):
    """The callables are already bound to the groups, files and runner (see main.py)."""
    bp = Blueprint("producers", __name__)

    @bp.get("/api/producers")
    def producers():
        try:
            return jsonify({"producers": list_producers()})
        except Exception as exc:
            # Whatever the renderer said or failed to say, verbatim -- the panel prints it instead
            # of three rows it cannot vouch for.
            return jsonify({"error": str(exc)}), 502

    @bp.post("/api/producers/<kind>/install")
    def install(kind):
        try:
            install_producer(kind)
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        # 202: a model group takes minutes to land, so the request only reports that it started.
        # How far it has got is read from /api/producers.
        return jsonify({"install": "running"}), 202

    @bp.post("/api/producers/<kind>/install/cancel")
    def cancel(kind):
        cancel_install()
        return "", 204

    return bp
