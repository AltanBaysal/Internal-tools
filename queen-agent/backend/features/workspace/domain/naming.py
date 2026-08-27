"""Naming rules shared by everything that puts a file somewhere.

The tools use it when the model asks for a name, and the trash uses it when a name is deleted
twice. Two copies of this rule would drift apart on the first change to either.
"""
import re


def folded(raw):
    """A name from the model, folded into another name: aylin, or yan-karakter.

    Sibling of tools.safe_name rather than the same rule: that one cleans a file name and keeps the
    dot, because the extension lives there. This one is going inside a file name, so the dot goes
    the way every other separator does.
    """
    return re.sub(r"[^A-Za-z0-9-]+", "-", str(raw or "")).strip("-").lower()


def unique_name(existing, name):
    """Nothing is ever overwritten: plan.md becomes plan-2.md, and p1 becomes p1-2."""
    if name not in existing:
        return name
    stem, dot, extension = name.rpartition(".")
    # A directory name has no extension, and rpartition hands the whole name back as the tail.
    suffix = f".{extension}" if dot else ""
    if not dot:
        stem = name
    number = 2
    while f"{stem}-{number}{suffix}" in existing:
        number += 1
    return f"{stem}-{number}{suffix}"
