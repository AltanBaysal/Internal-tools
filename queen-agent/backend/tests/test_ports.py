import inspect

import pytest

from backend.features.workspace.data.model_engine import ModelEngine
from backend.features.workspace.domain.ports import Engine
from backend.services.model.client import ModelClient


def test_the_engine_port_asks_for_what_its_adapter_takes():
    # A Protocol has no body, so nothing running catches it drifting from the thing that answers it.
    # Its signature can still be read, and that is the measure: what the port promises the domain
    # against what the adapter actually takes. Measured on the real adapter rather than on a fake --
    # the fakes are written to whatever the caller passes, so they would agree with either side.
    promised = list(inspect.signature(Engine.stream).parameters)
    given = list(inspect.signature(ModelEngine.stream).parameters)
    assert promised == given


@pytest.mark.parametrize("layer", [Engine, ModelEngine, ModelClient])
def test_nothing_is_left_of_the_complete_road(layer):
    # Madde 175. It was reached from nowhere in production -- stream_answer only ever streams --
    # and a road nobody walks is a road nobody notices going wrong.
    assert not hasattr(layer, "complete")


@pytest.mark.parametrize("layer", [Engine, ModelEngine, ModelClient])
def test_nothing_is_left_of_the_one_question_road(layer):
    # Madde 395, the owner's decision of 30 September: the main model writes each frame's action
    # itself, so the one tool that asked a model a question of its own took this road with it.
    assert not hasattr(layer, "write_once")


@pytest.mark.parametrize("layer", [Engine, ModelEngine, ModelClient])
def test_a_turn_names_no_conversation(layer):
    # Madde 383. The id only ever reached one provider's own cache header, and that provider is
    # gone: DeepSeek matches prefixes by itself.
    assert "conversation_id" not in inspect.signature(layer.stream).parameters
