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
# the frames in batches, check itself, build. Sixteen rounds carry it; an unbounded loop would burn both
# money and time. Reaching the limit is a stop, not a failure -- which is why the number has to be
# generous: a chain cut short looks exactly like a model that gave up.
MAX_ROUNDS = 16
DEFAULT_NAME = "note.md"

# Which tools can bring a file into being. The chat draws a card for each, so an edit is not in
# here: the file was already there. write_plan is, because the first plan of a name is new.
WRITES_FILES = {"create_file", "build_prompts", "build_character_prompts", "write_plan"}

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
            "name": "edit_file",
            "description": (
                "Change part of a file that already exists. The text you give as old must appear "
                "exactly once and match what is on disk now: read the file first if this turn has "
                "not seen it -- what this turn read or wrote is already in front of you -- and "
                "include enough of what surrounds it to be sure."
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
                },
                "required": ["name", "old", "new"],
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
        # moment rather than a copy of something that lives elsewhere.
        return ToolResult(content, None, wanted, counted(len(content.splitlines()), "line"))

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
        return ToolResult(f"That text is not in {wanted}.", None, wanted, "Not found")
    if found > 1:
        return ToolResult(
            f"That text appears {found} times in {wanted}; include more of what surrounds it.",
            None,
            wanted,
            # Reached only above one, so the plural is not a question here -- and "matchs" is what
            # the counted() rule would have produced.
            f"{found} matches",
        )

    file_store.write(project_id, wanted, content.replace(old, args.get("new") or "", 1))
    # No name handed back: the file was already there, and a card would call it new.
    return ToolResult(f"Edited {wanted}.", None, wanted, "Edited")


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
        f"Wrote {len(prompts)} prompts to {written}.",
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
    return ToolResult(
        f"Wrote {len(prompts)} prompts to {written}.",
        written,
        source,
        counted(len(prompts), "prompt"),
    )
