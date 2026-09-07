"""Which skill carries which instruction, and nothing about what the instruction says.

The texts themselves are in prompt.py since Madde 189, beside everything else the model is told.
What is left here is the mapping: the picker's ids on one side, a text on the other. It is a
product behaviour like the texts are, so it stays in the domain.

Two texts since Madde 101. Five others stood beside them and were deleted in Madde 94. The picker
still has an empty state -- having no skill selected is ordinary, and the base text holds anyway.
"""
from backend.features.workspace.domain import prompt

INSTRUCTIONS = {
    "generate-prompts-plus": prompt.GENERATE_PROMPTS_PLUS,
    "start-a-scenario": prompt.START_A_SCENARIO,
}


def instruction_for(skill):
    """Nothing for a skill nobody knows: a record can name one that has since been renamed."""
    return INSTRUCTIONS.get(skill, "")
