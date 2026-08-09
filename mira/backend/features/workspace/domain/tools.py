"""The three tools Mira can reach for, and the rules around them.

The rules live here rather than in data/ because what a file may be called is a product decision,
not a detail of how a directory works.
"""
import json
import re

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


def unique_name(existing, name):
    """Nothing is ever overwritten: plan.md becomes plan-2.md."""
    if name not in existing:
        return name
    stem, _, extension = name.rpartition(".")
    number = 2
    while f"{stem}-{number}.{extension}" in existing:
        number += 1
    return f"{stem}-{number}.{extension}"


def run_tool(file_store, project_id, name, arguments):
    """Run one call and answer the model in words. A miss is an answer, not a crash."""
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return "Those arguments were not valid JSON."

    if name == "list_files":
        names = file_store.list_names(project_id)
        return "\n".join(names) if names else "This project has no files yet."

    if name == "read_file":
        content = file_store.read(project_id, safe_name(args.get("name")))
        return content if content is not None else "There is no file by that name."

    if name == "create_file":
        wanted = unique_name(file_store.list_names(project_id), safe_name(args.get("name")))
        written = file_store.write(project_id, wanted, args.get("content", ""))
        return f"Saved as {written}."

    return f"There is no tool called {name}."
