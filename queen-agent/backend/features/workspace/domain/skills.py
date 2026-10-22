"""Which skill carries which instruction, and nothing about what the instruction says.

The texts themselves are in prompt.py since Madde 189, beside everything else the model is told.
What is left here is the mapping: the picker's ids on one side, a text on the other. It is a
product behaviour like the texts are, so it stays in the domain.

Four texts since Madde 492: a start and an edit for each image model. The SDXL two keep the ids they
had, so old messages and the picker a browser remembers still find them; Improve went in the same
item, and a record naming it runs on the base text like any id nobody knows. The picker still has
an empty state -- having no skill selected is ordinary, and the base text holds anyway.
"""
from backend.features.workspace.domain import prompt

INSTRUCTIONS = {
    "start-a-scenario": prompt.START_A_SCENARIO,
    "edit-prompts": prompt.EDIT_PROMPTS,
    "krea-start-scenario": prompt.KREA_START_SCENARIO,
    "krea-edit": prompt.KREA_EDIT,
}


def instruction_for(skill):
    """Nothing for a skill nobody knows: a record can name one that has since been renamed."""
    return INSTRUCTIONS.get(skill, "")
