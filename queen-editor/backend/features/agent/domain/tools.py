"""The agent's four tools, and what each call is told back (madde 420, 479, 481).

None takes a project: the agent works in the project the question was asked in and no other (the
user: "sadec açık projeye erişebilir"). A call is answered from the cards the question started with,
so a frame's number means the same frame for the whole question. Three only read; fix_frame changes a
frame's photo, the one change the agent can make (the user: "ben düzelt diyince tek tek izin alarak
düzeltmek").

A tool that changes something says so with its call: alongside its step and its work it hands back
the change, which the user allows or rejects on the screen before the work may run (madde 480). The
permission is the app's, not the agent's -- no tool's description mentions it. A reading call, and a
call that misses, has no change.

fix_frame's work is the photo feature's: main.py hands it in as `fix`, because a feature never
imports another. It is told the card the change was described from, and holds it against the frame as
it is by then.

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


def _tool(name, description, **words):
    """A tool on one frame, named by its number; `words` are its text arguments, each with what it
    is."""
    properties = {"frame": {"type": "integer", "description": prompt.THE_FRAME},
                  **{word: {"type": "string", "description": said} for word, said in words.items()}}
    return {"type": "function",
            "function": {"name": name, "description": description,
                         "parameters": {"type": "object", "properties": properties,
                                        "required": list(properties)}}}


TOOLS = [_tool("read_frame", prompt.READ_FRAME), _tool("look_at_frame", prompt.LOOK_AT_FRAME),
         _tool("check_frame", prompt.CHECK_FRAME),
         _tool("fix_frame", prompt.FIX_FRAME, prompt=prompt.THE_PROMPT,
               negative=prompt.THE_NEGATIVE)]
_NAMES = {tool["function"]["name"] for tool in TOOLS}

NAMED_BY_NUMBER = "A frame is named by its number, counting from 1."
FIX_NEEDS_WORDS = ("A fix needs the frame's whole new prompt, which cannot be empty, and its whole "
                   "new negative prompt, which can.")
# What the photo feature's fix answers, as the model is told it. Its four words are the photo
# feature's (fix_photo.py): a callable handed in by main.py cannot carry a shared constant.
FIX_TOLD = {
    "fixed": "Frame {number} was fixed: its prompt and negative were changed, its old photo was "
             "deleted, and its new photo is in the queue in the frame's own place.",
    "waiting": "Frame {number} was fixed: its prompt and negative were changed and its old photo "
               "was deleted, but another project's generation is running now, so its new photo "
               "waits in the queue until this project's queue runs.",
    # The card the agent holds stays as the question found it, so calling again could only fail
    # again: what stops the retry is said here.
    "changed": "Frame {number} changed after you read it, so nothing was changed. It is read again "
               "at the user's next question; do not call fix_frame on it again now.",
    "linked": "Frame {number} is where another frame's queued video ends, so it is not changed.",
}
PHOTO_GOES = {"label": "Fotoğraf", "text": "Eski fotoğraf silinecek; yenisi aynı yerde üretilecek."}


def card(number, frame, whole=False):
    """What the model is shown of one of the gallery's cards: the list before the question carries
    the short form, read_frame the whole."""
    said = {"frame": number, "status": frame["status"], "layers": list(frame["layers"]),
            "owed": frame["owed"], "failed": frame["failed"]}
    if whole:
        # The negative too: a fix may improve it, and needs it whole (madde 481). A card that names
        # none -- a frame from before the plan kept negatives -- had none.
        said.update(errors=frame["errors"], scene=frame["scene"], prompts=frame["prompts"],
                    negative=frame.get("negative", ""))
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


def _has_video(frame):
    """A frame with a video is not touched (the user's choice, madde 479). A failed video is in the
    layers too -- a failed slot is taken -- but no video was made."""
    return "video" in frame["layers"] and "video" not in frame["failed"]


def _nothing_to_compare(number, frame):
    """Why check_frame has nothing to compare in this frame, or None. Read off the card alone.

    A failed photo is in the layers the way a failed video is, and there is no photo. The frame's
    photo prompt is the truth the photo is held to, so a photo without one has nothing to be
    compared with.
    """
    taken, failed = frame["layers"], frame["failed"]
    if _has_video(frame):
        return f"Frame {number} has a video, so it is not checked."
    if "photo" in failed:
        return f"The photo of frame {number} failed, so there is nothing to compare."
    if "photo" not in taken:
        return f"Frame {number} has no photo."
    if not frame["prompts"].get("photo"):
        return f"Frame {number} has no photo prompt to compare the photo with."
    return None


def _unfixable(number, frame):
    """Why fix_frame leaves this frame alone, or None. Read off the card alone.

    A video in the queue counts as a video: it would be made from the photo the fix deletes (ana
    ajan, 20 Ekim), and the agent lists it as "videosu sırada, atlandı".
    """
    if _has_video(frame):
        return f"Frame {number} has a video, so it is not changed."
    if "video" in frame["owed"]:
        return f"Frame {number} has a video in the queue, so it is not changed."
    if "photo" not in frame["layers"] or "photo" in frame["failed"]:
        return f"Frame {number} has no photo to fix."
    if not frame["prompts"].get("photo"):
        return f"Frame {number} has no photo prompt to fix."
    return None


def _fix(fix, project, number, frame, arguments):
    """fix_frame: (step or None, work, change or None). The work hands the frame -- the card the
    change was described from -- to the photo feature, which makes its photo again in its place.

    Space around the words is not an edit, and does not reach the frame. A field that would not
    change is left off the change; a fix that changes neither is no fix.
    """
    why = _unfixable(number, frame)
    if why:
        return None, _told(why), None
    words, negative = arguments.get("prompt"), arguments.get("negative")
    if not isinstance(words, str) or not words.strip() or not isinstance(negative, str):
        return None, _told(FIX_NEEDS_WORDS), None
    words, negative = words.strip(), negative.strip()
    details = [{"label": label, "before": before, "after": after}
               for label, before, after in (
                   ("Prompt", frame["prompts"]["photo"], words),
                   ("Negatif prompt", frame.get("negative", ""), negative))
               if before.strip() != after]
    if not details:
        return None, _told(f"Frame {number} already has this prompt and negative, so nothing "
                           f"would change."), None

    def work():
        return FIX_TOLD[fix(project, frame, words, negative)].format(number=number), None

    # Neutral once done: the step is written before the work, which may find the frame changed and
    # change nothing; the agent's answer says which.
    return ((f"{number} numaralı kareyi düzeltiyor…",
             f"{number} numaralı karenin düzeltmesini işledi"), work,
            {"title": f"{number} numaralı kare düzeltilecek", "details": details + [PHOTO_GOES]})


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


def run_tool(ask, frames, picture, fix, project, call):
    """One call -> (the step's two sentences or None, work, change or None). `work()` does the call's
    reading and returns (what the model is told, parts to show it or None); the loop writes the step
    first.

    `change` is what the call would change, in Turkish for the screen, and it is None unless the
    work writes: {"title": "<what changes, the frame named>", "details": [detail]}, where a detail is
    {"label", "before", "after"} -- what a field is and what it becomes -- or {"label", "text"}, a
    sentence, such as that the old photo will be deleted. A call with a change runs its work only once
    the user allows it (madde 480).

    That can be much later -- the user may answer after minutes, while the gallery has moved on -- so
    a changing call's work must not trust what was true when the change was described: it finds its
    frame by what names it on disk (its id), never by its number in the gallery, and if the frame is
    no longer what `change`'s `before` describes, it changes nothing and tells the model so.

    fix_frame keeps to that: `fix` holds the card the change was described from against the frame as
    it is, by its identity.

    `ask` is Queen AI's question with pictures, which check_frame asks; `frames` is {number: card};
    `picture(project, file)` is the file's bytes, or None when it is not on disk; `fix(project,
    card, prompt, negative)` is the photo feature's fix, answering one of FIX_TOLD's words. A
    picture cannot ride in a tool's answer -- DeepSeek takes one only in a user message -- so the
    parts go back to the loop, which sends them after the round's answers. check_frame's work raises
    QueenAIFailed when the service failed.
    """
    name = call["function"]["name"]
    if name not in _NAMES:
        return None, _told(f"There is no tool called {name}."), None
    try:
        arguments = json.loads(call["function"]["arguments"] or "{}")
    except ValueError:
        arguments = None
    if not isinstance(arguments, dict):
        arguments = {}
    number = arguments.get("frame")
    # bool before int, because in Python True is an int: frame=true would quietly mean frame 1.
    if isinstance(number, bool) or not isinstance(number, int):
        return None, _told(NAMED_BY_NUMBER), None
    if number not in frames:
        return None, _told(f"There is no frame {number}; the frames are numbered 1 to "
                           f"{len(frames)}."), None

    frame = frames[number]
    if name == "fix_frame":
        return _fix(fix, project, number, frame, arguments)
    if name == "check_frame":
        step, work = _check(ask, picture, project, number, frame)
    elif name == "look_at_frame":
        step, work = _look(picture, project, number, frame)
    else:
        # Turkish prompts reach the model as they read, not as escapes.
        step, work = ((f"{number} numaralı kareyi okuyor…", f"{number} numaralı kareyi okudu"),
                      _told(json.dumps(card(number, frame, whole=True), ensure_ascii=False)))
    # The readers: nothing to ask the user about.
    return step, work, None
