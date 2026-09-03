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
# the frames in batches, check itself, build. Fifteen rounds carry it and the sixteenth closes the
# turn (Madde 137); an unbounded loop would burn both money and time. Reaching the limit is a stop,
# not a failure -- which is why the number has to be generous: a chain cut short looks exactly like
# a model that gave up.
MAX_ROUNDS = 16
DEFAULT_NAME = "note.md"

# What a frame is made of, as far as the model is concerned (Madde 152). This is what an incoming
# call is checked against; the tool's schema below spells the same four out, because each one needs
# its own description for the model to fill it well. A test holds the two lists together -- they can
# only drift by someone changing one of them alone, and then the model is offered a field the tool
# refuses.
_FRAME_FIELDS = ("characters", "location", "action", "camera")

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
                        # No .json since Madde 151: this tool cannot write one, and an example
                        # offering the extension would send the model at a closed door.
                        "description": "A short file name, as in bar-scene.md.",
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
            "name": "add_frames",
            "description": (
                "Add one frame to the end of a structure file's frames list. Give the frame field "
                "by field -- there is no JSON to write here and none to quote back, and where the "
                "frame goes is not yours to give: the end of a list is something the code knows. "
                "One call is one frame. Every name you use has to be in the file's maps already; a "
                "name nobody knows is refused and nothing is written. The answer says how many "
                "frames the file holds now, so a call made twice is visible without reading it "
                "back. To change a frame that is already there, use edit_file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The structure file's name."},
                    "characters": {
                        "type": "object",
                        "description": (
                            "Who is in the frame and what they wear: the character's name against "
                            "the list of outfits they have on, both named from the file's maps. "
                            "Whoever the frame is about goes first -- that one opens the prompt. "
                            "An empty list is someone wearing nothing named; leave the whole thing "
                            "out for a frame with nobody in it."
                        ),
                    },
                    "location": {
                        "type": "string",
                        "description": "Where it happens, named from the file's locations map.",
                    },
                    "action": {
                        "type": "string",
                        "description": (
                            "What is happening, as tags: the pose, the expression, where the eyes "
                            "look. Only what the camera sees."
                        ),
                    },
                    "camera": {
                        "type": "string",
                        "description": (
                            "How much of the body is in the picture and where it is looked at "
                            "from, as tags."
                        ),
                    },
                },
                "required": ["name", "action", "camera"],
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


def is_structure(name):
    """Whether this name belongs to a structure file (Madde 151).

    Asked of the cleaned name rather than the raw one, so what the door looks at is what the disk
    would get -- a path in front of it is safe_name's business and gone by here.

    Case is folded because a door a model can walk around by shouting the extension is not a door,
    and that is the kind of gap it finds while looking for one. The extension is the whole of the
    question: this app already speaks that way -- _build refuses with "a structure belongs in a
    .json file".
    """
    return name.lower().endswith(".json")


# Said once, by both tools that used to be able to write one. What it does not say is which tool to
# use instead: those do not exist yet, and naming one that is not there sends the model looking for
# it -- or inventing it. The names go in when they arrive.
_NOT_AS_TEXT = "{} is a structure file; it is not written or changed as text."


def _reads_as_json(content):
    """Whether this text still parses. A check rather than a source: what comes back is thrown away.

    Costs nothing extra where it is called -- _edit has the file in hand a line earlier, and reading
    it is work already done.
    """
    try:
        json.loads(content)
    except json.JSONDecodeError:
        return False
    return True


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
        # moment rather than a copy of something that lives elsewhere. Counted on the file rather
        # than on what was shown: the column is for the model, not part of the document.
        return ToolResult(
            numbered(content), None, wanted, counted(len(content.splitlines()), "line")
        )

    if name == "create_file":
        wanted = safe_name(args.get("name"))
        # Ahead of the taken-name check (Madde 151). Behind it, a name already on disk would answer
        # "already there" instead, and the model would read the difference as a door that opens for
        # a name nobody has used yet.
        if is_structure(wanted):
            return ToolResult(_NOT_AS_TEXT.format(wanted), None, wanted, "Refused")
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

    # After the read, and both halves are needed (Madde 151). On the extension alone a file the user
    # broke by hand would be refused too -- and since every structural tool dies at json.loads, that
    # would leave nothing able to put the comma back. On the content alone a .md holding valid JSON
    # would be shut. So: a structure file that still parses is the tools' to change; one that does
    # not is text, and text is what this is for.
    if is_structure(wanted) and _reads_as_json(content):
        return ToolResult(_NOT_AS_TEXT.format(wanted), None, wanted, "Refused")

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


def _add_frames(file_store, project_id, args):
    """One frame, taken apart field by field. The model names the fields; the shape is code's.

    The end of a list is something code knows, so the model never has to point at it. Appending
    through edit_file meant quoting the previous frame back -- once as the anchor and once inside
    its replacement -- because a JSON list closes with a bracket and the new frame goes before it.
    Nothing here takes a position, so there is no position to get wrong.

    And since Madde 152 nothing here takes a shape either. The model used to hand over frame objects
    it had built itself, which is the same as writing the file by hand with extra steps -- and Madde
    151 shut that door. What this signature promises is its own: the file's shape can change behind
    it without the model being taught anything again.
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

    # A closed set, and one stranger stops the whole call. Writing the fields that were understood
    # would leave the model believing in a frame that is not the one it asked for, and half a frame
    # is worse than either -- so nothing is written and the answer says what was not recognised.
    # The old frames list falls out here rather than needing a rule of its own.
    stranger = next((key for key in args if key not in _FRAME_FIELDS and key != "name"), None)
    if stranger is not None:
        return ToolResult(
            f"add_frames has no {stranger} field; it takes "
            f"{', '.join(sorted(_FRAME_FIELDS))}. Nothing was written.",
            None,
            source,
            "Refused",
        )

    # A frame that says neither what is happening nor where it is looked at from is not a frame.
    missing = [field for field in ("action", "camera") if not str(args.get(field) or "").strip()]
    if missing:
        return ToolResult(
            f"A frame needs {' and '.join(missing)}. Nothing was written.",
            None,
            source,
            "Refused",
        )

    # Looked up before anything is written (Madde 152). These misses used to surface when
    # build_prompts ran, a call or two later, with the frame already on disk and the model moved on.
    unknown = _unknown_names(structure, args.get("characters"))
    if unknown:
        return ToolResult(f"{unknown} Nothing was written.", None, source, "Refused")

    frames.append({field: args[field] for field in _FRAME_FIELDS if field in args})
    # Indented for the person who opens this file and fixes it by hand, and ensure_ascii off so
    # their own language survives the round trip -- their work is the first principle.
    file_store.write(project_id, source, json.dumps(structure, indent=2, ensure_ascii=False))
    # How many the file holds now: appending is not idempotent, and this is what keeps a doubled
    # call in front of the model rather than in a read it would have to make. How many went in is no
    # longer a question -- one call is one frame.
    return ToolResult(
        f"Added a frame to {source}; it holds {len(frames)} now.",
        None,
        source,
        "1 frame",
    )


def _unknown_names(structure, characters):
    """The first name in this frame that no map knows, said the way build_prompts says it.

    Its own function so the walk over a name-to-outfits map lives in one place, and empty when
    everything checks out -- a frame with nobody in it has nothing to look up.
    """
    if not isinstance(characters, dict):
        return ""
    known_people = structure.get("characters") or {}
    known_outfits = structure.get("outfits") or {}
    for person, worn in characters.items():
        for name, known, field in [(person, known_people, "characters")] + [
            (outfit, known_outfits, "outfits") for outfit in (worn or [])
        ]:
            if name not in known:
                # Only this map's names: place names are no help to someone looking for a character.
                # _looked_up's rule, and the same sentence, so the model reads one vocabulary.
                return (
                    f"{name} is not in {field}; "
                    f"known: {', '.join(sorted(known)) or 'nothing'}."
                )
    return ""


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
