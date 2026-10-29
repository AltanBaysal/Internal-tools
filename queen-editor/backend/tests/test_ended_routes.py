"""The queue-ended door (madde 509): the held ask.

The watch itself is faked: what is tried here is what the door hands it and what it answers.
"""
import pytest

from backend.web.app import create_app

STANDING = {"ended": 3, "last": {"status": "done", "project": "düğün"}}


class FakeWatch:
    def __init__(self):
        self.asked = []

    def changed_since(self, after, timeout):
        self.asked.append((after, timeout))
        return STANDING


@pytest.fixture
def watch():
    return FakeWatch()


@pytest.fixture
def client(watch):
    from backend.features.queue_ended.presentation.routes import make_ended_blueprint
    return create_app(blueprints=[make_ended_blueprint(watch)]).test_client()


def test_an_ask_from_a_count_is_held_for_the_doors_own_limit(client, watch):
    from backend.features.queue_ended.presentation.routes import ASK_WAIT_SECONDS

    response = client.get("/api/queue/ended?after=3")

    assert response.get_json() == STANDING
    assert watch.asked == [(3, ASK_WAIT_SECONDS)]


def test_the_limit_stays_under_the_tunnels_cut():
    """trycloudflare closes a request that has been quiet for about 100 seconds."""
    from backend.features.queue_ended.presentation.routes import ASK_WAIT_SECONDS

    assert 0 < ASK_WAIT_SECONDS < 100


@pytest.mark.parametrize("query", ["", "?after=", "?after=yarın"], ids=["none", "empty", "word"])
def test_an_ask_with_no_count_is_answered_at_once(client, watch, query):
    client.get(f"/api/queue/ended{query}")

    assert watch.asked[0][0] is None
