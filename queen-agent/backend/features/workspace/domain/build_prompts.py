"""Turning a scenario's structure into the prompt list.

Pure: it is handed the parsed structure and hands back strings, so it is the one part of the chain
that cannot be talked out of the rules. Assembly is exactly what a model must not do by hand -- a
character copied into forty frames drifts, a character resolved by code cannot.
"""
from backend.features.workspace.domain.errors import BadStructure


def build_prompts(structure):
    """Every frame as one prompt, or a sentence saying why none of them can be built."""
    if not isinstance(structure, dict):
        raise BadStructure(
            "A structure file is a JSON object with characters, locations and frames."
        )

    characters = structure.get("characters") or {}
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
        # would answer "why did this frame come out different" with "it varies".
        parts = [structure.get("quality", "")]
        for name in frame.get("characters") or []:
            parts.append(_looked_up(name, characters, "characters", number, misses))
        place = frame.get("location") or ""
        if place:
            parts.append(_looked_up(place, locations, "locations", number, misses))
        parts.append(frame.get("action", ""))
        parts.append(frame.get("camera", ""))
        built.append(_tags(parts))

    # Every miss at once and nothing written: one pass fixes them all, and a dirty structure never
    # produces a list.
    if misses:
        raise BadStructure("\n".join(misses))
    return built


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
