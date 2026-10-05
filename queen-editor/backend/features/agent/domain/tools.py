"""The agent's two tools, and what each call is told back (madde 420).

Both only read, and neither takes a project: the agent reads the project the question was asked in
and no other (the user: "sadec açık projeye erişebilir", "yani bir değişilik yapamasın"). A call is
answered from the cards the question started with, so a frame's number means the same frame for the
whole question.

What a call says on the chat is a step with two Turkish sentences -- while it goes on and once done.
A call that read nothing -- an unknown tool, a frame that is not there -- is no step: the model is
told why, and nothing is shown to the user.
"""
import base64
import json
import mimetypes

from backend.features.agent.domain import prompt


def _tool(name, description):
    return {"type": "function",
            "function": {"name": name, "description": description,
                         "parameters": {"type": "object",
                                        "properties": {"frame": {"type": "integer",
                                                                 "description": prompt.THE_FRAME}},
                                        "required": ["frame"]}}}


TOOLS = [_tool("read_frame", prompt.READ_FRAME), _tool("look_at_frame", prompt.LOOK_AT_FRAME)]

NAMED_BY_NUMBER = "A frame is named by its number, counting from 1."


def card(number, frame, whole=False):
    """What the model is shown of one of the gallery's cards: the list before the question carries
    the short form, read_frame the whole."""
    said = {"frame": number, "status": frame["status"], "layers": list(frame["layers"]),
            "owed": frame["owed"], "failed": frame["failed"]}
    if whole:
        said.update(errors=frame["errors"], scene=frame["scene"], prompts=frame["prompts"])
    return said


def _shown(number, name, data):
    """The photo as message parts: a line saying whose it is, then the picture as a data URL -- the
    file is on this machine and no link could point at it. Its type is read off its name."""
    media_type = mimetypes.guess_type(name)[0]
    return [{"type": "text", "text": f"The photo of frame {number}:"},
            {"type": "image_url",
             "image_url": {"url": f"data:{media_type};base64,{base64.b64encode(data).decode()}"}}]


def run_tool(frames, picture, project, call):
    """One call -> (the step's two sentences or None, what the model is told, parts to show it or
    None).

    `frames` is {number: card}; `picture(project, file)` is the file's bytes, or None when it is not
    on disk. A picture cannot ride in a tool's answer -- DeepSeek takes one only in a user message --
    so the parts go back to the loop, which sends them after the round's answers.
    """
    name = call["function"]["name"]
    if name not in ("read_frame", "look_at_frame"):
        return None, f"There is no tool called {name}.", None
    try:
        number = json.loads(call["function"]["arguments"] or "{}").get("frame")
    except (ValueError, AttributeError):
        number = None
    # bool before int, because in Python True is an int: frame=true would quietly mean frame 1.
    if isinstance(number, bool) or not isinstance(number, int):
        return None, NAMED_BY_NUMBER, None
    if number not in frames:
        return None, f"There is no frame {number}; the frames are numbered 1 to {len(frames)}.", None

    frame = frames[number]
    if name == "read_frame":
        # Turkish prompts reach the model as they read, not as escapes.
        return ((f"{number} numaralı kareyi okuyor…", f"{number} numaralı kareyi okudu"),
                json.dumps(card(number, frame, whole=True), ensure_ascii=False), None)

    looking = (f"{number} numaralı karenin görseline bakıyor…",
               f"{number} numaralı karenin görseline baktı")
    file = frame["layers"].get("photo")
    data = picture(project, file) if file else None
    if data is None:
        return looking, f"Frame {number} has no photo.", None
    return looking, f"The photo of frame {number} is in the next message.", _shown(number, file, data)
