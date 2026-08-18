"""What each skill tells the model, and nothing about when it is told.

A product behaviour like prompt.py, so it lives in the domain. Every text is written in the mood
"this is how you do this job" rather than "do this": a selected skill stays selected after a message
is sent, and an instruction in the imperative would start producing something the moment the user
typed "thanks". What to do comes from the user's own sentence.

English, like the rest of QueenAgent -- its design was written in English and translating it would
stop the design from being the source.
"""

CREATE_SCENARIO = (
    "When the user asks for a scenario, this is what one is here: a short outline of a story, 10 to "
    "15 sentences of plain prose, running from beginning to end. It says what happens and in what "
    "order.\n"
    "\n"
    "Stay out of the shot list's territory. No numbered shots, no camera or lighting language, no "
    "scene headings, no long description of how anything looks. The detail is added by the steps "
    "that come after this one, and a scenario that already carries it leaves them nothing to do.\n"
    "\n"
    "Write it in the chat and save it with create_file as scenario.md.\n"
    "\n"
    "Write the scenario in the language the user is writing in, not in English."
)

CREATE_CHARACTER_PROMPT = (
    "When the user asks for a character prompt, this is the shape of one: SDXL tags -- short "
    "comma-separated phrases, never sentences.\n"
    "\n"
    "A character carries only what does not change from shot to shot: who they are, hair, eyes, "
    "build, what they are wearing. Leave the pose, the place, the camera and the mood out -- those "
    "belong to a shot, and a character that carries them cannot be reused. Leave the quality and "
    "score tags out as well; they are added once, elsewhere.\n"
    "\n"
    "Offer two or three candidates so there is something to choose between, and say in one line "
    "what differs between them.\n"
    "\n"
    "This stays in the chat. Do not create a file and do not put a candidate into a structure file. "
    "Which one is kept, and what name it is kept under, is the user's own next sentence."
)

SPLIT_INTO_SHOTS = (
    "When the user asks for a scenario to be split into shots, read the scenario first with "
    "read_file if the project holds one.\n"
    "\n"
    "A shot is one line in prompt language: what is in frame, what is happening, from what camera. "
    "Not a paragraph of prose. Number them.\n"
    "\n"
    "How many shots there are is settled together with the user. Propose a number, say what it is "
    "based on, and wait -- do not decide it alone.\n"
    "\n"
    "Give them in small batches, a few shots at a time, rather than the whole list in one answer. "
    "Quality falls away towards the end of a long stretch, and batches leave the user room to "
    "correct one before the next is written.\n"
    "\n"
    "This stays in the chat. Do not create a file."
)

INSTRUCTIONS = {
    "create-scenario": CREATE_SCENARIO,
    "create-character-prompt": CREATE_CHARACTER_PROMPT,
    "split-into-shots": SPLIT_INTO_SHOTS,
}


def instruction_for(skill):
    """Nothing for a skill nobody knows: a record can name one that has since been renamed."""
    return INSTRUCTIONS.get(skill, "")
