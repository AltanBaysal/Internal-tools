"""The queue-watch door (madde 509, 518): the held ask.

The watch itself is faked: what is tried here is what the door hands it and what it answers.
"""
import pytest

from backend.web.app import create_app

STANDING = {"started": 4, "ended": 3, "last": {"status": "done", "project": "düğün"}}


class FakeWatch:
    def __init__(self):
        self.asked = []

    def changed_since(self, seen, timeout):
        self.asked.append((seen, timeout))
        return STANDING


@pytest.fixture
def watch():
    return FakeWatch()


@pytest.fixture
def client(watch):
    from backend.features.queue_watch.presentation.routes import make_watch_blueprint
    return create_app(blueprints=[make_watch_blueprint(watch)]).test_client()


def test_an_ask_from_both_counts_is_held_for_the_doors_own_limit(client, watch):
    from backend.features.queue_watch.presentation.routes import ASK_WAIT_SECONDS

    response = client.get("/api/queue/watch?started=4&ended=3")

    assert response.get_json() == STANDING
    assert watch.asked == [((4, 3), ASK_WAIT_SECONDS)]


def test_the_limit_stays_under_the_tunnels_cut():
    """trycloudflare closes a request that has been quiet for about 100 seconds."""
    from backend.features.queue_watch.presentation.routes import ASK_WAIT_SECONDS

    assert 0 < ASK_WAIT_SECONDS < 100


@pytest.mark.parametrize("query", ["", "?started=4", "?ended=3", "?started=&ended=3",
                                   "?started=yarın&ended=3"],
                         ids=["none", "no-end", "no-start", "empty", "word"])
def test_an_ask_without_both_counts_is_answered_at_once(client, watch, query):
    client.get(f"/api/queue/watch{query}")

    assert watch.asked[0][0] is None
