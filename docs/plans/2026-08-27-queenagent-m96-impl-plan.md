# Madde 96 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-27-queenagent-m96-sema-aractan-uygulama-design.md](../specs/2026-08-27-queenagent-m96-sema-aractan-uygulama-design.md)
**Tur 1:** otuz kırmızı commit'lendi *(`2981d55`)*. Bu turda test yazılmaz.
**Komut:** `python -m pytest queen-agent -q`

---

## 1 · Yeni dosya: `domain/schema.py`

```python
"""What a structure file looks like, and the rules it has to hold.

Its own module rather than a paragraph in skills.py: that file says what a skill does, this one says
what the file being written is. Two questions, and the second one gets a second asker in Madde 101.

Fetched rather than recited -- read_schema hands it back when a file is about to be written, so a
turn that writes nothing does not pay for it. The instruction travels at the end of every request
(Madde 93); this does not travel at all until it is asked for.
"""

STRUCTURE = (
    "The structure is one JSON file per scenario, named after it, as in intro-frames.json:\n"
    "\n"
    "{\n"
    '  "quality": "score_9_up, masterpiece, best quality, absurdres",\n'
    '  "characters": { "aylin": "long teal hair, green eyes, mature female" },\n'
    '  "outfits": { "gunluk": "jeans, black t-shirt", "atki": "red knit scarf" },\n'
    '  "locations": { "bedroom": "sunlit bedroom, morning light, ..." },\n'
    '  "frames": [\n'
    '    { "people": "1girl", "characters": { "aylin": ["gunluk", "atki"] },\n'
    '      "location": "bedroom",\n'
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
    "people says how many are in the frame -- 1girl, or 1boy, 1girl, or 2girls. Every frame carries "
    "it, a frame with one character included, and it is never inside a character's own entry: the "
    "same character stands alone in one frame and beside someone in the next. Write it and leave "
    "the placing alone -- code puts it where it goes.\n"
    "\n"
    "A frame's characters is a map: the key is the character, the value is the outfits they wear in "
    "that frame. Someone wearing nothing named has an empty list, and a frame with nobody in it is "
    "an empty map. The first name a frame lists leads the prompt -- it opens the frame, and whoever "
    "comes after is placed past the camera so two descriptions do not bleed into each other. Write "
    "whoever the frame is about first.\n"
    "\n"
    "Everything in this file is English -- an image model reads it."
)

# Its own constant rather than a paragraph in the text above: these are the rules, and keeping them
# in one place is what makes them countable and quotable.
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
    "5. A name defined in a map and used by no frame -- a note, not a violation.\n"
    "6. A count or a solo tag inside a character's own entry, when the frame's people is where it "
    "belongs. Nothing strips one for you: a tag written on purpose would go without a word, and "
    "which tag is a count can only be guessed at from a list of names that is never finished."
)

SCHEMA = (
    STRUCTURE
    + "\n\nBefore building, hold the file against these rules and fix what you find:\n\n"
    + RULEBOOK
)
```

## 2 · `domain/skills.py` — şema ve kural kitabı çıkıyor

`RULEBOOK` sabiti ve onu tanıtan yorum tamamen siliniyor. `GENERATE_PROMPTS_PLUS` bu hâle geliyor:

```python
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
```

Modül başlığındaki *"One text since Madde 94"* paragrafına bir cümle giriyor: biçim ve kurallar
artık burada değil.

## 3 · `domain/tools.py` — yedinci araç

`SCHEMA` import ediliyor:

```python
from backend.features.workspace.domain.schema import SCHEMA
```

`TOOL_SPECS`'in başına, `list_files`'ın hemen ardına:

```python
    {
        "type": "function",
        "function": {
            "name": "read_schema",
            "description": (
                "What a structure file looks like and the rules it has to hold. Read it before "
                "writing or changing one; no instruction repeats it."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
```

`run_tool`'da, `list_files` dalının ardına:

```python
    if name == "read_schema":
        # No arguments: there is one shape, so asking which one would be a question with a single
        # answer. The outcome is what was answered with rather than the answer -- a read says how
        # many lines, not the file.
        return ToolResult(SCHEMA, None, "", "Schema")
```

`WRITES_FILES` değişmiyor.

## 4 · `domain/modes.py` — tek satır

```python
READS = ("list_files", "read_file", "read_schema")
```

Yorumuna bir cümle: okuyan ve hiçbir şeyi değiştirmeyen bir araç, esirgenecek bir yanı yok.

## 5 · Koş

```
python -m pytest queen-agent -q
```

Beklenen: otuz kırmızı yeşil. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 6 · Commit

```
feat(queen-agent): the shape of a structure file is fetched, not recited
```
