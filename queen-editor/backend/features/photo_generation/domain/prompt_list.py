"""The pasted prompt list -> list[str]. Pure, and it never executes what it reads.

The text comes straight out of a notebook cell, so a leading `PROMPTS =` is stripped before
parsing and `ast.literal_eval` does the rest: it accepts literals only -- no calls, no names,
nothing executable -- so a paste can be wrong but never dangerous.
"""
import ast
import re

_ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*\s*=\s*")
_EXAMPLE = '["ilk prompt", "ikinci prompt"]'


class InvalidPrompts(Exception):
    """The pasted text is not a usable prompt list (message is user-facing)."""


def parse_prompts(text):
    if not text or not text.strip():
        raise InvalidPrompts("Prompt listesi boş.")

    body = _ASSIGNMENT.sub("", text.strip(), count=1)
    try:
        value = ast.literal_eval(body)
    except (ValueError, SyntaxError, MemoryError, RecursionError) as exc:
        # Python's own message, not a guess about what the user meant.
        raise InvalidPrompts(f"Prompt listesi okunamadı — Python listesi bekleniyor, örnek: "
                             f"{_EXAMPLE}. Python hatası: {exc}") from None

    if isinstance(value, str):
        raise InvalidPrompts(f"Tek metin geldi — köşeli parantezli liste bekleniyor: {_EXAMPLE}")
    if not isinstance(value, (list, tuple)):
        raise InvalidPrompts(f"Liste bekleniyordu, {type(value).__name__} geldi. Örnek: {_EXAMPLE}")
    if not all(isinstance(item, str) for item in value):
        raise InvalidPrompts(f"Listenin her öğesi metin olmalı. Örnek: {_EXAMPLE}")

    prompts = [item.strip() for item in value if item.strip()]
    if not prompts:
        raise InvalidPrompts("Listede dolu prompt yok.")
    return prompts
