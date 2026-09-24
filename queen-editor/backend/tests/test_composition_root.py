"""The composition root itself: proof that backend/main.py imports and serves.

Every other test builds its own object graph out of fakes, so main.py -- the one place concrete
classes are wired (CODE-STANDARD) -- was the file the suite never read. A name used above the line
that defines it broke Flask at import, the suite stayed green, and the break reached the user in
Colab instead (madde 309).

What is asserted is what the notebook waits for: the module comes up, and its app answers
/api/health. Nothing is faked because nothing in the graph reaches out at construction -- paths are
joined, weights are loaded on the first render, and torch is imported inside it.
"""
import importlib
import os
import sys

import pytest

from backend import config

VIDEO_MODEL = "QE_VIDEO_MODEL"


def _import_main(video_model):
    """backend.main, freshly imported under one video model.

    config reads the environment at import and main branches on what it read, so config is reloaded
    rather than re-imported: reload keeps the one module object every other importer already holds,
    and a second config object would leave two answers to the same question.
    """
    os.environ[VIDEO_MODEL] = video_model
    importlib.reload(config)
    sys.modules.pop("backend.main", None)
    return importlib.import_module("backend.main")


@pytest.fixture
def import_main():
    before = os.environ.get(VIDEO_MODEL)
    yield _import_main
    if before is None:
        os.environ.pop(VIDEO_MODEL, None)
    else:
        os.environ[VIDEO_MODEL] = before
    # The environment is what it was, so config is reloaded once more and the rest of the suite
    # reads the real one. main is dropped instead of re-imported: on a broken wiring importing it
    # again would raise out of a fixture, which reports as an error on top of the failure it
    # already has.
    sys.modules.pop("backend.main", None)
    importlib.reload(config)


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_comes_up_and_answers_health(import_main, video_model):
    """Both video producers are wired at module level, each in its own branch, and Colab runs h3 --
    so one import would leave the branch the user actually runs unread."""
    main = import_main(video_model)

    response = main.app.test_client().get("/api/health")

    assert response.status_code == 200


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_serves_referanstans_record(import_main, video_model):
    """Madde 317: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main(video_model)

    response = main.app.test_client().get("/api/projects/m317-yok/reference-settings")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m317-yok"}


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_hands_a_reference_run_to_the_use_case(import_main, video_model):
    """Madde 326: main.py hung this door with an argument queue_references does not take, and every
    press came back 500 -- the door's own tests wire it by hand. A missing project is the use case's
    first question, so its answer proves the call got in."""
    main = import_main(video_model)

    response = main.app.test_client().post("/api/projects/m326-yok/references/produce",
                                           json={"prompts": '["a"]', "variants": 1})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m326-yok"}
