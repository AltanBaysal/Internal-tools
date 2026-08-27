"""What each mode puts in the request. The rule that used to be a sentence in a skill's text.

The modes are named here the way the wire names them, and the module is imported inside each test
rather than at the top: a module that does not exist yet fails this whole file's collection, and
then none of the turn's other reds are visible anywhere in the suite.
"""
# read_schema joined them in Madde 96: it opens no file and changes nothing, so no mode has a
# reason to withhold it.
READS = {"list_files", "read_file", "read_schema"}


def _offered(mode):
    from backend.features.workspace.domain.modes import tools_for

    return {spec["function"]["name"] for spec in tools_for(mode)}


def test_ask_mode_can_only_read():
    # The item in one line: a model in this mode does not create a file because it has no tool that
    # creates one -- not because it was asked nicely and held itself back.
    assert _offered("ask") == READS


def test_plan_mode_can_write_a_plan_and_nothing_else():
    # Given create_file it could write the plan and the deliverable in the same turn, which is
    # doing the work instead of planning it.
    assert _offered("plan") == READS | {"write_plan"}


def test_edit_mode_can_write_a_plan_too():
    # Madde 97: the flow works in this mode because it writes files, and it keeps its place in a
    # plan. Without the tool here its first step cannot be taken at all.
    assert _offered("edit") == READS | {
        "create_file",
        "edit_file",
        "build_prompts",
        "build_character_prompts",
        "write_plan",
    }


def test_a_mode_nobody_knows_is_the_default_one():
    # An older browser, or a body with no mode in it at all. Losing the tools silently would look
    # exactly like a model that decided not to use them.
    assert _offered("") == _offered("edit")
    assert _offered("something-else") == _offered("edit")


def test_only_a_written_plan_ends_the_turn():
    # The plan reached disk and the next move is the user's. Nothing else stops a turn early -- the
    # same tool in edit mode would be an ordinary write.
    from backend.features.workspace.domain.modes import ends_the_turn

    assert ends_the_turn("plan", "write_plan")
    assert not ends_the_turn("edit", "write_plan")
    assert not ends_the_turn("plan", "read_file")
