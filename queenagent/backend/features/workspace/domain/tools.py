"""The three tools QueenAgent can reach for, and the rules around them.

The rules live here rather than in data/ because what a file may be called is a product decision,
not a detail of how a directory works.
"""
import json
import re
from collections import namedtuple
from dataclasses import dataclass

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


# Eight rounds carry the longest sensible chain -- list, read, read, write, explain -- while an
# unbounded loop would burn both money and time. Reaching the limit is a stop, not a failure.
MAX_ROUNDS = 8
DEFAULT_NAME = "note.md"

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

    return ToolResult(f"There is no tool called {name}.", None)
