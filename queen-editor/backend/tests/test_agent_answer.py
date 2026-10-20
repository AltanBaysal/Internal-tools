"""Queen Editor's agent (madde 420): it reads the open project and answers, through the box.

The loop runs with fakes (CODE-STANDARD, Tests): a box that answers from a list and keeps a copy of
every request as it was sent, the gallery's cards, a picture reader, and a run that writes down what
the agent writes to the chat. No network.

The new modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
import base64
import copy
import json

import pytest

from backend.services.deepseek.box import Answer

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
     "errors": {}, "scene": "", "prompts": {"photo": "mavi elbiseli kadın"}, "negative": ""},
    {"id": "P1_0", "status": "done", "layers": {"photo": "P1_0.png"}, "owed": [],
     "failed": ["video"], "errors": {"video": "ComfyUI: out of memory"}, "scene": "Kadın döner.",
     "prompts": {"photo": "yeşil elbiseli kadın", "video": "she turns"}, "negative": "lowres"},
    {"id": "P0_0", "status": "done", "layers": {"photo": "P0_0.png", "video": "P0_0.mp4"},
     "owed": ["audio"], "failed": [], "errors": {}, "scene": "Kadın tahtta oturur.",
     "prompts": {"photo": "kırmızı elbiseli kadın", "video": "she sits"}, "negative": ""},
]
# What the model is shown of each card before the question, frame 1 first.
LINES = [
    {"frame": 1, "status": "done", "layers": ["photo", "video"], "owed": ["audio"], "failed": []},
    {"frame": 2, "status": "done", "layers": ["photo"], "owed": [], "failed": ["video"]},
    {"frame": 3, "status": "pending", "layers": [], "owed": ["photo"], "failed": []},
]
# Frame 2 whole, the way read_frame gives it: the negative too, which a fix needs (madde 481).
FRAME_2 = {**LINES[1], "errors": {"video": "ComfyUI: out of memory"}, "scene": "Kadın döner.",
           "prompts": {"photo": "yeşil elbiseli kadın", "video": "she turns"}, "negative": "lowres"}
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
    when it was sent.

    A check of a frame (madde 479) is a question of its own, `ask`: it is answered from `checks` the
    same way and kept in `checked`."""

    def __init__(self, *answers, checks=()):
        self.answers = list(answers)
        self.asked = []
        self.checks = list(checks)
        self.checked = []

    def converse(self, messages, tools=()):
        self.asked.append((copy.deepcopy(messages), tools))
        answer = self.answers.pop(0)
        return answer() if callable(answer) else answer

    def ask(self, system, text="", images=()):
        self.checked.append((system, text, list(images)))
        answer = self.checks.pop(0)
        return answer() if callable(answer) else answer


class FakeRun:
    """The question being answered: writes down what the agent writes to the chat.

    A change asked about (madde 480) is written down too, and answered with the next of `permits`;
    an entry may be a function, which runs while the user is asked -- where a stop can land -- and
    returns the answer. A run with no permit left was never meant to be asked: reading is not."""

    def __init__(self, permits=()):
        self.wrote = []
        self.halted = False
        self.permits = list(permits)

    def stopped(self):
        return self.halted

    def permit(self, change):
        self.wrote.append(("permit", change))
        assert self.permits, f"Permission asked where nothing changes: {change}"
        allowed = self.permits.pop(0)
        return allowed() if callable(allowed) else allowed

    def add_step(self, running, done):
        self.wrote.append(("step", running, done))

    def finish_step(self):
        self.wrote.append(("stepDone",))

    def answer(self, text):
        self.wrote.append(("answer", text))

    def fail(self, text):
        self.wrote.append(("failure", text))


class Project:
    """The two readers main.py hands the agent, noting which project each was asked about, and the
    photo feature's fix (madde 481), which answers `fixing` and notes what it was asked."""

    def __init__(self, cards=CARDS, pictures=None, fixing="fixed"):
        self.cards = cards
        self.pictures = {"P0_0.png": PHOTO} if pictures is None else pictures
        self.fixing = fixing
        self.asked = []
        self.fixed = []

    def frames(self, project):
        self.asked.append(("frames", project))
        return copy.deepcopy(self.cards)

    def picture(self, project, file):
        self.asked.append(("picture", project, file))
        return self.pictures.get(file)

    def fix(self, project, seen, prompt, negative):
        self.fixed.append((project, seen, prompt, negative))
        return self.fixing


def answering(box, project=None, earlier=(), question=QUESTION, run=None):
    """The agent answers one question in düğün; what it wrote comes back."""
    from backend.features.agent.domain.usecases.answer_question import answer_question
    project = project or Project()
    run = run or FakeRun()
    answer_question(box, project.frames, project.picture, project.fix, run, "düğün",
                    list(earlier), question)
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
    # The rules of the image model and how a prompt is fixed: the agent decides a fix (madde 481).
    assert system == {"role": "system",
                      "content": prompt().INSTRUCTION + prompt().MIXUP_RULES + prompt().FIX_RULES
                      + prompt().SYSTEM_PROMPT_SUFFIX}
    assert cards["role"] == "system"
    assert frames_of(cards) == (prompt().FRAMES, LINES)
    assert asked == {"role": "user", "content": QUESTION}
    assert offered == tools()
    # Only the project the question was asked in.
    assert project.asked == [("frames", "düğün")]


def test_the_instruction_ends_with_the_prompt_writers_suffix():
    """The user: "aynı suffixi kullansın" -- the agent ends its instruction with the suffix Queen
    AI's prompt writers end theirs with (madde 407). The two are copies, one per feature, and this
    holds them to one text."""
    from backend.features.photo_generation.data.prompt_writer import SYSTEM_PROMPT_SUFFIX
    box = FakeBox(Answer("Projede 3 kare var."))

    answering(box)

    sent = box.asked[0][0][0]["content"]
    assert sent.endswith(SYSTEM_PROMPT_SUFFIX), (
        f"Agent'ın talimatı prompt yazıcılarının suffix'iyle bitmiyor:\n{sent}")
    assert prompt().SYSTEM_PROMPT_SUFFIX == SYSTEM_PROMPT_SUFFIX, (
        "Agent'ın suffix'i prompt yazıcılarınınkiyle aynı değil: queen-editor/backend/features/"
        "photo_generation/data/prompt_writer.py'deki SYSTEM_PROMPT_SUFFIX, "
        "queen-editor/backend/features/agent/domain/prompt.py'ye aynen kopyalanmalı"
    )


def test_the_tools_name_no_project():
    """The user: "sadec açık projeye erişebilir". Three readers, which a frame number is all they
    take, and the fix (madde 481), which takes the frame's whole new prompt and negative."""
    offered = tools()

    assert [tool["function"]["name"] for tool in offered] == ["read_frame", "look_at_frame",
                                                              "check_frame", "fix_frame"]
    for tool in offered:
        assert tool["type"] == "function"
        parameters = tool["function"]["parameters"]
        assert parameters["properties"]["frame"]["type"] == "integer"
    for tool in offered[:3]:
        parameters = tool["function"]["parameters"]
        assert list(parameters["properties"]) == ["frame"]
        assert parameters["required"] == ["frame"]
    fix = offered[3]["function"]["parameters"]
    assert list(fix["properties"]) == fix["required"] == ["frame", "prompt", "negative"]
    assert fix["properties"]["prompt"]["type"] == fix["properties"]["negative"]["type"] == "string"


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


# --- the mix-up check (madde 479) ----------------------------------------------------------------
#
# check_frame compares one frame's photo with the prompt it was made from, in a question of its own
# through the box: the conversation is told the verdict in words, and never holds the picture.

# Frame 2's photo is on disk for these tests; frame 1 has a video, frame 3 no photo.
PHOTO_2 = b"PNG2"
MIXED = "MIXED: the woman has white hair in the photo; the prompt gives white hair to the man."


def checking(number):
    return (f"{number} numaralı kareyi prompt'uyla karşılaştırıyor…",
            f"{number} numaralı kareyi prompt'uyla karşılaştırdı")


def check_instruction():
    return prompt().MIXUP_RULES + prompt().MIXUP_CHECK + prompt().SYSTEM_PROMPT_SUFFIX


def with_photo_2():
    return Project(pictures={"P0_0.png": PHOTO, "P1_0.png": PHOTO_2})


def test_check_frame_asks_about_the_photo_and_its_prompt_and_tells_the_verdict_in_words():
    box = FakeBox(calling(call("check_frame", '{"frame": 2}')), Answer("2 numaralı karede karışma var."),
                  checks=[Answer(MIXED)])
    project = with_photo_2()

    wrote = answering(box, project)

    assert box.checked == [(check_instruction(), "Prompt: yeşil elbiseli kadın",
                            [("P1_0.png", PHOTO_2)])]
    messages, _tools = box.asked[1]
    assert messages[4] == {"role": "tool", "tool_call_id": "call_1", "content": f"Frame 2: {MIXED}"}
    # The verdict is words: no picture enters the conversation, so none is sent again.
    assert len(messages) == 5
    assert project.asked == [("frames", "düğün"), ("picture", "düğün", "P1_0.png")]
    assert wrote == [step(LOOKING), DONE, step(checking(2)),
                     ("answer", "2 numaralı karede karışma var.")]


def test_a_frame_with_a_video_is_not_checked():
    """The user's choice: a frame with a video is not touched -- nothing is read and nothing is
    asked, and the agent lists it as skipped."""
    box = FakeBox(calling(call("check_frame", '{"frame": 1}')), Answer("1 atlandı."))
    project = Project()

    wrote = answering(box, project)

    assert box.checked == []
    assert project.asked == [("frames", "düğün")]
    assert box.asked[1][0][4]["content"] == "Frame 1 has a video, so it is not checked."
    assert wrote == [step(LOOKING), ("answer", "1 atlandı.")]


def test_a_frame_whose_video_failed_has_no_video_and_is_checked():
    """A failed layer stays in the card's layers (a failed slot is taken), but no video was made."""
    cards = [{"id": "P0_0", "status": "done",
              "layers": {"photo": "P0_0.png", "video": "P0_0.mp4"}, "owed": [],
              "failed": ["video"], "errors": {"video": "ComfyUI: out of memory"}, "scene": "",
              "prompts": {"photo": "kırmızı elbiseli kadın"}}]
    box = FakeBox(calling(call("check_frame", '{"frame": 1}')), Answer("Karışma yok."),
                  checks=[Answer("OK")])

    answering(box, Project(cards=cards))

    assert box.checked == [(check_instruction(), "Prompt: kırmızı elbiseli kadın",
                            [("P0_0.png", PHOTO)])]
    assert box.asked[1][0][4]["content"] == "Frame 1: OK"


def one_card(**changes):
    """A done frame with a photo and its prompt, and no video -- changed where a test says."""
    return [{"id": "P0_0", "status": "done", "layers": {"photo": "P0_0.png"}, "owed": [],
             "failed": [], "errors": {}, "scene": "", "prompts": {"photo": "kırmızı elbiseli kadın"},
             **changes}]


@pytest.mark.parametrize("cards, number, said", [
    (CARDS, 3, "Frame 3 has no photo."),
    (one_card(prompts={}), 1, "Frame 1 has no photo prompt to compare the photo with."),
    (one_card(failed=["photo"], errors={"photo": "ComfyUI: out of memory"}), 1,
     "The photo of frame 1 failed, so there is nothing to compare."),
], ids=["no-photo-layer", "no-prompt", "failed-photo"])
def test_a_frame_with_nothing_to_compare_is_not_read_asked_or_shown(cards, number, said):
    """Read off the card alone: the photo is not read, Queen AI is not asked, and since nothing was
    read there is no step. The frame's own prompt is the truth, so a photo without one has nothing to
    be compared with; a failed photo is in the layers (a failed slot is taken), but no photo was
    made."""
    box = FakeBox(calling(call("check_frame", json.dumps({"frame": number}))), Answer("Atlandı."))
    project = Project(cards=cards)

    wrote = answering(box, project)

    assert box.checked == []
    assert project.asked == [("frames", "düğün")]
    assert box.asked[1][0][4]["content"] == said
    assert wrote == [step(LOOKING), ("answer", "Atlandı.")]


def test_a_photo_missing_on_disk_is_read_and_not_asked_about():
    """Frame 2 has a photo layer and a prompt, but its file is not on disk."""
    box = FakeBox(calling(call("check_frame", '{"frame": 2}')), Answer("2'nin fotoğrafı yok."))
    project = Project()

    wrote = answering(box, project)

    assert box.checked == []
    assert project.asked == [("frames", "düğün"), ("picture", "düğün", "P1_0.png")]
    assert box.asked[1][0][4]["content"] == "Frame 2 has no photo."
    assert wrote == [step(LOOKING), DONE, step(checking(2)), ("answer", "2'nin fotoğrafı yok.")]


def test_a_photo_that_cannot_be_read_is_that_frame_s_line_and_the_agent_goes_on():
    """Drive's own words, and the verdicts before it are kept: the question does not end."""
    class Unreadable(Project):
        def picture(self, project, file):
            raise OSError(107, "Transport endpoint is not connected")

    box = FakeBox(calling(call("check_frame", '{"frame": 2}')), Answer("2 okunamadı."))

    wrote = answering(box, Unreadable())

    assert box.checked == []
    assert box.asked[1][0][4]["content"] == ("The photo of frame 2 could not be read: "
                                             "[Errno 107] Transport endpoint is not connected")
    assert wrote[-1] == ("answer", "2 okunamadı.")


def test_the_frame_s_step_is_on_the_chat_before_queen_ai_is_asked():
    """The chat says what goes on while it goes on: a check can take a while."""
    run = FakeRun()
    seen = []

    def asked_while_out():
        seen.append(list(run.wrote))
        return Answer("OK")

    box = FakeBox(calling(call("check_frame", '{"frame": 2}')), Answer("Karışma yok."),
                  checks=[asked_while_out])

    answering(box, with_photo_2(), run=run)

    assert seen == [[step(LOOKING), DONE, step(checking(2))]]


def test_a_refused_check_is_that_frame_s_line_and_the_agent_goes_on():
    """A refusal is the frame's answer: another frame may well be answered."""
    box = FakeBox(calling(call("check_frame", '{"frame": 2}')), Answer("2 kontrol edilemedi."),
                  checks=[Answer(REFUSED, failed=True, refused=True)])

    wrote = answering(box, with_photo_2())

    assert box.asked[1][0][4]["content"] == f"The check of frame 2 failed: {REFUSED}"
    assert wrote[-1] == ("answer", "2 kontrol edilemedi.")


def test_a_technical_failure_of_a_check_ends_the_question_in_its_own_words():
    """The service is down, and every later check would meet it: the question fails the way a
    failed round does, and no further check or round is sent."""
    box = FakeBox(calling(call("check_frame", '{"frame": 2}', "call_1"),
                          call("check_frame", '{"frame": 2}', "call_2")),
                  checks=[Answer("DeepSeek HTTP 503\nmeşgul", failed=True), Answer("OK")])

    wrote = answering(box, with_photo_2())

    assert len(box.checked) == 1
    assert len(box.asked) == 1
    assert wrote == [step(LOOKING), DONE, step(checking(2)),
                     ("failure", "DeepSeek HTTP 503\nmeşgul")]


def test_a_stop_between_two_calls_of_one_round_sends_nothing_more():
    """A check is a paid request: a stop that lands during one leaves the round's other calls
    unasked."""
    run = FakeRun()

    def stopped_while_out():
        run.halted = True
        return Answer("OK")

    box = FakeBox(calling(call("check_frame", '{"frame": 2}', "call_1"),
                          call("check_frame", '{"frame": 2}', "call_2")),
                  Answer("Hiç gitmemeli."), checks=[stopped_while_out, Answer("OK")])

    answering(box, with_photo_2(), run=run)

    assert len(box.checked) == 1
    assert len(box.asked) == 1


# --- the permission gate (madde 480) -------------------------------------------------------------
#
# A call that would change something comes with what it would change, and runs only once the user
# allows it; the agent is never told that permission exists. The gate is held apart from 481's fix:
# a fake fix_frame stands in front of the loop's run_tool here, and here alone.

FIXING = ("2 numaralı kareyi düzeltiyor…", "2 numaralı kareyi düzeltti")
# The shape 481's fix fills in: a title naming the frame, then the details, each either what it was
# and what it becomes, or a sentence.
CHANGE = {"title": "2 numaralı kare düzeltilecek",
          "details": [{"label": "Prompt", "before": "yeşil elbiseli kadın",
                       "after": "mavi elbiseli kadın"},
                      {"label": "Fotoğraf",
                       "text": "Eski fotoğraf silinecek; yenisi aynı yerde üretilecek."}]}
REJECTED = "The user rejected this change, so nothing was changed."


@pytest.fixture
def fix_frame(monkeypatch):
    """A stand-in for fix_frame: its change is CHANGE, and its work writes down the call it was run
    for in the list handed back. Any other call goes to the real tools."""
    from backend.features.agent.domain.usecases import answer_question as loop
    real = loop.run_tool
    changed = []

    def run_tool(ask, frames, picture, fix, project, call):
        if call["function"]["name"] != "fix_frame":
            return real(ask, frames, picture, fix, project, call)

        def work():
            changed.append(call["id"])
            return "Frame 2 was fixed.", None

        return FIXING, work, CHANGE

    monkeypatch.setattr(loop, "run_tool", run_tool)
    return changed


def test_a_change_is_asked_about_before_its_step_and_runs_once_allowed(fix_frame):
    """The step before it is done -- the model read it to ask for this -- so what is on the screen
    while the user decides is the change alone."""
    box = FakeBox(calling(call("fix_frame", '{"frame": 2}')), Answer("2 düzeltildi."))
    run = FakeRun(permits=[True])

    wrote = answering(box, run=run)

    assert wrote == [step(LOOKING), DONE, ("permit", CHANGE), step(FIXING),
                     ("answer", "2 düzeltildi.")]
    assert fix_frame == ["call_1"]
    assert box.asked[1][0][4] == {"role": "tool", "tool_call_id": "call_1",
                                  "content": "Frame 2 was fixed."}


def test_a_rejected_change_changes_nothing_the_agent_is_told_and_goes_on(fix_frame):
    """The user: "reddedilirse hiçbir şey değişmez ve ajana 'kullanıcı reddetti' döner". No step
    either: nothing was done. The round's next call runs as it would have."""
    box = FakeBox(calling(call("fix_frame", '{"frame": 2}', "call_1"),
                          call("read_frame", '{"frame": 2}', "call_2")),
                  Answer("Reddettin, 2'ye dokunmadım."))
    run = FakeRun(permits=[False])

    wrote = answering(box, run=run)

    assert fix_frame == []
    messages = box.asked[1][0]
    assert messages[4] == {"role": "tool", "tool_call_id": "call_1", "content": REJECTED}
    assert json.loads(messages[5]["content"]) == FRAME_2
    assert wrote == [step(LOOKING), DONE, ("permit", CHANGE), DONE, step(reading(2)),
                     ("answer", "Reddettin, 2'ye dokunmadım.")]


def test_a_stop_while_the_user_is_asked_changes_nothing_and_sends_nothing_more(fix_frame):
    """■ while the question is on the screen: a rejection, and the end of the question."""
    run = FakeRun()

    def stopped_while_asked():
        run.halted = True
        return False

    run.permits = [stopped_while_asked]
    box = FakeBox(calling(call("fix_frame", '{"frame": 2}', "call_1"),
                          call("read_frame", '{"frame": 2}', "call_2")),
                  Answer("Hiç gitmemeli."))

    wrote = answering(box, run=run)

    assert fix_frame == []
    assert len(box.asked) == 1
    assert wrote == [step(LOOKING), DONE, ("permit", CHANGE)]


def test_a_stop_after_the_change_is_allowed_and_before_its_work_changes_nothing(fix_frame):
    """■ lands while the allowed change's step is being written: the work never begins."""
    class StoppedAsTheStepIsWritten(FakeRun):
        def add_step(self, running, done):
            super().add_step(running, done)
            if ("permit", CHANGE) in self.wrote:
                self.halted = True

    box = FakeBox(calling(call("fix_frame", '{"frame": 2}')), Answer("Hiç gitmemeli."))
    run = StoppedAsTheStepIsWritten(permits=[True])

    answering(box, run=run)

    assert fix_frame == []
    assert len(box.asked) == 1


def test_each_change_of_a_round_is_asked_about_on_its_own(fix_frame):
    """481 fixes frame after frame: one answer never stands for the next change."""
    box = FakeBox(calling(call("fix_frame", '{"frame": 2}', "call_1"),
                          call("fix_frame", '{"frame": 2}', "call_2")),
                  Answer("Biri düzeltildi."))
    run = FakeRun(permits=[False, True])

    wrote = answering(box, run=run)

    assert fix_frame == ["call_2"]
    assert [line[0] for line in wrote].count("permit") == 2


def test_reading_tools_run_without_asking():
    """FakeRun refuses a permission it was not given: the three readers ask none."""
    box = FakeBox(calling(call("read_frame", '{"frame": 2}', "call_1"),
                          call("look_at_frame", '{"frame": 1}', "call_2"),
                          call("check_frame", '{"frame": 2}', "call_3")),
                  Answer("Okudum."), checks=[Answer("OK")])

    wrote = answering(box, with_photo_2())

    assert wrote[-1] == ("answer", "Okudum.")
    assert not [line for line in wrote if line[0] == "permit"]


# --- the fix (madde 481) -------------------------------------------------------------------------
#
# fix_frame changes a frame's prompt and negative, and the photo feature makes its photo again in the
# frame's own place. One call per frame, behind the gate; the agent goes on without waiting for the
# photo. Frame 2 is fixable: a photo, its prompt, and a video that failed -- no video was made.

NEW_PROMPT = "mavi elbiseli kadın"
NEW_NEGATIVE = "lowres, white hair"
PHOTO_LINE = {"label": "Fotoğraf", "text": "Eski fotoğraf silinecek; yenisi aynı yerde üretilecek."}


def fixing(number, prompt=NEW_PROMPT, negative=NEW_NEGATIVE, call_id="call_1"):
    return call("fix_frame", json.dumps({"frame": number, "prompt": prompt, "negative": negative},
                                        ensure_ascii=False), call_id)


def fix_step(number):
    """The finished sentence says the fix was handled, not that it succeeded: the step is written
    before the work, and the work may find the frame changed."""
    return (f"{number} numaralı kareyi düzeltiyor…", f"{number} numaralı karenin düzeltmesini işledi")


def test_a_fix_shows_what_changes_waits_for_the_user_and_hands_the_frame_to_the_photo_feature():
    """The user: "prompt'u güncelle ... eski fotoyu sil runı başlat sonraki fotoya geçe". The change
    names each field before and after, and the frame goes as the change was described from it, so
    the photo feature can tell whether it is still that frame."""
    box = FakeBox(calling(fixing(2)), Answer("2 düzeltildi."))
    project = Project()

    wrote = answering(box, project, run=FakeRun(permits=[True]))

    change = {"title": "2 numaralı kare düzeltilecek",
              "details": [{"label": "Prompt", "before": "yeşil elbiseli kadın", "after": NEW_PROMPT},
                          {"label": "Negatif prompt", "before": "lowres", "after": NEW_NEGATIVE},
                          PHOTO_LINE]}
    assert wrote == [step(LOOKING), DONE, ("permit", change), step(fix_step(2)),
                     ("answer", "2 düzeltildi.")]
    assert project.fixed == [("düğün", CARDS[1], NEW_PROMPT, NEW_NEGATIVE)]
    assert box.asked[1][0][4] == {
        "role": "tool", "tool_call_id": "call_1",
        "content": "Frame 2 was fixed: its prompt and negative were changed, its old photo was "
                   "deleted, and its new photo is in the queue in the frame's own place."}


def test_a_field_that_does_not_change_is_left_off_the_change():
    box = FakeBox(calling(fixing(2, prompt="yeşil elbiseli kadın")), Answer("2 düzeltildi."))
    run = FakeRun(permits=[True])

    answering(box, run=run)

    (asked,) = [line[1] for line in run.wrote if line[0] == "permit"]
    assert asked["details"] == [{"label": "Negatif prompt", "before": "lowres",
                                 "after": NEW_NEGATIVE}, PHOTO_LINE]


def test_space_around_the_words_is_not_a_change_and_does_not_reach_the_frame():
    box = FakeBox(calling(fixing(2, prompt=f"  {NEW_PROMPT}\n", negative=" lowres ")),
                  Answer("2 düzeltildi."))
    project = Project()
    run = FakeRun(permits=[True])

    answering(box, project, run=run)

    (asked,) = [line[1] for line in run.wrote if line[0] == "permit"]
    assert [detail["label"] for detail in asked["details"]] == ["Prompt", "Fotoğraf"]
    assert project.fixed[0][2:] == (NEW_PROMPT, "lowres")


def test_a_rejected_fix_hands_nothing_to_the_photo_feature():
    box = FakeBox(calling(fixing(2)), Answer("Dokunmadım."))
    project = Project()

    answering(box, project, run=FakeRun(permits=[False]))

    assert project.fixed == []
    assert box.asked[1][0][4]["content"] == REJECTED


@pytest.mark.parametrize("fixing_said, told", [
    ("waiting", "Frame 2 was fixed: its prompt and negative were changed and its old photo was "
                "deleted, but another project's generation is running now, so its new photo waits "
                "in the queue until this project's queue runs."),
    ("changed", "Frame 2 changed after you read it, so nothing was changed. It is read again at "
                "the user's next question; do not call fix_frame on it again now."),
    ("linked", "Frame 2 is where another frame's queued video ends, so it is not changed."),
], ids=["another-project-runs", "frame-changed", "linked-video-target"])
def test_what_the_photo_feature_says_is_what_the_model_is_told(fixing_said, told):
    box = FakeBox(calling(fixing(2)), Answer("Tamam."))

    answering(box, Project(fixing=fixing_said), run=FakeRun(permits=[True]))

    assert box.asked[1][0][4]["content"] == told


def test_frames_are_fixed_one_by_one_each_asked_about_on_its_own():
    """The agent does not wait for a photo: the round's next frame is asked about at once."""
    cards = [{**CARDS[1], "id": "P1_0"}, {**CARDS[1], "id": "P0_0", "layers": {"photo": "P0_0.png"}}]
    box = FakeBox(calling(fixing(1, call_id="call_1"), fixing(2, call_id="call_2")),
                  Answer("İkisi düzeltildi."))
    project = Project(cards=cards)

    wrote = answering(box, project, run=FakeRun(permits=[True, True]))

    assert [seen["id"] for _project, seen, _prompt, _negative in project.fixed] == ["P0_0", "P1_0"]
    assert [line[0] for line in wrote].count("permit") == 2


@pytest.mark.parametrize("cards, number, said", [
    (CARDS, 1, "Frame 1 has a video, so it is not changed."),
    (one_card(owed=["video"]), 1, "Frame 1 has a video in the queue, so it is not changed."),
    (CARDS, 3, "Frame 3 has no photo to fix."),
    (one_card(failed=["photo"]), 1, "Frame 1 has no photo to fix."),
    (one_card(prompts={}), 1, "Frame 1 has no photo prompt to fix."),
    (one_card(negative=NEW_NEGATIVE, prompts={"photo": NEW_PROMPT}), 1,
     "Frame 1 already has this prompt and negative, so nothing would change."),
], ids=["video", "video-queued", "no-photo", "failed-photo", "no-prompt", "nothing-changes"])
def test_a_frame_that_is_not_fixed_is_told_from_its_card_with_no_question_and_no_step(
        cards, number, said):
    """The user: "Videosu olan kareye ajan dokunmasın" -- and a video in the queue would be made from a
    photo deleted under it (ana ajan, 20 Ekim), so the agent lists it as "videosu sırada, atlandı"."""
    box = FakeBox(calling(fixing(number)), Answer("Atlandı."))
    project = Project(cards=cards)

    wrote = answering(box, project)

    assert project.fixed == []
    assert box.asked[1][0][4]["content"] == said
    assert wrote == [step(LOOKING), ("answer", "Atlandı.")]


@pytest.mark.parametrize("arguments", [
    {"frame": 2, "negative": "x"},
    {"frame": 2, "prompt": "  ", "negative": "x"},
    {"frame": 2, "prompt": 3, "negative": "x"},
    {"frame": 2, "prompt": "p"},
    {"frame": 2, "prompt": "p", "negative": None},
], ids=["no-prompt", "empty-prompt", "number-prompt", "no-negative", "null-negative"])
def test_a_fix_without_its_words_is_told_what_it_needs(arguments):
    box = FakeBox(calling(call("fix_frame", json.dumps(arguments))), Answer("Tamam."))
    project = Project()

    wrote = answering(box, project)

    assert project.fixed == []
    assert box.asked[1][0][4]["content"] == (
        "A fix needs the frame's whole new prompt, which cannot be empty, and its whole new "
        "negative prompt, which can.")
    assert wrote == [step(LOOKING), ("answer", "Tamam.")]


def test_the_fix_rules_say_the_three_fixes_queen_agent_names():
    """479 left them out of the check, which only finds; the agent decides a fix with them (copied
    from QueenAgent's Rule 4, Rule 5 and Step 8, not imported)."""
    rules = prompt().FIX_RULES

    assert "remove the extra part" in rules
    assert "make the part simpler, and keep the same moment" in rules
    assert "remove the hidden tag" in rules
    assert "remove the extra part" not in prompt().MIXUP_RULES
