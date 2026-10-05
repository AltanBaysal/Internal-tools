"""Queen Editor's agent (madde 420): it reads the open project and answers, through the box.

The loop runs with fakes (CODE-STANDARD, Tests): a box that answers from a list and keeps a copy of
every request as it was sent, the gallery's cards, a picture reader, and a run that writes down what
the agent writes to the chat. No network.

The new modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
import base64
import copy
import importlib.util
import json
import os

import pytest

from backend.services.deepseek.box import Answer

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
QUEEN_AGENT_PROMPT = os.path.join(os.path.dirname(TOOL), "queen-agent", "backend", "features",
                                  "workspace", "domain", "prompt.py")

QUESTION = "Kaç kare var?"
REFUSED = "Model hata döndü, farklı şekilde dene."
LOOKING = ("Projeye bakıyor…", "Projeye baktı")
# The designer's sentence for a project with no frames (sohbet.js, EMPTY).
NO_FRAMES = ("Projede henüz kare yok. Prompt'ları yazıp kuyruğa eklediğinde kareler galeride "
             "belirir; sonra sorularını kareler üzerinden cevaplayabilirim.")

# düğün's gallery, top first, the way list_frames answers. The gallery's badge counts from the
# bottom, so P0_0 is frame 1 and P2_0 is frame 3.
CARDS = [
    {"id": "P2_0", "status": "pending", "layers": {}, "owed": ["photo"], "failed": [],
     "errors": {}, "scene": "", "prompts": {"photo": "mavi elbiseli kadın"}},
    {"id": "P1_0", "status": "done", "layers": {"photo": "P1_0.png"}, "owed": [],
     "failed": ["video"], "errors": {"video": "ComfyUI: out of memory"}, "scene": "Kadın döner.",
     "prompts": {"photo": "yeşil elbiseli kadın", "video": "she turns"}},
    {"id": "P0_0", "status": "done", "layers": {"photo": "P0_0.png", "video": "P0_0.mp4"},
     "owed": ["audio"], "failed": [], "errors": {}, "scene": "Kadın tahtta oturur.",
     "prompts": {"photo": "kırmızı elbiseli kadın", "video": "she sits"}},
]
# What the model is shown of each card before the question, frame 1 first.
LINES = [
    {"frame": 1, "status": "done", "layers": ["photo", "video"], "owed": ["audio"], "failed": []},
    {"frame": 2, "status": "done", "layers": ["photo"], "owed": [], "failed": ["video"]},
    {"frame": 3, "status": "pending", "layers": [], "owed": ["photo"], "failed": []},
]
# Frame 2 whole, the way read_frame gives it.
FRAME_2 = {**LINES[1], "errors": {"video": "ComfyUI: out of memory"}, "scene": "Kadın döner.",
           "prompts": {"photo": "yeşil elbiseli kadın", "video": "she turns"}}
# Only frame 1's photo is on disk: frame 2 has a photo layer whose file is gone.
PHOTO = b"PNGDATA"


def call(name, arguments, call_id="call_1"):
    """A tool call the way DeepSeek sends one: its arguments are JSON text."""
    return {"id": call_id, "type": "function", "function": {"name": name, "arguments": arguments}}


def calling(*calls):
    """The box handing back tool calls, unchecked (madde 419)."""
    return Answer("", tool_calls=list(calls))


class FakeBox:
    """Answers each request with the next of `answers`. An entry may be a function: it runs while the
    request is out -- where a stop can land -- and returns the answer. Keeps every request as it was
    when it was sent."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.asked = []

    def converse(self, messages, tools=()):
        self.asked.append((copy.deepcopy(messages), tools))
        answer = self.answers.pop(0)
        return answer() if callable(answer) else answer


class FakeRun:
    """The question being answered: writes down what the agent writes to the chat."""

    def __init__(self):
        self.wrote = []
        self.halted = False

    def stopped(self):
        return self.halted

    def add_step(self, running, done):
        self.wrote.append(("step", running, done))

    def finish_step(self):
        self.wrote.append(("stepDone",))

    def answer(self, text):
        self.wrote.append(("answer", text))

    def fail(self, text):
        self.wrote.append(("failure", text))


class Project:
    """The two readers main.py hands the agent, noting which project each was asked about."""

    def __init__(self, cards=CARDS):
        self.cards = cards
        self.asked = []

    def frames(self, project):
        self.asked.append(("frames", project))
        return copy.deepcopy(self.cards)

    def picture(self, project, file):
        self.asked.append(("picture", project, file))
        return {"P0_0.png": PHOTO}.get(file)


def answering(box, project=None, earlier=(), question=QUESTION, run=None):
    """The agent answers one question in düğün; what it wrote comes back."""
    from backend.features.agent.domain.usecases.answer_question import answer_question
    project = project or Project()
    run = run or FakeRun()
    answer_question(box, project.frames, project.picture, run, "düğün", list(earlier), question)
    return run.wrote


def prompt():
    from backend.features.agent.domain import prompt as module
    return module


def tools():
    from backend.features.agent.domain import tools as module
    return module.TOOLS


def step(pair):
    return ("step", *pair)


DONE = ("stepDone",)


def reading(number):
    return (f"{number} numaralı kareyi okuyor…", f"{number} numaralı kareyi okudu")


def looking_at(number):
    return (f"{number} numaralı karenin görseline bakıyor…",
            f"{number} numaralı karenin görseline baktı")


def frames_of(message):
    """The cards message read back: its first line, and each frame's line as JSON."""
    first, *rest = message["content"].split("\n")
    return first, [json.loads(line) for line in rest]


def _queen_agent_suffix():
    """QueenAgent's suffix, the value QueenAgent sends -- loaded, not parsed, the way
    test_video_prompt_writer reads it. The module imports nothing, so nothing else comes with it."""
    spec = importlib.util.spec_from_file_location("queen_agent_prompt", QUEEN_AGENT_PROMPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SYSTEM_PROMPT_SUFFIX


def test_a_project_with_no_frames_is_answered_with_no_request():
    """Nothing to read: the look at the project, then the designer's sentence (BEHAVIOUR.md, Agent
    panel -- "A project with no frames gets one answer saying so")."""
    box = FakeBox()

    wrote = answering(box, Project(cards=[]))

    assert wrote == [step(LOOKING), ("answer", NO_FRAMES)]
    assert box.asked == []


def test_the_first_request_is_the_instruction_the_cards_and_the_question():
    """The project card by card, before the question (the user: "kart yapılı"), numbered the way the
    gallery's badge numbers them."""
    box = FakeBox(Answer("Projede 3 kare var."))
    project = Project()

    answering(box, project)

    (messages, offered), = box.asked
    system, cards, asked = messages
    assert system == {"role": "system",
                      "content": prompt().INSTRUCTION + prompt().SYSTEM_PROMPT_SUFFIX}
    assert cards["role"] == "system"
    assert frames_of(cards) == (prompt().FRAMES, LINES)
    assert asked == {"role": "user", "content": QUESTION}
    assert offered == tools()
    # Only the project the question was asked in.
    assert project.asked == [("frames", "düğün")]


def test_the_instruction_ends_with_queen_agent_s_suffix():
    """The user: "aynı suffixi kullansın" -- asked of QueenAgent's own text, as madde 407 asks it of
    the prompt writers. The copy is pinned to it: the day the owner rewrites QueenAgent's, this goes
    red until the copy follows."""
    box = FakeBox(Answer("Projede 3 kare var."))

    answering(box)

    sent = box.asked[0][0][0]["content"]
    suffix = _queen_agent_suffix()
    assert sent.endswith(suffix), f"Agent'ın talimatı QueenAgent'ın suffix'iyle bitmiyor:\n{sent}"
    assert prompt().SYSTEM_PROMPT_SUFFIX == suffix, (
        "Agent'ın suffix'i QueenAgent'ınkiyle aynı değil: queen-agent/backend/features/workspace/"
        "domain/prompt.py'deki SYSTEM_PROMPT_SUFFIX, queen-editor/backend/features/agent/domain/"
        "prompt.py'ye aynen kopyalanmalı"
    )


def test_the_tools_only_read_and_name_no_project():
    """The user: "yani bir değişilik yapamasın", "sadec açık projeye erişebilir". Two readers, and a
    frame number is all either takes."""
    offered = tools()

    assert [tool["function"]["name"] for tool in offered] == ["read_frame", "look_at_frame"]
    for tool in offered:
        assert tool["type"] == "function"
        parameters = tool["function"]["parameters"]
        assert list(parameters["properties"]) == ["frame"]
        assert parameters["properties"]["frame"]["type"] == "integer"
        assert parameters["required"] == ["frame"]


def test_words_alone_are_the_answer():
    """The look at the project is not finished by the agent: the answer finishes it (the record's
    fold, BEHAVIOUR.md)."""
    box = FakeBox(Answer("Projede 3 kare var."))

    assert answering(box) == [step(LOOKING), ("answer", "Projede 3 kare var.")]
    assert len(box.asked) == 1


def test_read_frame_gives_the_frame_whole():
    read = call("read_frame", '{"frame": 2}')
    box = FakeBox(calling(read), Answer("2 numaralı karenin videosu hata verdi."))

    wrote = answering(box)

    messages, _tools = box.asked[1]
    assert len(messages) == 5
    assert messages[3] == {"role": "assistant", "content": "", "tool_calls": [read]}
    told = messages[4]
    assert (told["role"], told["tool_call_id"]) == ("tool", "call_1")
    assert json.loads(told["content"]) == FRAME_2
    assert wrote == [step(LOOKING), DONE, step(reading(2)),
                     ("answer", "2 numaralı karenin videosu hata verdi.")]


def test_look_at_frame_shows_its_photo():
    """A picture rides in a user message, the way the prompt writers send one: DeepSeek takes none in
    a system message, nor in a tool's answer."""
    box = FakeBox(calling(call("look_at_frame", '{"frame": 1}')), Answer("Kadın tahtta oturuyor."))
    project = Project()

    wrote = answering(box, project)

    messages, _tools = box.asked[1]
    assert messages[4] == {"role": "tool", "tool_call_id": "call_1",
                           "content": "The photo of frame 1 is in the next message."}
    assert messages[5] == {"role": "user", "content": [
        {"type": "text", "text": "The photo of frame 1:"},
        {"type": "image_url",
         "image_url": {"url": "data:image/png;base64," + base64.b64encode(PHOTO).decode()}},
    ]}
    assert project.asked == [("frames", "düğün"), ("picture", "düğün", "P0_0.png")]
    assert wrote == [step(LOOKING), DONE, step(looking_at(1)), ("answer", "Kadın tahtta oturuyor.")]


@pytest.mark.parametrize("frame", [3, 2], ids=["no-photo-layer", "photo-not-on-disk"])
def test_looking_at_a_frame_with_no_photo_says_so(frame):
    box = FakeBox(calling(call("look_at_frame", json.dumps({"frame": frame}))),
                  Answer("Fotoğrafı yok."))

    wrote = answering(box)

    messages, _tools = box.asked[1]
    assert len(messages) == 5
    assert messages[4] == {"role": "tool", "tool_call_id": "call_1",
                           "content": f"Frame {frame} has no photo."}
    assert wrote == [step(LOOKING), DONE, step(looking_at(frame)), ("answer", "Fotoğrafı yok.")]


@pytest.mark.parametrize("name, arguments, said", [
    ("rename_frame", '{"frame": 1}', "There is no tool called rename_frame."),
    ("read_frame", '{"frame": ', "A frame is named by its number, counting from 1."),
    ("read_frame", '{"frame": "3"}', "A frame is named by its number, counting from 1."),
    ("look_at_frame", '{"frame": 0}', "There is no frame 0; the frames are numbered 1 to 3."),
    ("read_frame", '{"frame": 4}', "There is no frame 4; the frames are numbered 1 to 3."),
], ids=["unknown-tool", "not-json", "text-number", "zero", "past-the-last"])
def test_a_miss_writes_no_step_and_tells_the_model_why(name, arguments, said):
    """A step is something the agent read; a miss read nothing. The model is told why, and the loop
    goes on."""
    box = FakeBox(calling(call(name, arguments)), Answer("Tamam."))

    wrote = answering(box)

    assert box.asked[1][0][4] == {"role": "tool", "tool_call_id": "call_1", "content": said}
    assert wrote == [step(LOOKING), ("answer", "Tamam.")]


def test_several_calls_in_one_round_go_in_order():
    """Each new step finishes the one before it; the round's pictures follow all its tools' answers."""
    read = call("read_frame", '{"frame": 2}', "call_1")
    look = call("look_at_frame", '{"frame": 1}', "call_2")
    box = FakeBox(calling(read, look), Answer("İkisi de hazır."))

    wrote = answering(box)

    messages, _tools = box.asked[1]
    assert [message["role"] for message in messages[3:]] == ["assistant", "tool", "tool", "user"]
    assert [message["tool_call_id"] for message in messages[4:6]] == ["call_1", "call_2"]
    assert wrote == [step(LOOKING), DONE, step(reading(2)), DONE, step(looking_at(1)),
                     ("answer", "İkisi de hazır.")]


def test_the_chats_earlier_questions_go_before_the_cards():
    """A chat carries on where it stopped (BEHAVIOUR.md): its questions, and the answers the agent
    gave, go first. A question that got no answer goes alone."""
    earlier = [
        {"text": "Kaç kare var?", "askedAt": "2026-10-06T10:00:00+00:00", "steps": [],
         "outcome": {"kind": "answer", "text": "3 kare."}},
        {"text": "7 numaralı kare ne?", "askedAt": "2026-10-06T10:05:00+00:00", "steps": [],
         "outcome": {"kind": "failure", "text": REFUSED}},
    ]
    box = FakeBox(Answer("1 ve 2 numaralı kareler."))

    answering(box, earlier=earlier, question="Hangileri hazır?")

    messages = box.asked[0][0]
    assert len(messages) == 6
    assert messages[1:4] == [{"role": "user", "content": "Kaç kare var?"},
                             {"role": "assistant", "content": "3 kare."},
                             {"role": "user", "content": "7 numaralı kare ne?"}]
    assert frames_of(messages[4])[0] == prompt().FRAMES
    assert messages[5] == {"role": "user", "content": "Hangileri hazır?"}


def test_the_32nd_round_is_the_last_told_so_offered_no_tools_and_its_words_are_the_answer():
    """The user: "agentic looptada sınır 32 olsun"; at the limit, "queen agent ne yapıyorsa onu
    yapar" -- QueenAgent's last round is told so and handed no tools (Madde 137)."""
    read = call("read_frame", '{"frame": 1}')
    box = FakeBox(*[calling(read)] * 31, Answer("Elimdekiyle: 3 kare var."))

    wrote = answering(box)

    assert len(box.asked) == 32
    closing = {"role": "system", "content": prompt().LAST_ROUND}
    for messages, offered in box.asked[:31]:
        assert offered == tools()
        assert closing not in messages
    messages, offered = box.asked[31]
    assert offered == ()
    assert messages[-1] == closing
    assert wrote[-1] == ("answer", "Elimdekiyle: 3 kare var.")


@pytest.mark.parametrize("failure", [
    Answer(REFUSED, failed=True, refused=True),
    Answer("DeepSeek HTTP 503\nmeşgul", failed=True),
], ids=["refusal", "technical"])
def test_the_box_s_failure_is_written_in_its_own_words(failure):
    """The refusal's sentence, or the error's own text (v9-3): the box already says which."""
    assert answering(FakeBox(failure)) == [step(LOOKING), ("failure", failure.text)]


def test_a_stopped_agent_sends_no_further_round():
    run = FakeRun()

    def stopped_while_out():
        run.halted = True
        return calling(call("read_frame", '{"frame": 2}'))

    box = FakeBox(stopped_while_out, Answer("Hiç gitmemeli."))

    wrote = answering(box, run=run)

    assert len(box.asked) == 1
    assert [line for line in wrote if line[0] in ("answer", "failure")] == []
