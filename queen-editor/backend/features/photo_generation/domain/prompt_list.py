"""The pasted prompt list -> list[str]. Pure, and it never executes what it reads.

The text comes straight out of a notebook cell, so a leading `PROMPTS =` is stripped before
parsing and `ast.literal_eval` does the rest: it accepts literals only -- no calls, no names,
nothing executable -- so a paste can be wrong but never dangerous.
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


def parse_prompts(text):
    if not text or not text.strip():
        raise InvalidPrompts(EMPTY)

    body = _ASSIGNMENT.sub("", text.strip(), count=1)
    try:
        value = ast.literal_eval(body)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        raise InvalidPrompts(UNREADABLE) from None

    # A bare string, a number, a dict, a list holding anything but strings -- all the same answer.
    if isinstance(value, str) or not isinstance(value, (list, tuple)) \
            or not all(isinstance(item, str) for item in value):
        raise InvalidPrompts(UNREADABLE)

    prompts = [item.strip() for item in value if item.strip()]
    if not prompts:
        # A list of blanks is an empty list, not a broken one.
        raise InvalidPrompts(EMPTY)
    return prompts
