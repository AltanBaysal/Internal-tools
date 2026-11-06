"""The queue-watch door (madde 509, 518): the held ask for the queue starting and ending."""
from flask import Blueprint, jsonify, request

ASK_WAIT_SECONDS = 50
"""How long one ask may be held while the counts do not move.

Long polling, as QueenAgent's events door does it (madde 491): the Quick Tunnel holds a GET's body
until it ends, so the answer is one that ends, and the screen asks again at once. Under the tunnel's
cut of about 100 quiet seconds, with room for the way there and back; QueenAgent holds 15 s because
its screen wants to hear a turn's progress, while this one waits for a single event.
"""


def make_watch_blueprint(watch):
    bp = Blueprint("queue_watch", __name__)

    @bp.get("/api/queue/watch")
    def ask():
        # Both counts or none: an ask missing one, or with one that is not a number, is answered at
        # once, as they stand.
        started = request.args.get("started", type=int)
        ended = request.args.get("ended", type=int)
        seen = None if started is None or ended is None else (started, ended)
        return jsonify(watch.changed_since(seen, ASK_WAIT_SECONDS))

    return bp
