"""The pasted prompt list, read. Pure, and it never executes what it reads.

The text comes straight out of a notebook cell, so a leading `PROMPTS =` is stripped before
parsing and `ast.literal_eval` does the rest: it accepts literals only -- no calls, no names,
nothing executable -- so a paste can be wrong but never dangerous.

Two shapes are read (madde 397). The flat list of strings is every list written before
QueenAgent's; QueenAgent's is a record per frame -- `scene` and `photo`, each in triple quotes --
the shape its build_prompts.render_module writes.
"""
import ast
import re

_ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*\s*=\s*")

# One line, no detail. The design's rule: the box turns red and says only that the list could not
# be read -- no expected shape, no example, no line or column, no Python message. What went wrong
# is answered by looking at the text, and a long explanation under a small box was never read.
UNREADABLE = "Format hatası — liste okunamadı"
EMPTY = "Prompt listesi boş."


class InvalidPrompts(Exception):
    """The pasted text is not a usable prompt list (message is user-facing)."""


def parse_photo_list(text):
    """The photo panel's list -> [{"prompt": …}] or [{"prompt": …, "scene": …}], one per prompt.

    A record's `photo` is the prompt, and its `scene` rides with it as it was written: every frame
    the prompt opens keeps it. A flat list's entry carries no scene, so the plan line it makes is
    the line it always made.
    """
    if not text or not text.strip():
        raise InvalidPrompts(EMPTY)

    body = _ASSIGNMENT.sub("", text.strip(), count=1)
    try:
        value = ast.literal_eval(body)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        raise InvalidPrompts(UNREADABLE) from None

    # A bare string, a number, a dict, a list mixing the two shapes or holding anything else -- all
    # the same answer.
    if not isinstance(value, (list, tuple)):
        raise InvalidPrompts(UNREADABLE)
    if all(isinstance(item, str) for item in value):
        entries = [{"prompt": item.strip()} for item in value]
    elif all(isinstance(item, dict) and isinstance(item.get("scene"), str)
             and isinstance(item.get("photo"), str) for item in value):
        entries = [{"prompt": item["photo"].strip(), "scene": item["scene"]} for item in value]
    else:
        raise InvalidPrompts(UNREADABLE)

    # nova-3dcg's contract: an empty item is a deliberate "skip this line" switch, and a record with
    # no photo is the same switch.
    entries = [entry for entry in entries if entry["prompt"]]
    if not entries:
        # A list of blanks is an empty list, not a broken one.
        raise InvalidPrompts(EMPTY)
    return entries


def parse_prompts(text):
    """The flat list alone -> list[str]: what the reference pool's box reads.

    QueenAgent's list is refused here: its prompts are photo tags, and this box asks for the words a
    video is made from.
    """
    entries = parse_photo_list(text)
    if any("scene" in entry for entry in entries):
        raise InvalidPrompts(UNREADABLE)
    return [entry["prompt"] for entry in entries]
