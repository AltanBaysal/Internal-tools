"""The tools QueenAgent can reach for, and the rules around them.

The rules live here rather than in data/ because what a file may be called is a product decision,
not a detail of how a directory works.
"""
import json
import re
from collections import namedtuple
from dataclasses import dataclass

from backend.features.workspace.domain.build_prompts import (
    build_character_prompts,
    build_prompts,
    cast_of,
    character_prompts_name,
    prompts_name,
    render_module,
)
from backend.features.workspace.domain.errors import BadStructure
from backend.features.workspace.domain.schema import SCHEMA

# What the model is told, separately whether a file was born, and separately the file the call was
# about. Parsing the sentence back out would be fragile.
#
# `target` is answered here rather than by the caller because cleaning a name and settling a clash
# are this module's rules: worked out anywhere else they would be a second copy, and the copy would
# drift on the first change to either. Empty when the call was about no file in particular.
#
# `outcome` is a few words for a reader rather than for the model: what the call amounted to, said
# in one line. Never the result itself -- a read's result is the file, and that is already on disk.
ToolResult = namedtuple("ToolResult", "text created target outcome", defaults=("", ""))


@dataclass(frozen=True)
class FileStarted:
    """The model asked for a file. Its name is not settled until the tool has run."""


@dataclass(frozen=True)
class FileWritten:
    name: str


# The longest sensible chain is the structured prompt run: read the pair, write the skeleton, add
# the frames in batches, check itself, build. Fifteen rounds carry it and the sixteenth closes the
# turn (Madde 137); an unbounded loop would burn both money and time. Reaching the limit is a stop,
# not a failure -- which is why the number has to be generous: a chain cut short looks exactly like
# a model that gave up.
MAX_ROUNDS = 16
DEFAULT_NAME = "note.md"

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
            "name": "read_prompt_structure_schema",
            "description": (
                "What a structure file looks like and the rules it has to hold, shown with an "
                "example. A structure file is the one JSON per scenario that prompts are built "
                "from: the characters, outfits and locations written once, and the frames that "
                "name them. Call it before writing or changing one -- no instruction repeats "
                "the schema, so never write one from memory. It takes no arguments; there is "
                "one schema for the whole app."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read one of this project's files.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "The file's name."}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": (
                "Save a document into this project. Reach for it only when the user asked for "
                "something worth keeping -- a draft, a report, a summary they will come back to. "
                "Refuses a name that is already taken: to change a file that exists, use "
                "edit_file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": (
                            "A short file name: .md for a document, .json for a structure file."
                        ),
                    },
                    "content": {"type": "string", "description": "The document itself."},
                },
                "required": ["name", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_scenario",
            "description": (
                "Open a new scenario: the structure file prompts are built from. It is born empty "
                "-- no characters, no outfits, no locations, no frames -- and the tools that add "
                "each of those are what fill it. You give a name and nothing else; the shape is "
                "the code's, and the file is always .json. Refuses a name that is already taken: "
                "a scenario is opened and added to, never started a second time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "What the scenario is called, as in bar-scene.",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": (
                "Change part of a file that already exists. The text you give as old must appear "
                "exactly once and match what is on disk now, without the line numbers a read "
                "shows it with: read the file first if this turn has "
                "not seen it -- what this turn read or wrote is already in front of you -- and "
                "include enough of what surrounds it to be sure. When you mean every occurrence "
                "rather than one -- a map entry renamed through all the frames that call on it -- "
                "pass replace_all instead of growing the text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The file's name."},
                    "old": {"type": "string", "description": "The exact text to replace."},
                    "new": {
                        "type": "string",
                        "description": "What takes its place. Empty takes the text out.",
                    },
                    "replace_all": {
                        "type": "boolean",
                        "description": (
                            "Change every occurrence. Left out, text that appears more than once "
                            "is refused rather than guessed at."
                        ),
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
            "description": (
                "Write a new character into a scenario: the tags an image model draws them from, "
                "written once here and named by every frame they appear in. Refuses a name that is "
                "already there -- to change one that exists, use update_character."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The scenario's file name."},
                    "name": {
                        "type": "string",
                        "description": (
                            "What this character is called in this scenario, as in aylin. Frames "
                            "name them by it."
                        ),
                    },
                    "tags": {
                        "type": "string",
                        "description": (
                            "The character as tags: how many people this entry draws, their age, "
                            "body, hair and face. As in 1girl, woman in her mid 20s, long black "
                            "hair, green eyes, slim body. No clothes here -- those are outfits."
                        ),
                    },
                },
                "required": ["file", "name", "tags"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_character",
            "description": (
                "Change a character that is already in a scenario: its tags, its name, or both. "
                "Only what you give changes. Renaming reaches every frame that names it, so the "
                "scenario still builds afterwards. Refuses a name that is not there."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The scenario's file name."},
                    "name": {"type": "string", "description": "Which character to change."},
                    "tags": {
                        "type": "string",
                        "description": (
                            "The whole entry as it should now read -- this replaces the text "
                            "rather than adding to it. Leave it out to change only the name."
                        ),
                    },
                    "new_name": {
                        "type": "string",
                        "description": (
                            "What to call it from now on. Leave it out to change only the tags."
                        ),
                    },
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_character",
            "description": (
                "Take a character out of a scenario. Refused while any frame still names it, and "
                "the answer says which frames -- take them out of those frames first, or remove "
                "the frames. Nothing here can be undone by calling it again."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The scenario's file name."},
                    "name": {"type": "string", "description": "Which character to remove."},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_frames",
            "description": (
                "Add frames to the end of a structure file's frames list. Where they go is not "
                "yours to give -- the end of a list is something the code knows -- so there is no "
                "text to quote back and nothing to read first. The answer says how many went in "
                "and how many the file holds now: adding twice adds twice, and that second number "
                "is how you see it. To change a frame that is already there, use edit_file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The structure file's name."},
                    "frames": {
                        "type": "array",
                        "description": (
                            "The frames to add, each shaped as the schema says. A list even when "
                            "there is one of them."
                        ),
                        "items": {"type": "object"},
                    },
                },
                "required": ["name", "frames"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_prompts",
            "description": (
                "Build the prompt list from a structure file. Code assembles every frame in a fixed "
                "order, so a character reads the same in all of them. Writes a Python file named "
                "after the structure, replacing what it wrote last time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The structure file's name."}
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_character_prompts",
            "description": (
                "Build a preview list for one character: one prompt for every outfit the "
                "structure names, joined the same way a frame's prompt is. Reach for it when the "
                "user wants to look at one character on its own, before any frame. Writes a "
                "Python file named after the structure and the character, replacing what it "
                "wrote last time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The structure file's name."},
                    "character": {"type": "string", "description": "Which character to preview."},
                },
                "required": ["name", "character"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_plan",
            "description": (
                "Break the work into numbered steps and save the plan. Writes over the plan of "
                "that name if there is one, so hand back the whole plan rather than the part you "
                "changed -- read it first if this turn has not seen it. A turn asked only to "
                "plan ends with this call -- the "
                "user reads the plan, fixes it in the file if they want to, and runs it "
                "themselves. A plan that is the first step of a larger job is an ordinary step: "
                "carry on from it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "What the plan is for, as in bar-scene.",
                    },
                    "content": {"type": "string", "description": "The plan itself."},
                },
                "required": ["name", "content"],
            },
        },
    },
]


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


def run_tool(file_store, project_id, name, arguments):
    """Run one call and answer the model in words. A miss is an answer, not a crash."""
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return ToolResult("Those arguments were not valid JSON.", None, "", "Bad arguments")

    if name == "read_prompt_structure_schema":
        # No arguments: there is one shape, so asking which one would be a question with a single
        # answer. The outcome is what was answered with rather than the answer -- a read says how
        # many lines, not the file.
        return ToolResult(SCHEMA, None, "", "Schema")

    if name == "read_file":
        wanted = safe_name(args.get("name"))
        content = file_store.read(project_id, wanted)
        # The target stands whether or not the file was there: asking for a file that does not
        # exist is still a step the turn took.
        if content is None:
            return ToolResult("There is no file by that name.", None, wanted, "No file by that name")
        # How much was read is nowhere on disk, so it cannot go stale -- it is a note about this
        # moment rather than a copy of something that lives elsewhere. Counted on the file rather
        # than on what was shown: the column is for the model, not part of the document.
        return ToolResult(
            numbered(content), None, wanted, counted(len(content.splitlines()), "line")
        )

    if name == "create_file":
        wanted = safe_name(args.get("name"))
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

    if name == "edit_file":
        return _edit(file_store, project_id, args)

    if name == "add_character":
        return _add_entry(file_store, project_id, args, "characters")

    if name == "update_character":
        return _update_entry(file_store, project_id, args, "characters")

    if name == "remove_character":
        return _remove_entry(file_store, project_id, args, "characters")

    if name == "add_frames":
        return _add_frames(file_store, project_id, args)

    if name == "build_prompts":
        return _build(file_store, project_id, args)

    if name == "build_character_prompts":
        return _try_character(file_store, project_id, args)

    return ToolResult(f"There is no tool called {name}.", None, "", "Unknown tool")


def _edit(file_store, project_id, args):
    """create_file refuses a name that is taken, so this is the only way to change anything."""
    wanted = safe_name(args.get("name"))
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
        # The parser's own sentence, as in _build and _add_frames: a guessed cause sends the model
        # somewhere else entirely.
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


def _unknown(key, entries, which):
    """The sentence a name nobody knows gets, wherever it is met.

    Only this map's names: place names are no help to somebody looking for a character. Shaped like
    build_prompts._looked_up's, so one miss reads the same on both roads.
    """
    return f"{key} is not in {which}; known: {', '.join(sorted(entries)) or 'nothing'}."


def _frames_naming(frames, which, key):
    """Which frames stand on this entry, by number, one-based as the model counts them.

    Only characters today. Outfits ride inside a character's list and a location is a field of its
    own, so each map answers this question differently -- and each brings its own answer with its
    own tests, in Madde 169 and 170.
    """
    return [
        number
        for number, frame in enumerate(frames, start=1)
        if key in [name for name, _ in cast_of(frame)]
    ]


def _renamed_in_frames(frames, which, key, moving):
    """Carry a rename through the frames, and answer how many followed.

    Both shapes, because both are on disk: the map form a frame writes today, and the plain list of
    names files written before outfits carry. cast_of reads them; this writes them back the way it
    found them, since turning one into the other would rewrite a file nobody asked to convert.
    """
    followed = 0
    for frame in frames:
        people = frame.get("characters")
        if isinstance(people, dict):
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
        return ToolResult(f"A {single} needs a name.", None, source, "Refused")

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
            f"There is already a {single} called {key}.", None, source, "Already there"
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
        return ToolResult(f"A {single} needs a name.", None, source, "Refused")

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
            f"There is already a {single} called {moving}.", None, source, "Already there"
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
        return ToolResult(f"A {single} needs a name.", None, source, "Refused")

    entries = structure.get(which) or {}
    if key not in entries:
        return ToolResult(_unknown(key, entries, which), None, source, "Not there")

    standing = _frames_naming(structure["frames"], which, key)
    if standing:
        # The numbers rather than a count: the model's next move is to open those frames, and a
        # count would send it looking for them.
        return ToolResult(
            f"{key} is still in frames {', '.join(str(number) for number in standing)}. "
            "Nothing was removed.",
            None,
            source,
            "Still in use",
        )

    del entries[key]
    _saved(file_store, project_id, source, structure)
    return ToolResult(f"Removed {key} from {which}.", None, source, "Removed")


def _add_frames(file_store, project_id, args):
    """The end of a list is something code knows, so the model never has to point at it.

    Appending through edit_file meant quoting the previous frame back -- once as the anchor and once
    inside its replacement -- because a JSON list closes with a bracket and the new frame goes
    before it. Nothing here takes a position, so there is no position to get wrong.
    """
    source = safe_name(args.get("name"))
    content = file_store.read(project_id, source)
    if content is None:
        return ToolResult("There is no file by that name.", None, source, "No file by that name")

    try:
        structure = json.loads(content)
    except json.JSONDecodeError as broken:
        # The parser's own sentence, as in _build: a guessed cause sends the model somewhere else.
        return ToolResult(f"{source} is not valid JSON: {broken}", None, source, "Not valid JSON")

    coming = args.get("frames")
    if not isinstance(coming, list):
        return ToolResult(
            "add_frames takes a list of frames, even when there is one of them.",
            None,
            source,
            "Refused",
        )

    # Asked of a dictionary only: a file whose top level is something else has no frames either, and
    # an AttributeError would tell the model nothing it could act on.
    frames = structure.get("frames") if isinstance(structure, dict) else None
    if not isinstance(frames, list):
        return ToolResult(
            f"{source} has no frames list to add to; a structure file carries one.",
            None,
            source,
            "Refused",
        )

    if not coming:
        # Nothing to do is not a failure, and writing the file to say so would touch a document for
        # no reason at all.
        return ToolResult(
            f"No frames were given, so {source} is unchanged.", None, source, "Nothing to add"
        )

    frames.extend(coming)
    # Indented for the person who opens this file and fixes it by hand, and ensure_ascii off so
    # their own language survives the round trip -- their work is the first principle.
    file_store.write(project_id, source, json.dumps(structure, indent=2, ensure_ascii=False))
    # Both numbers: what this call did, and where the file stands after it. Appending is not
    # idempotent, and the second is what keeps a doubled call in front of the model rather than in
    # a read it would have to make.
    return ToolResult(
        f"Added {counted(len(coming), 'frame')} to {source}; it holds {len(frames)} now.",
        None,
        source,
        counted(len(coming), "frame"),
    )


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
