import inspect

import pytest

from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.domain.ports import Engine


@pytest.mark.parametrize("method", ["write_once", "stream"])
def test_the_engine_port_asks_for_what_its_adapter_takes(method):
    # A Protocol has no body, so nothing running catches it drifting from the thing that answers it.
    # Its signature can still be read, and that is the measure: what the port promises the domain
    # against what the adapter actually takes. Measured on the real adapter rather than on a fake --
    # the fakes are written to whatever the caller passes, so they would agree with either side.
    #
    # The two live roads, since Madde 164. It used to measure complete, which nothing called.
    promised = list(inspect.signature(getattr(Engine, method)).parameters)
    given = list(inspect.signature(getattr(XaiEngine, method)).parameters)
    assert promised == given


@pytest.mark.parametrize("layer", [Engine, XaiEngine])
def test_neither_the_port_nor_its_adapter_still_offers_complete(layer):
    # Madde 164. A conversation goes through stream and a one-shot through write_once; complete was
    # a third road nothing walked, and a port promising it would have an adapter answering it.
    # Watched rather than simply deleted, so it cannot come back.
    assert not hasattr(layer, "complete")


def test_the_port_no_longer_hands_a_model_to_the_call():
    # Madde 82 settled it: one model, named once in config.py. The signature test does not reach
    # this -- a parameter can go while the sentence explaining it stays, and then the file says
    # something that is no longer true. Watched rather than simply deleted, so it cannot come back.
    #
    # Read off stream since Madde 164: what it guards is the sentence, and the method it used to
    # stand in is gone.
    assert "travels with the call" not in inspect.getdoc(Engine.stream)
