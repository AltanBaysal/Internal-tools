"""The Üreticiler panel's one endpoint."""
from flask import Blueprint, jsonify


def make_producers_blueprint(list_producers):
    """The callable is already bound to the producer map (see main.py)."""
    bp = Blueprint("producers", __name__)

    @bp.get("/api/producers")
    def producers():
        try:
            return jsonify({"producers": list_producers()})
        except Exception as exc:
            # Whatever the renderer said or failed to say, verbatim -- the panel prints it instead
            # of three rows it cannot vouch for.
            return jsonify({"error": str(exc)}), 502

    return bp
