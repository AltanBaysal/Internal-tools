"""Naming rules shared by everything that puts a file somewhere.

The tools use it when the model asks for a name, and the trash uses it when a name is deleted
twice. Two copies of this rule would drift apart on the first change to either.
"""


def unique_name(existing, name):
    """Nothing is ever overwritten: plan.md becomes plan-2.md."""
    if name not in existing:
        return name
    stem, _, extension = name.rpartition(".")
    number = 2
    while f"{stem}-{number}.{extension}" in existing:
        number += 1
    return f"{stem}-{number}.{extension}"
