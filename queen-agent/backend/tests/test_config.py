from backend import config


def test_the_default_model_is_the_cheap_one_with_the_long_context():
    # Pinned like MAX_ROUNDS: this is a decision, and changing it without noticing changes what the
    # user pays. grok-4.3 costs half of grok-4.5 and carries 1M of context against its 500k, and
    # the runs here are long -- structure file, scenario and frame list pile up in one chat.
    #
    # An XAI_MODEL in the environment overrides this and the resolved value is what lands here, so
    # on a machine that sets it this test fails and says something true: the default running here
    # is not the one the repository ships.
    assert config.XAI_MODEL == "grok-4.3"
