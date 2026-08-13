"""The Üreticiler panel's endpoint: what is on this machine.

One endpoint, and it only reads. Installing a model happens in the Colab notebook before the app
starts (FOUNDATION 9), so there is nothing here to start or to cancel.
"""
from flask import Blueprint, jsonify


def make_producers_blueprint(list_producers):
    """The callable is already bound to the groups and the files (see main.py)."""
    bp = Blueprint("producers", __name__)

    @bp.get("/api/producers")
    def producers():
        try:
            return jsonify({"producers": list_producers()})
        except Exception as exc:
            # Whatever the reader said or failed to say, verbatim -- the panel prints it instead
            # of three rows it cannot vouch for.
            return jsonify({"error": str(exc)}), 502

    return bp
