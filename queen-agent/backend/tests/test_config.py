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


def test_the_default_model_is_the_cheaper_queen():
    # Pinned like MAX_ROUNDS: this is a decision, and changing it without noticing changes what the
    # user pays and what fits. It is also what an old record resolves to -- every message written
    # before Madde 146 names no model at all.
    #
    # Madde 177 moved it off Grok. What the composer offers is two models now, and this has to be
    # the same id models.js defaults to, or the button would say one thing while the request went
    # somewhere else.
    assert config.DEFAULT_MODEL == "deepseek-v4-flash"


def test_the_model_that_only_writes_prompts_stays_in_the_table():
    # It left the menu in Madde 177, not the app: Madde 175 wires it as the prompt writer, and a
    # row removed here would be a KeyError the first time a frame was written.
    assert "grok-build-0.1" in config.MODELS


def test_the_three_models_resolve_to_their_provider():
    assert config.MODELS["grok-build-0.1"]["base_url"] == "https://api.x.ai/v1"
    # No /v1 on this one: it is DeepSeek's documented base, and the client appends
    # /chat/completions to whatever it is given.
    assert config.MODELS["deepseek-v4-flash"]["base_url"] == "https://api.deepseek.com"
    assert config.MODELS["deepseek-v4-pro"]["base_url"] == "https://api.deepseek.com"


def test_each_model_names_the_key_it_spends():
    # Two providers, two keys. Which one a model costs is the model's own business rather than
    # something the composition root is told twice.
    assert config.MODELS["grok-build-0.1"]["key"] == "XAI_API_KEY"
    assert config.MODELS["deepseek-v4-flash"]["key"] == "DEEPSEEK_API_KEY"
    assert config.MODELS["deepseek-v4-pro"]["key"] == "DEEPSEEK_API_KEY"


def test_the_prompt_writer_is_a_role_rather_than_a_choice():
    # Madde 175, and the user's decision of 5 Sep: Grok is not an option in the composer, it is a
    # line in config.py. Which model writes a frame's action is the app's, not the user's -- what
    # they choose is which model runs the conversation.
    assert config.PROMPT_MODEL == "grok-build-0.1"


def test_the_prompt_writer_is_one_of_the_models_that_are_wired():
    # A name outside the table would be a KeyError inside the engine, and it would land at the
    # moment a prompt was asked for -- in a trial, in front of the user, rather than at startup.
    assert config.PROMPT_MODEL in config.MODELS


def test_a_known_model_resolves_to_its_own_wiring():
    model, base_url, _ = config.engine_for("deepseek-v4-flash")
    assert (model, base_url) == ("deepseek-v4-flash", "https://api.deepseek.com")


def test_an_unknown_or_absent_model_falls_back_to_the_default():
    # skills.py's instruction_for rule, and the same reason: a record can name something that has
    # since been renamed, and a message written before this field names nothing at all. Neither may
    # stop a chat from being answered.
    assert config.engine_for("")[0] == "deepseek-v4-flash"
    assert config.engine_for("grok-4.3")[0] == "deepseek-v4-flash"
