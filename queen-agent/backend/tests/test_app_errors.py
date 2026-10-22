"""What a request that fails on the disk answers (Madde 490): the operating system's own sentence, as
JSON the screen reads, rather than Flask's HTML page that the screen showed as "HTTP 500"."""
from flask import Blueprint

from backend.services.store.store import PathOutsideRoot
from backend.web.app import create_app


def _failing(error):
    failing = Blueprint("failing", __name__)

    @failing.get("/api/failing")
    def fail():
        raise error

    return create_app(blueprints=(failing,)).test_client()


def test_a_disk_failure_answers_503_with_its_own_sentence():
    answer = _failing(OSError(107, "Transport endpoint is not connected", "/content/drive")).get(
        "/api/failing"
    )
    assert answer.status_code == 503
    assert answer.get_json() == {
        "error": "[Errno 107] Transport endpoint is not connected: '/content/drive'"
    }


def test_a_path_escaping_the_root_is_still_our_own_fault():
    # Not an OSError: a path out of the root is a bug of ours, not the disk going away.
    assert _failing(PathOutsideRoot("../x")).get("/api/failing").status_code == 500
