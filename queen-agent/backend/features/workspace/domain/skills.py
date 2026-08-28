"""What each skill tells the model, and nothing about when it is told.

A product behaviour like prompt.py, so it lives in the domain. Every text is written in the mood
"this is how you do this job" rather than "do this": a selected skill stays selected after a message
is sent, and an instruction in the imperative would start producing something the moment the user
typed "thanks". What to do comes from the user's own sentence.

The instruction texts are English, like the rest of QueenAgent's own words. What the model writes
back follows the user's language (prompt.py); the exception is what an image model reads -- the
prompts and the structure file -- and the skill that produces those says so in as many words.

Two texts since Madde 101. Five others stood here and were deleted in Madde 94: what they said about
how to work now sits in prompt.py, where it holds whatever is selected, and what they said about
their own task either lives in the texts below or went with them on purpose. The picker still has an
empty state -- having no skill selected is ordinary.

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

START_A_SCENARIO = (
    "When the user wants a scenario made, this skill walks them through it by asking. Five steps in "
    "a fixed order -- the plan, the characters, the places, the scenes, the prompts -- and each one "
    "leaves the same thing behind however much or little the user said. What a talkative user "
    "changes is how many turns a step takes, never what it produces.\n"
    "\n"
    "The first move is always the same: list_files, then write_plan. Whatever the opening sentence "
    "was, the plan is written before anything is asked, and it is where the flow keeps its place. A "
    "plan already in the project is that memory -- read it and carry on from the step it left open "
    "rather than writing a second one, which is how work continues in a fresh chat when a "
    "conversation has grown too long. With more than one plan there, ask which.\n"
    "\n"
    "Call read_schema before writing the structure file. It hands back what the file looks like and "
    "the rules it has to hold; neither is repeated here, so there is one copy of both and it "
    "arrives when it is needed.\n"
    "\n"
    "A step ends when the user approves it, not when an answer is written. Say what was saved and "
    "ask; if they want something changed, change it and ask again. Nothing moves on in between.\n"
    "\n"
    "An answer arrives three ways and all three end the same. Tags the user wrote themselves are "
    "taken as they are. A description in their own words becomes tags. Nothing at all becomes a "
    "placeholder -- a plain character, a plain background -- and the step still ends. Never stop "
    "the flow waiting for a description.\n"
    "\n"
    "Clothes are written where they are heard: somebody described in a dress at the character step "
    "goes into outfits there, and the places step does not ask about it again.\n"
    "\n"
    "The scenes step writes twice -- the frames into the structure file, and a list of its own "
    "where each scene is one sentence. The list is what the user reads.\n"
    "\n"
    "Then build_prompts, which is the flow's own last move: the user does not change skill to "
    "finish what they started. Do not assemble a prompt by hand.\n"
    "\n"
    "A character can be looked at before entering a frame -- build_character_prompts gives one "
    "character against every outfit the file names. Offer it at the character step; it is a side "
    "door rather than a step, so carry on from where the flow was if the user is not interested."
)

INSTRUCTIONS = {
    "generate-prompts-plus": GENERATE_PROMPTS_PLUS,
    "start-a-scenario": START_A_SCENARIO,
}


def instruction_for(skill):
    """Nothing for a skill nobody knows: a record can name one that has since been renamed."""
    return INSTRUCTIONS.get(skill, "")
