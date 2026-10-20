"""The agent's three tools, and what each call is told back (madde 420, 479).

All only read, and none takes a project: the agent reads the project the question was asked in and
no other (the user: "sadec açık projeye erişebilir", "yani bir değişilik yapamasın"). A call is
answered from the cards the question started with, so a frame's number means the same frame for the
whole question.

check_frame asks Queen AI about one frame in a question of its own -- the photo and the prompt it
was made from -- and tells the conversation the verdict in words. A picture put into the
conversation would be sent again with every later round; a verdict in words is sent once.

What a call says on the chat is a step with two Turkish sentences -- while it goes on and once done.
The step is known from the card alone, so it is on the chat before the call's slow work -- a disk
read, a question to Queen AI -- begins. A call that reads nothing -- an unknown tool, a frame that is
not there, a frame check_frame has nothing to compare in -- is no step: the model is told why, and
nothing is shown to the user.
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


TOOLS = [_tool("read_frame", prompt.READ_FRAME), _tool("look_at_frame", prompt.LOOK_AT_FRAME),
         _tool("check_frame", prompt.CHECK_FRAME)]
_NAMES = {tool["function"]["name"] for tool in TOOLS}

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


class QueenAIFailed(Exception):
    """A check met a technical failure, in the box's own words: the service is down, and every
    later check would meet it too, so the question ends (madde 479). A refusal is not one -- it is
    that frame's answer."""


def _told(said, parts=None):
    """A work that is already done: what the model is told, read off the card."""
    return lambda: (said, parts)


def _nothing_to_compare(number, frame):
    """Why check_frame has nothing to compare in this frame, or None. Read off the card alone.

    A frame with a video is not touched (the user's choice, madde 479). A failed video is in the
    layers too -- a failed slot is taken -- but no video was made, so that frame is checked; a
    failed photo is in them the same way, and there is no photo. The frame's photo prompt is the
    truth the photo is held to, so a photo without one has nothing to be compared with.
    """
    taken, failed = frame["layers"], frame["failed"]
    if "video" in taken and "video" not in failed:
        return f"Frame {number} has a video, so it is not checked."
    if "photo" in failed:
        return f"The photo of frame {number} failed, so there is nothing to compare."
    if "photo" not in taken:
        return f"Frame {number} has no photo."
    if not frame["prompts"].get("photo"):
        return f"Frame {number} has no photo prompt to compare the photo with."
    return None


def _check(ask, picture, project, number, frame):
    """check_frame: (step or None, work). The work reads the photo and asks Queen AI about it."""
    why = _nothing_to_compare(number, frame)
    if why:
        return None, _told(why)
    file, words = frame["layers"]["photo"], frame["prompts"]["photo"]

    def work():
        try:
            data = picture(project, file)
        except OSError as exc:
            # One frame's unreadable photo is that frame's line: the verdicts before it stay.
            return f"The photo of frame {number} could not be read: {exc}", None
        if data is None:
            return f"Frame {number} has no photo.", None
        said = ask(prompt.MIXUP_RULES + prompt.MIXUP_CHECK + prompt.SYSTEM_PROMPT_SUFFIX,
                   f"Prompt: {words}", [(file, data)])
        if said.failed and not said.refused:
            raise QueenAIFailed(said.text)
        if said.failed:
            return f"The check of frame {number} failed: {said.text}", None
        return f"Frame {number}: {said.text}", None

    return ((f"{number} numaralı kareyi prompt'uyla karşılaştırıyor…",
             f"{number} numaralı kareyi prompt'uyla karşılaştırdı"), work)


def _look(picture, project, number, frame):
    def work():
        file = frame["layers"].get("photo")
        data = picture(project, file) if file else None
        if data is None:
            return f"Frame {number} has no photo.", None
        return f"The photo of frame {number} is in the next message.", _shown(number, file, data)

    return ((f"{number} numaralı karenin görseline bakıyor…",
             f"{number} numaralı karenin görseline baktı"), work)


def run_tool(ask, frames, picture, project, call):
    """One call -> (the step's two sentences or None, work). `work()` does the call's reading and
    returns (what the model is told, parts to show it or None); the loop writes the step first.

    `ask` is Queen AI's question with pictures, which check_frame asks; `frames` is {number: card};
    `picture(project, file)` is the file's bytes, or None when it is not on disk. A picture cannot
    ride in a tool's answer -- DeepSeek takes one only in a user message -- so the parts go back to
    the loop, which sends them after the round's answers. check_frame's work raises QueenAIFailed
    when the service failed.
    """
    name = call["function"]["name"]
    if name not in _NAMES:
        return None, _told(f"There is no tool called {name}.")
    try:
        number = json.loads(call["function"]["arguments"] or "{}").get("frame")
    except (ValueError, AttributeError):
        number = None
    # bool before int, because in Python True is an int: frame=true would quietly mean frame 1.
    if isinstance(number, bool) or not isinstance(number, int):
        return None, _told(NAMED_BY_NUMBER)
    if number not in frames:
        return None, _told(f"There is no frame {number}; the frames are numbered 1 to "
                           f"{len(frames)}.")

    frame = frames[number]
    if name == "check_frame":
        return _check(ask, picture, project, number, frame)
    if name == "look_at_frame":
        return _look(picture, project, number, frame)
    # Turkish prompts reach the model as they read, not as escapes.
    return ((f"{number} numaralı kareyi okuyor…", f"{number} numaralı kareyi okudu"),
            _told(json.dumps(card(number, frame, whole=True), ensure_ascii=False)))
