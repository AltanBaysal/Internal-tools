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


def test_the_deepseek_key_comes_from_the_environment(monkeypatch):
    # The second provider's key travels the road the first one does, and the app cannot tell where
    # either came from.
    monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-from-the-environment")
    try:
        assert _reloaded().DEEPSEEK_API_KEY == "ds-from-the-environment"
    finally:
        monkeypatch.undo()
        _reloaded()


def test_the_openrouter_key_comes_from_the_environment(monkeypatch):
    # The third provider's key, since Madde 149, and it travels the road the other two do.
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-from-the-environment")
    try:
        assert _reloaded().OPENROUTER_API_KEY == "or-from-the-environment"
    finally:
        monkeypatch.undo()
        _reloaded()


def test_the_default_model_is_grok_build():
    # Pinned like MAX_ROUNDS: this is a decision, and changing it without noticing changes what the
    # user pays and what fits. It is also what an old record resolves to -- every message written
    # before Madde 146 names no model at all.
    assert config.DEFAULT_MODEL == "grok-build-0.1"


def test_the_five_models_resolve_to_their_provider():
    assert config.MODELS["grok-build-0.1"]["base_url"] == "https://api.x.ai/v1"
    # No /v1 on this one: it is DeepSeek's documented base, and the client appends
    # /chat/completions to whatever it is given.
    assert config.MODELS["deepseek-v4-flash"]["base_url"] == "https://api.deepseek.com"
    assert config.MODELS["deepseek-v4-pro"]["base_url"] == "https://api.deepseek.com"
    # The same two weights reached a second way since Madde 149. The id carries a slash here, which
    # no id did before; nothing in the app takes an id apart, so it costs nothing.
    assert (
        config.MODELS["deepseek/deepseek-v4-flash-0731"]["base_url"]
        == "https://openrouter.ai/api/v1"
    )
    assert (
        config.MODELS["deepseek/deepseek-v4-pro-0813"]["base_url"]
        == "https://openrouter.ai/api/v1"
    )


def test_each_model_names_the_key_it_spends():
    # Three providers, three keys. Which one a model costs is the model's own business rather than
    # something the composition root is told twice.
    assert config.MODELS["grok-build-0.1"]["key"] == "XAI_API_KEY"
    assert config.MODELS["deepseek-v4-flash"]["key"] == "DEEPSEEK_API_KEY"
    assert config.MODELS["deepseek-v4-pro"]["key"] == "DEEPSEEK_API_KEY"
    assert config.MODELS["deepseek/deepseek-v4-flash-0731"]["key"] == "OPENROUTER_API_KEY"
    assert config.MODELS["deepseek/deepseek-v4-pro-0813"]["key"] == "OPENROUTER_API_KEY"


PINNED = {"provider": {"order": ["deepinfra"], "allow_fallbacks": False}}


def test_the_openrouter_rows_are_pinned_to_deepinfra():
    """Nailed down rather than left to the router, and this is a terms assertion.

    OpenRouter serves these weights from many providers and picks one; `allow_fallbacks` false is
    what stops it. Which provider answers decides whose terms the request runs under, and at least
    one of them forbids this work outright -- so a request that fell through would be running under
    a contract that does not allow it.
    """
    assert config.MODELS["deepseek/deepseek-v4-flash-0731"]["extra"] == PINNED
    assert config.MODELS["deepseek/deepseek-v4-pro-0813"]["extra"] == PINNED


def test_a_row_that_goes_direct_carries_no_extra():
    # Nothing to add to the body, so nothing is written -- rather than an empty dict everywhere,
    # which would be a field saying nothing in three rows out of five.
    for model in ("grok-build-0.1", "deepseek-v4-flash", "deepseek-v4-pro"):
        assert "extra" not in config.MODELS[model]


def test_a_known_model_resolves_to_its_own_wiring():
    model, base_url, _, _ = config.engine_for("deepseek-v4-flash")
    assert (model, base_url) == ("deepseek-v4-flash", "https://api.deepseek.com")


def test_engine_for_gives_the_extra_as_its_fourth_thing():
    # Read through engine_for rather than off the table, because that is the one road the
    # composition root travels -- a row's extra that never reached it would be a pin nobody sends.
    assert config.engine_for("deepseek/deepseek-v4-flash-0731")[3] == PINNED
    # And nothing where there is nothing, in whatever shape config settles on -- the point is that
    # it does not carry another model's pin.
    assert not config.engine_for("grok-build-0.1")[3]


def test_an_unknown_or_absent_model_falls_back_to_the_default():
    # skills.py's instruction_for rule, and the same reason: a record can name something that has
    # since been renamed, and a message written before this field names nothing at all. Neither may
    # stop a chat from being answered.
    assert config.engine_for("")[0] == "grok-build-0.1"
    assert config.engine_for("grok-4.3")[0] == "grok-build-0.1"
