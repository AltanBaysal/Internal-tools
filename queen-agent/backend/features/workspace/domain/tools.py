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

# Which tools can bring a file into being. The chat draws a card for each, so an edit is not in
# here: the file was already there. write_plan is, because the first plan of a name is new.
WRITES_FILES = {
    "create_file",
    "start_scenario",
    "build_prompts",
    "build_character_prompts",
    "write_plan",
}

# The rules a map entry's tags are written by, and the whole of what is left of the schema
# (Madde 172). Named for what it is: the reader is an SDXL-family image model, and these are the
# rules its prompts hold.
#
# read_prompt_structure_schema handed back two halves. The half describing the file's shape died as
# the tools took the shape over: start_scenario opens the file, the add_ and update_ and remove_
# tools build it, and create_file cannot touch it -- so the model was studying a JSON example of a
# form it is no longer allowed to type. Nothing about the shape belongs here, or the dead half comes
# back in a text that rides in every request.
#
# The other half split again, by author. What goes into a map entry is Queen's and is written here;
# what goes into a frame's action is the prompt writer's, and lives in Madde 176's own system
# prompt. Carried here it would ride on six tools that never write an action.
#
# Not in the system prompt, where every chat would carry it including the ones writing no tags --
# Madde 94 pruned the skill texts for exactly that. Its cost is paid all the same, because a tool's
# description travels every turn as well: six copies is roughly a thousand tokens on every request.
# What is bought is where the attention falls -- the rule sits beside the parameter it governs and
# is read while the tool is being chosen -- and a round, since nothing is fetched.
SDXL_PROMPT_RULES = (
    "How to write the tags. They are read by an SDXL-family image model, so they are English, and "
    "they are short comma-separated fragments rather than a sentence: an article is not a tag, and "
    "sitting on couch, by window is the density to match.\n"
    "\n"
    "How many people a character entry draws belongs in that entry and nowhere else -- 1girl, woman "
    "in her mid 20s -- because that is the one place a count lands beside the person it counts. The "
    "word solo does not go there: the same character stands alone in one frame and beside somebody "
    "in the next, so an entry claiming it is wrong in half of them. An entry for somebody only "
    "part of the way into shot -- a pov_ one, hands and arms and no face -- carries no count at "
    "all, because there is no whole person in the picture to count.\n"
    "\n"
    "Clothes are never in a character's entry; they are an outfit of their own, named after the "
    "garment rather than after whoever wears it, because two characters can wear the same one. One "
    "entry dresses one person: its text is handed whole to whoever wears it, so one entry covering "
    "two people puts the man in the dress. A location has nobody in it and no count -- who is there "
    "is the frame's business, and a person written into a place is drawn into every frame set "
    "there.\n"
    "\n"
    "No quality tags anywhere: code writes those at the front of every prompt, and yours would be "
    "printed twice. No or inside a value -- the model draws one picture and cannot toss a coin, so "
    "pick one."
)

# What the prompt writer is told about its job (Madde 176), with the rules above appended.
#
# The other half of the schema Madde 172 split. The half about writing a tag went to the tools that
# take tags; this half is about what happens in a frame and how it is shot, and it belongs to the
# one model that writes that -- read once per request, by a model that has nothing else to do.
#
# QueenAgent's own SYSTEM_PROMPT stays out. It is a page about tools, files, chats and how to talk
# to a user, and none of it is true here: this model calls nothing, opens nothing, and is not
# talking to anybody.
WRITE_FRAME_SYSTEM_PROMPT = (
    "You write the action line of one frozen frame, for an SDXL-family image model. You are handed "
    "a scene in one sentence, who is in the frame, and where -- and you answer with the action "
    "line alone: no preamble, no explanation, no quotes around it, and nothing about having "
    "written it.\n"
    "\n"
    "The action is what is happening in this one frozen instant, and the shot it is seen through: "
    "there is no camera field, so the framing and the angle live inside your line -- close-up, "
    "from below, over the shoulder, wide shot. Neighbouring frames of one scenario should not "
    "repeat the same framing and angle, because the same framing twice is one picture twice.\n"
    "\n"
    "Do not describe anybody's looks, their clothes or the place. Those are written once in the "
    "file's own maps and the code puts them into every prompt already; written here again they "
    "would be said twice in one prompt, and the second copy is the one that contradicts the "
    "first. What you are handed them for is so your line fits what is there -- somebody in a long "
    "coat does not shrug it off in your sentence.\n"
    "\n"
    "What their body is doing in this instant is yours, though, and so is the face it does it "
    "with. Name what is visible of them rather than writing around it -- erect penis, penis "
    "penetrating vagina, mouth on penis -- because the model draws what is named and invents "
    "whatever a euphemism left out, which is how a frame comes back with a body that melts. Give "
    "the face its expression as well: a map describes a face, and nothing anywhere says what it is "
    "doing right now. Neither of these could live in a map, because the same person is calm in one "
    "frame and not in the next. What covers them is still an outfit and still not yours -- "
    "somebody wearing none in a frame is already bare without you saying so.\n"
    "\n" + SDXL_PROMPT_RULES
)

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
                "edit_file. It does not write scenarios; start_scenario opens those."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "A short file name, as in notes.md.",
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
                "Change part of a document that already exists -- a document, not a scenario: a "
                "structure file is changed by the tools that know its shape. The text you give as "
                "old must appear "
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
                "already there -- to change one that exists, use update_character.\n"
                "\n" + SDXL_PROMPT_RULES
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
                "scenario still builds afterwards. Refuses a name that is not there.\n"
                "\n" + SDXL_PROMPT_RULES
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
            "name": "add_outfit",
            "description": (
                "Write a new outfit into a scenario: a set of clothes with a name, worn by whoever "
                "a frame puts it on. Kept apart from the character because the same person wears "
                "different things across the frames, and the same clothes can be worn by more than "
                "one person. Refuses a name that is already there.\n"
                "\n" + SDXL_PROMPT_RULES
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The scenario's file name."},
                    "name": {
                        "type": "string",
                        "description": "What this outfit is called, as in nightgown.",
                    },
                    "tags": {
                        "type": "string",
                        "description": (
                            "The clothes as tags, and nothing else: white nightgown, lace trim, "
                            "bare shoulders. No person here -- no count, no body, no hair. One "
                            "entry dresses one person; two people dressed differently are two "
                            "outfits."
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
            "name": "update_outfit",
            "description": (
                "Change an outfit that is already in a scenario: its tags, its name, or both. Only "
                "what you give changes, and renaming reaches every frame wearing it. Refuses a "
                "name that is not there.\n"
                "\n" + SDXL_PROMPT_RULES
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The scenario's file name."},
                    "name": {"type": "string", "description": "Which outfit to change."},
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
            "name": "remove_outfit",
            "description": (
                "Take an outfit out of a scenario. Refused while any frame still has somebody "
                "wearing it, and the answer says which frames -- change what they wear first, or "
                "remove those frames."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The scenario's file name."},
                    "name": {"type": "string", "description": "Which outfit to remove."},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_location",
            "description": (
                "Write a new location into a scenario: a place a frame can be set in. Refuses a "
                "name that is already there.\n"
                "\n" + SDXL_PROMPT_RULES
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The scenario's file name."},
                    "name": {
                        "type": "string",
                        "description": "What this place is called, as in bedroom.",
                    },
                    "tags": {
                        "type": "string",
                        "description": (
                            "The place as tags: cozy bedroom, morning light through curtains, "
                            "indoors. Nobody is in it -- who is there is the frame's business, and "
                            "a person written here would be drawn into every frame set in it."
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
            "name": "update_location",
            "description": (
                "Change a location that is already in a scenario: its tags, its name, or both. "
                "Only what you give changes, and renaming reaches every frame set there. Refuses a "
                "name that is not there.\n"
                "\n" + SDXL_PROMPT_RULES
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The scenario's file name."},
                    "name": {"type": "string", "description": "Which location to change."},
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
            "name": "remove_location",
            "description": (
                "Take a location out of a scenario. Refused while any frame is still set there, "
                "and the answer says which frames -- a frame has one place, so give those frames "
                "another one first, or remove them."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The scenario's file name."},
                    "name": {"type": "string", "description": "Which location to remove."},
                },
                "required": ["file", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_scene",
            "description": (
                "Add scenes to a structure file, one frame each, in the order they happen. They go "
                "at the end unless before names a frame to go in front of. A frame's number is not "
                "yours to give either way -- it is simply its place in the list, and every frame "
                "after an insertion moves up. Every name a scene uses has to be in the file's maps "
                "already: a name nobody knows is refused, together with the names that are known, "
                "and the whole call is refused with it -- nothing is written unless every scene in "
                "it is good. The answer names the frames it made, which is how you say which one "
                "you mean next: a frame is born without its action, and write_frame_prompt is what "
                "writes one."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "before": {
                        "type": "integer",
                        "description": (
                            "Go in front of this frame, by its number, rather than at the end. The "
                            "frames from there on move up and keep everything they carry, their "
                            "actions included -- so this is how a scene goes into the middle of a "
                            "scenario, and taking the tail out to add it again is not. One past "
                            "the last frame is the end."
                        ),
                    },
                    "scenes": {
                        "type": "array",
                        "description": (
                            "The scenes to add. A list even when there is one of them."
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "scene": {
                                    "type": "string",
                                    "description": (
                                        "What happens, in one sentence and in the language the "
                                        "work is being done in. The brief this frame is built "
                                        "from, never the tags themselves."
                                    ),
                                },
                                "characters": {
                                    "type": "object",
                                    "description": (
                                        "Who is in the frame: each name from the file's "
                                        "characters, with the list of outfits they wear. Whoever "
                                        "is written first leads the frame's prompt. Left out for a "
                                        "frame with nobody in it."
                                    ),
                                },
                                "location": {
                                    "type": "string",
                                    "description": (
                                        "Where it happens, named as the file's locations name it. "
                                        "Left out for a frame that shows no place of its own."
                                    ),
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
            "description": (
                "Change a frame that is already in a structure file, naming it by its number. Only "
                "what you give is changed and the rest of the frame stays as it is, so a place "
                "corrected leaves the cast alone. Giving a field empty clears it -- a frame with "
                "nobody in it, or one that shows no place of its own -- except the scene, which a "
                "frame is never without. Names come from the file's maps here as they do when the "
                "frame is written. A frame's action is not among these: write_frame_prompt is what "
                "writes one, and calling it again with a note is how one is changed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "frame": {
                        "type": "integer",
                        "description": "Which frame, by its number, counting from 1.",
                    },
                    "scene": {
                        "type": "string",
                        "description": "What happens, in one sentence. Replaces the sentence there.",
                    },
                    "characters": {
                        "type": "object",
                        "description": (
                            "Who is in the frame, each name with the outfits they wear. Replaces "
                            "the whole cast rather than adding to it; empty leaves nobody in it."
                        ),
                    },
                    "location": {
                        "type": "string",
                        "description": (
                            "Where it happens, named as the file's locations name it. Empty takes "
                            "the place off the frame."
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
            "name": "remove_frame",
            "description": (
                "Take one frame out of a structure file, naming it by its number. Every frame "
                "after it moves up a place and the numbers follow, so the answer says how many are "
                "left: a number you were told before this call may not mean the same frame after "
                "it. Nothing in the maps is touched -- a character or a place left in no frame at "
                "all stays where it is, and taking it out is the user's to ask for."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "frame": {
                        "type": "integer",
                        "description": "Which frame, by its number, counting from 1.",
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
                "Write one frame's action -- what is happening in that frozen instant, and the "
                "shot it is seen through. Asked of a model kept for this and nothing else, so the "
                "sentence is not yours to write and not yours to read back: it goes straight into "
                "the frame. The frame needs its scene first, which is the brief the action is "
                "written from; who is in it and where are read from the file. Written over "
                "whatever was there, so calling this again on the same frame is how an action is "
                "changed -- with a note when there is something to fix, and the note is the whole "
                "of what the writer hears about it. One frame per call."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "The structure file's name."},
                    "frame": {
                        "type": "integer",
                        "description": "Which frame, by its number, counting from 1.",
                    },
                    "note": {
                        "type": "string",
                        "description": (
                            "What to do differently, in your own words -- what the user said about "
                            "the last one, or what this frame needs that the scene does not say. "
                            "Left out the first time."
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
    """Only what was given, and never the action (Madde 174).

    The action belongs to the prompt model, which writes it because the main model will not write
    that kind of sentence well. A field here would be the way round it, and the way round a quality
    gate is the road every gate ends up on unless it is simply not there.
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
    given = {key: args[key] for key in ("scene", "characters", "location") if key in args}
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
            WRITE_FRAME_SYSTEM_PROMPT, _frame_seen(frame, structure, args.get("note"))
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
