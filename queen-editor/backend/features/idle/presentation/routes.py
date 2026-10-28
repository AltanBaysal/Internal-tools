"""The idle watch's two doors (madde 498): the held ask, and Buradayım."""
from flask import Blueprint, jsonify, request

ASK_WAIT_SECONDS = 50
"""How long one ask may be held while the question does not move.

Long polling, as QueenAgent's events door does it (madde 491): the Quick Tunnel holds a GET's body
until it ends, so the answer is one that ends, and the screen asks again at once. Under the tunnel's
cut of about 100 quiet seconds, with room for the way there and back; QueenAgent holds 15 s because
its screen wants to hear a turn's progress, while this one waits for a single event.
"""


def make_idle_blueprint(watch):
    bp = Blueprint("idle", __name__)

    @bp.get("/api/idle")
    def ask():
        # Not a number is no version: answered at once, as it stands.
        after = request.args.get("after", type=int)
        return jsonify(watch.changed_since(after, ASK_WAIT_SECONDS))

    @bp.post("/api/idle/here")
    def here():
        return jsonify(watch.here())

    return bp
