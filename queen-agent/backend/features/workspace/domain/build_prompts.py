"""Turning a scenario's structure into the prompt list.

Pure: it is handed the parsed structure and hands back strings, so it is the one part of the chain
that cannot be talked out of the rules. Assembly is exactly what a model must not do by hand -- a
character copied into forty frames drifts, a character resolved by code cannot.
"""
from collections import Counter

from backend.features.workspace.domain.errors import BadStructure
from backend.features.workspace.domain.naming import folded

# The chain every prompt opens with. In code rather than in each structure file since Madde 110: it
# is the same in every scenario, and a model writing it meant a model copying it out of the schema
# example -- which is how a chain mixing two model families reached real files.
#
# The one chain, since Madde 150. A file used to be able to name its own and win, and that door is
# what kept the field -- and the field is what kept the model deciding something whose right answer
# never changed. Another chain is a change here, where one edit reaches every scenario at once.
DEFAULT_QUALITY = (
    "score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres"
)

# What goes between two character blocks. A feature of the interface that reads the prompt rather
# than of the model: queen-editor's positive encoder splits on this literal string (Madde 138), and
# an encoder that does not know it takes the word as one more tag. Spaces on either side rather than
# commas, because the split leaves whatever touches it inside the chunk it opens.
BREAK = " BREAK "

# The kinds a count can be written from, in the order it writes them (Madde 156). Boy before girl
# because that is how the tag pair reads in what an SDXL model was trained on, and the order is fixed
# here rather than taken from the frame: who opens a prompt is the frame's own decision, how many are
# in it is not. A kind outside this tuple counts as nothing -- the same door a character with no kind
# at all falls through, and there is no second check because there is no second case.
COUNTED = ("boy", "girl")


def build_prompts(structure):
    """Every frame as one prompt, or a sentence saying why none of them can be built."""
    if not isinstance(structure, dict):
        raise BadStructure(
            "A structure file is a JSON object with characters, locations and frames."
        )

    characters = structure.get("characters") or {}
    outfits = structure.get("outfits") or {}
    locations = structure.get("locations") or {}
    # A transition, not a second name: files written before the rename keep their list under
    # "shots", and a rename cannot turn what is already on the user's disk into rubbish. Dropping
    # the fallback is its own decision, for the day those files are gone.
    frames = structure.get("frames") or structure.get("shots") or []
    if not frames:
        raise BadStructure("That file has no frames to build from.")

    misses, built = [], []
    for number, frame in enumerate(frames, start=1):
        # Whoever the frame wrote first leads it. No field names them -- the order already carries
        # it, and a second place saying the same thing is a place that can disagree. Read before the
        # prompt is opened, because the count is worked out from the same list.
        in_frame = _worn(frame.get("characters"))
        # The order is fixed here rather than in the file: a structure that could reorder itself
        # would answer "why did this frame come out different" with "it varies". It also keeps two
        # descriptions apart -- whoever leads opens the prompt, everyone else closes it, and the
        # place, the action and the camera sit in between so the two do not bleed together.
        #
        # A written count wins (Madde 156). Every file already on disk carries one and none of their
        # characters carries a kind, so counting over the top of it would answer the user's own
        # writing with nothing.
        lead = [DEFAULT_QUALITY, frame.get("people") or _counted(in_frame, characters)]
        lead.extend(_block(in_frame[:1], characters, outfits, number, misses))
        place = frame.get("location") or ""
        if place:
            lead.append(_looked_up(place, locations, "locations", number, misses))
        lead.append(frame.get("action", ""))
        lead.append(frame.get("camera", ""))
        # Everyone behind the lead gets a block of their own rather than a comma. Distance alone
        # only moves two descriptions apart; the break makes the encoder read them apart, and it
        # costs nothing to give the third the same separation as the second (Madde 139).
        blocks = [lead] + [
            _block([person], characters, outfits, number, misses) for person in in_frame[1:]
        ]
        # Each block carries its own commas and the break never touches one. Empty blocks are
        # dropped rather than joined: a prompt ending on a break, or holding two side by side,
        # would open a chunk with nothing in it.
        built.append(BREAK.join(tags for tags in map(_tags, blocks) if tags))

    # Every miss at once and nothing written: one pass fixes them all, and a dirty structure never
    # produces a list.
    if misses:
        raise BadStructure("\n".join(misses))
    return built


def build_character_prompts(structure, character):
    """One character on their own, once for every outfit the file names.

    The same joining a frame goes through, so what is seen here is what a frame will show. No count:
    how many people are in a picture is a frame's question, and there is no frame here.
    """
    if not isinstance(structure, dict):
        raise BadStructure(
            "A structure file is a JSON object with characters, locations and frames."
        )

    characters = structure.get("characters") or {}
    if character not in characters:
        # The sentence a frame gets, without the frame number: there is no frame to name.
        raise BadStructure(
            f"{character} is not in characters; known: {', '.join(sorted(characters)) or 'nothing'}"
        )

    identity = _identity(characters[character])
    outfits = structure.get("outfits") or {}
    if not outfits:
        return [_tags([DEFAULT_QUALITY, identity])]
    return [_tags([DEFAULT_QUALITY, identity, worn]) for worn in outfits.values()]


def render_module(prompts):
    """The file the user copies out of: triple quotes, trailing comma, one name to import."""
    lines = ["PROMPTS = ["]
    lines.extend(f'    """{_quoted(text)}""",' for text in prompts)
    lines.append("]")
    return "\n".join(lines) + "\n"


def prompts_name(source):
    """The output is the source under a new extension, so a project can hold several scenarios."""
    stem, dot, _ = source.rpartition(".")
    return f"{stem if dot else source}.py"


def character_prompts_name(source, character):
    """Named after both, so two characters can be tried side by side and neither one lands in the
    scene's own list."""
    stem, dot, _ = source.rpartition(".")
    return f"{stem if dot else source}-{folded(character)}.py"


def _worn(field):
    """A frame's characters as (name, outfits) pairs, whichever way the field was written.

    The one place the two shapes meet, so nothing downstream has to ask which it was holding. A
    plain list is what files written before outfits existed carry: names, wearing nothing. A single
    name written without its list is read as that one name -- the instruction asks for a list, but
    walking a string letter by letter would answer a small slip with nonsense.
    """
    if isinstance(field, dict):
        return [
            (name, [worn] if isinstance(worn, str) else list(worn or []))
            for name, worn in field.items()
        ]
    return [(name, []) for name in field or []]


def _identity(entry):
    """The tags out of a character's entry, whichever shape it was written in.

    Plain text is every file written before Madde 154; the map form carries a kind beside the tags,
    which is what the count is worked out from. The kind never reaches a prompt -- girl beside the
    frame's own 1girl would be the same thing said twice, in a place where saying it twice weights
    it.
    """
    return entry.get("tags", "") if isinstance(entry, dict) else entry


def _kind(entry):
    """What a character is, or nothing at all.

    Apart from _identity because the two answer opposite questions: that one hands back what goes
    into the prompt, this one hands back what never does. Plain text has no kind and none is guessed
    at -- a file written before Madde 154 says who is in it and not what they are, and a wrong count
    is worse than no count.
    """
    return entry.get("kind", "") if isinstance(entry, dict) else ""


def _counted(people, characters):
    """How many of each kind stand in this frame, in the tags an image model counts with.

    Handed the pairs _worn already made rather than the raw field, so the frame is read once. A name
    no map knows counts as nothing and is left to _looked_up, which is the one place that says so.
    """
    kinds = Counter(_kind(characters.get(name)) for name, _ in people)
    return ", ".join(
        f"{kinds[kind]}{kind}" if kinds[kind] == 1 else f"{kinds[kind]}{kind}s"
        for kind in COUNTED
        if kinds[kind]
    )


def _block(people, characters, outfits, number, misses):
    """One character then what they wear, name after name.

    Its own function because the frame is built in two halves and this shape appears in both: the
    one in front and everyone left behind them. The neighbour rule -- an identity and its outfits
    touching -- is what tells an image model whose clothes are whose, and it is written once.
    """
    parts = []
    for name, worn in people:
        parts.append(_identity(_looked_up(name, characters, "characters", number, misses)))
        parts.extend(_looked_up(outfit, outfits, "outfits", number, misses) for outfit in worn)
    return parts


def _looked_up(name, known, field, number, misses):
    if name in known:
        return known[name]
    # Only this map's names: place names are no help to someone looking for a character. The tool
    # never guesses at a near miss -- the model looks and fixes it, or asks.
    misses.append(
        f"frame {number}: {name} is not in {field}; known: {', '.join(sorted(known)) or 'nothing'}"
    )
    return ""


def _tags(parts):
    # A prompt is comma-separated tags, so the join happens tag by tag: a trailing comma in a map
    # entry or an empty field cannot leave ", ," behind.
    return ", ".join(
        tag for part in parts for tag in (piece.strip() for piece in str(part).split(",")) if tag
    )


def _quoted(text):
    # Tags carry no quotes in practice, but a file that will not parse is worse than an ugly one.
    escaped = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    # A quote at the very end would run into the closing three and end the string early.
    return f'{escaped[:-1]}\\"' if escaped.endswith('"') else escaped
