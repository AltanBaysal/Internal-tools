"""What the stop registry promises. Nothing here touches the disk -- see the module's own note."""
from backend.features.workspace.data.memory_stops import MemoryStops


def test_a_chat_nobody_asked_about_is_not_wanted():
    assert MemoryStops().wanted("p1", "c1") is False


def test_asking_makes_it_wanted():
    stops = MemoryStops()
    stops.want("p1", "c1")
    assert stops.wanted("p1", "c1") is True


def test_clearing_puts_it_back():
    # Left standing, the flag would cut the next answer the moment it was born.
    stops = MemoryStops()
    stops.want("p1", "c1")
    stops.clear("p1", "c1")
    assert stops.wanted("p1", "c1") is False


def test_one_chat_is_stopped_without_stopping_its_neighbour():
    # The record is per chat, not per project: two chats in one project answer independently.
    stops = MemoryStops()
    stops.want("p1", "c1")
    assert stops.wanted("p1", "c2") is False


def test_clearing_something_nobody_asked_about_is_quiet():
    # The answer clears the flag when it ends, and most answers end without ever being stopped.
    MemoryStops().clear("p1", "c1")
