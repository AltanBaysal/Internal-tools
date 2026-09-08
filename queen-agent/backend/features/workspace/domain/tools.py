"""The tools QueenAgent can reach for, and the rules around them.

The rules live here rather than in data/ because what a file may be called is a product decision,
not a detail of how a directory works.

What the model is TOLD is not here at all since Madde 189: every description below names a constant
in prompt.py, and so does the writer's system prompt. What it is told BACK stays -- a ToolResult's
sentence is built from the values of the call that produced it, and there is nothing to gather.
"""
import json
import re
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from backend.features.workspace.domain import prompt
from backend.features.workspace.domain.build_prompts import (
    build_character_prompts,
    build_prompts,
    cast_of,
    character_prompts_name,
    prompts_name,
    render_module,
)
from backend.features.workspace.domain.errors import BadStructure
from backend.features.workspace.domain.naming import folded

# What the model is told, separately whether a file was born, and separately the file the call was
# about. Parsing the sentence back out would be fragile.
#
# `target` is answered here rather than by the caller because cleaning a name and settling a clash
# are this module's rules: worked out anywhere else they would be a second copy, and the copy would
# drift on the first change to either. Empty when the call was about no file in particular.
#
# `outcome` is a few words for a reader rather than for the model: what the call amounted to, said
# in one line. Never the result itself -- a read's result is the file, and that is already on disk.
#
# `spent` is what the call cost, for a tool that asks a model something of its own (Madde 175).
# None rather than zeroes: a tool that spent nothing and a tool that cannot spend are one thing to
# the turn's stamp, and neither should add a row of noughts to it.
ToolResult = namedtuple("ToolResult", "text created target outcome spent", defaults=("", "", None))


@dataclass(frozen=True)
class FileStarted:
    """The model asked for a file. Its name is not settled until the tool has run."""


@dataclass(frozen=True)
class FileWritten:
    name: str


# The longest sensible chain is the structured prompt run: read the pair, open the scenario, fill
# the three maps, add the scenes, build. Fifteen rounds carry it and the sixteenth closes the
# turn (Madde 137); an unbounded loop would burn both money and time. Reaching the limit is a stop,
# not a failure -- which is why the number has to be generous: a chain cut short looks exactly like
# a model that gave up.
MAX_ROUNDS = 16
DEFAULT_NAME = "note.md"

# How many of one call's requests are in the air at once (Madde 185). Threads rather than anything
# cleverer because what is waited on is a network, not a processor.
#
# Not the number of frames: a file of forty would open forty sockets at a service that answers a
# burst like that with a rate limit, and the wall-clock difference between eight and forty is not
# worth a round of retries. Not measured against any one service's published limit -- comfortably
# under what any of them would object to.
AT_ONCE = 8

# Which tools can bring a file into being. The chat draws a card for each, so an edit is not in
# here: the file was already there. write_plan is, because the first plan of a name is new.
WRITES_FILES = {
    "create_file",
    "start_scenario",
    "build_prompts",
    "build_character_prompts",
    "write_plan",
}

# What a scenario is on the day it is born (Madde 167). The one place this shape is written down:
# the maps empty and waiting, and no frames -- a scenario opens with nobody in it, and the tools
# that follow are what put someone there.
#
# Dumped rather than copied, everywhere it is used. What goes to disk is text, and a constant nobody
# can reach into cannot be edited by accident from across the module.
EMPTY_SCENARIO = {"characters": {}, "outfits": {}, "locations": {}, "frames": []}

TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": prompt.READ_FILE,
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": prompt.THE_FILES_NAME}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": prompt.CREATE_FILE,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": prompt.CREATE_FILE_NAME},
                    "content": {"type": "string", "description": prompt.CREATE_FILE_CONTENT},
                },
                "required": ["name", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_scenario",
            "description": prompt.START_SCENARIO,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": prompt.START_SCENARIO_NAME}
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": prompt.EDIT_FILE,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": prompt.THE_FILES_NAME},
                    "old": {"type": "string", "description": prompt.EDIT_FILE_OLD},
                    "new": {"type": "string", "description": prompt.EDIT_FILE_NEW},
                    "replace_all": {
                        "type": "boolean",
                        "description": prompt.EDIT_FILE_REPLACE_ALL,
                    },
                },
                "required": ["name", "old", "new"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_character",
            "description": prompt.ADD_CHARACTER,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_SCENARIOS_FILE},
                    "name": {"type": "string", "description": prompt.ADD_CHARACTER_NAME},
                    "tags": {"type": "string", "description": prompt.ADD_CHARACTER_TAGS},
                },
                "required": ["file", "name", "tags"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_character",
            "description": prompt.UPDATE_CHARACTER,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_SCENARIOS_FILE},
                    "name": {"type": "string", "description": prompt.UPDATE_CHARACTER_NAME},
                    "tags": {"type": "string", "description": prompt.AN_ENTRYS_NEW_TAGS},
                    "new_name": {"type": "string", "description": prompt.AN_ENTRYS_NEW_NAME},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_character",
            "description": prompt.REMOVE_CHARACTER,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_SCENARIOS_FILE},
                    "name": {"type": "string", "description": prompt.REMOVE_CHARACTER_NAME},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_outfit",
            "description": prompt.ADD_OUTFIT,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_SCENARIOS_FILE},
                    "name": {"type": "string", "description": prompt.ADD_OUTFIT_NAME},
                    "tags": {"type": "string", "description": prompt.ADD_OUTFIT_TAGS},
                },
                "required": ["file", "name", "tags"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_outfit",
            "description": prompt.UPDATE_OUTFIT,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_SCENARIOS_FILE},
                    "name": {"type": "string", "description": prompt.UPDATE_OUTFIT_NAME},
                    "tags": {"type": "string", "description": prompt.AN_ENTRYS_NEW_TAGS},
                    "new_name": {"type": "string", "description": prompt.AN_ENTRYS_NEW_NAME},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_outfit",
            "description": prompt.REMOVE_OUTFIT,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_SCENARIOS_FILE},
                    "name": {"type": "string", "description": prompt.REMOVE_OUTFIT_NAME},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_location",
            "description": prompt.ADD_LOCATION,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_SCENARIOS_FILE},
                    "name": {"type": "string", "description": prompt.ADD_LOCATION_NAME},
                    "tags": {"type": "string", "description": prompt.ADD_LOCATION_TAGS},
                },
                "required": ["file", "name", "tags"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_location",
            "description": prompt.UPDATE_LOCATION,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_SCENARIOS_FILE},
                    "name": {"type": "string", "description": prompt.UPDATE_LOCATION_NAME},
                    "tags": {"type": "string", "description": prompt.AN_ENTRYS_NEW_TAGS},
                    "new_name": {"type": "string", "description": prompt.AN_ENTRYS_NEW_NAME},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_location",
            "description": prompt.REMOVE_LOCATION,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_SCENARIOS_FILE},
                    "name": {"type": "string", "description": prompt.REMOVE_LOCATION_NAME},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_scene",
            "description": prompt.ADD_SCENE,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_STRUCTURES_FILE},
                    "before": {"type": "integer", "description": prompt.ADD_SCENE_BEFORE},
                    "scenes": {
                        "type": "array",
                        "description": prompt.ADD_SCENE_SCENES,
                        "items": {
                            "type": "object",
                            "properties": {
                                "scene": {
                                    "type": "string",
                                    "description": prompt.ADD_SCENE_SCENE,
                                },
                                "characters": {
                                    "type": "object",
                                    "description": prompt.ADD_SCENE_CHARACTERS,
                                },
                                "location": {
                                    "type": "string",
                                    "description": prompt.ADD_SCENE_LOCATION,
                                },
                            },
                            "required": ["scene"],
                        },
                    },
                },
                "required": ["file", "scenes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_frame",
            "description": prompt.UPDATE_FRAME,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_STRUCTURES_FILE},
                    "frame": {"type": "integer", "description": prompt.WHICH_FRAME},
                    "scene": {"type": "string", "description": prompt.UPDATE_FRAME_SCENE},
                    "characters": {
                        "type": "object",
                        "description": prompt.UPDATE_FRAME_CHARACTERS,
                    },
                    "location": {"type": "string", "description": prompt.UPDATE_FRAME_LOCATION},
                    "action": {"type": "string", "description": prompt.UPDATE_FRAME_ACTION},
                },
                "required": ["file", "frame"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_frame",
            "description": prompt.REMOVE_FRAME,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_STRUCTURES_FILE},
                    "frame": {"type": "integer", "description": prompt.WHICH_FRAME},
                },
                "required": ["file", "frame"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_frame_prompt",
            "description": prompt.WRITE_FRAME_PROMPT,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_STRUCTURES_FILE},
                    "frame": {"type": "integer", "description": prompt.WHICH_FRAME},
                    "note": {"type": "string", "description": prompt.WRITE_FRAME_PROMPT_NOTE},
                },
                "required": ["file", "frame"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_prompt_piece",
            "description": prompt.READ_PROMPT_PIECE,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": prompt.READ_PROMPT_PIECE_NAME}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_missing_actions",
            "description": prompt.WRITE_MISSING_ACTIONS,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_STRUCTURES_FILE}
                },
                "required": ["file"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_prompts",
            "description": prompt.BUILD_PROMPTS,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": prompt.THE_STRUCTURES_FILE}
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_character_prompts",
            "description": prompt.BUILD_CHARACTER_PROMPTS,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": prompt.THE_STRUCTURES_FILE},
                    "character": {
                        "type": "string",
                        "description": prompt.BUILD_CHARACTER_PROMPTS_CHARACTER,
                    },
                },
                "required": ["name", "character"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_plan",
            "description": prompt.WRITE_PLAN,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": prompt.WRITE_PLAN_NAME},
                    "content": {"type": "string", "description": prompt.WRITE_PLAN_CONTENT},
                },
                "required": ["name", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mark_step_done",
            "description": prompt.MARK_STEP_DONE,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": prompt.MARK_STEP_DONE_NAME},
                    "step": {"type": "integer", "description": prompt.MARK_STEP_DONE_STEP},
                },
                "required": ["name", "step"],
            },
        },
    },
]


def _ticked(content, step):
    """The plan with that step's box filled, and what was found there (Madde 198).

    Line by line and one character changed. The alternative was the model handing back the whole
    plan with a tick added, and then what a ticked step looks like is its to invent -- which is what
    left the last turn unable to read the one before it.

    Answers `done`, `already` or `missing`, because the three are three different sentences to the
    model and only the first writes.
    """
    lines = content.split("\n")
    state = "missing"
    for index, line in enumerate(lines):
        head = line.lstrip()
        for box, found in (("- [ ] ", "done"), ("- [x] ", "already")):
            # The number as the model wrote it, and only at the front of the step: a plan that
            # mentions step 2 inside step 1's sentence must not be ticked by it.
            if head.startswith(f"{box}{step}.") or head.startswith(f"{box}{step} "):
                if found == "done":
                    lines[index] = line.replace("- [ ] ", "- [x] ", 1)
                return "\n".join(lines), found
    return content, state


def counted(many, word):
    """"1 line", "45 lines". One of a thing is one of it, not one of them."""
    return f"{many} {word}" if many == 1 else f"{many} {word}s"


def numbered(content):
    """The contents with a line number in front of each line, the way `cat -n` writes them.

    Shown rather than stored: the file on disk carries no column, and an edit matches the file. The
    column is there so the model can see for itself whether the text it is about to use as an anchor
    occurs once -- a judgement it was making by eye over near-identical frames, and a wrong guess
    cost a whole round.

    Padded rather than bare, because a ragged left edge is worse than none: at line 10 the text
    would step right and stay there for the rest of the file. Empty content answers empty -- zero
    lines, zero numbers, since a lone 1 would put a line in front of the model that the file
    does not have.
    """
    return "\n".join(f"{n:>6}\t{line}" for n, line in enumerate(content.splitlines(), 1))


def safe_name(raw):
    """A name from the model never reaches the disk as it is."""
    # Only the last segment survives: the model cannot open a folder, because the design has no
    # such idea in it.
    name = str(raw or "").replace("\\", "/").split("/")[-1].strip()
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-").lstrip(".")
    if not name:
        return DEFAULT_NAME
    return name if "." in name else f"{name}.md"


def plan_name(name):
    """A plan is named so that it reads as one, and so the tool cannot write anything else.

    Runs after safe_name: cleaning what came from the model is that one's job, naming is this one's.
    """
    stem = name.rsplit(".", 1)[0]
    return f"{stem}.md" if stem.endswith("-plan") else f"{stem}-plan.md"


def scenario_name(name):
    """A scenario is always .json, whatever it was asked for (Madde 167).

    plan_name's sibling and it runs in the same place, after safe_name. The reason is not tidiness:
    Madde 171 shuts .json to create_file and edit_file, so the tool that opens one has to land on
    the extension the door guards. Two that disagreed would leave the door in front of a file
    nothing writes, and the model holding a structure it could still edit as text.
    """
    return f"{name.rsplit('.', 1)[0]}.json"


def run_tool(file_store, project_id, name, arguments, engine=None):
    """Run one call and answer the model in words. A miss is an answer, not a crash.

    The engine is here for the one tool that answers out of a model rather than out of the file
    store (Madde 175). Optional, because the other eighteen neither take it nor notice it.
    """
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return ToolResult("Those arguments were not valid JSON.", None, "", "Bad arguments")

    if name == "read_file":
        wanted = safe_name(args.get("name"))
        content = file_store.read(project_id, wanted)
        # The target stands whether or not the file was there: asking for a file that does not
        # exist is still a step the turn took.
        if content is None:
            return ToolResult("There is no file by that name.", None, wanted, "No file by that name")
        # A receipt rather than the document (Madde 179). The contents ride in the context box,
        # which reads them from disk on every round; handed back here as well they would ride twice
        # -- once frozen where this answer was written, once fresh -- and a file written to later in
        # the same turn makes the two disagree with nothing to say which is the file. Madde 129
        # killed that staleness across turns and it went on living inside one.
        #
        # Where the file went is said in as many words: a model handed a sentence where it expected
        # a document reads that as not having seen the file, and reads it again.
        lines = counted(len(content.splitlines()), "line")
        return ToolResult(f"{wanted}, {lines}; it is in your opened files.", None, wanted, lines)

    if name == "create_file":
        wanted = safe_name(args.get("name"))
        shut = _shut(wanted)
        if shut is not None:
            return shut
        # Asked of the names rather than by reading the file: the question is whether the name is
        # taken, and pulling a whole document back to learn that is work nobody needs.
        if wanted in file_store.list_names(project_id):
            # The sentence is the instruction. Saying only that one exists would leave the next
            # move to a guess, and a guess is what put the model here.
            return ToolResult(
                f"There is already a file called {wanted}. Use edit_file to change it, or pick "
                "another name for a new document.",
                None,
                wanted,
                "Already there",
            )
        written = file_store.write(project_id, wanted, args.get("content", ""))
        # The name it got, which is the cleaned one rather than whatever the model wished for. Not
        # repeated in the outcome: the line above already carries it.
        return ToolResult(f"Saved as {written}.", written, written, "Saved")

    if name == "start_scenario":
        wanted = scenario_name(safe_name(args.get("name")))
        # Asked of the names rather than by reading the file, for create_file's reason: the question
        # is whether the name is taken, and pulling a whole scenario back to learn that is work
        # nobody needs.
        if wanted in file_store.list_names(project_id):
            # Its own way out rather than create_file's. A scenario is not changed with edit_file --
            # Madde 171 shuts that door -- so the sentence points at the tools that add to one.
            return ToolResult(
                f"There is already a file called {wanted}. Open it and add to it, or pick "
                "another name for a new scenario.",
                None,
                wanted,
                "Already there",
            )
        # Indented and with ensure_ascii off, the way every write to a structure goes: the user
        # opens this file and fixes it by hand, and their work is the first principle.
        written = file_store.write(
            project_id, wanted, json.dumps(EMPTY_SCENARIO, indent=2, ensure_ascii=False)
        )
        return ToolResult(f"Started {written}.", written, written, "Started")

    if name == "write_plan":
        wanted = plan_name(safe_name(args.get("name")))
        # Overwrites where create_file numbers. A second plan sitting in bar-scene-plan-2.md would
        # lose which of the two is the one to follow.
        born = file_store.read(project_id, wanted) is None
        written = file_store.write(project_id, wanted, args.get("content", ""))
        # A card only the first time: after that the file was already there, which is the rule
        # edit_file follows too.
        return ToolResult(
            f"Saved as {written}.",
            written if born else None,
            written,
            "Saved" if born else "Rewritten",
        )

    if name == "mark_step_done":
        wanted = plan_name(safe_name(args.get("name")))
        content = file_store.read(project_id, wanted)
        if content is None:
            return ToolResult(f"There is no {wanted}.", None, wanted, "No plan by that name")
        step = args.get("step")
        marked, state = _ticked(content, step)
        if state != "done":
            # A miss is an answer here, the way it is everywhere else in this file: the model reads
            # what happened and carries on rather than the turn falling over.
            return ToolResult(
                f"There is no step {step} waiting in {wanted}."
                if state == "missing"
                else f"Step {step} was already done.",
                None,
                wanted,
                "Nothing to tick" if state == "missing" else "Already done",
            )
        file_store.write(project_id, wanted, marked)
        # No card: the file was already there, which is the rule edit_file follows too.
        return ToolResult(f"Step {step} is done in {wanted}.", None, wanted, "Ticked")

    if name == "edit_file":
        return _edit(file_store, project_id, args)

    if name == "add_character":
        return _add_entry(file_store, project_id, args, "characters")

    if name == "update_character":
        return _update_entry(file_store, project_id, args, "characters")

    if name == "remove_character":
        return _remove_entry(file_store, project_id, args, "characters")

    if name == "add_outfit":
        return _add_entry(file_store, project_id, args, "outfits")

    if name == "update_outfit":
        return _update_entry(file_store, project_id, args, "outfits")

    if name == "remove_outfit":
        return _remove_entry(file_store, project_id, args, "outfits")

    if name == "add_location":
        return _add_entry(file_store, project_id, args, "locations")

    if name == "update_location":
        return _update_entry(file_store, project_id, args, "locations")

    if name == "remove_location":
        return _remove_entry(file_store, project_id, args, "locations")

    if name == "add_scene":
        return _add_scene(file_store, project_id, args)

    if name == "update_frame":
        return _update_frame(file_store, project_id, args)

    if name == "remove_frame":
        return _remove_frame(file_store, project_id, args)

    if name == "write_frame_prompt":
        return _write_frame_prompt(file_store, project_id, args, engine)

    if name == "write_missing_actions":
        return _write_missing_actions(file_store, project_id, args, engine)

    if name == "read_prompt_piece":
        return _read_prompt_piece(args)

    if name == "build_prompts":
        return _build(file_store, project_id, args)

    if name == "build_character_prompts":
        return _try_character(file_store, project_id, args)

    return ToolResult(f"There is no tool called {name}.", None, "", "Unknown tool")


def _edit(file_store, project_id, args):
    """create_file refuses a name that is taken, so this is the only way to change a document.

    A document, and since Madde 171 only a document: a structure file is changed by the tools that
    know its shape, and this one is shut out of it before it reads anything.
    """
    wanted = safe_name(args.get("name"))
    shut = _shut(wanted)
    if shut is not None:
        return shut
    content = file_store.read(project_id, wanted)
    if content is None:
        return ToolResult("There is no file by that name.", None, wanted, "No file by that name")

    old = args.get("old") or ""
    if not old:
        return ToolResult("An edit needs the text to replace.", None, wanted, "Nothing to replace")

    found = content.count(old)
    if found == 0:
        # No search for something close: a near miss edited silently is worse than a refusal.
        # Before the flag is looked at: it multiplies a match rather than conjuring one.
        return ToolResult(f"That text is not in {wanted}.", None, wanted, "Not found")

    # Every match only when it was asked for. Doing it by default would change more than was meant
    # and nothing on the screen would say so -- and the file is the user's (1st principle).
    every = bool(args.get("replace_all"))
    if found > 1 and not every:
        return ToolResult(
            f"That text appears {found} times in {wanted}; include more of what surrounds it, "
            "or pass replace_all to change every one.",
            None,
            wanted,
            # Reached only above one, so the plural is not a question here -- and "matchs" is what
            # the counted() rule would have produced.
            f"{found} matches",
        )

    new = args.get("new") or ""
    written = content.replace(old, new) if every else content.replace(old, new, 1)
    file_store.write(project_id, wanted, written)
    # No name handed back: the file was already there, and a card would call it new.
    if found == 1:
        # Asking for all of something there is one of is not a different event, and "1 place" would
        # draw it as one.
        return ToolResult(f"Edited {wanted}.", None, wanted, "Edited")
    # The count rather than a read-back: the model learns what it did from the answer, which is the
    # habit Madde 129 and 131 have been taking a reason away from at a time.
    return ToolResult(
        f"Edited {wanted} in {counted(found, 'place')}.", None, wanted, f"Edited {found} places"
    )


def _opened(file_store, project_id, args):
    """The file, parsed, with a frames list -- or the answer saying why not (Madde 168).

    Written once so the map tools cannot start disagreeing about what a missing file or a broken one
    is called. Hands back (source, structure, refused); a caller with a refusal returns it as it is.

    The frames list is demanded even by the tools that never touch it. Removing an entry asks
    whether anything still stands on it and renaming rewrites whatever does -- both answered in the
    frames -- so a file without one cannot do this work at all, and saying so while adding beats
    crashing while removing.
    """
    source = safe_name(args.get("file"))
    content = file_store.read(project_id, source)
    if content is None:
        return source, None, ToolResult(
            "There is no file by that name.", None, source, "No file by that name"
        )

    try:
        structure = json.loads(content)
    except json.JSONDecodeError as broken:
        # The parser's own sentence, as in _build: a guessed cause sends the model somewhere else
        # entirely.
        return source, None, ToolResult(
            f"{source} is not valid JSON: {broken}", None, source, "Not valid JSON"
        )

    frames = structure.get("frames") if isinstance(structure, dict) else None
    if not isinstance(frames, list):
        return source, None, ToolResult(
            f"{source} has no frames list to add to; a structure file carries one.",
            None,
            source,
            "Refused",
        )
    return source, structure, None


def _saved(file_store, project_id, source, structure):
    """Indented and in the user's own language: they open this file and fix it by hand."""
    file_store.write(project_id, source, json.dumps(structure, indent=2, ensure_ascii=False))


def _shut(wanted):
    """The refusal a structure file gets from the text tools, or None if this is not one (Madde 171).

    Asked before anything else about the file -- before it is read, before a match is looked for.
    Refusing to touch a structure as text does not depend on learning anything else about it.

    The extension is the measure, case folded: Windows opens BAR.JSON and bar.json as one file, and
    a door that read the case would stand beside its own frame.

    No exception for a broken one, by the user's decision of 5 Sep. The map tools will not open a
    file that does not parse, so a broken structure came from somebody editing by hand -- and
    repairing what a person wrote by letting the model guess at it is not a repair. The model says
    the file is broken and where; the user fixes it.
    """
    if not wanted.lower().endswith(".json"):
        return None
    return ToolResult(
        f"{wanted} is a structure file; it is not written or changed as text. Use start_scenario "
        "to open one, and the add_, update_ and remove_ tools to change it.",
        None,
        wanted,
        "Not as text",
    )


def _article(word):
    """"a character", "an outfit". One shared sentence over three maps has to survive the singular
    it is handed, and outfit is the one that starts on a vowel."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def _unknown(key, entries, which):
    """The sentence a name nobody knows gets, wherever it is met.

    Only this map's names: place names are no help to somebody looking for a character. Shaped like
    build_prompts._looked_up's, so one miss reads the same on both roads.
    """
    return f"{key} is not in {which}; known: {', '.join(sorted(entries)) or 'nothing'}."


# How a refusal says what is standing on an entry. Three maps, three relations: a character is in a
# frame, an outfit is worn by somebody in one, and a place is what the frame is set in. One table
# rather than three sentences in three functions, which would go stale one at a time.
_STILL_USED_IN = {
    "characters": "is still in frames",
    "outfits": "is still worn in frames",
    "locations": "is still the place in frames",
}


def _frames_naming(frames, which, key):
    """Which frames stand on this entry, by number, one-based as the model counts them.

    One reading of the cast answers it for both maps: a character is a name in it, an outfit is a
    name inside what that name wears. Locations are not here at all -- a frame names its place in a
    field of its own, and Madde 170 brings that branch with its own tests.
    """
    standing = []
    for number, frame in enumerate(frames, start=1):
        if which == "locations":
            # Not in the cast at all: a frame names its place in a field of its own, and there is
            # exactly one of it.
            found = frame.get("location") == key
        else:
            cast = cast_of(frame)
            found = (
                any(name == key for name, _ in cast)
                if which == "characters"
                else any(key in worn for _, worn in cast)
            )
        if found:
            standing.append(number)
    return standing


def _renamed_in_frames(frames, which, key, moving):
    """Carry a rename through the frames, and answer how many followed.

    Both shapes, because both are on disk: the map form a frame writes today, and the plain list of
    names files written before outfits carry. This writes them back the way it found them -- a
    rename is not a conversion, and a file that came back in a shape its user does not recognise is
    a file this tool damaged.
    """
    followed = 0
    for frame in frames:
        if which == "locations":
            # One field, one string, no second shape to preserve.
            if frame.get("location") == key:
                frame["location"] = moving
                followed += 1
            continue
        people = frame.get("characters")
        if which == "outfits":
            followed += _outfit_renamed(frame, people, key, moving)
        elif isinstance(people, dict):
            if key not in people:
                continue
            # Rebuilt rather than popped and re-added: a renamed entry keeps its place in the frame,
            # and the first name in a frame is the one that leads its prompt.
            frame["characters"] = {
                (moving if name == key else name): worn for name, worn in people.items()
            }
            followed += 1
        elif isinstance(people, list):
            if key not in people:
                continue
            frame["characters"] = [moving if name == key else name for name in people]
            followed += 1
    return followed


def _outfit_renamed(frame, people, key, moving):
    """An outfit is renamed inside whoever wears it, and the wearer's own name is left alone.

    Its own function because the shape it walks is a level deeper than a character's, and folding
    both into one loop would put two unrelated conditions on the same line.
    """
    if not isinstance(people, dict):
        # The old plain list of names carries no outfits at all, so there is nothing here to rename.
        return 0
    wearing = False
    for name, worn in people.items():
        if isinstance(worn, str):
            # The slip cast_of forgives -- one outfit written without its list -- kept in the shape
            # it was written in.
            if worn == key:
                people[name] = moving
                wearing = True
        elif isinstance(worn, list) and key in worn:
            people[name] = [moving if one == key else one for one in worn]
            wearing = True
    return 1 if wearing else 0


def _add_entry(file_store, project_id, args, which):
    """One name and its tags into one map. Refuses a name that is already there (Madde 168).

    create_file's rule, one level down: a second entry of the same name would replace the first in
    silence, and every frame naming it would change without anybody asking.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    single = which[:-1]
    key = str(args.get("name") or "").strip()
    if not key:
        return ToolResult(
            f"{_article(single).capitalize()} {single} needs a name.", None, source, "Refused"
        )

    tags = args.get("tags")
    if not str(tags or "").strip():
        # An entry with no text is one every frame naming it builds nothing from. Refused at birth
        # rather than found later in a prompt.
        return ToolResult(f"A new {single} needs tags.", None, source, "Refused")

    entries = structure.get(which)
    if not isinstance(entries, dict):
        entries = {}
        structure[which] = entries
    if key in entries:
        return ToolResult(
            f"There is already {_article(single)} {single} called {key}.",
            None,
            source,
            "Already there",
        )

    entries[key] = tags
    _saved(file_store, project_id, source, structure)
    return ToolResult(f"Added {key} to {which}.", None, source, "Added")


def _update_entry(file_store, project_id, args, which):
    """One name's text, or the name itself, or both (Madde 168).

    Renaming lives here rather than in a rename_ tool of its own: putting several actions behind one
    tool is for actions on one resource, and a rename is an action on the entry itself. It has to
    reach the frames -- a name changed in the map and left alone in the frames is a structure that
    will not build.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    single = which[:-1]
    key = str(args.get("name") or "").strip()
    if not key:
        return ToolResult(
            f"{_article(single).capitalize()} {single} needs a name.", None, source, "Refused"
        )

    entries = structure.get(which) or {}
    if key not in entries:
        return ToolResult(_unknown(key, entries, which), None, source, "Not there")

    # `in` rather than .get(), because an empty string is a value: it is the only way the model can
    # clear a text it wrote before, and .get() would read that as nothing having been given.
    tags = args["tags"] if args.get("tags") is not None else None
    moving = str(args.get("new_name") or "").strip()
    if tags is None and not moving:
        # No silent success: a model told nothing happened moves on believing it did.
        return ToolResult(
            f"Nothing was given to change about {key}.", None, source, "Nothing to change"
        )
    if moving == key:
        return ToolResult(f"{key} is already called that.", None, source, "Nothing to change")
    if moving and moving in entries:
        # Two entries folded into one is the one thing here that calling again cannot undo.
        return ToolResult(
            f"There is already {_article(single)} {single} called {moving}.",
            None,
            source,
            "Already there",
        )

    if tags is not None:
        entries[key] = tags
    frames = structure["frames"]
    if not moving:
        touched = len(_frames_naming(frames, which, key))
        _saved(file_store, project_id, source, structure)
        return ToolResult(
            f"Changed {key} in {which}; {counted(touched, 'frame')} name it.",
            None,
            source,
            "Changed",
        )

    # Rebuilt rather than popped and re-added, so the entry keeps its place in the map: a file the
    # user reads is a file whose order they recognise.
    structure[which] = {(moving if name == key else name): text for name, text in entries.items()}
    followed = _renamed_in_frames(frames, which, key, moving)
    _saved(file_store, project_id, source, structure)
    also = " and changed its text" if tags is not None else ""
    return ToolResult(
        f"Renamed {key} to {moving} in {which}{also}; {counted(followed, 'frame')} followed.",
        None,
        source,
        "Renamed",
    )


def _remove_entry(file_store, project_id, args, which):
    """One name out of one map, if nothing is standing on it (Madde 168).

    Not an update with the value left out. An empty value meaning delete would let a model that
    simply failed to fill a field wipe the entry in silence, and nothing here can be undone by
    calling it again.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    single = which[:-1]
    key = str(args.get("name") or "").strip()
    if not key:
        return ToolResult(
            f"{_article(single).capitalize()} {single} needs a name.", None, source, "Refused"
        )

    entries = structure.get(which) or {}
    if key not in entries:
        return ToolResult(_unknown(key, entries, which), None, source, "Not there")

    standing = _frames_naming(structure["frames"], which, key)
    if standing:
        # The numbers rather than a count: the model's next move is to open those frames, and a
        # count would send it looking for them.
        return ToolResult(
            f"{key} {_STILL_USED_IN[which]} "
            f"{', '.join(str(number) for number in standing)}. Nothing was removed.",
            None,
            source,
            "Still in use",
        )

    del entries[key]
    _saved(file_store, project_id, source, structure)
    return ToolResult(f"Removed {key} from {which}.", None, source, "Removed")


def _add_scene(file_store, project_id, args):
    """A frame is born with its scene, its cast and its place, and none of them is text (Madde 173).

    Madde 128 took the position out of the model's hands: appending through edit_file meant quoting
    the previous frame back, once as the anchor and once inside its replacement, because a JSON list
    closes with a bracket. That still holds -- nothing here takes a position.

    What it did not take was the frame. add_frames was handed objects and looked inside none of
    them, so a frame naming somebody nobody had written landed on disk and was found rounds later,
    inside build_prompts, as a miss in a file nobody was editing any more. The fields are in the
    signature now, and every name in them is looked for before anything is written.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    coming = args.get("scenes")
    if not isinstance(coming, list):
        return ToolResult(
            "add_scene takes a list of scenes, even when there is one of them.",
            None,
            source,
            "Refused",
        )

    frames = structure["frames"]
    if not coming:
        # Nothing to do is not a failure, and writing the file to say so would touch a document for
        # no reason at all.
        return ToolResult(
            f"No scenes were given, so {source} is unchanged.", None, source, "Nothing to add"
        )

    # Where they go (Madde 180). The end unless a frame is named to go in front of, and one past the
    # last frame is the end -- refusing that would refuse a call that named its place correctly.
    # A ceiling of its own, because the sentence has to say how many frames there are rather than
    # how many places they leave.
    place = len(frames) + 1
    if args.get("before") is not None:
        place, missing = _numbered(args["before"], source, len(frames), ceiling=place)
        if missing is not None:
            return missing

    born, problems = [], []
    for offset, scene in enumerate(coming):
        # The number it is going to get, not where it sits in the argument: a complaint carrying the
        # latter would name a frame that already exists and send the model to the wrong one.
        made = _frame_from(scene, place + offset, structure, problems)
        if made is not None:
            born.append(made)

    if problems:
        # Every one of them at once, and nothing written -- build_prompts' rule one step earlier.
        # The whole call falls, including the scenes that were fine: half a batch on disk would
        # leave the model working out which half, and the numbers it was told would be wrong.
        return ToolResult("\n".join(problems + ["Nothing was added."]), None, source, "Refused")

    # Counted before the insertion, while the list still means what the number was measured against.
    moved = len(frames) - (place - 1)
    frames[place - 1 : place - 1] = born
    _renumbered(frames)
    _saved(file_store, project_id, source, structure)
    # Said only when something did move. A sentence about frames that stayed where they were is the
    # one Madde 174 refused when the last frame came out and there was nothing left to renumber.
    after = f"; {counted(moved, 'frame')} after it moved up" if moved else ""
    # The numbers rather than a total. What the model does next is name one of these frames, and a
    # count would send it reading the file back to learn what to call them.
    return ToolResult(
        f"Added {counted(len(born), 'scene')} to {source} as {_made_frames(born)}{after}.",
        None,
        source,
        counted(len(born), "scene"),
    )


def _renumbered(frames):
    """Every frame's number is its place, counted rather than read (Madde 174).

    Shared by the two tools that move places -- taking a frame out and putting one in (Madde 180) --
    because one rule written twice is one rule that will disagree with itself. Frames written before
    Madde 173 carry no number at all, and counting gives them one on the way past.
    """
    for place, frame in enumerate(frames, start=1):
        frame["number"] = place


def _frame_from(scene, number, structure, problems):
    """One scene as one frame, with whatever is wrong about it left in `problems`.

    Goes on building after it finds a problem, and hands the frame back either way: the caller
    throws the whole batch away when anything is wrong, and what is wanted here is every problem
    rather than the first. The one thing it will not do is look inside something that is not an
    object.
    """
    if not isinstance(scene, dict):
        problems.append(
            f"frame {number}: a scene is an object with scene, characters and location."
        )
        return None

    said = str(scene.get("scene") or "").strip()
    if not said:
        # The one required field. A frame with a cast and no scene is a frame there is nothing to
        # write a prompt from, and a space is not a brief.
        problems.append(f"frame {number}: a scene needs a sentence saying what happens.")
    frame = {"number": number, "scene": said}

    people = scene.get("characters")
    if people is not None:
        cast = _cast_checked(people, number, structure, problems)
        if cast is not None:
            frame["characters"] = cast

    place = scene.get("location")
    if place is not None:
        checked = _place_checked(place, number, structure, problems)
        if checked:
            frame["location"] = checked
    # A field nobody gave is left out rather than emptied: an empty one says somebody chose it.
    return frame


def _cast_checked(people, number, structure, problems):
    """A frame's cast as it will be written, or None if the shape is wrong (Madde 174).

    Its own function because a frame meets this twice -- when it is born and when it is changed --
    and one rule written in two places is one rule that will disagree with itself.
    """
    # The values are checked before any name is read: one sentence for the shape, rather than the
    # same sentence once per bad value, which would send the model looking for two faults.
    if not isinstance(people, dict) or not all(
        isinstance(worn, (str, list)) for worn in people.values()
    ):
        problems.append(
            f"frame {number}: characters is a map from a name to the outfits they wear."
        )
        return None

    cast = {}
    for name, worn in people.items():
        _looked_for(name, structure.get("characters") or {}, "characters", number, problems)
        # Written down in the canonical shape. cast_of forgives a lone outfit on the way out
        # because both shapes are already on disk; writing has no such excuse.
        wearing = [worn] if isinstance(worn, str) else list(worn)
        for outfit in wearing:
            _looked_for(outfit, structure.get("outfits") or {}, "outfits", number, problems)
        cast[name] = wearing
    return cast


def _place_checked(place, number, structure, problems):
    """A frame's place, checked the same way on both roads. None if it is not a name at all."""
    if not isinstance(place, str):
        # Looked up with `in`, so anything unhashable would crash rather than answer.
        problems.append(f"frame {number}: location is the name of one place, as a string.")
        return None
    if place:
        _looked_for(place, structure.get("locations") or {}, "locations", number, problems)
    return place


def _looked_for(name, known, which, number, problems):
    """A name that is in no map is _unknown's sentence with the frame's number in front of it.

    The same wording as the map tools and as build_prompts. A miss reads the same everywhere in the
    app, whichever road the model was on when it made one.
    """
    if name not in known:
        problems.append(f"frame {number}: {_unknown(name, known, which)}")


def _made_frames(born):
    """"frame 3", or "frames 3-5". Always one run: they go in side by side, wherever they go."""
    numbers = [frame["number"] for frame in born]
    if len(numbers) == 1:
        return f"frame {numbers[0]}"
    return f"frames {numbers[0]}-{numbers[-1]}"


def _numbered(wanted, source, many, ceiling=None):
    """Which frame a call means, or the answer saying there is no such frame (Madde 174).

    Both frame tools start here, so a number that is not one reads the same whichever was called.

    `ceiling` is how high a number may go when that is not how many frames there are: add_scene's
    `before` may name the place after the last one (Madde 180), and the sentence still has to say
    how many frames the file holds rather than how many places they leave between them.
    """
    top = many if ceiling is None else ceiling
    if isinstance(wanted, str) and wanted.strip().isdigit():
        # One slip with exactly one meaning, forgiven the way a lone outfit is (Madde 173): sending
        # it back would cost a round to learn nothing.
        wanted = int(wanted.strip())
    # bool before int, because in Python True is an int: frame=True would quietly mean frame 1.
    if isinstance(wanted, bool) or not isinstance(wanted, int) or wanted < 1:
        return None, ToolResult(
            "A frame is named by its number, counting from 1.", None, source, "Refused"
        )
    if wanted > top:
        return None, ToolResult(
            f"{source} has {counted(many, 'frame')}; there is no frame {wanted}.",
            None,
            source,
            "Not there",
        )
    return wanted, None


def _update_frame(file_store, project_id, args):
    """Only what was given, the action among it since Madde 201.

    174 kept the action out because the main model would not write that kind of sentence, and 176
    handed it to a model that would. That is no longer true of the model running the conversation,
    and the road left in its place carried the whole of a fix in a note to somebody who had not
    read the line. Correcting a line and having one written from the scene are two jobs now:
    this is the first, and write_frame_prompt is still the second.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    frames = structure["frames"]
    number, missing = _numbered(args.get("frame"), source, len(frames))
    if missing is not None:
        return missing

    # `in` rather than .get(), because an empty value is a value: it is how a field is cleared, and
    # .get() would read that as nothing having been given. The order is this tuple's rather than the
    # call's, so the answer reads the same whichever way the arguments arrived.
    given = {key: args[key] for key in ("scene", "characters", "location", "action") if key in args}
    if not given:
        # No silent success: a model told nothing happened moves on believing it did.
        return ToolResult(
            f"Nothing was given to change about frame {number}.", None, source, "Nothing to change"
        )

    problems, changing = [], {}
    if "scene" in given:
        said = str(given["scene"] or "").strip()
        if not said:
            # Required at birth, so it cannot be emptied later: the two together would leave a
            # frame add_scene refuses to write sitting in the file anyway.
            problems.append(f"frame {number}: a scene needs a sentence saying what happens.")
        changing["scene"] = said
    if "characters" in given:
        people = given["characters"]
        changing["characters"] = (
            _cast_checked(people, number, structure, problems) if people else {}
        )
    if "location" in given:
        place = given["location"]
        changing["location"] = _place_checked(place, number, structure, problems) if place else ""
    if "action" in given:
        # Nothing to check it against: an action names no map entry, and the rules it is written by
        # are the model's to keep rather than this tool's to enforce. Stripped like the scene, so a
        # line arriving with a newline on it does not reach the prompt with one.
        changing["action"] = str(given["action"] or "").strip()

    if problems:
        return ToolResult("\n".join(problems + ["Nothing was changed."]), None, source, "Refused")

    frame = frames[number - 1]
    for key, value in changing.items():
        # An empty value takes the field off the frame rather than emptying it: a frame written
        # without one looks exactly like this (Madde 173), and a file with two ways of saying
        # nothing is a file whose readers have to know both.
        if value:
            frame[key] = value
        else:
            frame.pop(key, None)
    _saved(file_store, project_id, source, structure)
    return ToolResult(
        f"Changed {_and_joined(given)} of frame {number} in {source}.", None, source, "Changed"
    )


def _remove_frame(file_store, project_id, args):
    """One frame out, and every frame after it moves up a place (Madde 174)."""
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    frames = structure["frames"]
    number, missing = _numbered(args.get("frame"), source, len(frames))
    if missing is not None:
        return missing

    del frames[number - 1]
    # The number is a frame's place, so a removal moves every number after it. Nothing in the maps
    # is touched: an entry left in no frame stays where it is, and asking for it to go is the
    # user's (their decision, 5 Sep).
    _renumbered(frames)
    _saved(file_store, project_id, source, structure)
    left = (
        f"{counted(len(frames), 'frame')} left, renumbered from 1" if frames else "no frames left"
    )
    return ToolResult(f"Removed frame {number} from {source}; {left}.", None, source, "Removed")


def _write_frame_prompt(file_store, project_id, args, engine):
    """One frame's action, written by the model that writes those (Madde 176).

    The border between the two models this app runs on. The agent building the scenario says which
    frame and, when it has something to add, why; this asks the writer for the sentence and puts it
    where it goes. Nothing of the answer reaches the chat -- what was written is in the file, and
    Madde 130's rule is that a built prompt is not printed back.

    Every refusal comes before the request, cheapest first: nothing is paid to be told the frame
    was not there.
    """
    if engine is None:
        # A wiring fault rather than the model's doing, and said as one: there is nothing the model
        # can do about it, and a sentence blaming the call would send it round again.
        return ToolResult("There is no model to write with.", None, "", "Refused")

    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    frames = structure["frames"]
    number, missing = _numbered(args.get("frame"), source, len(frames))
    if missing is not None:
        return missing

    frame = frames[number - 1]
    said = str(frame.get("scene") or "").strip()
    if not said:
        # The brief is the whole of what this model is being asked. Without one there is nothing to
        # write from, and asking anyway would spend money to be handed an invention.
        return ToolResult(
            f"Frame {number} has no scene to write from.", None, source, "Nothing to write from"
        )

    try:
        answer = engine.write_once(
            prompt.write_frame_system_prompt(), _frame_seen(frame, structure, args.get("note"))
        )
    except Exception as failure:
        # The service's own words, and the frame left as it was. No retry in here: calling this
        # again is what a retry is, and a loop would pay twice with nobody watching it happen.
        return ToolResult(
            f"The prompt model did not answer: {failure}", None, source, "Did not answer"
        )

    written = str(answer.get("text") or "").strip()
    if not written:
        # An empty action builds into a prompt with a hole where the sentence goes, and nothing
        # downstream could say which frame it came from.
        return ToolResult(
            f"The prompt model answered with nothing; frame {number} is unchanged.",
            None,
            source,
            "Answered with nothing",
        )

    # Always over whatever was there. A second call carrying a note is a correction, and a
    # correction that kept the old sentence beside the new one would be an argument.
    frame["action"] = written
    _saved(file_store, project_id, source, structure)
    return ToolResult(
        f"Wrote frame {number} of {source}.", None, source, "Written", answer.get("spent")
    )


def _read_prompt_piece(args):
    """One piece of the library, as it is written (Madde 187).

    The only tool here that is handed no file store: what it answers with lives in the repo rather
    than in a project, because a position reads the same in every scenario and one written twice
    reads two ways.

    It shows and stops. Putting a piece into a frame is update_frame's, and a tool doing both would
    leave its own answer unable to say which of the two it had done.

    Nothing is picked. What is asked for is what comes back -- SDXL_PROMPT_RULES says the model
    cannot toss a coin, and neither can this.
    """
    wanted = folded(args.get("name"))
    if wanted in prompt.PROMPT_PIECES:
        return ToolResult(
            f"{wanted}: {prompt.PROMPT_PIECES[wanted]}", None, "", "Looked up"
        )

    # The names, on both roads out. Asking is how the model learns what is here, and it pays for
    # that once -- a list carried in the request would be paid for every round and would grow with
    # the library, which is the whole lesson of Madde 185.
    known = ", ".join(sorted(prompt.PROMPT_PIECES))
    if not wanted:
        return ToolResult(f"The pieces there are: {known}.", None, "", "Listed")
    # Shaped like _unknown's and like build_prompts' misses, so one miss reads the same everywhere.
    return ToolResult(
        f"{wanted} is not a piece I have; known: {known}.", None, "", "No piece by that name"
    )


def _write_missing_actions(file_store, project_id, args, engine):
    """Every frame still waiting, asked for at the same time (Madde 185).

    write_frame_prompt takes one frame per call, and a scenario of twenty-one cost twenty-one
    rounds of the main agent -- each of them resending the system prompt, the skill text and a
    context box holding a structure that grew with every write. The writer's own requests were
    never the expensive part.

    What is waiting is what is empty. No range: the file already knows which frames those are, and
    a from/to would put the answer in two places and make the model keep them agreeing. No note
    either -- this is the first writing, and a note is what a correction carries.
    """
    if engine is None:
        # A wiring fault rather than the model's doing, said the way the single-frame tool says it.
        return ToolResult("There is no model to write with.", None, "", "Refused")

    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    # Numbered here, while the whole list is in front of us: what the answer says has to be the
    # number the model will name next, and a frame's number is its place.
    waiting, left = [], []
    for place, frame in enumerate(structure["frames"], start=1):
        if str(frame.get("action") or "").strip():
            continue
        if not str(frame.get("scene") or "").strip():
            # Refused before the request, cheapest first: nothing is paid to be told there was no
            # brief to write from.
            left.append((place, "no scene to write from"))
            continue
        waiting.append((place, frame))

    written, spent = [], {}
    if waiting:
        # Built once for the whole call: every request carries the same message, and building it in
        # the loop would ask the module the same question once per frame.
        said_to_the_writer = prompt.write_frame_system_prompt()
        with ThreadPoolExecutor(max_workers=min(AT_ONCE, len(waiting))) as pool:
            # _frame_seen runs here rather than inside a thread: it reads the structure, and the
            # threads are handed two finished strings and nothing to reach into. Note is None --
            # there is nothing anybody has said about a frame nobody has written yet.
            asked = {
                pool.submit(
                    engine.write_once,
                    said_to_the_writer,
                    _frame_seen(frame, structure, None),
                ): (place, frame)
                for place, frame in waiting
            }
            # Walked in the order they were sent, so the numbers in the answer come out ascending
            # however the network chose to answer.
            for future, (place, frame) in asked.items():
                try:
                    answer = future.result()
                except Exception as failure:
                    # The service's own words, and the frame left as it was. One that fell over
                    # does not undo the ones that landed: they are paid for, and throwing an hour
                    # of work away over one failure is a worse answer than naming it.
                    left.append((place, str(failure)))
                    continue
                spent = _added(spent, answer.get("spent"))
                said = str(answer.get("text") or "").strip()
                if not said:
                    # An empty action builds into a prompt with a hole where the sentence goes.
                    # Its bill is counted all the same: that request was made and charged for.
                    left.append((place, "answered with nothing"))
                    continue
                frame["action"] = said
                written.append(place)

    if not waiting and not left:
        # Nothing was asked, so nothing was spent: a row of noughts on the turn's stamp says a
        # request happened.
        return ToolResult(
            f"There are no frames waiting for an action in {source}.", None, source, "Nothing to do"
        )

    # One write, after every answer is in: a file caught half filled would be a state nothing else
    # in here can produce.
    if written:
        _saved(file_store, project_id, source, structure)

    said = f"Wrote {counted(len(written), 'frame')} of {source}"
    said += f": {', '.join(str(place) for place in written)}." if written else "."
    if left:
        # Each with its own reason. One sentence for all of them would make the model guess which
        # frame the reason belonged to.
        why = "; ".join(f"{place} ({reason})" for place, reason in sorted(left))
        said += f" {counted(len(left), 'frame')} not written: {why}."
    return ToolResult(said, None, source, f"Wrote {len(written)}", spent or None)


def _added(total, spent):
    """One bill out of many, key by key (Madde 185).

    Whatever the service named, rather than a fixed three: a figure this side has never heard of
    is still a figure somebody paid, and dropping it would understate the call.
    """
    for key, amount in (spent or {}).items():
        total[key] = total.get(key, 0) + amount
    return total


def _frame_seen(frame, structure, note):
    """What the writer is shown: this frame, and nothing else in the file (Madde 176).

    The user's decision of 5 September, and the reason this request stays cheap -- a file of forty
    frames would otherwise send forty casts to write one sentence. Names as well as tags, because a
    note saying "aylin looks bored" has to reach the person the tags describe.

    A name the maps do not hold is shown without tags rather than refused: add_scene refuses those
    on the way in, so one here came from somebody editing the file by hand, and this tool is not
    where that is punished.
    """
    characters = structure.get("characters") or {}
    outfits = structure.get("outfits") or {}
    locations = structure.get("locations") or {}

    lines = [f"Scene: {frame['scene']}"]
    cast = cast_of(frame)
    if cast:
        lines.append("In frame:")
        for name, worn in cast:
            lines.append(f"- {name}: {characters.get(name, '')}")
            lines.extend(f"  wearing {outfit}: {outfits.get(outfit, '')}" for outfit in worn)
    place = frame.get("location")
    if place:
        lines.append(f"Place: {place}: {locations.get(place, '')}")
    if note:
        # Last, where the instruction sits in every other request this app makes: what is fixed
        # leads and what changes trails (Madde 93).
        lines.append(f"Note: {note}")
    return "\n".join(lines)


def _and_joined(words):
    """"scene", "scene and location", "scene, characters and location"."""
    words = list(words)
    if len(words) == 1:
        return words[0]
    return f"{', '.join(words[:-1])} and {words[-1]}"


def _build(file_store, project_id, args):
    """The structure is the model's; the prompts are the code's."""
    source = safe_name(args.get("name"))
    content = file_store.read(project_id, source)
    # The source rather than the output, all the way through: the file card already names what was
    # written, and a line repeating it would carry nothing the card does not.
    if content is None:
        return ToolResult("There is no file by that name.", None, source, "No file by that name")

    target = prompts_name(source)
    if target == source:
        return ToolResult(
            f"{source} would be written over by its own output; a structure belongs in a .json file.",
            None,
            source,
            "Refused",
        )

    try:
        structure = json.loads(content)
    except json.JSONDecodeError as broken:
        # The parser's own sentence. A guessed cause would send the model looking in the wrong place.
        return ToolResult(f"{source} is not valid JSON: {broken}", None, source, "Not valid JSON")

    try:
        prompts = build_prompts(structure)
    except BadStructure as refused:
        return ToolResult(str(refused), None, source, "Refused")

    # Written over on purpose: this file is derived, and regenerating it after an edit is the whole
    # point. Numbering it would leave a pile with no way to tell which one is now.
    written = file_store.write(project_id, target, render_module(prompts))
    return ToolResult(
        f"Wrote {counted(len(prompts), 'prompt')} to {written}.",
        written,
        source,
        counted(len(prompts), "prompt"),
    )


def _try_character(file_store, project_id, args):
    """One character, looked at before it enters a frame. The reading is _build's, the assembling
    is the other constructor's."""
    source = safe_name(args.get("name"))
    content = file_store.read(project_id, source)
    if content is None:
        return ToolResult("There is no file by that name.", None, source, "No file by that name")

    try:
        structure = json.loads(content)
    except json.JSONDecodeError as broken:
        return ToolResult(f"{source} is not valid JSON: {broken}", None, source, "Not valid JSON")

    character = str(args.get("character") or "")
    try:
        prompts = build_character_prompts(structure, character)
    except BadStructure as refused:
        return ToolResult(str(refused), None, source, "Refused")

    target = character_prompts_name(source, character)
    written = file_store.write(project_id, target, render_module(prompts))
    # Handed back as well as written (Madde 135). This tool is a look -- the user wants to see the
    # character before it enters a frame -- and a look that answers only with a file name sends the
    # model straight back to read it. build_prompts stays silent for the opposite reason: its list
    # is there to sit in the file, and Madde 130 keeps it out of the chat.
    return ToolResult(
        f"Wrote {counted(len(prompts), 'prompt')} to {written}:\n\n" + "\n\n".join(prompts),
        written,
        source,
        counted(len(prompts), "prompt"),
    )
