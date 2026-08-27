"""Turning a scenario's structure into the prompt list.

Pure: it is handed the parsed structure and hands back strings, so it is the one part of the chain
that cannot be talked out of the rules. Assembly is exactly what a model must not do by hand -- a
character copied into forty frames drifts, a character resolved by code cannot.
"""
from backend.features.workspace.domain.errors import BadStructure
from backend.features.workspace.domain.naming import folded


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
        # The order is fixed here rather than in the file: a structure that could reorder itself
        # would answer "why did this frame come out different" with "it varies". It also keeps two
        # descriptions apart -- whoever leads opens the prompt, everyone else closes it, and the
        # place, the action and the camera sit in between so the two do not bleed together.
        #
        # The count is placed, never worked out: the code knows who entered the frame but not what
        # they are, and no field says so.
        parts = [structure.get("quality", ""), frame.get("people", "")]
        # Whoever the frame wrote first leads it. No field names them -- the order already carries
        # it, and a second place saying the same thing is a place that can disagree.
        in_frame = _worn(frame.get("characters"))
        parts.extend(_block(in_frame[:1], characters, outfits, number, misses))
        place = frame.get("location") or ""
        if place:
            parts.append(_looked_up(place, locations, "locations", number, misses))
        parts.append(frame.get("action", ""))
        parts.append(frame.get("camera", ""))
        parts.extend(_block(in_frame[1:], characters, outfits, number, misses))
        built.append(_tags(parts))

    # Every miss at once and nothing written: one pass fixes them all, and a dirty structure never
    # produces a list.
    if misses:
        raise BadStructure("\n".join(misses))
    return built


def build_character_prompts(structure, character):
    """One character on their own, once for every outfit the file names.

    The same joining a frame goes through, so what is seen here is what a frame will show. No count:
    how many people are in a picture is a frame's own field, and there is no frame here.
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

    quality = structure.get("quality", "")
    identity = characters[character]
    outfits = structure.get("outfits") or {}
    if not outfits:
        return [_tags([quality, identity])]
    return [_tags([quality, identity, worn]) for worn in outfits.values()]


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


def _block(people, characters, outfits, number, misses):
    """One character then what they wear, name after name.

    Its own function because the frame is built in two halves and this shape appears in both: the
    one in front and everyone left behind them. The neighbour rule -- an identity and its outfits
    touching -- is what tells an image model whose clothes are whose, and it is written once.
    """
    parts = []
    for name, worn in people:
        parts.append(_looked_up(name, characters, "characters", number, misses))
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
