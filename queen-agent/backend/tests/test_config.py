import importlib

import pytest

from backend import config


def _reloaded():
    """The value the app ends up with, rather than what the module's source says.

    Reloading is the only way to ask it: the constants resolve once at import, and by the time a
    test runs that import already happened.
    """
    return importlib.reload(config)


def test_the_deepseek_key_comes_from_the_environment(monkeypatch):
    # Madde 62: the one road. On Colab it arrives from Secrets through the notebook, locally from
    # the shell -- and the app cannot tell the two apart, which is the point.
    monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-from-the-environment")
    try:
        assert _reloaded().DEEPSEEK_API_KEY == "ds-from-the-environment"
    finally:
        # Undone here rather than left to the fixture: monkeypatch restores the environment, but
        # the module reloaded under it would stay reloaded and every later test would read it.
        monkeypatch.undo()
        _reloaded()


def test_without_it_the_key_is_empty_rather_than_missing(monkeypatch):
    # Empty is the ordinary starting state: the app runs without a key and only asking for an answer
    # fails. A None here would turn that into a crash on the first request instead.
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    try:
        assert _reloaded().DEEPSEEK_API_KEY == ""
    finally:
        monkeypatch.undo()
        _reloaded()


def test_the_default_model_is_deepseek_flash():
    # Pinned like MAX_ROUNDS: this is a decision, and changing it without noticing changes what the
    # user pays and what fits.
    #
    # Madde 336 kept the one model under the name DeepSeek gives it today, and since Madde 358 this
    # line alone says which model answers every turn: the screen names none and the browser sends none.
    assert config.DEFAULT_MODEL == "deepseek-flash"


def test_deepseek_is_the_one_row_in_the_table():
    # Madde 336 left DeepSeek one name, the one the model has today. Madde 383 (the owner, 30
    # September: "kalksın") took out the other provider's row, which nothing had pointed at since
    # Madde 202, and its key with it.
    assert set(config.MODELS) == {"deepseek-flash"}


def test_the_model_resolves_to_its_provider():
    # No /v1: it is DeepSeek's documented base, and the client appends /chat/completions to
    # whatever it is given.
    assert config.MODELS["deepseek-flash"]["base_url"] == "https://api.deepseek.com"


def test_the_model_names_the_key_it_spends():
    # Which key a model costs is the model's own business rather than something the composition
    # root is told.
    assert config.MODELS["deepseek-flash"]["key"] == "DEEPSEEK_API_KEY"


@pytest.mark.parametrize("model", list(config.MODELS))
def test_every_row_resolves_at_startup(model):
    # main.py walks the table at startup, and engine_for looks each row's key up by name among
    # config's own constants. A row naming a key config no longer holds stops the app there.
    assert config.engine_for(model)[0] == model


def test_no_model_is_kept_for_writing_actions():
    # Madde 395, the owner's decision of 30 September: the main model writes each frame's action
    # itself, so DEFAULT_MODEL is the one choice left.
    assert not hasattr(config, "PROMPT_MODEL")


def test_a_known_model_resolves_to_its_own_wiring():
    model, base_url, _ = config.engine_for("deepseek-flash")
    assert (model, base_url) == ("deepseek-flash", "https://api.deepseek.com")


def test_an_id_the_table_does_not_hold_is_a_wiring_fault():
    # Madde 358. The fallback to the default was there for a record naming a model since dropped;
    # no record steers a turn any more, and the only caller is main.py walking the table itself. An
    # id outside it is a mistake in the wiring, and it should stop the app at startup rather than be
    # quietly answered by another model.
    with pytest.raises(KeyError):
        config.engine_for("a-model-nobody-wired")
