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
    # Madde 334: the DeepSeek pair is answered through OpenRouter until DeepSeek's own account is
    # paid for, and that key travels the road the other two do.
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-from-the-environment")
    try:
        assert _reloaded().OPENROUTER_API_KEY == "or-from-the-environment"
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


def test_the_grok_row_is_kept_as_the_way_back():
    # Madde 202 took the writing off it, so by Madde 183's own rule -- a row nobody will use is dead
    # configuration -- this one would go. It stays, knowingly: deleting it would drag XAI_API_KEY and
    # its secret in the notebook along with it, and the way back is one constant either way. If the
    # lines DeepSeek writes come out worse, the road is still here.
    assert "grok-4.3" in config.MODELS


def test_the_writer_grok_4_3_replaced_is_gone_from_the_table():
    # Madde 183. The proof of a deletion is an absence, and only a test that looks for it sees one --
    # test_skills.py's DELETED list keeps the same watch over the skills Madde 94 removed.
    #
    # The new id first: on its own, a "not in" passes just as well over an empty table, and this run
    # has already watched six tests go green because nothing had happened yet.
    assert "grok-4.3" in config.MODELS
    assert "grok-build-0.1" not in config.MODELS


def test_the_three_models_resolve_to_their_provider():
    assert config.MODELS["grok-4.3"]["base_url"] == "https://api.x.ai/v1"
    # Madde 334: the DeepSeek pair goes through OpenRouter while DeepSeek's own account has no
    # credit, and there it is held to DeepSeek itself -- the pin test further down.
    assert config.MODELS["deepseek-v4-flash"]["base_url"] == "https://openrouter.ai/api/v1"
    assert config.MODELS["deepseek-v4-pro"]["base_url"] == "https://openrouter.ai/api/v1"


def test_each_model_names_the_key_it_spends():
    # Which key a model costs is the model's own business rather than something the composition
    # root is told twice. Madde 334 leaves DEEPSEEK_API_KEY without a row and still read: going
    # back to DeepSeek's own API is a madde of its own, and the way back is these two rows.
    assert config.MODELS["grok-4.3"]["key"] == "XAI_API_KEY"
    assert config.MODELS["deepseek-v4-flash"]["key"] == "OPENROUTER_API_KEY"
    assert config.MODELS["deepseek-v4-pro"]["key"] == "OPENROUTER_API_KEY"


def test_the_prompt_writer_is_a_role_rather_than_a_choice():
    # Madde 175, and the user's decision of 5 Sep: which model writes a frame's action is the app's
    # business, not the user's -- what they choose is which model runs the conversation. Madde 202
    # made it the same id the composer defaults to, and the role is unchanged by that: this line
    # decides who writes an action, and no picker on the screen reaches it.
    assert config.PROMPT_MODEL == "deepseek-v4-flash"


def test_the_prompt_writer_is_one_of_the_models_that_are_wired():
    # A name outside the table would be a KeyError inside the engine, and it would land at the
    # moment a prompt was asked for -- in a trial, in front of the user, rather than at startup.
    assert config.PROMPT_MODEL in config.MODELS


def test_a_known_model_resolves_to_its_own_wiring():
    # The first value is still the app's own id -- the one a message is written with and the engine
    # finds its client by. What the provider is told comes after the key (Madde 334).
    model, base_url = config.engine_for("deepseek-v4-flash")[:2]
    assert (model, base_url) == ("deepseek-v4-flash", "https://openrouter.ai/api/v1")


def test_the_deepseek_pair_is_sent_under_openrouter_s_names():
    # Madde 334. OpenRouter knows a model as author/slug, while the menu and every stored message
    # carry DeepSeek's own ids -- so the table says what the provider is told, and the ids stay.
    # One name for both rows: DeepSeek's own API had been answering both with V4.1 Flash since 14
    # September, and this keeps that (the user's decision, 25 Eylül).
    assert config.engine_for("deepseek-v4-flash")[3] == "deepseek/deepseek-v4.1-flash"
    assert config.engine_for("deepseek-v4-pro")[3] == "deepseek/deepseek-v4.1-flash"


def test_grok_is_sent_under_its_own_id():
    # xAI knows its model by the id the table is keyed by, and Madde 334 leaves the xAI models as
    # they are.
    assert config.engine_for("grok-4.3")[3] == "grok-4.3"


PINNED_TO_DEEPSEEK = {"provider": {"order": ["deepseek"], "allow_fallbacks": False}}


def test_the_deepseek_pair_is_answered_by_deepseek_alone():
    """A terms assertion rather than a routing preference (Madde 334, the user's call of 25 Eylül).

    OpenRouter serves these weights from many providers and picks one on its own; `order` names
    DeepSeek and `allow_fallbacks` false is what keeps it from going anywhere else. Whichever
    provider answers is whose terms the request runs under, at least one of them forbids this work,
    and DeepSeek's are the ones the direct API ran under. When DeepSeek does not answer, the error
    shows rather than another provider answering. Madde 149's road, with DeepSeek where DeepInfra
    was.
    """
    assert config.engine_for("deepseek-v4-flash")[4] == PINNED_TO_DEEPSEEK
    assert config.engine_for("deepseek-v4-pro")[4] == PINNED_TO_DEEPSEEK


def test_grok_adds_nothing_to_its_body():
    # Asked as "nothing" in whatever shape config settles on: the point is that an xAI request does
    # not carry OpenRouter's routing.
    assert not config.engine_for("grok-4.3")[4]


def test_an_unknown_or_absent_model_falls_back_to_the_default():
    # skills.py's instruction_for rule, and the same reason: a record can name something that has
    # since been renamed, and a message written before this field names nothing at all. Neither may
    # stop a chat from being answered.
    # The example is a name that can never be a model. It used to be grok-4.3, which Madde 183 made
    # a real row -- and a test whose example turns real goes green for the wrong reason.
    assert config.engine_for("")[0] == "deepseek-v4-flash"
    assert config.engine_for("a-model-nobody-wired")[0] == "deepseek-v4-flash"
