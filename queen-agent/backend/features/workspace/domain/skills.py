"""What each skill tells the model, and nothing about when it is told.

A product behaviour like prompt.py, so it lives in the domain. Every text is written in the mood
"this is how you do this job" rather than "do this": a selected skill stays selected after a message
is sent, and an instruction in the imperative would start producing something the moment the user
typed "thanks". What to do comes from the user's own sentence.

The instruction texts are English, like the rest of QueenAgent's own words. What the model writes
back follows the user's language (prompt.py); the exception is what an image model reads -- the
prompts and the structure file -- and the two skills that produce those say so in as many words.
"""

CREATE_SCENARIO = (
    "When the user asks for a scenario, this is what one is here: a short outline of a story, "
    "written as bullet points, running from beginning to end. One line per beat, in order.\n"
    "\n"
    "Keep it short. This step is not the finished story -- it is where the user sees what you "
    "understood of theirs, and a page of prose hides a misunderstanding that a list makes "
    "obvious.\n"
    "\n"
    "Stay out of the frame list's territory. No numbered frames, no camera or lighting language, "
    "no scene headings, no long description of how anything looks. The detail is added by the steps "
    "that come after this one, and a scenario that already carries it leaves them nothing to do.\n"
    "\n"
    "Write it in the chat and save it with create_file. Name the file after what the scenario is "
    "about, as in bar-scene.md -- one project holds several scenarios, and a fixed name loses "
    "which is which.\n"
    "\n"
    "When the user corrects something afterwards, change the file too with edit_file. A correction "
    "that only lands in the chat leaves two scenarios, and the one on disk is the one the next "
    "step reads."
)

CREATE_CHARACTER_PROMPT = (
    "When the user asks for a character prompt, this is the shape of one: SDXL tags -- short "
    "comma-separated phrases, never sentences.\n"
    "\n"
    "A character carries only what does not change from frame to frame: who they are, hair, eyes, "
    "build. Clothing is not one of those -- it changes between frames, so it lives in the structure "
    "file's outfits map and is named by the frame. Leave the pose, the place, the camera and the "
    "mood out for the same reason: they belong to a frame, and a character that carries them "
    "cannot be reused. Leave the quality and score tags out as well; they are added once, "
    "elsewhere.\n"
    "\n"
    "How many candidates to write is the user's call. If they said a number, write that many. If "
    "they did not, ask before writing -- a guess is either more than they wanted or fewer.\n"
    "\n"
    "If the user pastes a prompt they liked, read it as an example of the format: how dense the "
    "tags are, what order they come in, what language they use. Take the shape, not the contents. "
    "What belongs to a frame -- the pose, the place, the camera, the quality and score tags -- is "
    "left behind.\n"
    "\n"
    "Write the candidates to a file with create_file, not into the chat. The file is JSON in the "
    "same shape as a structure file's maps, so it can be pasted straight in:\n"
    "\n"
    "{\n"
    '  "characters": { "aylin": "1girl, pale skin, long black hair, green eyes" },\n'
    '  "outfits": { "gunluk": "oversized black t-shirt, black thong" }\n'
    "}\n"
    "\n"
    "Name the file after the character, as in aylin.json. Several candidates go in the same file "
    "under numbered names -- aylin-1, aylin-2 -- and what differs between them is said in one line "
    "in the chat, where the person choosing reads it.\n"
    "\n"
    "Clothing goes in outfits, named after the garment rather than whoever wears it, never inside "
    "the character's own entry. If no clothing was asked for, leave outfits out altogether rather "
    "than writing an empty one."
)

SPLIT_INTO_FRAMES = (
    "When the user asks for a scenario to be split into frames, read the scenario first with "
    "read_file if the project holds one.\n"
    "\n"
    "A frame is one or two sentences: who is in it, what is happening, from what camera. Not a "
    "paragraph of prose. Number them.\n"
    "\n"
    "How many frames there are is settled together with the user. Propose a number, say what it is "
    "based on, and wait -- do not decide it alone.\n"
    "\n"
    "Give them in small batches, a few frames at a time, rather than the whole list in one answer. "
    "Quality falls away towards the end of a long stretch, and batches leave the user room to "
    "correct one before the next is written.\n"
    "\n"
    "This stays in the chat. Do not create a file."
)

GENERATE_PROMPTS = (
    "When the user asks for the prompts of a frame list, this skill writes each one whole: no "
    "structure file, and no call to build_prompts.\n"
    "\n"
    "A prompt is SDXL tags in this order, the same order every time: the quality tags, then the "
    "characters, then the place, then what is happening, then the camera.\n"
    "\n"
    "The prompts are English whatever language the chat is in -- an image model reads them, not a "
    "person.\n"
    "\n"
    "They go into a Python file with create_file, in this shape:\n"
    "\n"
    "PROMPTS = [\n"
    '    """the first prompt""",\n'
    '    """the second prompt""",\n'
    "]\n"
    "\n"
    "Name the file after the scenario and end the name with -plain, as in intro-plain.py, so it can "
    "sit beside the one built from a structure without either replacing the other.\n"
    "\n"
    "Do not try the whole list in one answer. Write the first few frames with create_file and add "
    "the rest with edit_file, a few at a time: quality falls away towards the end of a long "
    "stretch, and an interruption then costs one batch rather than everything."
)

# One text, two readers: the structured skill checks itself against it before it builds, and Verify
# applies it whenever it is asked to. Two copies would come apart on the first change to either.
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

VERIFY_PROMPTS = (
    "When the user asks for the prompts to be checked, read this project's structure files with "
    "list_files and read_file, and hold them against these rules:\n"
    "\n" + RULEBOOK + "\n"
    "\n"
    "Report what you find: which file, which frame, which rule. Say plainly when a file is clean "
    "-- silence is not an answer.\n"
    "\n"
    "Do not fix anything. Do not create a file and do not edit one. Rule 3 in particular is not "
    "yours to settle: which of the two texts is the right one is the user's own call. Fixing "
    "happens when the user asks for it, and not before."
)

INSTRUCTIONS = {
    "create-scenario": CREATE_SCENARIO,
    "create-character-prompt": CREATE_CHARACTER_PROMPT,
    "split-into-frames": SPLIT_INTO_FRAMES,
    "generate-prompts": GENERATE_PROMPTS,
    "generate-prompts-plus": GENERATE_PROMPTS_PLUS,
    "verify-prompts": VERIFY_PROMPTS,
}


def instruction_for(skill):
    """Nothing for a skill nobody knows: a record can name one that has since been renamed."""
    return INSTRUCTIONS.get(skill, "")
