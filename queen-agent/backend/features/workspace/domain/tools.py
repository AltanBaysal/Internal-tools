"""The tools QueenAgent can reach for, and the rules around them.

The rules live here rather than in data/ because what a file may be called is a product decision,
not a detail of how a directory works.
"""
import json
import re
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from backend.features.workspace.domain.build_prompts import (
    _worn,
    build_character_prompts,
    build_prompts,
    character_prompts_name,
    prompts_name,
    render_module,
)
from backend.features.workspace.domain.errors import BadStructure

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
# `spent` is what the tool itself paid, and it is None for every tool but one. Madde 155 gave a tool
# the ability to ask the model on its own, dozens of times in a call: without a way home, that
# spending would happen where the turn's total cannot see it.
ToolResult = namedtuple(
    "ToolResult", "text created target outcome spent", defaults=("", "", None)
)


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

# What update_frame will change (Madde 158). The four above plus the scene, which never reaches a
# prompt but is a field of the frame and gets corrected like any other -- a separate update_scene
# would be a fifth tool teaching nothing the fourth did not. Kept apart from _FRAME_FIELDS rather
# than folded in: that tuple is what the sub-model's answer is filtered against, and a scene has no
# business arriving from there.
_UPDATABLE = _FRAME_FIELDS + ("scene",)

# Which tools can bring a file into being. The chat draws a card for each, so an edit is not in
# here: the file was already there. write_plan is, because the first plan of a name is new.
WRITES_FILES = {
    "create_file",
    "build_prompts",
    "build_character_prompts",
    "write_plan",
    "create_structure",
}

# How many frames one call will write, and how many requests fly at once (Madde 155).
#
# The cap is there because a run is meant to be repeatable rather than complete: the tool fills what
# is empty, so a file with more than this is finished by calling again. Five at once because a
# provider answers a full pool with a 429 and this app does not retry -- a dropped request is a
# dropped frame, and going fast is not worth losing one.
AT_MOST = 100
AT_ONCE = 5

# The rules an SDXL prompt value is written by, and the whole of what is left of the schema
# (Madde 159). Named for what it is: the first name, CRAFT, said nothing to whoever met it cold.
#
# read_prompt_structure_schema handed back two halves. The half describing the file's shape died as
# the tools took the shape over: create_file cannot write one, the set_ and remove_ and update_
# tools build it, and read_file shows the result -- so the model was studying a JSON example of a
# form it is no longer allowed to type. Nothing about the shape belongs here, or the dead half comes
# back in a text that rides in every request.
#
# One text rather than a paragraph per tool (user decision, 3 Sep). set_character sees the frame's
# rules too; harmless, and being one source it cannot go stale against itself.
#
# Not in the system prompt, where every chat would carry it including the ones writing no prompts --
# Madde 94 pruned the skill texts for exactly that. Its cost is paid all the same, because a tool's
# description travels every turn as well: four copies is roughly 700-900 tokens on every request.
# What is bought is where the attention falls -- the rule sits beside the parameter it governs and
# is read while the tool is being chosen, rather than at the top of a long context -- and a round,
# since nothing is fetched.
SDXL_PROMPT_RULES = (
    "Every value here is read by an SDXL-family image model, which reads tags rather than "
    "sentences: short comma-separated fragments, no articles -- sitting on couch, by window. One "
    "prompt is one frozen instant, so nothing that needs time to be seen belongs in it: a movement "
    "is written as the pose it passes through, and a cause or a moment outside the frame is "
    "written as what it looks like -- turned away, downcast eyes, tense shoulders -- or left out. "
    "An action holds only what the camera sees: the pose, the expression, where the eyes look. A "
    "camera is two decisions -- how much of the body is in the picture (close-up, upper body, "
    "medium shot, full body) and where it is looked at from (from side, from above, from behind, "
    "looking at viewer) -- and both halves come from those lists. No or in any value: the model "
    "draws one picture and cannot toss a coin. No quality tags: code writes those, and yours would "
    "be printed twice. A count of people belongs in a character's own tags and nowhere else, "
    "because that is the one place it lands beside the person it counts. Whoever a frame names "
    "first opens its prompt, so "
    "write whoever the frame is about first. Everything is English -- the one exception is a "
    "frame's scene, which stays in the user's own language and never reaches a prompt."
)

# What the model writing a frame's prompt is told, and the whole of what it is told (Madde 155).
#
# Its own text rather than the app's system prompt, which describes a chat assistant with a project
# and tools -- everything this call is not. Nothing here about neighbouring frames either: the
# request cannot see them, and asking for something it has no way to know would be a rule written
# to be broken.
#
# Built on SDXL_PROMPT_RULES since Madde 159. It carried its own copy of the rules while the schema
# still stood, and two copies is two texts able to tell one model something the other was never
# told.
WRITE_FRAME_SYSTEM_PROMPT = (
    "You write prompts for an SDXL-family image model. You are given one scene in the user's own "
    "language and the maps of a scenario -- its characters, outfits and locations -- and you "
    "answer with the fields of one frame.\n"
    "\n"
    "The scene briefs the frame and is never text to copy into it: what the picture shows is "
    "yours to decide, and a sentence retold as the action is a caption rather than a prompt.\n"
    "\n"
    "Answer with JSON and nothing else: characters, location, action, camera. characters maps a "
    "character's name to the list of outfits they wear; whoever the frame is about goes first. "
    "location is one name. Every name you use must be one of the names you were given -- you "
    "choose from the maps, you never describe a person or a place in your own words, and you never "
    "invent a name.\n"
    "\n" + SDXL_PROMPT_RULES
)

TOOL_SPECS = [
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
            "name": "add_scene",
            "description": (
                "Open frames in a structure file, one per sentence, each carrying nothing but the "
                "beat it is for. Write the sentences in the user's own language: they are the "
                "brief, never the prompt, and no image model reads them. What the picture holds is "
                "not decided here -- write_frame_prompt fills these in afterwards, one request per "
                "frame. Give them all in one call, in the order they happen; the answer says which "
                "numbers they got, and those are how you name a frame from then on."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "scenes": {
                        "type": "array",
                        "description": (
                            "One sentence per scene, in order. What happens and who it is about -- "
                            "a brief for whoever writes the frame, not tags."
                        ),
                        "items": {"type": "string"},
                    },
                },
                "required": ["file", "scenes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_structure",
            "description": (
                "Start a new structure file: the one JSON per scenario that prompts are built "
                "from. It comes out empty -- no characters, no outfits, no locations, no frames -- "
                "and is filled with set_character, set_outfit, set_location and add_scene. Reach "
                "for it once per scenario, before anything else; a name that is already taken is "
                "refused rather than written over."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "What the scenario is called, as in bar-scene.",
                    },
                },
                "required": ["file"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_character",
            "description": (
                "Write a character into a structure file: who they are, in tags. This is what "
                "stays the same about them in every frame -- face, hair, build, age. Clothing never "
                "goes here, because clothing is what changes from frame to frame: that belongs in "
                "set_outfit, and a frame names the two together. "
                "A name that is already there is updated rather than added twice, and the answer "
                "says how many frames the change reached. On a character who is already there, send "
                "only what you are changing -- anything you leave out stays as it is; a new one "
                "needs tags.\n\n" + SDXL_PROMPT_RULES
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "name": {
                        "type": "string",
                        "description": (
                            "What the frames will call this character, as in aylin. Short and "
                            "lower case; it is a key, not something the picture shows."
                        ),
                    },
                    "tags": {
                        "type": "string",
                        "description": (
                            "Who they are, as short comma-separated fragments, opening with what "
                            "this one person counts as: 1girl, woman in her mid 20s, long teal "
                            "hair, green eyes. Always 1 -- one entry is one person, and a frame "
                            "holding several of them shows each one's tags in turn. No sentence "
                            "and no clothing."
                        ),
                    },
                    "new_name": {
                        "type": "string",
                        "description": (
                            "Only to rename: the character keeps everything it has and every frame "
                            "naming it is rewritten to the new name. Refused if the new name is "
                            "taken. Leave this out unless the name itself is changing."
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
            "name": "set_outfit",
            "description": (
                "Write an outfit into a structure file. An outfit is named after the garment "
                "rather than whoever wears it -- two characters can wear the same one -- and each "
                "entry dresses one person: the text is copied whole to whoever names it, so one "
                "entry trying to cover two people puts the man in the dress and the woman in the "
                "trousers. Two people dressed differently are two entries. A name that is already "
                "there is updated rather than added twice, and on one that is there you send only "
                "what you are changing.\n\n" + SDXL_PROMPT_RULES
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "name": {
                        "type": "string",
                        "description": (
                            "What the frames will call this outfit, after the garment: denim-jacket "
                            "rather than aylins-clothes."
                        ),
                    },
                    "tags": {
                        "type": "string",
                        "description": (
                            "The clothes, as short comma-separated fragments: denim jacket, white "
                            "t-shirt. Required for an outfit that does not exist yet."
                        ),
                    },
                    "new_name": {
                        "type": "string",
                        "description": (
                            "Only to rename: the outfit keeps its text and every frame wearing it "
                            "is rewritten to the new name. Refused if the new name is taken."
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
            "name": "set_location",
            "description": (
                "Write a place into a structure file. A frame names one of these and never "
                "describes a place in its own words, so that the same room reads the same in every "
                "frame it appears in. A name that is already there is updated rather than added "
                "twice, and on one that is there you send only what you are changing.\n\n"
                + SDXL_PROMPT_RULES
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "name": {
                        "type": "string",
                        "description": "What the frames will call this place, as in bedroom.",
                    },
                    "tags": {
                        "type": "string",
                        "description": (
                            "The place, as short comma-separated fragments, with its light: sunlit "
                            "bedroom, morning light, indoors. Required for a place that does not "
                            "exist yet."
                        ),
                    },
                    "new_name": {
                        "type": "string",
                        "description": (
                            "Only to rename: the place keeps its text and every frame happening "
                            "there is rewritten to the new name. Refused if the new name is taken."
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
                "Take a character out of a structure file. Refused while any frame still names "
                "them, and the answer says which frames those are -- change or remove those frames "
                "first. Refused too if there is no character by that name, so a removal that "
                "answers is a removal that happened."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "name": {"type": "string", "description": "Which character to remove."},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_outfit",
            "description": (
                "Take an outfit out of a structure file. Refused while any frame still has someone "
                "wearing it, and the answer says which frames those are. Refused too if there is no "
                "outfit by that name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "name": {"type": "string", "description": "Which outfit to remove."},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_location",
            "description": (
                "Take a place out of a structure file. Refused while any frame still happens there, "
                "and the answer says which frames those are. Refused too if there is no place by "
                "that name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "name": {"type": "string", "description": "Which place to remove."},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_frame",
            "description": (
                "Take one frame out of a structure file, by its number. Every frame after it moves "
                "up, so the numbers you were told before this call are no longer the numbers -- the "
                "answer says how many are left, and any frame you name after this is named from "
                "that. Removes the frame whether or not its prompt is written."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "frame": {
                        "type": "integer",
                        "description": "Which frame to remove, as the number it carries.",
                    },
                },
                "required": ["file", "frame"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_frame",
            "description": (
                "Change a frame that is already written. Send only the fields you are changing -- "
                "every field you leave out stays exactly as it is. Its scene is corrected here too. "
                "A frame whose prompt has never been written is refused: write_frame_prompt writes "
                "that one from its scene. Reach for this when the user wants one frame different, "
                "rather than rebuilding anything.\n\n" + SDXL_PROMPT_RULES
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "frame": {
                        "type": "integer",
                        "description": "Which frame to change, as the number it carries.",
                    },
                    "scene": {
                        "type": "string",
                        "description": (
                            "What this frame is about, in the user's own language. It briefs the "
                            "frame and never goes into the prompt."
                        ),
                    },
                    "characters": {
                        "type": "object",
                        "description": (
                            "Who is in the frame: each character's name mapped to the list of "
                            "outfits they wear in it, empty for someone wearing none. Whoever the "
                            "frame is about goes first -- they open the prompt. Every name must "
                            "already be in the file's maps."
                        ),
                        "additionalProperties": {"type": "array", "items": {"type": "string"}},
                    },
                    "location": {
                        "type": "string",
                        "description": "Where it happens, as a name the file's locations knows.",
                    },
                    "action": {
                        "type": "string",
                        "description": (
                            "What the camera sees, as short comma-separated fragments: the pose, "
                            "the expression, where the eyes look. One frozen instant, so a "
                            "movement is written as the pose it passes through."
                        ),
                    },
                    "camera": {
                        "type": "string",
                        "description": (
                            "Two decisions: how much of the body is in the picture -- close-up, "
                            "upper body, medium shot, full body -- and where it is looked at from "
                            "-- from side, from above, from behind, looking at viewer."
                        ),
                    },
                },
                "required": ["file", "frame"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_frame_prompt",
            "description": (
                "Write the prompt of every frame that has a scene and no prompt yet. Each frame "
                "gets a request of its own, carrying that scene and the file's maps and nothing "
                "else, so a long scenario costs no more attention per frame than a short one. It "
                "takes no fields from you: what goes into a frame is worked out from its scene. "
                "Frames that are already written are left alone, so calling it again after adding "
                "scenes -- or after some frames came back empty -- picks up exactly what is left. "
                "The answer says how many were written and how many were not."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                },
                "required": ["file"],
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


def structure_name(name):
    """A structure file ends in .json, whatever the model called it (Madde 154).

    plan_name's shape and plan_name's reason. safe_name gives an extensionless name .md, and a
    structure file called bar-scene.md would be refused by every tool that owns its shape -- born
    outside the door built for it.
    """
    return f"{name.rsplit('.', 1)[0]}.json"


def run_tool(file_store, project_id, name, arguments, engine=None, model=""):
    """Run one call and answer the model in words. A miss is an answer, not a crash.

    `engine` and `model` are optional because one tool out of a dozen asks the model something of
    its own (Madde 155); everything else works with a store and a name. A caller that hands neither
    gets a refusal from that tool rather than a crash from every other one.
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

    if name == "create_structure":
        return _create_structure(file_store, project_id, args)

    if name == "set_character":
        return _set_entry(file_store, project_id, args, "characters")

    if name == "set_outfit":
        return _set_entry(file_store, project_id, args, "outfits")

    if name == "set_location":
        return _set_entry(file_store, project_id, args, "locations")

    if name == "remove_character":
        return _remove_entry(file_store, project_id, args, "characters")

    if name == "remove_outfit":
        return _remove_entry(file_store, project_id, args, "outfits")

    if name == "remove_location":
        return _remove_entry(file_store, project_id, args, "locations")

    if name == "remove_frame":
        return _remove_frame(file_store, project_id, args)

    if name == "update_frame":
        return _update_frame(file_store, project_id, args)

    if name == "add_scene":
        return _add_scene(file_store, project_id, args)

    if name == "write_frame_prompt":
        return _write_frame_prompt(file_store, project_id, args, engine, model)

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


def _opened(file_store, project_id, args):
    """The file, parsed, with its frames list -- or the answer saying why not (Madde 155).

    Four tools begin the same four lines. Written once so they cannot start disagreeing about what
    a missing file or a broken one is called.
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
        # The parser's own sentence, as in _build: a guessed cause sends the model somewhere else.
        return source, None, ToolResult(
            f"{source} is not valid JSON: {broken}", None, source, "Not valid JSON"
        )

    # Asked of a dictionary only: a file whose top level is something else has no frames either, and
    # an AttributeError would tell the model nothing it could act on.
    frames = structure.get("frames") if isinstance(structure, dict) else None
    if not isinstance(frames, list):
        return source, None, ToolResult(
            f"{source} has no frames list to add to; a structure file carries one.",
            None,
            source,
            "Refused",
        )
    return source, structure, None


def _add_scene(file_store, project_id, args):
    """Frames opened from their sentences, carrying nothing else yet (Madde 155).

    The scenes used to be a second file, matched to the frames by position -- and a paragraph of
    instruction held that pairing together, with nothing able to see it slip. A sentence written
    into the frame it belongs to has nothing left to match.

    A plain list of strings, so the model builds no shape here either. Several at once because the
    order the beats happen in is one thought, and asking for it a call at a time would spend the
    turn's rounds on typing.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    coming = args.get("scenes")
    if not isinstance(coming, list):
        return ToolResult(
            "add_scene takes a list of sentences, even when there is one of them.",
            None,
            source,
            "Refused",
        )
    if not coming:
        return ToolResult("No scenes were given; nothing to open.", None, source, "Refused")
    # All or nothing, as everywhere else in this module. Opening the ones that read as sentences
    # would leave a file holding some of what was asked for and no way to tell which.
    if any(not isinstance(scene, str) or not scene.strip() for scene in coming):
        return ToolResult(
            "Every scene is a sentence. Nothing was written.", None, source, "Refused"
        )

    frames = structure["frames"]
    was = len(frames)
    frames.extend({"scene": scene} for scene in coming)
    _renumber(frames)
    file_store.write(project_id, source, json.dumps(structure, indent=2, ensure_ascii=False))
    # The numbers, because from here on that is how the model names a frame -- and this answer is
    # where it learns them.
    span = f"frame {was + 1}" if len(coming) == 1 else f"frames {was + 1}-{len(frames)}"
    return ToolResult(
        f"Added {counted(len(coming), 'scene')} to {source} as {span}.",
        None,
        source,
        counted(len(coming), "scene"),
    )


def _write_frame_prompt(file_store, project_id, args, engine, model):
    """Every empty frame filled from a request of its own (Madde 155).

    Not one request for the file. Sixteen rounds in the main chat could never have carried forty
    frames, and each of those rounds would have re-sent the whole conversation to write one -- so
    the attention spent per frame fell as the scenario grew. Here each frame is a small question
    with the same shape: this scene, these maps, nothing else.

    Nothing is retried. A frame whose request fell over, or whose answer would not parse, or which
    named something no map knows, is left empty and counted -- and since the tool only fills what is
    empty, calling it again is the retry.
    """
    if engine is None:
        return ToolResult(
            "write_frame_prompt cannot run without a model to ask.", None, "", "Refused"
        )

    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    frames = structure["frames"]
    # A scene to write from and nothing written yet. Both halves matter: a frame with no brief would
    # have the model inventing one, and a frame already written is somebody's work.
    waiting = [
        frame
        for frame in frames
        if str(frame.get("scene") or "").strip() and not _is_written(frame)
    ]
    if not waiting:
        return ToolResult(f"Every frame in {source} is written.", None, source, "Nothing to write")

    left = max(0, len(waiting) - AT_MOST)
    waiting = waiting[:AT_MOST]
    # The invariant half first, the scene last: the provider's prefix cache can only hit on what
    # every request shares, and it shares everything but the final line.
    maps = json.dumps(
        {which: structure.get(which) or {} for which in ("characters", "outfits", "locations")},
        indent=2,
        ensure_ascii=False,
    )

    def _written(frame):
        try:
            answer = engine.write_once(
                WRITE_FRAME_SYSTEM_PROMPT, f"{maps}\n\nScene: {frame['scene']}", model
            )
            fields = json.loads(answer.get("text") or "")
        except Exception:
            # Whatever went wrong -- the connection, the service, an answer that is not JSON -- the
            # frame stays empty and the ones around it are not punished for it. What the model needs
            # is the count, and it is in the report.
            return None, None
        if not isinstance(fields, dict) or _unknown_names(structure, fields.get("characters")):
            return None, None
        return {field: fields[field] for field in _FRAME_FIELDS if field in fields}, answer.get(
            "usage"
        )

    # The first alone, then the rest in waves. Alone because instruction and maps are identical in
    # every request, and if they all left together none would find that prefix warm.
    done = [_written(waiting[0])]
    if len(waiting) > 1:
        with ThreadPoolExecutor(max_workers=AT_ONCE) as pool:
            done.extend(pool.map(_written, waiting[1:]))

    spent, wrote = {}, 0
    for frame, (fields, usage) in zip(waiting, done):
        # Written by frame rather than in the order the answers came back: which request finished
        # first is not something the file should be able to show.
        if fields is not None:
            frame.update(fields)
            wrote += 1
        for what, much in (usage or {}).items():
            spent[what] = spent.get(what, 0) + much

    file_store.write(project_id, source, json.dumps(structure, indent=2, ensure_ascii=False))
    said = f"Wrote {counted(wrote, 'frame')} in {source}."
    if wrote < len(waiting):
        said += f" {counted(len(waiting) - wrote, 'frame')} left empty; call again to try them."
    if left:
        said += f" {counted(left, 'frame')} still waiting past this call's limit."
    return ToolResult(said, None, source, counted(wrote, "frame"), spent or None)


def _create_structure(file_store, project_id, args):
    """The empty skeleton, and nothing else in it (Madde 154).

    What create_file did for this kind of file until Madde 151 shut it. Empty rather than seeded
    with an example: a file born with a character in it would be a file the model did not write, and
    the first thing it would do is wonder whether to keep it.
    """
    wanted = structure_name(safe_name(args.get("file")))
    if wanted in file_store.list_names(project_id):
        # The sentence is the instruction. Writing over it would delete a scenario the user built,
        # and say nothing about having done so.
        return ToolResult(
            f"There is already a file called {wanted}. Open it and add to it, or pick another "
            "name for a new scenario.",
            None,
            wanted,
            "Already there",
        )
    empty = {"characters": {}, "outfits": {}, "locations": {}, "frames": []}
    written = file_store.write(
        project_id, wanted, json.dumps(empty, indent=2, ensure_ascii=False)
    )
    return ToolResult(f"Started {written}.", written, written, "Started")


def _set_entry(file_store, project_id, args, which):
    """One name's text in one map, and since Madde 161 the name itself.

    Split in front of the model and joined behind it, on purpose. What differs between a character,
    an outfit and a place is what the model has to be told -- three names, three descriptions, three
    rules it meets while doing the thing each rule is about. What they do is the same sentence, and
    three copies of it would be three copies to keep in step.

    Renaming lives here rather than in a rename_ tool of its own for the reason remove_entry was
    refused: putting several actions behind one tool is for actions on one resource, and a rename is
    an action on the entry itself. It opens through _opened now, because rewriting the frames that
    name the old key means the frames list is a real requirement -- _remove_entry moved for the same
    reason in Madde 157.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    key = str(args.get("name") or "").strip()
    if not key:
        return ToolResult(f"A {which[:-1]} needs a name.", None, source, "Refused")

    # `in` rather than .get(), because an empty string is a value: it is the only way the model can
    # clear a text it wrote before, and .get() would read that as nothing having been given.
    tags = args["tags"] if args.get("tags") is not None else None
    moving = args.get("new_name")

    entries = structure.setdefault(which, {})
    if key not in entries:
        if moving is not None:
            # A call carrying new_name means to move something, and the something is not here.
            # Creating a fresh entry under either name would answer a question nobody asked.
            return ToolResult(
                f"{key} is not in {which}; known: {', '.join(sorted(entries)) or 'nothing'}. "
                "Nothing was renamed.",
                None,
                source,
                "Not there",
            )
        # Required on a name that does not exist, optional on one that does: an entry with no text
        # is a name the prompts would build nothing out of. One rule for the three maps since Madde
        # 163 -- a character has no second field left to be missing.
        if tags is None:
            return ToolResult(f"A new {which[:-1]} needs tags.", None, source, "Refused")

    if key in entries and tags is None and moving is None:
        # Silent success is a model believing it changed something. The same refusal update_frame
        # and the remove_ tools give when a call asks for nothing.
        return ToolResult(
            f"Nothing was given to change about {key}.", None, source, "Nothing to change"
        )

    # Every refusal about the new name lands before anything is written, as everywhere else here.
    if moving is not None:
        moving = str(moving).strip()
        if not moving:
            return ToolResult(f"A {which[:-1]} needs a name.", None, source, "Refused")
        if moving == key:
            return ToolResult(
                f"{key} is already called that.", None, source, "Nothing to change"
            )
        if moving in entries:
            # Two entries collapsing into one hands every frame naming either the same text, and
            # whichever lost is gone without a word.
            return ToolResult(
                f"There is already a {which[:-1]} called {moving}.", None, source, "Already there"
            )

    # Given changes, left out stands -- update_frame's rule, so four tools teach one. A name that is
    # not there yet cannot reach here without tags, so there is no third case to write.
    stood = key in entries
    if tags is not None:
        entries[key] = tags

    followed = _renamed(structure, which, key, moving) if moving else 0
    file_store.write(project_id, source, json.dumps(structure, indent=2, ensure_ascii=False))

    if not stood:
        return ToolResult(f"Added {key} to {which}.", None, source, "Added")
    if moving:
        # What else moved with it, because a call can carry both and the answer is where the model
        # reads what it just did.
        also = " and changed its text" if tags is not None else ""
        return ToolResult(
            f"Renamed {key} to {moving} in {which}{also}; "
            f"{counted(followed, 'frame')} followed.",
            None,
            source,
            "Renamed",
        )
    # How far the change reached, which is the whole reason the maps exist: the text sits in one
    # place and every frame naming it moves at once. Said only when something changed -- a name
    # nobody uses yet would answer a question that was not asked.
    return ToolResult(
        f"Changed {key} in {which}; "
        f"{counted(len(_frames_naming(structure, which, key)), 'frame')} name it.",
        None,
        source,
        "Changed",
    )


def _renamed(structure, which, old, new):
    """The key changes name where it stands, and every frame that named it follows. How many, is
    the answer.

    Rebuilt rather than popped and re-added. Python keeps a key where it was first written, so
    `entries[new] = entries.pop(old)` sends the new name to the end -- whichever place it held. The
    rule here is that a rename changes a name and nothing else: whoever was third is third
    afterwards, in the map and in every frame. _renumber rebuilds for the same reason, and it is the
    same reason: a position that carries meaning cannot be moved by assignment.

    In a frame that meaning is who opens the prompt (build_prompts reads the first name), and in a
    character's outfit list it is the order the clothes are written in. The map at the top of the
    file is read by nobody in order -- it is kept for the person who opens the file.

    Counted while walking rather than by _frames_naming afterwards, because afterwards the old name
    is gone and there is nothing left to count.
    """
    entries = structure[which]
    structure[which] = {(new if name == old else name): value for name, value in entries.items()}

    followed = 0
    for frame in structure.get("frames") or []:
        if which == "locations":
            if frame.get("location") == old:
                frame["location"] = new
                followed += 1
            continue

        people = frame.get("characters")
        if which == "characters":
            if isinstance(people, dict) and old in people:
                # The same rebuild, and here every position carries something: the first name opens
                # the prompt and the rest follow the camera in the order they stand.
                frame["characters"] = {
                    (new if name == old else name): worn for name, worn in people.items()
                }
                followed += 1
            elif isinstance(people, list) and old in people:
                frame["characters"] = [new if name == old else name for name in people]
                followed += 1
            continue

        if not isinstance(people, dict):
            continue
        wearing = False
        for name, worn in people.items():
            if isinstance(worn, list) and old in worn:
                # In place, because the order of the list is the order the clothes are written in.
                people[name] = [new if outfit == old else outfit for outfit in worn]
                wearing = True
            elif worn == old:
                # The slip _worn forgives -- one name written without its list -- kept in the shape
                # it was written in.
                people[name] = new
                wearing = True
        followed += wearing

    return followed


def _remove_entry(file_store, project_id, args, which):
    """One name out of one map, if nothing is standing on it (Madde 157).

    _set_entry's opposite, and it opens through _opened where that one reads the file itself: setting
    a name works without ever looking at a frame, removing one cannot -- whether the name is still
    used is the whole question, and the answer is in the frames.

    Not a set_ with the value left out. An empty value meaning delete would let a model that simply
    failed to fill a field wipe the entry in silence, and nothing here can be undone by calling it
    again.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    key = str(args.get("name") or "").strip()
    if not key:
        return ToolResult(f"A {which[:-1]} needs a name.", None, source, "Refused")

    entries = structure.get(which) or {}
    if key not in entries:
        # No silent success. A model told nothing happened will move on believing it did, and the
        # thing it meant to remove is still there in the prompts. _looked_up's own sentence, so a
        # name that is not there reads the same wherever it is met.
        return ToolResult(
            f"{key} is not in {which}; known: {', '.join(sorted(entries)) or 'nothing'}.",
            None,
            source,
            "Not there",
        )

    used = _frames_naming(structure, which, key)
    if used:
        # Rule 5 of the fourteen, and now an answer at the moment it is about something. The numbers
        # are the useful half: what the model does next is fix those frames.
        return ToolResult(
            f"{key} {_STILL[which]} {', '.join(str(place) for place in used)}. Nothing was removed.",
            None,
            source,
            "Still in use",
        )

    del entries[key]
    file_store.write(project_id, source, json.dumps(structure, indent=2, ensure_ascii=False))
    return ToolResult(f"Removed {key} from {which}.", None, source, "Removed")


def _remove_frame(file_store, project_id, args):
    """One frame out of the list, and the ones after it move up (Madde 157).

    No guard on a frame that is already written. Removing one is not an accident to catch, it is the
    ordinary thing to do with a beat that left the scenario, and the number in the call says which.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    frames = structure["frames"]
    number, refused = _the_frame(source, frames, args)
    if refused is not None:
        return refused

    del frames[number - 1]
    _renumber(frames)
    file_store.write(project_id, source, json.dumps(structure, indent=2, ensure_ascii=False))
    # What is left, because the model names a frame by its number in the next breath and this is the
    # only place it can learn that everything past the gap has moved.
    left = (
        "no frames left" if not frames else f"{counted(len(frames), 'frame')} left, renumbered from 1"
    )
    return ToolResult(
        f"Removed frame {number} from {source}; {left}.", None, source, "Removed"
    )


def _update_frame(file_store, project_id, args):
    """The fields a call names, changed; the ones it does not, left alone (Madde 158).

    The last of the holes Madde 151 opened. Since edit_file was shut on a structure file a written
    frame could be removed but not corrected, and rebuilding a scenario around a camera angle is not
    a correction.

    Apart from write_frame_prompt rather than one tool deciding which it is: this way the intent is
    in the call rather than in whatever the tool finds when it arrives, and nothing is written over
    by accident.
    """
    source, structure, refused = _opened(file_store, project_id, args)
    if refused is not None:
        return refused

    # Before the frame is even looked at (Madde 152's rule). Writing the fields that parsed and
    # dropping the rest would leave the model believing it wrote a frame that does not exist, and
    # half a frame is a thing nobody asked for.
    strangers = sorted(set(args) - {"file", "frame"} - set(_UPDATABLE))
    if strangers:
        return ToolResult(
            f"A frame has no {', '.join(strangers)}. It takes {', '.join(_UPDATABLE)}. "
            "Nothing was changed.",
            None,
            source,
            "Refused",
        )

    frames = structure["frames"]
    number, refused = _the_frame(source, frames, args)
    if refused is not None:
        return refused

    frame = frames[number - 1]
    if not _is_written(frame):
        # The same measure write_frame_prompt gathers by, read from the same function: a frame that
        # tool would pick up is exactly the frame this one refuses, and two readings of "written"
        # would leave one frame in two states depending on which tool asked.
        return ToolResult(
            f"Frame {number} has no prompt yet; write_frame_prompt writes it from its scene.",
            None,
            source,
            "Not written yet",
        )

    changing = {field: args[field] for field in _UPDATABLE if field in args}
    if not changing:
        return ToolResult(
            f"Nothing was given to change in frame {number}.", None, source, "Nothing to change"
        )

    if "characters" in changing:
        unknown = _unknown_names(structure, changing["characters"])
        if unknown:
            return ToolResult(f"{unknown} Nothing was changed.", None, source, "Refused")

    frame.update(changing)
    file_store.write(project_id, source, json.dumps(structure, indent=2, ensure_ascii=False))
    # Which fields moved, because the model's next sentence is about what it just did and this is
    # where it reads it.
    return ToolResult(
        f"Updated frame {number} of {source}: {', '.join(changing)}.", None, source, "Updated"
    )


def _the_frame(source, frames, args):
    """The number a call names, or the answer saying there is no such frame.

    Shared by remove_frame and update_frame since Madde 158, so the one comparison guarding both ends
    lives in one place. Both ends in one line is what keeps frames[-1] from ever being reached: a
    negative number is legal Python, and it would quietly take the last frame -- or rewrite it.
    """
    number = _a_number(args.get("frame"))
    if number is None:
        return None, ToolResult(
            "frame is the number of the frame, as in 3.", None, source, "Refused"
        )
    if not 1 <= number <= len(frames):
        return number, ToolResult(
            f"{source} has no frames." if not frames
            else f"{source} has {counted(len(frames), 'frame')}; there is no frame {number}.",
            None,
            source,
            "No such frame",
        )
    return number, None


def _is_written(frame):
    """Whether this frame's prompt has been written.

    One reading for both tools that care: write_frame_prompt gathers the frames this says no to, and
    update_frame refuses them. The action is the measure because it is the field a frame cannot be
    without -- a prompt with a place and a camera and nothing happening is not a frame.
    """
    return bool(str(frame.get("action") or "").strip())


def _a_number(given):
    """A frame number, or None for anything that is not one.

    A string of digits counts: models send 2 as "2" often enough that refusing it would be a refusal
    about typing rather than about the file, and there is only one way to read it. A bool does not,
    even though it is an int in Python -- True would take frame 1 away. A float does not either:
    int(1.5) is 1, which is the quietest way there is to lose somebody's work.
    """
    if isinstance(given, bool):
        return None
    if isinstance(given, int):
        return given
    if isinstance(given, str) and given.strip().lstrip("-").isdigit():
        return int(given)
    return None


# How a frame reaches each map, said as the middle of one sentence rather than as three sentences.
# A character is in a frame, an outfit is worn in one, a place is where one happens -- three
# relationships, and one verb for all of them would read as though they were the same thing.
_STILL = {
    "characters": "is still in frames",
    "outfits": "is still worn in frames",
    "locations": "is still the place in frames",
}


def _frames_naming(structure, which, key):
    """Which frames reach for this entry, by number. Empty is an answer: a name never used.

    The numbers rather than a count since Madde 157, because a removal is refused by naming them and
    two walks over the same question would be two answers able to disagree. They come from the place
    in the list rather than from the frame's own stamp: Madde 153 keeps the two equal and the list is
    the one of them nothing can edit by hand.
    """
    reached = []
    for place, frame in enumerate(structure.get("frames") or [], start=1):
        if which == "locations":
            if frame.get("location") == key:
                reached.append(place)
            continue
        for person, worn in _worn(frame.get("characters")):
            if (person == key) if which == "characters" else (key in worn):
                reached.append(place)
                break
    return reached


def _renumber(frames):
    """Press each frame's place in the list onto it, in front of everything else (Madde 153).

    A stamp rather than an identity, and every write presses all of them again. That is what keeps
    the number equal to the position: a removal moves everything below up rather than leaving a hole
    for the model to read meaning into. It is what lets the user say "frame 15" and the tools find
    it without quoting text back.

    Rebuilt rather than assigned into, because a dict keeps a key where it was first written: on a
    frame that already carries one, `frame = n` would update the number and leave it wherever it
    sat. Being the first line is half of what this is for -- whoever opens the file should not have
    to read into a frame to see which one it is.
    """
    for place, frame in enumerate(frames, start=1):
        ordered = {"frame": place}
        ordered.update((key, value) for key, value in frame.items() if key != "frame")
        frames[place - 1] = ordered


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
