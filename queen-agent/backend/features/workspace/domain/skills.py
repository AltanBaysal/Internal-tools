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
"""

# Its own constant rather than a paragraph in the text below: these are the rules, and keeping them
# in one place is what makes them countable and quotable. Verify was the second reader until Madde
# 94; the one that stayed applies them before it builds.
RULEBOOK = (
    "1. A frame describing a character or a place in plain words when the maps already hold an "
    "entry for it. This is the one worth hunting: it is the silent copy coming back.\n"
    "2. Clothing written inside a character's own entry, or inside a frame's action, when outfits "
    "is where it belongs. Both are rule 1 wearing different clothes: the text copied in instead of "
    "the name named.\n"
    "3. Quality tags written inside a frame's own fields. Code adds them once, so they would be "
    "printed twice.\n"
    "4. The same name carrying different text in two structure files in this project. Copying is "
    "allowed; a copy that has drifted is not.\n"
    "5. A name defined in a map and used by no frame -- a note, not a violation."
)

GENERATE_PROMPTS_PLUS = (
    "When the user asks for the prompts of a frame list, this skill builds them from parts, so a "
    "character reads the same in every frame for a stronger reason than remembering to copy it.\n"
    "\n"
    "The structure is one JSON file per scenario, named after it, as in intro-frames.json:\n"
    "\n"
    "{\n"
    '  "quality": "score_9_up, masterpiece, best quality, absurdres",\n'
    '  "characters": { "aylin": "1girl, long teal hair, ..." },\n'
    '  "outfits": { "gunluk": "jeans, black t-shirt", "atki": "red knit scarf" },\n'
    '  "locations": { "bedroom": "sunlit bedroom, morning light, ..." },\n'
    '  "frames": [\n'
    '    { "characters": { "aylin": ["gunluk", "atki"] }, "location": "bedroom",\n'
    '      "action": "sitting on the edge of the bed, holding a letter",\n'
    '      "camera": "medium shot, from slightly above" }\n'
    "  ]\n"
    "}\n"
    "\n"
    "Whatever repeats across frames is written once, in the maps at the top. A frame names it and "
    "never carries the text again -- that is what makes updating a character one edit instead of "
    "forty. location is a single name because a frame happens in one place.\n"
    "\n"
    "What a character always is goes in characters; what changes from frame to frame goes in "
    "outfits. Clothing is the thing that changes, so it never belongs in a character's own entry. "
    "An outfit is named after the garment rather than whoever wears it, because two characters can "
    "wear the same one.\n"
    "\n"
    "A frame's characters is a map: the key is the character, the value is the outfits they wear in "
    "that frame. Someone wearing nothing named has an empty list, and a frame with nobody in it is "
    "an empty map.\n"
    "\n"
    "Take the character and place tags from what the user settled in the chat. If a frame needs one "
    "that was never settled, ask for it rather than inventing it.\n"
    "\n"
    "Everything in this file is English -- an image model reads it.\n"
    "\n"
    "Write it in two stages. First the skeleton -- the quality tags, the maps, and an empty frames "
    "list -- with create_file. Then add the frames with edit_file in batches of five, each batch "
    "reaching disk before the next one is written. Never the whole list in one answer.\n"
    "\n"
    "Before building, hold the file against these rules and fix what you find:\n"
    "\n" + RULEBOOK + "\n"
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
