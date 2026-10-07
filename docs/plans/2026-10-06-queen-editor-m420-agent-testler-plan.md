# Madde 420 — Queen Editor'ün agent'ı, test turunun planı

> **Koşum:** bu oturumda, satır satır, madde 420'nin kendi dalında. Testler yazılır, dört satır
> koşulur, yeni testlerin kırmızısı görülür, ve kırmızı hâliyle commit'lenir.

**Hedef:** Agent'ın yalnız açık projeyi okuyup soruyu kutudan cevapladığını, en çok 32 tur koştuğunu,
adımlarını ve sonucunu sohbete yazdığını, sunucuda çalıştığını, durdurulduğunu, ve 425'in üç kapısını
anlatan testler.

**Yaklaşım:** Döngü sahte kutu, sahte kartlar ve sahte `run`'la; koşucu sahte kayıt ve bekletilen
işlerle; kapılar `main.py`'nin bağlamasıyla elle, gerçek kayıtla; `main.py` gerçek DeepSeek
istemcisi ve sahte `requests.post`'la. Kaydın kilidi gerçek iş parçacıklarıyla.

**Araçlar:** pytest (`parametrize`), `threading`.

**Spec:** [m420 test turu](../specs/2026-10-06-queen-editor-m420-agent-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**; kullanıcının gördüğü metin Türkçe, modelin okuduğu
  İngilizce.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod değişmiyor.
- Hiçbir test ağa çıkmaz; tek gerçek bekleme kilit testinin 0,2 saniyesi.
- Yeni modüller testlerin içinde import edilir: yokken testler çağırdıkları yerde kırmızıya düşer,
  toplanırken değil.
- Cümleler testlerde harfi harfine durur: *"Projeye bakıyor…"* / *"Projeye baktı"*, *"N numaralı
  kareyi okuyor…"* / *"…okudu"*, *"N numaralı karenin görseline bakıyor…"* / *"…baktı"*, tasarımcının
  karesiz proje cümlesi, *"Soru boş."*, *"Bu sohbette agent hâlâ çalışıyor."*.

**Arayüz — uygulama turunun vereceği:**
- `backend.features.agent.domain.usecases.answer_question.answer_question(box, frames, picture, run,
  project, earlier, question)`.
- `backend.features.agent.domain.prompt` — `INSTRUCTION`, `SYSTEM_PROMPT_SUFFIX`, `LAST_ROUND`,
  `FRAMES` (tek satır).
- `backend.features.agent.domain.tools.TOOLS`.
- `backend.features.agent.runner.AgentRunner(record, spawn=None)` — `start(project, chat_id, text, at,
  work) -> bool`, `stop(project, chat_id)`, `working(project) -> list[int]`.
- `backend.features.agent.domain.usecases.chats` — `ask_question(record, runner, agent, now, project,
  chat_id, text)`, `stop_agent(record, runner, project, chat_id)`, `working_chats(record, runner,
  project)`.
- `backend.features.agent.presentation.routes.make_agent_blueprint(ask_question, stop_agent,
  working_chats)`.
- `backend.main._agent(run, project, earlier, question)`.

---

## Görev 1: `backend/tests/test_agent_answer.py` — döngü

**Dosya:** Oluştur: `queen-editor/backend/tests/test_agent_answer.py`

- [ ] **Adım 1: Dosyanın tamamı.**

```python
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
```

## Görev 2: `backend/tests/test_agent_runner.py` — koşucu

**Dosya:** Oluştur: `queen-editor/backend/tests/test_agent_runner.py`

- [ ] **Adım 1: Dosyanın tamamı.**

```python
"""Which chats' agents are working, and what a run may still write (madde 420).

The agent runs on the server: it goes on when the panel closes or the page reloads, two chats may
run at once, a working chat takes no second question, and a stop lands at once -- whatever the run
writes after it lands nowhere.

Tried with a fake record and with the work held back: `spawn` puts the work in a list and the test
runs it when it wants -- the moment a request would be out -- so nothing waits on a real thread.

The new module is imported inside the tests: it is written after this file, and an import at the top
would stop the whole collection instead of failing these questions.
"""
import pytest

ASKED = "2026-10-06T10:00:00+00:00"
READING = ("2 numaralı kareyi okuyor…", "2 numaralı kareyi okudu")
REFUSED = "Model hata döndü, farklı şekilde dene."


class FakeRecord:
    """Writes down every line, as (what, project, chat, *the rest)."""

    def __init__(self):
        self.lines = []

    def add_question(self, project, chat_id, text, at):
        self.lines.append(("question", project, chat_id, text, at))

    def add_step(self, project, chat_id, running, done):
        self.lines.append(("step", project, chat_id, running, done))

    def finish_step(self, project, chat_id):
        self.lines.append(("stepDone", project, chat_id))

    def answer(self, project, chat_id, text):
        self.lines.append(("answer", project, chat_id, text))

    def fail(self, project, chat_id, text):
        self.lines.append(("failure", project, chat_id, text))

    def stop(self, project, chat_id):
        self.lines.append(("stopped", project, chat_id))


@pytest.fixture
def record():
    return FakeRecord()


@pytest.fixture
def held():
    """The work started and not yet run."""
    return []


@pytest.fixture
def runner(record, held):
    from backend.features.agent.runner import AgentRunner
    return AgentRunner(record, spawn=held.append)


def answers(text):
    """Work that reads a frame and answers."""
    def work(run):
        run.add_step(*READING)
        run.answer(text)
    return work


def test_starting_writes_the_question_and_the_chat_is_working(runner, record, held):
    assert runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("3 kare.")) is True

    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED)]
    assert runner.working("düğün") == [1]
    assert len(held) == 1


def test_a_working_chat_takes_no_second_question(runner, record, held):
    runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("3 kare."))

    assert runner.start("düğün", 1, "Peki 7?", ASKED, answers("7 hazır.")) is False

    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED)]
    assert len(held) == 1


def test_two_chats_work_at_once_in_one_project_or_two(runner, held):
    for project, chat in (("düğün", 2), ("düğün", 1), ("kına", 1)):
        assert runner.start(project, chat, "Kaç kare var?", ASKED, answers("3 kare.")) is True

    assert runner.working("düğün") == [1, 2]
    assert runner.working("kına") == [1]
    assert len(held) == 3


@pytest.mark.parametrize("end, line", [
    (lambda run: run.answer("3 kare."), ("answer", "düğün", 1, "3 kare.")),
    (lambda run: run.fail(REFUSED), ("failure", "düğün", 1, REFUSED)),
], ids=["answer", "failure"])
def test_an_answer_or_a_failure_ends_the_work(runner, record, held, end, line):
    def work(run):
        run.add_step(*READING)
        run.finish_step()
        end(run)

    runner.start("düğün", 1, "Kaç kare var?", ASKED, work)
    held.pop()()

    assert record.lines[1:] == [("step", "düğün", 1, *READING), ("stepDone", "düğün", 1), line]
    assert runner.working("düğün") == []


def test_work_that_raises_fails_in_its_own_words(runner, record, held):
    """A disk that went away, a project deleted under the agent: the error's own words, never a
    guessed cause."""
    def work(run):
        raise OSError("[Errno 107] Transport endpoint is not connected")

    runner.start("düğün", 1, "Kaç kare var?", ASKED, work)
    held.pop()()

    assert record.lines[-1] == ("failure", "düğün", 1,
                                "[Errno 107] Transport endpoint is not connected")
    assert runner.working("düğün") == []


def test_a_stop_is_written_at_once_and_nothing_after_it_lands(runner, record, held):
    """The request out when the stop is pressed cannot be cut -- the box waits on it -- so what it
    brings back is dropped: no half an answer is ever written (BEHAVIOUR.md, Agent panel)."""
    seen = []

    def work(run):
        seen.append(run.stopped())
        run.add_step(*READING)
        run.answer("Yarım kalan cevap.")

    runner.start("düğün", 1, "Kaç kare var?", ASKED, work)
    runner.stop("düğün", 1)

    assert record.lines[-1] == ("stopped", "düğün", 1)
    assert runner.working("düğün") == []

    held.pop()()

    assert seen == [True]
    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED),
                            ("stopped", "düğün", 1)]


@pytest.mark.parametrize("answered", [False, True], ids=["never-asked", "already-answered"])
def test_stopping_a_chat_that_is_not_working_writes_nothing(runner, record, held, answered):
    """A ■ that lands as the answer arrives must not turn the answer into "Durduruldu"."""
    if answered:
        runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("3 kare."))
        held.pop()()
    before = list(record.lines)

    runner.stop("düğün", 1)

    assert record.lines == before


def test_a_stopped_chat_takes_a_new_question_and_the_old_work_writes_nothing(runner, record, held):
    runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("Eski cevap."))
    runner.stop("düğün", 1)

    assert runner.start("düğün", 1, "Peki 7?", ASKED, answers("7 hazır.")) is True

    old, new = held
    old()
    assert runner.working("düğün") == [1]
    new()
    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED),
                            ("stopped", "düğün", 1),
                            ("question", "düğün", 1, "Peki 7?", ASKED),
                            ("step", "düğün", 1, *READING),
                            ("answer", "düğün", 1, "7 hazır.")]
    assert runner.working("düğün") == []
```

## Görev 3: `backend/tests/test_agent_routes.py` — kapılar

**Dosya:** Oluştur: `queen-editor/backend/tests/test_agent_routes.py`

- [ ] **Adım 1: Dosyanın tamamı.**

```python
"""The agent at the door (madde 420): a question asked, the agent stopped, and which chats' agents
are working -- the doors the screen (425) calls.

Wired by hand over a temp folder, the wiring main.py does: the real chat record, the real runner, the
real loop, and a fake box. The gallery's cards come from a fake, the way main.py hands the photo
feature's answer in. The work runs inline where only its end matters, and is held back where the
test has to look while the agent is at work.

The new modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
import copy
from functools import partial

import pytest

from backend.services.deepseek.box import Answer
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

ASKED = "2026-10-06T10:00:00+00:00"
CHATS = "/api/projects/düğün/chats"
QUESTIONS = f"{CHATS}/1/questions"
STOP = f"{CHATS}/1/stop"
WORKING = f"{CHATS}/working"
REFUSED = "Model hata döndü, farklı şekilde dene."
NO_FRAMES = ("Projede henüz kare yok. Prompt'ları yazıp kuyruğa eklediğinde kareler galeride "
             "belirir; sonra sorularını kareler üzerinden cevaplayabilirim.")
# düğün's gallery, top first: P0_0 is frame 1, P1_0 is frame 2.
CARDS = [
    {"id": "P1_0", "status": "done", "layers": {"photo": "P1_0.png"}, "owed": [], "failed": [],
     "errors": {}, "scene": "", "prompts": {"photo": "yeşil elbiseli kadın"}},
    {"id": "P0_0", "status": "done", "layers": {"photo": "P0_0.png"}, "owed": [], "failed": [],
     "errors": {}, "scene": "", "prompts": {"photo": "kırmızı elbiseli kadın"}},
]


def finished(running, done):
    return {"running": running, "done": done, "finished": True}


LOOKED = finished("Projeye bakıyor…", "Projeye baktı")
READ_2 = finished("2 numaralı kareyi okuyor…", "2 numaralı kareyi okudu")
LOOKED_AT_1 = finished("1 numaralı karenin görseline bakıyor…",
                       "1 numaralı karenin görseline baktı")


def call(name, frame, call_id="call_1"):
    return {"id": call_id, "type": "function",
            "function": {"name": name, "arguments": f'{{"frame": {frame}}}'}}


def calling(*calls):
    return Answer("", tool_calls=list(calls))


class FakeBox:
    """Answers each request with the next of `answers`; an entry may be a function, which runs while
    the request is out and returns the answer. Keeps every request as it was sent."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.asked = []

    def converse(self, messages, tools=()):
        self.asked.append((copy.deepcopy(messages), tools))
        answer = self.answers.pop(0)
        return answer() if callable(answer) else answer


def app_over(drive, dist, box, cards=CARDS, hold=False):
    """(client, held) over `drive`, wired the way main.py wires it -- built again over the same
    folder, it is a restart. With `hold`, the work started waits in `held` until the test runs it."""
    from backend.features.agent.data.chat_record import DriveChatRecord
    from backend.features.agent.domain.usecases import chats
    from backend.features.agent.domain.usecases.answer_question import answer_question
    from backend.features.agent.presentation.routes import (
        make_agent_blueprint,
        make_chats_blueprint,
    )
    from backend.features.agent.runner import AgentRunner
    record = DriveChatRecord(DriveStorage(str(drive)))
    held = []
    runner = AgentRunner(record, spawn=held.append if hold else lambda work: work())
    agent = partial(answer_question, box, lambda project: copy.deepcopy(cards),
                    lambda project, file: b"PNG")
    app = create_app(dist_dir=str(dist), blueprints=[
        make_chats_blueprint(new_chat=partial(chats.new_chat, record),
                             list_chats=partial(chats.list_chats, record),
                             open_chat=partial(chats.open_chat, record)),
        make_agent_blueprint(ask_question=partial(chats.ask_question, record, runner, agent,
                                                  lambda: ASKED),
                             stop_agent=partial(chats.stop_agent, record, runner),
                             working_chats=partial(chats.working_chats, record, runner)),
    ])
    return app.test_client(), held


@pytest.fixture
def dist(tmp_path):
    folder = tmp_path / "dist"
    folder.mkdir()
    (folder / "index.html").write_text("x", encoding="utf-8")
    return folder


@pytest.fixture
def drive(tmp_path):
    """A root holding one project, düğün."""
    root = tmp_path / "drive"
    (root / "düğün").mkdir(parents=True)
    return root


def opened(client, chat=1):
    return client.get(f"{CHATS}/{chat}").get_json()


def test_a_question_is_answered_by_reading_the_project(drive, dist):
    box = FakeBox(calling(call("read_frame", 2, "call_1"), call("look_at_frame", 1, "call_2")),
                  Answer("2 numaralı karede yeşil elbiseli bir kadın var."))
    client, _held = app_over(drive, dist, box)
    client.post(CHATS)

    response = client.post(QUESTIONS, json={"text": "2 numaralı karede ne var?"})

    whole = {"id": 1, "questions": [{
        "text": "2 numaralı karede ne var?", "askedAt": ASKED,
        "steps": [LOOKED, READ_2, LOOKED_AT_1],
        "outcome": {"kind": "answer", "text": "2 numaralı karede yeşil elbiseli bir kadın var."}}]}
    assert response.status_code == 200
    assert response.get_json() == whole
    assert opened(client) == whole


def test_the_door_returns_at_once_and_the_answer_lands_later(drive, dist):
    """The agent runs on the server: the page that asked can close, reload or go elsewhere."""
    client, held = app_over(drive, dist, FakeBox(Answer("Projede 2 kare var.")), hold=True)
    client.post(CHATS)

    response = client.post(QUESTIONS, json={"text": "Kaç kare var?"})

    assert response.status_code == 200
    assert response.get_json()["questions"][0]["outcome"] is None
    assert client.get(WORKING).get_json() == {"working": [1]}
    # The page reloaded: the chat is read again, and the agent is still at it.
    assert opened(client)["questions"][0]["outcome"] is None

    held.pop()()

    question = opened(client)["questions"][0]
    assert question["steps"] == [LOOKED]
    assert question["outcome"] == {"kind": "answer", "text": "Projede 2 kare var."}
    assert client.get(WORKING).get_json() == {"working": []}


def test_a_working_chat_takes_no_second_question(drive, dist):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Kaç kare var?"})

    response = client.post(QUESTIONS, json={"text": "Peki 7?"})

    assert response.status_code == 409
    assert response.get_json() == {"error": "Bu sohbette agent hâlâ çalışıyor."}
    assert [question["text"] for question in opened(client)["questions"]] == ["Kaç kare var?"]


def test_two_chats_work_at_once(drive, dist):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Birinci"})
    # Chat 1 has a question now, so a new chat is a new one.
    assert client.post(CHATS).get_json()["id"] == 2

    assert client.post(f"{CHATS}/2/questions", json={"text": "İkinci"}).status_code == 200

    assert client.get(WORKING).get_json() == {"working": [1, 2]}


def test_a_stop_keeps_the_finished_steps_and_says_stopped_with_no_half_answer(drive, dist):
    """The model read frame 2 and was reading what it brought when ■ was pressed: that step was going
    on and drops, the look at the project stays, and the words of the round that was out are never
    written (BEHAVIOUR.md, Agent panel)."""
    stops = []

    def pressed_while_out():
        stops.append(client.post(STOP))
        return Answer("Yarım kalan cevap.")

    box = FakeBox(calling(call("read_frame", 2)), pressed_while_out)
    client, held = app_over(drive, dist, box, hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "2 numaralı karede ne var?"})

    held.pop()()

    question = opened(client)["questions"][0]
    assert question["steps"] == [LOOKED]
    assert question["outcome"] == {"kind": "stopped"}
    assert stops[0].status_code == 200
    assert stops[0].get_json()["questions"][0] == question
    assert len(box.asked) == 2
    assert client.get(WORKING).get_json() == {"working": []}


def test_a_stopped_chat_takes_a_new_question_at_once(drive, dist):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Kaç kare var?"})
    client.post(STOP)

    assert client.post(QUESTIONS, json={"text": "Peki 7?"}).status_code == 200


def test_stopping_a_chat_that_is_not_working_changes_nothing(drive, dist):
    client, _held = app_over(drive, dist, FakeBox(Answer("Projede 2 kare var.")))
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Kaç kare var?"})
    before = opened(client)

    response = client.post(STOP)

    assert response.status_code == 200
    assert response.get_json() == before
    assert opened(client) == before


@pytest.mark.parametrize("failure", [
    Answer(REFUSED, failed=True, refused=True),
    Answer("DeepSeek HTTP 503\nmeşgul", failed=True),
], ids=["refusal", "technical"])
def test_a_refusal_and_a_technical_failure_land_as_failures(drive, dist, failure):
    """One card on the screen, its words the box's (BEHAVIOUR.md, Agent panel)."""
    client, _held = app_over(drive, dist, FakeBox(failure))
    client.post(CHATS)

    question = client.post(QUESTIONS, json={"text": "Kaç kare var?"}).get_json()["questions"][0]

    assert question["steps"] == [LOOKED]
    assert question["outcome"] == {"kind": "failure", "text": failure.text}


def test_a_project_with_no_frames_is_told_so(drive, dist):
    box = FakeBox()
    client, _held = app_over(drive, dist, box, cards=[])
    client.post(CHATS)

    question = client.post(QUESTIONS, json={"text": "Kaç kare var?"}).get_json()["questions"][0]

    assert question["steps"] == [LOOKED]
    assert question["outcome"] == {"kind": "answer", "text": NO_FRAMES}
    assert box.asked == []


def test_after_a_restart_an_unanswered_question_is_not_working_and_takes_a_new_one(drive, dist):
    """What works lives in the process; a restart leaves the question with no outcome and invents
    nothing about why."""
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Kaç kare var?"})

    restarted, _held = app_over(drive, dist, FakeBox(), hold=True)

    assert restarted.get(WORKING).get_json() == {"working": []}
    assert opened(restarted)["questions"][0]["outcome"] is None
    assert restarted.post(QUESTIONS, json={"text": "Peki 7?"}).status_code == 200


@pytest.mark.parametrize("body", [{"text": ""}, {"text": "   \n"}, {}, {"text": 7}],
                         ids=["empty", "spaces", "no-text", "a-number"])
def test_an_empty_question_is_refused(drive, dist, body):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)

    response = client.post(QUESTIONS, json=body)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Soru boş."}
    assert opened(client) == {"id": 1, "questions": []}


@pytest.mark.parametrize("method, url", [("post", "/api/projects/yok/chats/1/questions"),
                                         ("post", "/api/projects/yok/chats/1/stop"),
                                         ("get", "/api/projects/yok/chats/working")])
def test_an_unknown_project_is_a_404_and_no_folder_is_made(drive, dist, method, url):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)

    response = getattr(client, method)(url, json={"text": "Kaç kare var?"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: yok"}
    assert not (drive / "yok").exists()


@pytest.mark.parametrize("url", [f"{CHATS}/7/questions", f"{CHATS}/7/stop"])
def test_an_unknown_chat_is_a_404(drive, dist, url):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)

    response = client.post(url, json={"text": "Kaç kare var?"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Sohbet yok: 7"}


def broken_drive(*_args):
    raise OSError("[Errno 107] Transport endpoint is not connected")


@pytest.mark.parametrize("method, url", [("post", QUESTIONS), ("post", STOP), ("get", WORKING)])
def test_a_disk_error_answers_in_the_systems_own_words(dist, method, url):
    from backend.features.agent.presentation.routes import make_agent_blueprint
    client = create_app(dist_dir=str(dist), blueprints=[
        make_agent_blueprint(ask_question=broken_drive, stop_agent=broken_drive,
                             working_chats=broken_drive)]).test_client()

    response = getattr(client, method)(url, json={"text": "Kaç kare var?"})

    assert response.status_code == 500
    assert response.get_json() == {"error": "[Errno 107] Transport endpoint is not connected"}
```

## Görev 4: `backend/tests/test_chat_record.py` — kayıt

**Dosya:** Değiştir: `queen-editor/backend/tests/test_chat_record.py`

- [ ] **Adım 1: `import threading`** — `import os`'un altına.

- [ ] **Adım 2: 417'nin 8. testi — cevap ve hata artık son adımı bitirir.** Docstring'in sonuna
  *"Each outcome finishes its own chat's step and no other (madde 420)."*; iki beklenen adım
  `step(READING, True)` ve `step(LOOKING, True)`.

- [ ] **Adım 3: Dosyanın sonuna.**

```python
# --- Madde 420: what the agent writes ------------------------------------------------------------

@pytest.mark.parametrize("end, outcome", [
    (lambda record: record.answer("düğün", 1, "12 kare."), {"kind": "answer", "text": "12 kare."}),
    (lambda record: record.fail("düğün", 1, REFUSED), {"kind": "failure", "text": REFUSED}),
], ids=["answer", "failure"])
def test_an_answer_or_a_failure_finishes_the_step_going_on(record, end, outcome):
    """BEHAVIOUR.md, Agent panel: "An answer or a failure finishes the last step." The agent keeps a
    step going while the model reads what it brought."""
    asked(record)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.add_step("düğün", 1, *LOOKING)

    end(record)

    question = record.chats("düğün")[0]["questions"][0]
    assert question["steps"] == [step(READING, True), step(LOOKING, True)]
    assert question["outcome"] == outcome


def test_a_stop_drops_the_step_going_on_and_keeps_the_finished_ones(record):
    """BEHAVIOUR.md, Agent panel: "Stopping keeps the finished steps and drops the one that was going
    on, since it did not finish." """
    asked(record)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.add_step("düğün", 1, *LOOKING)

    record.stop("düğün", 1)

    question = record.chats("düğün")[0]["questions"][0]
    assert question["steps"] == [step(READING, True)]
    assert question["outcome"] == {"kind": "stopped"}


def test_a_line_for_a_project_whose_folder_is_gone_is_refused_and_makes_no_folder(tmp_path,
                                                                                    record):
    """An agent still at work when its project was renamed or deleted must not bring the folder back:
    every folder under the root is a project (madde 417)."""
    from backend.features.agent.domain.usecases.chats import ProjectMissing

    with pytest.raises(ProjectMissing) as refused:
        record.answer("taşındı", 1, "12 kare.")

    assert str(refused.value) == "Proje yok: taşındı"
    assert not (tmp_path / "taşındı").exists()


class HeldStorage:
    """A storage that holds the first line it is given half-written until the test lets it go, and
    notes whether a second line began while the first was still being written."""

    def __init__(self):
        self.lines = []
        self.writing = False
        self.overlapped = False
        self.first_in = threading.Event()
        self.let_go = threading.Event()

    def dir_exists(self, subdir):
        return True

    def append_line(self, subdir, name, line):
        if self.writing:
            self.overlapped = True
        self.writing = True
        if not self.first_in.is_set():
            self.first_in.set()
            self.let_go.wait(5)
        self.lines.append(line)
        self.writing = False


def test_two_writers_never_add_a_line_at_the_same_time():
    """Two agents, the door that asks and the door that stops all write to one chats.jsonl from
    their own threads; two appends at once can tear a line or lose one. The second writer is given a
    fifth of a second to start while the first line is held -- proving that it waited takes a wait."""
    from backend.features.agent.data.chat_record import DriveChatRecord
    storage = HeldStorage()
    record = DriveChatRecord(storage)
    first = threading.Thread(target=record.answer, args=("düğün", 1, "Bir."))
    first.start()
    assert storage.first_in.wait(5)
    second = threading.Thread(target=record.answer, args=("düğün", 2, "İki."))
    second.start()
    second.join(0.2)

    storage.let_go.set()
    first.join(5)
    second.join(5)

    assert storage.overlapped is False
    assert len(storage.lines) == 2
```

## Görev 5: `backend/tests/test_composition_root.py` — `main.py`'nin bağlaması

**Dosya:** Değiştir: `queen-editor/backend/tests/test_composition_root.py`

- [ ] **Adım 1: İmportlar** — `import base64`, `import json`; `test_deepseek_box`'tan `Answers`'ın
  yanına `calling`.

- [ ] **Adım 2: `PHOTO = ("P0_0.png", b"PNG")`'nin önüne.**

```python
@pytest.mark.parametrize("video_model", ["", "h3"])
@pytest.mark.parametrize("method, url", [("post", "/api/projects/m420-yok/chats/1/questions"),
                                         ("post", "/api/projects/m420-yok/chats/1/stop"),
                                         ("get", "/api/projects/m420-yok/chats/working")],
                         ids=["ask", "stop", "working"])
def test_the_app_serves_the_agents_doors(import_main, video_model, method, url):
    """Madde 420: the doors' own tests wire them by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the doors' words -- a door never hung would not."""
    main = import_main(video_model)

    response = getattr(main.app.test_client(), method)(url, json={"text": "Kaç kare var?"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m420-yok"}


class FakeRun:
    """The question being answered: writes down what the agent writes to the chat."""

    def __init__(self):
        self.wrote = []

    def stopped(self):
        return False

    def add_step(self, running, done):
        self.wrote.append(("step", running, done))

    def finish_step(self):
        self.wrote.append(("stepDone",))

    def answer(self, text):
        self.wrote.append(("answer", text))

    def fail(self, text):
        self.wrote.append(("failure", text))


def test_the_agent_reads_the_open_project_through_the_box_and_changes_nothing(
        import_main, monkeypatch, tmp_path):
    """Madde 420, as main.py wires it: the agent reads the gallery's cards and a frame's photo out of
    the open project, asks Queen AI through the box -- the tool calls go unchecked, the words are
    checked -- and writes nothing into the project ("yani bir değişilik yapamasın"). requests.post is
    the one the client sends with, so no request leaves this machine."""
    project = tmp_path / "düğün"
    project.mkdir()
    (project / "P0_0.png").write_bytes(b"PNG")
    row = {"file": "P0_0.png", "frame": "P0_0", "layer": "photo", "status": "done",
           "prompt": "kırmızı elbiseli kadın"}
    (project / "photos.jsonl").write_text(json.dumps(row, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    before = {path.name: path.read_bytes() for path in project.iterdir()}
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "k-1")
    main = import_main("h3")
    read = {"id": "call_1", "type": "function",
            "function": {"name": "read_frame", "arguments": '{"frame": 1}'}}
    look = {"id": "call_2", "type": "function",
            "function": {"name": "look_at_frame", "arguments": '{"frame": 1}'}}
    http = Answers([calling(read, look), answering("Projede tek kare var: kırmızı elbiseli kadın."),
                    answering("APPROVED")])
    monkeypatch.setattr(requests, "post", http.post)
    run = FakeRun()

    main._agent(run, "düğün", [], "Projede ne var?")

    assert run.wrote[-1] == ("answer", "Projede tek kare var: kırmızı elbiseli kadın.")
    first, second, _check = http.calls
    assert [tool["function"]["name"] for tool in first["body"]["tools"]] == ["read_frame",
                                                                             "look_at_frame"]
    told = second["body"]["messages"]
    assert any(message["role"] == "tool" and "kırmızı elbiseli kadın" in message["content"]
               for message in told)
    pictures = [part["image_url"]["url"] for message in told
                if message["role"] == "user" and isinstance(message["content"], list)
                for part in message["content"] if part["type"] == "image_url"]
    assert pictures == ["data:image/png;base64," + base64.b64encode(b"PNG").decode()]
    assert {path.name: path.read_bytes() for path in project.iterdir()} == before
```

## Görev 6: Koşu — kırmızı, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde kırmızılar yalnız bu planın testleri — `test_agent_answer.py`'nin
20'si ve `test_agent_routes.py`'nin 23'ü yeni modül olmadığı için, `test_agent_runner.py`'nin 10'u
fixture'da `ModuleNotFoundError`'la (hata olarak); `test_chat_record.py`'de 417'nin değişen 8. testi,
cevap / hata (2), durdurma, klasör ve kilit (6); `test_composition_root.py`'de kapılar (6) ve agent
(1). Toplam 56 kırmızı ve 10 hata; öteki her şey yeşil (1375). QueenAgent'ın pytest'i yeşil (989).
İki vitest satırı bu çalışma ağacında başlayamaz — `node_modules` yok, `'vitest' is not recognized`;
bu madde ekrana dokunmuyor.

- [ ] **Adım 2: Commit** — testler, spec ve bu plan, kırmızı hâliyle:

```powershell
git add docs/specs/2026-10-06-queen-editor-m420-agent-testler-design.md docs/plans/2026-10-06-queen-editor-m420-agent-testler-plan.md queen-editor/backend/tests/test_agent_answer.py queen-editor/backend/tests/test_agent_runner.py queen-editor/backend/tests/test_agent_routes.py queen-editor/backend/tests/test_chat_record.py queen-editor/backend/tests/test_composition_root.py
git commit -m @'
test(queen-editor): Madde 420 red -- the agent answers about the open project alone: it looks at the gallery's cards, reads a frame and looks at its photo through two read-only tools that name no project, its instruction ends with QueenAgent's suffix, it runs at most 32 rounds and the last is told so and offered no tools; its steps and outcome land in the chat, a stop drops the step going on and writes no half answer; it runs on the server, two chats at once, a working chat takes no second question; the record keeps its lines whole and makes no folder; three doors ask, stop and say which chats are working

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
