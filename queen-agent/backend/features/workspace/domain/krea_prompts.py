"""A Krea scenario: its shape, and the prompt list built from it (Madde 492).

A Krea scenario is a style and frames, each frame a scene and a prompt -- {"style", "frames":
[{"scene", "prompt"}]} and nothing else. The style is the look every photo shares, so the code puts
it in front of each frame's prompt: the model writes it once, and it cannot drift between frames
(FOUNDATION 5).

Its own module beside build_prompts.py, the SDXL builder: each kind's rules stand with that kind.
Which kind a file is, its name says (tools.scenario_kind); this module is only ever handed a
.krea.json, and content that does not fit is refused here, naming what does not fit, rather than
read as the other kind.

Pure, like build_prompts: handed the parsed structure, it hands back sentences or the list.
"""
from backend.features.workspace.domain.errors import BadStructure

SCENARIO_KEYS = ("style", "frames")
FRAME_KEYS = ("scene", "prompt")

# What a Krea scenario is on the day it is born, before krea_start_scenario writes the style the user
# gave into it: no frames yet. Beside its keys, so the shape is written in one place.
EMPTY_KREA_SCENARIO = {"style": "", "frames": []}


def krea_problems(source, structure):
    """Every way this structure is not a Krea scenario, as sentences; empty when it is one.

    Every one at once, the way build_prompts names every miss: one pass fixes them all.
    """
    if not isinstance(structure, dict):
        return [f"{source}: a Krea scenario is a JSON object with style and frames."]
    problems = _keys(structure, SCENARIO_KEYS, source, "a Krea scenario has style and frames.")
    if "style" in structure and not isinstance(structure["style"], str):
        problems.append(f"{source}: the style is not text.")
    frames = structure.get("frames")
    if "frames" in structure and not isinstance(frames, list):
        problems.append(f"{source}: frames is not a list.")
        return problems
    for number, frame in enumerate(frames or [], start=1):
        problems.extend(_frame_problems(source, number, frame))
    return problems


def build_krea_prompts(source, structure):
    """Every frame as its scene and its photo prompt -- the style, then the frame's prompt.

    The shape first, then what is empty: a style or a prompt with nothing in it would build a photo
    of nothing, and every one of them is named at once.
    """
    problems = krea_problems(source, structure)
    if problems:
        raise BadStructure("\n".join(problems))
    frames = structure["frames"]
    if not frames:
        # build_prompts' own sentence: the same miss reads the same on both kinds.
        raise BadStructure("That file has no frames to build from.")

    style = structure["style"].strip()
    empty = [] if style else [f"{source} has an empty style."]
    empty.extend(
        f"{source}: frame {number} has an empty prompt."
        for number, frame in enumerate(frames, start=1)
        if not frame["prompt"].strip()
    )
    if empty:
        raise BadStructure("\n".join(empty))
    # The shape build_prompts hands back, so render_module and Queen Editor read both kinds alike.
    return [
        {"scene": frame["scene"], "photo": f"{style} {frame['prompt'].strip()}"} for frame in frames
    ]


def _frame_problems(source, number, frame):
    if not isinstance(frame, dict):
        return [f"{source}: frame {number} is not an object with scene and prompt."]
    where = f"{source}: frame {number}"
    problems = _keys(frame, FRAME_KEYS, where, "a Krea frame has scene and prompt.")
    problems.extend(
        f"{where}'s {key} is not text."
        for key in FRAME_KEYS
        if key in frame and not isinstance(frame[key], str)
    )
    return problems


def _keys(given, wanted, where, shape):
    """What is missing, then what is extra, each said beside the shape it should have.

    `where` is what the sentence is about: the file, or the file and one of its frames.
    """
    missing = [f"{where} has no {key}; {shape}" for key in wanted if key not in given]
    extra = [f"{where} has {key}; {shape}" for key in given if key not in wanted]
    return missing + extra
