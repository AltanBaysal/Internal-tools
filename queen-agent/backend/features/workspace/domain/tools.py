"""The tools QueenAgent can reach for, and the rules around them.

The rules live here rather than in data/ because what a file may be called is a product decision,
not a detail of how a directory works.
"""
import json
import re
from collections import namedtuple
from dataclasses import dataclass

from backend.features.workspace.domain.build_prompts import (
    build_prompts,
    prompts_name,
    render_module,
)
from backend.features.workspace.domain.errors import BadStructure
from backend.features.workspace.domain.naming import unique_name

# What the model is told, and separately whether a file was born. Parsing the sentence back out
# would be fragile.
ToolResult = namedtuple("ToolResult", "text created")


@dataclass(frozen=True)
class FileStarted:
    """The model asked for a file. Its name is not settled until the tool has run."""


@dataclass(frozen=True)
class FileWritten:
    name: str


# The longest sensible chain is the structured prompt run: list, read, write the skeleton, add the
# frames in batches, check itself, build. Sixteen rounds carry it; an unbounded loop would burn both
# money and time. Reaching the limit is a stop, not a failure -- which is why the number has to be
# generous: a chain cut short looks exactly like a model that gave up.
MAX_ROUNDS = 16
DEFAULT_NAME = "note.md"

# Which tools can bring a file into being. The chat draws a card for each, so an edit is not in
# here: the file was already there.
WRITES_FILES = {"create_file", "build_prompts"}

TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List the names of the files this project already holds.",
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
                "something worth keeping as a file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "A short file name ending in .md."},
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
                "exactly once, so include enough of what surrounds it to be sure."
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
]


def safe_name(raw):
    """A name from the model never reaches the disk as it is."""
    # Only the last segment survives: the model cannot open a folder, because the design has no
    # such idea in it.
    name = str(raw or "").replace("\\", "/").split("/")[-1].strip()
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-").lstrip(".")
    if not name:
        return DEFAULT_NAME
    return name if "." in name else f"{name}.md"


def run_tool(file_store, project_id, name, arguments):
    """Run one call and answer the model in words. A miss is an answer, not a crash."""
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return ToolResult("Those arguments were not valid JSON.", None)

    if name == "list_files":
        names = file_store.list_names(project_id)
        return ToolResult("\n".join(names) if names else "This project has no files yet.", None)

    if name == "read_file":
        content = file_store.read(project_id, safe_name(args.get("name")))
        return ToolResult(
            content if content is not None else "There is no file by that name.", None
        )

    if name == "create_file":
        wanted = unique_name(file_store.list_names(project_id), safe_name(args.get("name")))
        written = file_store.write(project_id, wanted, args.get("content", ""))
        return ToolResult(f"Saved as {written}.", written)

    if name == "edit_file":
        return _edit(file_store, project_id, args)

    if name == "build_prompts":
        return _build(file_store, project_id, args)

    return ToolResult(f"There is no tool called {name}.", None)


def _edit(file_store, project_id, args):
    """create_file never overwrites, so without this there is no way to change anything."""
    wanted = safe_name(args.get("name"))
    content = file_store.read(project_id, wanted)
    if content is None:
        return ToolResult("There is no file by that name.", None)

    old = args.get("old") or ""
    if not old:
        return ToolResult("An edit needs the text to replace.", None)

    found = content.count(old)
    if found == 0:
        # No search for something close: a near miss edited silently is worse than a refusal.
        return ToolResult(f"That text is not in {wanted}.", None)
    if found > 1:
        return ToolResult(
            f"That text appears {found} times in {wanted}; include more of what surrounds it.",
            None,
        )

    file_store.write(project_id, wanted, content.replace(old, args.get("new") or "", 1))
    # No name handed back: the file was already there, and a card would call it new.
    return ToolResult(f"Edited {wanted}.", None)


def _build(file_store, project_id, args):
    """The structure is the model's; the prompts are the code's."""
    source = safe_name(args.get("name"))
    content = file_store.read(project_id, source)
    if content is None:
        return ToolResult("There is no file by that name.", None)

    target = prompts_name(source)
    if target == source:
        return ToolResult(
            f"{source} would be written over by its own output; a structure belongs in a .json file.",
            None,
        )

    try:
        structure = json.loads(content)
    except json.JSONDecodeError as broken:
        # The parser's own sentence. A guessed cause would send the model looking in the wrong place.
        return ToolResult(f"{source} is not valid JSON: {broken}", None)

    try:
        prompts = build_prompts(structure)
    except BadStructure as refused:
        return ToolResult(str(refused), None)

    # Written over on purpose: this file is derived, and regenerating it after an edit is the whole
    # point. Numbering it would leave a pile with no way to tell which one is now.
    written = file_store.write(project_id, target, render_module(prompts))
    return ToolResult(f"Wrote {len(prompts)} prompts to {written}.", written)
