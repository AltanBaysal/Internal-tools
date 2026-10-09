"""What a mode lets through without asking. The rule that used to be a sentence in a skill's text.

The modes are named here the way the wire names them, and the module is imported inside each test
rather than at the top: a module that does not exist yet fails this whole file's collection, and
then none of the turn's other reds are visible anywhere in the suite.
"""
# One since Madde 172: the schema tool went with the shape it taught, and reading a file is the only
# thing left that opens nothing and changes nothing.
READS = ("read_file",)
WRITES = (
    "create_file",
    "edit_file",
    "build_prompts",
    # Madde 128 and 173. It takes neither a position nor a shape from the model, but it still
    # changes the user's file, so the quieter modes keep their gate in front of it.
    "add_frame",
    # Madde 167. It writes no text of the model's own -- four empty maps the code knows -- but a
    # file appears in the project, and a file appearing is what the quieter modes gate.
    "start_scenario",
    # Madde 168, and 456. They change the user's scenario, and a rename reaches every frame that
    # names the entry -- the widest edit any tool here makes.
    "set_character",
    "remove_character",
    # Madde 169. Same reason, second map.
    "set_outfit",
    "remove_outfit",
    # Madde 170, third map.
    "set_location",
    "remove_location",
    # Madde 174. A removal renumbers every frame left, which is the widest change any of these
    # makes to a file the user is reading.
    "update_frame",
    "remove_frame",
)


def _asks(mode, tool):
    from backend.features.workspace.domain.modes import needs_permission

    return needs_permission(mode, tool)


def test_ask_mode_asks_before_it_writes():
    # The item in one line: since Madde 99 the model is offered the tool either way, and the gate
    # is the running of it rather than the list it was handed.
    assert all(_asks("ask", tool) for tool in WRITES)


def test_no_mode_lists_a_tool_that_is_gone():
    # Every mode's list names only tools the model is given. A name left behind when a tool goes or
    # is renamed -- list_files, write_plan, add_scene and the rest -- would read as a tool that exists
    # and is simply never asked about, the one thing this file is about. Read off the lists rather
    # than asked of needs_permission: that answers False for a tool nobody knows, so a leftover
    # entry claims nothing there and passes green.
    from backend.features.workspace.domain.modes import _WITHOUT_ASKING
    from backend.features.workspace.domain.tools import TOOL_SPECS

    known = {spec["function"]["name"] for spec in TOOL_SPECS}
    for mode, allowed in _WITHOUT_ASKING.items():
        assert set(allowed) <= known, mode


def test_ask_mode_reads_without_asking():
    # The schema reader is among them since Madde 96: it opens no file and changes nothing.
    assert not any(_asks("ask", tool) for tool in READS)


def test_reading_a_file_is_the_only_call_no_mode_asks_about():
    # Madde 187 put a second call in here -- looking a ready piece up, which opened no file and
    # wrote nothing -- and Madde 205 took it back out with the tool itself.
    #
    # Written as an equality rather than a "not in": needs_permission answers False for a tool
    # nobody knows, so a loop built on a name that no longer exists asserts nothing and passes
    # green. This run has watched twelve tests do exactly that.
    from backend.features.workspace.domain.modes import READS

    assert READS == ("read_file",)
    for mode in ("ask", "plan", "edit"):
        assert not _asks(mode, "read_file"), mode


def test_edit_mode_asks_for_nothing():
    # The mode's whole meaning. Asked of every tool there is rather than of a list written here --
    # a ninth tool must join this claim by existing, not by somebody remembering to add it.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    assert not any(_asks("edit", spec["function"]["name"]) for spec in TOOL_SPECS)


def test_plan_mode_writes_one_file_without_asking():
    # Madde 207. The privilege used to be write_plan's, and the fear was that create_file would let
    # the mode write the plan and the deliverable in one turn. It cannot: the first write is what
    # ends the turn, one line below this.
    assert not _asks("plan", "create_file")
    assert _asks("plan", "edit_file")
    assert _asks("plan", "add_frame")


def test_a_mode_nobody_knows_is_the_default_one():
    # An older browser, or a body with no mode in it at all. A question nobody expected would stop
    # a turn that used to run.
    assert not _asks("", "create_file")
    assert not _asks("something-else", "create_file")


def test_a_tool_nobody_knows_is_never_asked_about():
    # It will not run whatever the answer is, so asking would put a name this app does not have in
    # front of the user and make them approve it.
    assert not _asks("ask", "delete_everything")


def test_only_the_plan_modes_own_file_ends_the_turn():
    # The plan reached disk and the next move is the user's. Nothing else stops a turn early -- the
    # same call in edit mode is an ordinary write, which is what it has always been there.
    from backend.features.workspace.domain.modes import ends_the_turn

    assert ends_the_turn("plan", "create_file")
    assert not ends_the_turn("edit", "create_file")
    assert not ends_the_turn("plan", "read_file")
