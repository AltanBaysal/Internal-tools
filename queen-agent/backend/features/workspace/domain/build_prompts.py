"""Turning a scenario's structure into the prompt list.

Pure: it is handed the parsed structure and hands back strings, so it is the one part of the chain
that cannot be talked out of the rules. Assembly is exactly what a model must not do by hand -- a
character copied into forty shots drifts, a character resolved by code cannot.
"""
from backend.features.workspace.domain.errors import BadStructure


def build_prompts(structure):
    """Every shot as one prompt, or a sentence saying why none of them can be built."""
    if not isinstance(structure, dict):
        raise BadStructure("A structure file is a JSON object with characters, locations and shots.")

    characters = structure.get("characters") or {}
    locations = structure.get("locations") or {}
    shots = structure.get("shots") or []
    if not shots:
        raise BadStructure("That file has no shots to build from.")

    misses, built = [], []
    for number, shot in enumerate(shots, start=1):
        # The order is fixed here rather than in the file: a structure that could reorder itself
        # would answer "why did this shot come out different" with "it varies".
        parts = [structure.get("quality", "")]
        for name in shot.get("characters") or []:
            parts.append(_looked_up(name, characters, "characters", number, misses))
        place = shot.get("location") or ""
        if place:
            parts.append(_looked_up(place, locations, "locations", number, misses))
        parts.append(shot.get("action", ""))
        parts.append(shot.get("camera", ""))
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
        f"shot {number}: {name} is not in {field}; known: {', '.join(sorted(known)) or 'nothing'}"
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
