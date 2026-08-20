import importlib

from backend import config


def _reloaded():
    """The value the app ends up with, rather than what the module's source says.

    Reloading is the only way to ask it: the constants resolve once at import, and by the time a
    test runs that import already happened.
    """
    return importlib.reload(config)


def test_the_api_key_comes_from_the_environment(monkeypatch):
    # Madde 62: the one road. On Colab it arrives from Secrets through the notebook, locally from
    # the shell -- and the app cannot tell the two apart, which is the point.
    monkeypatch.setenv("XAI_API_KEY", "xai-from-the-environment")
    try:
        assert _reloaded().XAI_API_KEY == "xai-from-the-environment"
    finally:
        # Undone here rather than left to the fixture: monkeypatch restores the environment, but
        # the module reloaded under it would stay reloaded and every later test would read it.
        monkeypatch.undo()
        _reloaded()


def test_without_it_the_key_is_empty_rather_than_missing(monkeypatch):
    # Empty is the ordinary starting state: the app runs without a key and only asking for an answer
    # fails. A None here would turn that into a crash on the first request instead.
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    try:
        assert _reloaded().XAI_API_KEY == ""
    finally:
        monkeypatch.undo()
        _reloaded()


def test_the_default_model_is_the_cheap_one_with_the_long_context():
    # Pinned like MAX_ROUNDS: this is a decision, and changing it without noticing changes what the
    # user pays. grok-4.3 costs half of grok-4.5 and carries 1M of context against its 500k, and
    # the runs here are long -- structure file, scenario and frame list pile up in one chat.
    #
    # An XAI_MODEL in the environment overrides this and the resolved value is what lands here, so
    # on a machine that sets it this test fails and says something true: the default running here
    # is not the one the repository ships.
    assert config.XAI_MODEL == "grok-4.3"
