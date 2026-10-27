"""The idle watch's two doors (madde 498): the held ask and Buradayım.

The watch itself is faked: what is tried here is what the doors hand it and what they answer.
"""
import pytest

from backend.web.app import create_app

STANDING = {"version": 3, "asking": True}


class FakeWatch:
    def __init__(self):
        self.asked = []
        self.here_count = 0

    def changed_since(self, version, timeout):
        self.asked.append((version, timeout))
        return STANDING

    def here(self):
        self.here_count += 1
        return {"version": 4, "asking": False}


@pytest.fixture
def watch():
    return FakeWatch()


@pytest.fixture
def client(watch):
    from backend.features.idle.presentation.routes import make_idle_blueprint
    return create_app(blueprints=[make_idle_blueprint(watch)]).test_client()


def test_an_ask_from_a_version_is_held_for_the_doors_own_limit(client, watch):
    from backend.features.idle.presentation.routes import ASK_WAIT_SECONDS

    response = client.get("/api/idle?after=3")

    assert response.get_json() == STANDING
    assert watch.asked == [(3, ASK_WAIT_SECONDS)]


def test_the_limit_stays_under_the_tunnels_cut():
    """trycloudflare closes a request that has been quiet for about 100 seconds."""
    from backend.features.idle.presentation.routes import ASK_WAIT_SECONDS

    assert 0 < ASK_WAIT_SECONDS < 100


@pytest.mark.parametrize("query", ["", "?after=", "?after=yarın"], ids=["none", "empty", "word"])
def test_an_ask_with_no_version_is_answered_at_once(client, watch, query):
    client.get(f"/api/idle{query}")

    assert watch.asked[0][0] is None


def test_buradayim_answers_with_the_question_as_it_now_stands(client, watch):
    response = client.post("/api/idle/here")

    assert response.get_json() == {"version": 4, "asking": False}
    assert watch.here_count == 1
