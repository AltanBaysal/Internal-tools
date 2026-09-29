import importlib

import pytest

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


def test_the_deepseek_key_comes_from_the_environment(monkeypatch):
    # The second provider's key travels the road the first one does, and the app cannot tell where
    # either came from.
    monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-from-the-environment")
    try:
        assert _reloaded().DEEPSEEK_API_KEY == "ds-from-the-environment"
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


def test_the_grok_row_is_kept_as_the_way_back():
    # Madde 202 took the writing off it, so by Madde 183's own rule -- a row nobody will use is dead
    # configuration -- this one would go. It stays, knowingly: deleting it would drag XAI_API_KEY and
    # the notebook's three secrets along with it, and the way back is one constant either way. If the
    # lines DeepSeek writes come out worse, the road is still here.
    assert "grok-4.3" in config.MODELS


def test_deepseek_is_wired_under_the_one_name_it_has_today():
    # Madde 336. DeepSeek closed deepseek-v4-pro on 14 September and answers it with Flash, and
    # deepseek-v4-flash is only an alias now -- so the table holds the name the model has today and
    # nothing else of DeepSeek's. Grok stays, knowingly (above).
    assert set(config.MODELS) == {"grok-4.3", "deepseek-flash"}


def test_the_writer_grok_4_3_replaced_is_gone_from_the_table():
    # Madde 183. The proof of a deletion is an absence, and only a test that looks for it sees one --
    # test_skills.py's DELETED list keeps the same watch over the skills Madde 94 removed.
    #
    # The new id first: on its own, a "not in" passes just as well over an empty table, and this run
    # has already watched six tests go green because nothing had happened yet.
    assert "grok-4.3" in config.MODELS
    assert "grok-build-0.1" not in config.MODELS


def test_the_two_models_resolve_to_their_provider():
    assert config.MODELS["grok-4.3"]["base_url"] == "https://api.x.ai/v1"
    # No /v1 on this one: it is DeepSeek's documented base, and the client appends
    # /chat/completions to whatever it is given.
    assert config.MODELS["deepseek-flash"]["base_url"] == "https://api.deepseek.com"


def test_each_model_names_the_key_it_spends():
    # Two providers, two keys. Which one a model costs is the model's own business rather than
    # something the composition root is told twice.
    assert config.MODELS["grok-4.3"]["key"] == "XAI_API_KEY"
    assert config.MODELS["deepseek-flash"]["key"] == "DEEPSEEK_API_KEY"


def test_the_prompt_writer_is_a_role_rather_than_a_choice():
    # Madde 175, and the user's decision of 5 Sep: which model writes a frame's action is a role of
    # its own. Madde 202 made it the same id DEFAULT_MODEL carries, and the role is unchanged by that:
    # this line decides who writes an action, and either line can move without the other.
    assert config.PROMPT_MODEL == "deepseek-flash"


def test_the_prompt_writer_is_one_of_the_models_that_are_wired():
    # A name outside the table would be a KeyError inside the engine, and it would land at the
    # moment a prompt was asked for -- in a trial, in front of the user, rather than at startup.
    assert config.PROMPT_MODEL in config.MODELS


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
