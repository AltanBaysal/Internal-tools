"""What each skill tells the model, and nothing about when it is told.

A product behaviour like prompt.py, so it lives in the domain. Every text is written in the mood
"this is how you do this job" rather than "do this": a selected skill stays selected after a message
is sent, and an instruction in the imperative would start producing something the moment the user
typed "thanks". What to do comes from the user's own sentence.

The instruction texts are English, like the rest of QueenAgent's own words. What the model writes
back follows the user's language (prompt.py); the exception is what an image model reads -- the
prompts and the structure file -- and the skill that produces those says so in as many words.

One text since Madde 94. Five others stood here and were deleted: what they said about how to work
now sits in prompt.py, where it holds whatever is selected, and what they said about their own task
either lives in the text below or went with them on purpose. The picker still exists and still has
an empty state -- having no skill selected is ordinary, and the list will grow again.

What a structure file looks like is not here either, since Madde 96: it lives in schema.py and is
fetched by a tool. A text that travels with every request should carry what is true every turn, and
the shape of a file is only true of the turn that writes one.
"""

GENERATE_PROMPTS_PLUS = (
    "When the user asks for the prompts of a frame list, this skill builds them from parts, so a "
    "character reads the same in every frame for a stronger reason than remembering to copy it.\n"
    "\n"
    "Call read_schema before writing anything. It hands back what a structure file looks like and "
    "the rules it has to hold; neither is repeated here, so there is one copy of both and it "
    "arrives when it is needed.\n"
    "\n"
    "Take the character and place tags from what the user settled in the chat. If a frame needs one "
    "that was never settled, ask for it rather than inventing it.\n"
    "\n"
    "Write it in two stages. First the skeleton -- the quality tags, the maps, and an empty frames "
    "list -- with create_file. Then add the frames with edit_file in batches of five, each batch "
    "reaching disk before the next one is written. Never the whole list in one answer.\n"
    "\n"
    "Then call build_prompts with the structure file's name. It resolves the names and assembles "
    "every frame in a fixed order. Do not assemble a prompt yourself and do not write the Python "
    "file by hand: doing either takes away the only thing this skill has that the plain one has "
    "not."
)

INSTRUCTIONS = {
    "generate-prompts-plus": GENERATE_PROMPTS_PLUS,
}


def instruction_for(skill):
    """Nothing for a skill nobody knows: a record can name one that has since been renamed."""
    return INSTRUCTIONS.get(skill, "")
