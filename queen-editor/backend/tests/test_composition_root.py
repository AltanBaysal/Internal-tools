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
