"""What a structure file looks like, and the rules it has to hold.

Its own module rather than a paragraph in skills.py: that file says what a skill does, this one says
what the file being written is. Two questions, and the second one gets a second asker in Madde 101.

Fetched rather than recited -- read_prompt_structure_schema hands it back when a file is about to
be written, so a turn that writes nothing does not pay for it. The instruction travels at the end of every request
(Madde 93); this does not travel at all until it is asked for.
"""

STRUCTURE = (
    "Every prompt built from this file goes to an SDXL-family image model. The model reads tags, "
    "never sentences, and one prompt renders one single still picture -- a frozen instant. "
    "Nothing that needs time to be seen reaches the picture: no motion, no sound, no before and "
    "after. A movement is written as the pose it passes through -- mid-stride, leaning in, head "
    "thrown back.\n"
    "\n"
    "The structure is one JSON file per scenario, named after it, as in intro-frames.json:\n"
    "\n"
    "{\n"
    '  "characters": { "aylin": "woman in her mid 20s, long teal hair, green eyes, mature '
    'female",\n'
    '                  "deniz": "man in his late 20s, short black hair, brown eyes, stubble" },\n'
    '  "outfits": { "gunluk": "jeans, black t-shirt", "atki": "red knit scarf",\n'
    '               "ceket": "denim jacket, white t-shirt" },\n'
    '  "locations": { "bedroom": "sunlit bedroom, morning light, natural light, indoors" },\n'
    '  "frames": [\n'
    '    { "people": "1girl", "characters": { "aylin": ["gunluk", "atki"] },\n'
    '      "location": "bedroom",\n'
    '      "action": "sitting on edge of bed, holding letter, pensive expression, light blush, '
    'looking down",\n'
    '      "camera": "medium shot, from above" },\n'
    '    { "people": "1boy, 1girl",\n'
    '      "characters": { "aylin": ["gunluk"], "deniz": ["ceket"] },\n'
    '      "location": "bedroom",\n'
    '      "action": "standing by window, talking, looking at each other, soft smiles",\n'
    '      "camera": "upper body, from side" }\n'
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
    "wear the same one. An entry dresses one person: the text it holds is copied whole to whoever "
    "names it, so two people dressed differently are two entries. One entry trying to cover both "
    "-- or, for the man, for the woman -- puts the man in the dress and the woman in the "
    "trousers.\n"
    "\n"
    "people says how many are in the frame -- 1girl; 1boy, 1girl; 2girls. Every frame carries it, "
    "even a frame with one character, and it is never inside a character's own entry: the same "
    "character stands alone in one frame and beside someone in the next. Write it and leave the "
    "placing alone -- code puts it where it goes.\n"
    "\n"
    "A frame's characters is a map: the key is the character, the value is the outfits they wear in "
    "that frame. A character with no outfit named has an empty list, and a frame with nobody in it "
    "is an empty map. The first name a frame lists leads the prompt: it opens the prompt, and "
    "everyone after it is placed at the end, after the camera tags, so two descriptions do not "
    "bleed into each other. Write whoever the frame is about first.\n"
    "\n"
    "Every value in this file is written the same way: short comma-separated fragments -- tags "
    "and brief phrases -- never a sentence telling the story. An article is not a tag, so it is "
    "dropped: sitting on couch, by window. An action carries the pose, the expression and where "
    "the eyes look; a camera carries the framing and the angle. The example is the measure: "
    "match its density.\n"
    "\n"
    "An action holds only what the camera sees. A scene sentence carries why something is "
    "happening and what came before it; a frame carries neither, because nothing in the picture "
    "shows them. A cause is written as what it looks like -- turned away, downcast eyes, tense "
    "shoulders -- or it is left out.\n"
    "\n"
    "A camera is two decisions: how much of the body is in the picture -- close-up, upper body, "
    "medium shot, full body -- and where it is looking from -- from side, from above, from "
    "behind, looking at viewer. Both are written, both halves come from the lists just given -- "
    "a half that is not in them is not a tag -- and the pair is chosen for the scene rather "
    "than kept from the frame before.\n"
    "\n"
    "The quality chain is not in this file: code puts it at the front of every prompt, the same "
    "way for every scenario. Write a quality field only when this one needs a different chain -- "
    "what is written there is used instead.\n"
    "\n"
    "Everything in this file is English -- an image model reads it."
)

# Its own constant rather than a paragraph in the text above: these are the rules, and keeping them
# in one place is what makes them countable and quotable.
RULEBOOK = (
    "1. A frame describing a character or a place in plain words when the maps already hold an "
    "entry for it. This is the one worth hunting: it is the silent copy coming back.\n"
    "2. Clothing written inside a character's own entry, or inside a frame's action, when outfits "
    "is where it belongs. Both are rule 1 in another form: the text copied in instead of the name "
    "being used.\n"
    "3. Quality tags written inside a frame's own fields. Code adds them once, so they would be "
    "printed twice.\n"
    "4. The same name carrying different text in two structure files in this project. Copying is "
    "allowed; a copy that has drifted is not.\n"
    "5. A name defined in a map and used by no frame -- a note, not a violation.\n"
    "6. A count or a solo tag inside a character's own entry, when the frame's people is where it "
    "belongs. Nothing strips it for you -- code cannot tell a count from any other tag, so move "
    "it yourself.\n"
    "7. A value written as a sentence -- articles, a subject doing a verb -- when fragments are "
    "what an image model reads. Break it into short comma-separated fragments.\n"
    "8. One outfit entry covering two people -- or, for the man, for the woman. Whoever names it "
    "is handed the whole text, so split it into one entry per set of clothes.\n"
    "9. A cause or a moment outside the frame written into an action -- after the argument, "
    "later, again. Nothing in the picture shows it, so write what it looks like instead."
)

SCHEMA = (
    STRUCTURE
    # "Writing or changing", not "building": since K40 the writer and the builder are different
    # skills, and the rulebook's best catches are writing-time mistakes -- a check tied to
    # building would let the flow skip it.
    + "\n\nBefore writing or changing the file, hold it against these rules and fix what you "
    "find:\n\n"
    + RULEBOOK
)
