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


# --- what the registry holds is the connection itself (Madde 90) ---------------------------------


def test_a_stop_cuts_the_connection_it_is_holding():
    # The item in one line: what is kept here is not a note saying somebody asked, it is the
    # connection -- so the press lands on xAI rather than on a flag somebody may read later.
    cuts = []
    stops = MemoryStops()
    stops.hold("p1", "c1", lambda: cuts.append("cut"))
    stops.want("p1", "c1")
    assert cuts == ["cut"]


def test_a_stop_asked_before_the_connection_exists_cuts_it_the_moment_it_arrives():
    # The reason the item exists: the press lands while the model is still thinking, and the answer
    # may not have opened a connection yet. Which of the two comes first is not something either
    # side can arrange, so both orders end the same way.
    cuts = []
    stops = MemoryStops()
    stops.want("p1", "c1")
    stops.hold("p1", "c1", lambda: cuts.append("cut"))
    assert cuts == ["cut"]


def test_a_forgotten_connection_is_not_cut():
    # The answer ended and let go of its socket. A stop arriving afterwards has nothing to reach,
    # and the number it would reach for belongs to somebody else by then.
    cuts = []
    stops = MemoryStops()
    stops.hold("p1", "c1", lambda: cuts.append("cut"))
    stops.clear("p1", "c1")
    stops.want("p1", "c1")
    assert cuts == []


def test_one_chats_connection_is_cut_without_touching_its_neighbours():
    # Per chat, not per project: two chats in one project answer down two connections.
    cuts = []
    stops = MemoryStops()
    stops.hold("p1", "c1", lambda: cuts.append("c1"))
    stops.hold("p1", "c2", lambda: cuts.append("c2"))
    stops.want("p1", "c1")
    assert cuts == ["c1"]
