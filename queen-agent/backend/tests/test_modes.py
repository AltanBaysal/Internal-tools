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
    "build_character_prompts",
    "write_plan",
    # Madde 128. It takes no position from the model, but it still changes the user's file, so the
    # quieter modes keep their gate in front of it.
    "add_frames",
    # Madde 167. It writes no text of the model's own -- four empty maps the code knows -- but a
    # file appears in the project, and a file appearing is what the quieter modes gate.
    "start_scenario",
    # Madde 168. They change the user's scenario, and a rename reaches every frame that names the
    # entry -- the widest edit any tool here makes.
    "add_character",
    "update_character",
    "remove_character",
    # Madde 169. Same reason, second map.
    "add_outfit",
    "update_outfit",
    "remove_outfit",
    # Madde 170, third map.
    "add_location",
    "update_location",
    "remove_location",
)


def _asks(mode, tool):
    from backend.features.workspace.domain.modes import needs_permission

    return needs_permission(mode, tool)


def test_ask_mode_asks_before_it_writes():
    # The item in one line: since Madde 99 the model is offered the tool either way, and the gate
    # is the running of it rather than the list it was handed.
    assert all(_asks("ask", tool) for tool in WRITES)


def test_no_mode_lists_a_tool_that_is_gone():
    # Madde 127 took the listing tool away. A name left in this module's own list would read as a
    # tool that exists and is simply never asked about -- the one thing this file is about.
    from backend.features.workspace.domain.modes import READS
    from backend.features.workspace.domain.tools import TOOL_SPECS

    assert set(READS) <= {spec["function"]["name"] for spec in TOOL_SPECS}
    assert "list_files" not in READS


def test_ask_mode_reads_without_asking():
    # The schema reader is among them since Madde 96: it opens no file and changes nothing.
    assert not any(_asks("ask", tool) for tool in READS)


def test_edit_mode_asks_for_nothing():
    # The mode's whole meaning. Asked of every tool there is rather than of a list written here --
    # a ninth tool must join this claim by existing, not by somebody remembering to add it.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    assert not any(_asks("edit", spec["function"]["name"]) for spec in TOOL_SPECS)


def test_plan_mode_writes_a_plan_without_asking_and_asks_for_the_rest():
    # Given create_file it could write the plan and the deliverable in the same turn, which is
    # doing the work instead of planning it.
    assert not _asks("plan", "write_plan")
    assert _asks("plan", "create_file")


def test_a_mode_nobody_knows_is_the_default_one():
    # An older browser, or a body with no mode in it at all. A question nobody expected would stop
    # a turn that used to run.
    assert not _asks("", "create_file")
    assert not _asks("something-else", "create_file")


def test_a_tool_nobody_knows_is_never_asked_about():
    # It will not run whatever the answer is, so asking would put a name this app does not have in
    # front of the user and make them approve it.
    assert not _asks("ask", "delete_everything")


def test_only_a_written_plan_ends_the_turn():
    # The plan reached disk and the next move is the user's. Nothing else stops a turn early -- the
    # same tool in edit mode would be an ordinary write.
    from backend.features.workspace.domain.modes import ends_the_turn

    assert ends_the_turn("plan", "write_plan")
    assert not ends_the_turn("edit", "write_plan")
    assert not ends_the_turn("plan", "read_file")
