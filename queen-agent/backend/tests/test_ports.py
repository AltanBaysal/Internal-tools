import inspect

import pytest

from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.domain.ports import Engine
from backend.services.xai.client import XaiClient


@pytest.mark.parametrize("method", ["write_once", "stream"])
def test_the_engine_port_asks_for_what_its_adapter_takes(method):
    # A Protocol has no body, so nothing running catches it drifting from the thing that answers it.
    # Its signature can still be read, and that is the measure: what the port promises the domain
    # against what the adapter actually takes. Measured on the real adapter rather than on a fake --
    # the fakes are written to whatever the caller passes, so they would agree with either side.
    promised = list(inspect.signature(getattr(Engine, method)).parameters)
    given = list(inspect.signature(getattr(XaiEngine, method)).parameters)
    assert promised == given


@pytest.mark.parametrize("layer", [Engine, XaiEngine, XaiClient])
def test_nothing_is_left_of_the_complete_road(layer):
    # Madde 175. It was reached from nowhere in production -- stream_answer only ever streams --
    # and a road nobody walks is a road nobody notices going wrong. write_once takes its place, and
    # it is not the same journey: no tools, no conversation, and a system prompt of the caller's.
    assert not hasattr(layer, "complete")
