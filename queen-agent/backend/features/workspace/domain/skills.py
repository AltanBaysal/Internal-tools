"""What each skill tells the model, and nothing about when it is told.

A product behaviour like prompt.py, so it lives in the domain. Every text is written in the mood
"this is how you do this job" rather than "do this": a selected skill stays selected after a message
is sent, and an instruction in the imperative would start producing something the moment the user
typed "thanks". What to do comes from the user's own sentence.

The instruction texts are English, like the rest of QueenAgent's own words. What the model writes
back follows the user's language (prompt.py); the exception is what an image model reads -- the
prompts and the structure file -- and the schema fetched before writing one says so in as many
words (schema.py).

Two texts since Madde 101. Five others stood here and were deleted in Madde 94: what they said about
how to work now sits in prompt.py, where it holds whatever is selected, and what they said about
their own task either lives in the texts below or went with them on purpose. The picker still has an
empty state -- having no skill selected is ordinary.

What a structure file looks like is not here either, since Madde 96: it lives in schema.py and is
fetched by a tool. A text that travels with every request should carry what is true every turn, and
the shape of a file is only true of the turn that writes one.
"""

GENERATE_PROMPTS_PLUS = (
    "When the user wants the prompts of a scenario built or changed, this is the skill for both. "
    "A prompt is never written out by hand: characters, outfits and places live in the structure "
    "file's maps, a frame only names them, and build_prompts assembles every frame from those "
    "parts in a fixed order -- which is why a character reads the same in frame three and frame "
    "forty. The work here is getting that file right and then calling the builder.\n"
    "\n"
    "It picks up where Start a scenario stops, and it also stands alone. A scenario left by the "
    "flow is a structure file and a scene list named after it, as in bar-scene.json and "
    "bar-scene-scenes.md: find the pair with list_files, read both, and turn each sentence into "
    "a frame in the list's order -- a frame's characters and its location come from the maps the "
    "file already holds. With more than one scenario there, ask which. Standing alone, the same "
    "work starts one "
    "step earlier: the skeleton first -- the quality tags, the maps, and an empty frames list -- "
    "with create_file.\n"
    "\n"
    "The sentence is the scene's brief, never text to copy into the frame: the action and the "
    "camera detail are this skill's own work -- asking is for names never settled, not for "
    "craft. Two frames carrying the same framing and angle read as one picture twice, so "
    "neighbours differ in at least one. Fewer frames than sentences means work left: carry on "
    "from the first sentence with no frame.\n"
    "\n"
    "Call read_prompt_structure_schema before writing anything. It hands back what a structure "
    "file looks like and the rules it has to hold; nothing here repeats them, so never write one "
    "from memory.\n"
    "\n"
    "Take the character and place tags from what the user settled in the chat or what the file "
    "already holds. If a frame needs one that was never settled, ask for it rather than "
    "inventing it.\n"
    "\n"
    "Add the frames with edit_file in batches of five, each batch reaching disk before the next "
    "one is written. Never the whole list in one answer.\n"
    "\n"
    "Then call build_prompts with the structure file's name. It resolves the names and assembles "
    "every frame in a fixed order. Do not assemble a prompt yourself and do not write the Python "
    "file by hand: assembled by hand, a character drifts from frame to frame; assembled by code, "
    "it cannot.\n"
    "\n"
    "When the user comes back unhappy with a prompt, changing it is the same road: find the frame "
    "it came from -- the built list runs in the frames' order -- fix what is wrong with "
    "edit_file, and call build_prompts again. What is wrong is either the frame's own action or "
    "camera, or the entry in a map the frame names: a map entry is the one edit that reaches "
    "every frame naming it. The prompt file is written from the structure file every time, so it "
    "is rebuilt rather than patched, and never edited by hand."
)

START_A_SCENARIO = (
    "When the user wants a scenario made, this skill walks them through it by asking. Five steps "
    "in a fixed order, and each one leaves the same thing behind however much or little the user "
    "said. What a talkative user changes is how many turns a step takes, never what it produces. "
    "What this skill leaves is the foundation -- the structure file and a readable scene list; "
    "writing the frames in detail is Generate prompts+'s work, not this one's.\n"
    "\n"
    "Every step runs the same loop. The flow asks, writes what it heard, then says what was saved "
    "and asks whether it is right: a step ends when the user approves it, not when an answer is "
    "written, and "
    "nothing moves on in between. An answer arrives three ways and all three end the same -- "
    "tags the user wrote themselves are taken as they are, a description in their own words "
    "becomes tags, and nothing at all becomes a placeholder, a plain character, a plain "
    "background. Never stop the flow waiting for a description. A fourth way is a delegation -- "
    "you decide. It answers only the question that was asked: the flow chooses for that one "
    "step, shows what it chose, and the step still ends when the user approves it; the next "
    "step's question is asked as ever, because deciding one step is not authority over the "
    "flow. The plan writes a delegation with the name of the step it closed, never as a "
    "standing authority -- a fresh chat reads the plan and inherits exactly what is written "
    "there. When a step is approved, its "
    "line in the plan is marked done -- the plan remembers only what is written into it.\n"
    "\n"
    "1. The plan. The first move whatever the opening sentence was: list_files, then write_plan, "
    "and the plan is written before anything is asked -- it is where the flow keeps its place. A "
    "plan already in the project is that memory: read it and carry on from the step it left open "
    "rather than writing a second one, which is how work continues in a fresh chat when a "
    "conversation has grown too long. With more than one plan there, ask which. This is the one "
    "step that waits for no approval; the first question follows in the same answer.\n"
    "\n"
    "2. The characters. Who is in the scenario, described or pasted as tags. Call "
    "read_prompt_structure_schema first -- it hands back what the file looks like and the rules "
    "it has to hold; nothing here repeats them -- and the structure file is born once, at this "
    "step, with its frames list empty; every later change to it is an edit, never a second "
    "file. Clothes are written where they are heard: somebody described in a dress goes into "
    "outfits now, and the places step does not ask again. A character can also be looked at "
    "before entering a frame -- build_character_prompts gives one character, once for every "
    "outfit the file names. Offer it; it is a side door rather than a step, so carry on from "
    "where the "
    "flow was if the user is not interested.\n"
    "\n"
    "3. The places. Where it happens and what is worn go into locations and outfits -- the same "
    "three ways an answer arrives, the same placeholder when none does.\n"
    "\n"
    "4. The scenes. The flow asks how many scenes and which moments matter, then writes one "
    "file: a list of its own named after the structure file, as in bar-scene-scenes.md, where "
    "each scene is one sentence, "
    "written in their own language -- the list is what the user reads, and what the frames will "
    "be written from. Nothing goes into the structure file at this step: frames stay empty on "
    "purpose.\n"
    "\n"
    "5. The handoff. The foundation is standing -- characters, places, scenes -- and this skill's "
    "work ends with this message: name the two files, say the scenario is ready, and send the "
    "user to Generate prompts+ in the skills menu, which reads the scene list, writes each scene "
    "as a detailed frame, and builds the prompt list. Frames are never written here, not even "
    "when the user asks for them: writing them in batches and choosing a frame's camera are that "
    "skill's own work, so the ask is answered by pointing there. Like the plan, this step waits "
    "for no approval -- it is the last word."
)

INSTRUCTIONS = {
    "generate-prompts-plus": GENERATE_PROMPTS_PLUS,
    "start-a-scenario": START_A_SCENARIO,
}


def instruction_for(skill):
    """Nothing for a skill nobody knows: a record can name one that has since been renamed."""
    return INSTRUCTIONS.get(skill, "")
