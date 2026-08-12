"""Which producers this machine has, and which of them are installed."""
import pytest

from backend.features.producers.domain.usecases.list_producers import list_producers


class FakeProducer:
    def __init__(self, installed=True, boom=None):
        self._installed = installed
        self._boom = boom

    def installed(self):
        if self._boom:
            raise RuntimeError(self._boom)
        return self._installed


def test_all_three_are_listed_in_the_order_the_engine_works_in():
    rows = list_producers({})

    assert [row["id"] for row in rows] == ["photo", "video", "audio"]
    assert [row["name"] for row in rows] == [
        "Fotoğraf üreticisi", "Video üreticisi", "Ses üreticisi"]


def test_a_producer_that_says_it_is_installed_is_installed():
    rows = list_producers({"photo": FakeProducer(installed=True)})

    assert rows[0]["installed"] is True


def test_a_producer_that_says_it_is_not_is_not():
    rows = list_producers({"photo": FakeProducer(installed=False)})

    assert rows[0]["installed"] is False


def test_a_kind_with_no_producer_at_all_is_not_installed():
    rows = list_producers({})

    assert [row["installed"] for row in rows] == [False, False, False]


def test_a_producer_that_cannot_answer_is_not_quietly_called_missing():
    # Saying "not installed" would invite a download nobody needs; the caller has to hear the
    # renderer's own words instead.
    with pytest.raises(RuntimeError):
        list_producers({"photo": FakeProducer(boom="Bağlantı yok")})
