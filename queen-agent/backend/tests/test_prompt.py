from pathlib import Path

import pytest

from backend.features.workspace.domain.prompt import SYSTEM_PROMPT

# --- one place for every text the model is told (Madde 189) ---------------------------------------
#
# They were spread over four files: this one, skills.py, the nine hundred lines of TOOL_SPECS, and
# stream_answer's heading for the context box. Reading them meant walking four files, and a rule
# said twice in two of them could not be seen at all -- 182 only found such a copy because a word
# cap went red.
#
# The line this madde draws is between what the model is TOLD and what it is TOLD BACK. Instructions
# move: they are written once and read on every call. Answers stay where they are made, because an
# answer is an f-string over values that exist only at that call, and a template pulled into another
# file is a copy of the call's shape -- and a copy is the side that goes stale.


def _texts_named_by(module):
    """Every string this module names in capitals, which is how a text is written down here."""
    return {
        value
        for name, value in vars(module).items()
        if name.isupper() and isinstance(value, str)
    }


def _descriptions_in(properties):
    """Every description under a parameter map, following arrays into their items.

    add_frame's frames is a list of objects and those objects carry descriptions of their own. A
    walk that stopped at the first level would leave the deepest texts unwatched, which is where a
    forgotten one would sit.
    """
    for said in properties.values():
        if "description" in said:
            yield said["description"]
        inner = said.get("items", {}).get("properties")
        if inner:
            yield from _descriptions_in(inner)


def test_every_text_a_tool_carries_comes_from_the_prompt_module():
    from backend.features.workspace.domain import prompt
    from backend.features.workspace.domain.tools import TOOL_SPECS

    known = _texts_named_by(prompt)
    # Before anything else: an empty set would let the loop below pass over an empty TOOL_SPECS too,
    # and this run has already watched seven tests go green because nothing had happened yet.
    assert len(known) > 10

    for spec in TOOL_SPECS:
        function = spec["function"]
        assert function["description"] in known, function["name"]
        for said in _descriptions_in(function["parameters"]["properties"]):
            assert said in known, function["name"]


def _rules_of(guide):
    """A guide's rules, one per line, without the dash they are listed with."""
    from backend.features.workspace.domain.prompt import GUIDES

    return [line[2:] for line in GUIDES[guide].splitlines() if line.startswith("- ")]


GUIDE_NAMES = ["sdxl-prompt-writing.md", "krea-prompt-writing.md"]


@pytest.mark.parametrize("guide", GUIDE_NAMES)
def test_no_tool_carries_a_guides_rule(guide):
    # Madde 492, the user's decision of 22 October: a model's prompt rules stand in its own guide
    # and its own skills and nowhere else ("model instructlarını onunla alakalı skill hariç hiçbir
    # yerde olmadığından emin olalım"). A tool's description says what the tool does and what a
    # field holds; a rule copied back onto one would ride every request, in front of either model.
    #
    # Line by line: a copy of one rule is the same rule said twice and would slip past a search for
    # the whole text.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    rules = _rules_of(guide)
    # Before the loop: an empty guide would let it pass over nothing.
    assert len(rules) > 5
    for spec in TOOL_SPECS:
        function = spec["function"]
        said = [function["description"], *_descriptions_in(function["parameters"]["properties"])]
        for text in said:
            for rule in rules:
                assert rule not in text, (function["name"], rule)


@pytest.mark.parametrize("guide", GUIDE_NAMES)
def test_the_system_prompt_carries_no_guides_rule(guide):
    # The same decision for the text every request opens with: no rule goes out in a turn that has
    # no skill selected (the user, 22 October: "hiçbiri gitmez").
    rules = _rules_of(guide)
    assert rules
    for rule in rules:
        assert rule not in SYSTEM_PROMPT, rule


def test_there_are_two_guides_and_both_say_something():
    from backend.features.workspace.domain.prompt import GUIDES

    assert sorted(GUIDES) == sorted(GUIDE_NAMES)
    for name, text in GUIDES.items():
        assert text.strip(), name


def test_the_krea_guide_says_nothing_about_sdxl():
    # Each model's rules in its own place, never in the other's.
    from backend.features.workspace.domain.prompt import GUIDES

    said = GUIDES["krea-prompt-writing.md"]
    assert "Write the prompt in English, as one paragraph of plain sentences." in said
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    for word in ("SDXL", "Danbooru", "Write tags", "Rule 1"):
        assert word not in said, word


def test_the_sdxl_guide_says_nothing_about_krea():
    from backend.features.workspace.domain.prompt import GUIDES

    said = GUIDES["sdxl-prompt-writing.md"]
    assert "Write tags, never sentences." in said
    assert "krea" not in said.lower()


def test_the_sdxl_guide_carries_the_rules_the_tools_gave_up():
    # Madde 492's audit: what left the tool texts was a rule the guide did not already have -- solo,
    # who leads a frame, the fixed order -- and the scene's own rules (the user, 22 October).
    from backend.features.workspace.domain.prompt import GUIDES

    said = GUIDES["sdxl-prompt-writing.md"]
    assert "Never write solo in a character's entry." in said
    assert "Whoever is written first among a frame's characters leads the frame's prompt." in said
    assert "fixed order, so a character reads the same in all of them" in said
    assert "## The scene" in said


@pytest.mark.parametrize("guide", GUIDE_NAMES)
def test_both_guides_carry_the_scene_rules(guide):
    # The scene becomes the video in either model, so each guide says how one is written.
    from backend.features.workspace.domain.prompt import GUIDES

    scene = GUIDES[guide].split("## The scene")[1]
    assert "- Write each scene in English.\n" in scene
    assert "- Write each scene in sentences, never as tags.\n" in scene
    assert "inside quotes" in scene
    assert "four seconds" in scene


@pytest.mark.parametrize(
    "module,name",
    [
        ("tools", "SDXL_PROMPT_RULES"),
        ("skills", "START_A_SCENARIO"),
        # Madde 186 renamed this one with the skill it belongs to. The guard keeps watching the
        # name it had when it moved as well: a text put back under the old name in skills.py is
        # the same failure as one put back under the new one.
        ("skills", "GENERATE_PROMPTS_PLUS"),
        ("skills", "EDIT_PROMPTS"),
        # Madde 492. The SDXL document is a guide's body now, and Improve is gone.
        ("prompt", "SDXL_DOCUMENT"),
        ("prompt", "IMPROVE"),
    ],
)
def test_no_text_is_still_written_down_where_it_used_to_live(module, name):
    """The source rather than the module, and that is not fussiness.

    An imported name becomes an attribute of the module that imported it, so hasattr says yes long
    after the text has moved. What this madde forbids is the text being *written* in two places, and
    only the source says where it was written. test_notebook.py watches its notebook the same way.
    """
    from backend.features.workspace.domain import prompt, skills, tools

    modules = {"tools": tools, "skills": skills, "prompt": prompt}
    source = Path(modules[module].__file__).read_text(encoding="utf-8")
    assert f"{name} = " not in source, f"{name} is still assigned in {module}.py"


MUST_BE_FULL = (
    "SYSTEM_PROMPT",
    "LAST_ROUND",
    "START_A_SCENARIO",
    "EDIT_PROMPTS",
    "KREA_START_SCENARIO",
    "KREA_EDIT",
)
"""The texts this app writes, and every one of them says something.

Read by the test below and by the one about Madde 196's second part, which is deliberately not on
this list -- lifted out of that test so the absence can be asserted rather than only meant.
"""


def test_the_prompt_module_holds_the_texts_the_others_gave_up():
    # The floor under the two above: both of them would pass over an empty module, one with an empty
    # set of texts and one with an empty source.
    from backend.features.workspace.domain import prompt

    for name in MUST_BE_FULL:
        assert getattr(prompt, name, "").strip(), name


def test_the_app_forces_no_language_of_its_own():
    # The interface is English because its design was written in English. That is a rule about
    # labels, and it was never a reason to answer a Turkish question in English.
    assert "English" not in SYSTEM_PROMPT


# --- how the text is written ---------------------------------------------------------------------
#
# What the system prompt says is the user's, written with them line by line (Madde 468), and no test
# holds its wording. What stays is its shape.


def test_the_text_ends_on_its_last_word():
    # system_prompt() puts the owner's part behind a blank line; a blank line of this text's own
    # would make two, and an empty suffix returns this text as it is -- the cached prefix's head.
    assert SYSTEM_PROMPT == SYSTEM_PROMPT.strip()


# --- what the turn's last round is told (Madde 137) -----------------------------------------------
#
# Imported inside each test rather than at the top of the file: until the constant exists a module
# level import would stop this file being collected at all, and the fourteen guards above would read
# as errors of this item's making. The same shape allowed() and refused() use in test_run_turn.
#
# The text is only half the item -- the round really is handed no tools, and test_run_turn
# measures that. What is guarded here is that the sentence says the two things the failure asked
# for: that nothing more will run, and what the closing answer owes the reader.


def test_the_last_round_notice_says_no_tool_will_run():
    # Why it says so rather than only asking for a summary: the model is not stopping early, it is
    # being told the road ends here. A sentence that said wrap up would leave it free to spend the
    # round on one more call -- which is the failure this item comes from.
    from backend.features.workspace.domain.prompt import LAST_ROUND

    said = LAST_ROUND.lower()
    assert "last round" in said
    assert "no tool" in said


def test_the_last_round_notice_asks_what_is_left():
    # The user's own two words for what a closing answer owes them. Saying only what was done
    # leaves the reader to work out where it stopped, and the next message is where they pick it up.
    from backend.features.workspace.domain.prompt import LAST_ROUND

    said = LAST_ROUND.lower()
    assert "what is left" in said
    assert "next step" in said


@pytest.mark.parametrize(
    "task",
    ["scenario", "frame", "character", "prompt", "sdxl", "outfit", "structure file"],
)
def test_the_base_names_no_task(task):
    # The item's own boundary, and the one worth guarding: what goes into the base is how to work,
    # never what the work is. A task word here would make every chat carry knowledge that belongs
    # to one skill -- and would quietly answer a question Madde 94 has not asked yet.
    assert task not in SYSTEM_PROMPT.lower()


# --- the second part, which is the user's own (Madde 196) ----------------------------------------


def test_a_plan_is_written_as_boxes_to_tick():
    # Madde 198. The ticking was instructed long before the shape was, and an instruction without a
    # shape is one the model answers differently every turn -- so the plan a fresh chat opens says
    # nothing about where the work stopped.
    #
    # The shape used to live in write_plan's description; Madde 207 takes that tool away, and
    # correction 10 had already decided where the shape goes instead: into the sentence of the step
    # that writes the plan, so that it holds whichever tool writes it.
    from backend.features.workspace.domain import prompt

    assert "- [ ]" in prompt.START_A_SCENARIO


def test_the_system_prompt_has_a_second_part():
    from backend.features.workspace.domain import prompt

    assert isinstance(prompt.SYSTEM_PROMPT_SUFFIX, str)


def test_the_second_part_is_allowed_to_be_empty():
    """The one text in this module the app does not write.

    What goes in it is the user's own, and the item builds the place rather than filling it -- so it
    is born empty and stays legal that way. Asserted as an absence from the list rather than as a
    sentence in a comment: a name added there would fail this madde on the day somebody leaves the
    suffix blank, which is every day until the user writes something.
    """
    assert "SYSTEM_PROMPT_SUFFIX" not in MUST_BE_FULL
