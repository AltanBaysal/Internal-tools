"""Picking a chat's mode (Madde 463): onto its row, never into its file."""
import pytest

from backend.features.workspace.domain.errors import ChatNotFound, UnknownMode
from backend.features.workspace.domain.usecases.pick_mode import pick_mode


class Rows:
    """A chat store holding one chat's row, and nothing that opens a chat."""

    def __init__(self):
        self.modes = {"c1": "edit"}

    def set_mode(self, project_id, chat_id, mode):
        if chat_id not in self.modes:
            return False
        self.modes[chat_id] = mode
        return True


@pytest.mark.parametrize("mode", ["plan", "ask", "edit"])
def test_a_known_mode_goes_onto_the_chat(mode):
    rows = Rows()
    assert pick_mode(rows, "p1", "c1", mode) == mode
    assert rows.modes["c1"] == mode


@pytest.mark.parametrize("mode", ["", "write", None, 5, ["ask"]])
def test_a_mode_nobody_knows_is_refused_and_nothing_is_written(mode):
    rows = Rows()
    with pytest.raises(UnknownMode):
        pick_mode(rows, "p1", "c1", mode)
    assert rows.modes == {"c1": "edit"}


def test_a_chat_that_is_not_there_is_refused():
    with pytest.raises(ChatNotFound):
        pick_mode(Rows(), "p1", "ghost", "ask")
