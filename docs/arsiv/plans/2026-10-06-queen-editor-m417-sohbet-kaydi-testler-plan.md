# Madde 417 — Agent'ın sohbetlerinin kaydı, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Testler kırmızı
> commit'lenir; spec ve bu plan aynı commit'te.

**Hedef:** Agent'ın sohbetlerinin projenin klasöründe kalıcı tutulduğunu — soruları, adımları ve
sonuçlarıyla, yalnız eklenen tek dosyada — ve sunucunun kapısının yeni sohbeti (bekleyen boş varsa
onu), listeyi ve tek sohbeti verdiğini, silmenin kapısı olmadığını anlatan testler.

**Yaklaşım:** Kayıt gerçek `DriveStorage`'la geçici klasörde; use case'ler sahte kayıtla; kapı
`main.py`'nin bağlamasıyla elle, geçici klasörde; `main.py`'nin kendisi `test_composition_root`'ta.
420'nin yazacaklarını testler kaydın kendi yöntemleriyle yazar.

**Araçlar:** pytest (`parametrize`, `tmp_path`), Flask'ın test istemcisi.

**Spec:** [m417 test turu](../specs/2026-10-06-queen-editor-m417-sohbet-kaydi-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**; kullanıcının gördüğü metin Türkçe.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod değişmiyor.
- Yeni modüller testlerin **içinde** import edilir: başta bir import, modül yazılmadan önce bütün
  toplamayı durdurur.
- Hiçbir test gerçek Drive'a ya da saate dokunmaz; zamanlar sabit ISO metinleri.

**Arayüz — uygulama turunun vereceği:**
- `backend/features/agent/data/chat_record.py` — `DriveChatRecord(storage)`:
  `project_exists(project)`, `chats(project) -> list[dict]`, `add_chat(project, chat_id)`,
  `add_question(project, chat_id, text, at)`, `add_step(project, chat_id, running, done)`,
  `finish_step(project, chat_id)`, `answer(project, chat_id, text)`, `fail(project, chat_id, text)`,
  `stop(project, chat_id)`. Dosya: `<proje>/chats.jsonl`.
- Sohbet: `{"id", "questions": [{"text", "askedAt", "steps": [{"running", "done", "finished"}],
  "outcome": None | {"kind": "answer"|"failure", "text"} | {"kind": "stopped"}}]}`.
- `backend/features/agent/domain/usecases/chats.py` — `ProjectMissing`, `ChatMissing`,
  `new_chat(record, project)`, `list_chats(record, project)` (satır `{"id", "firstQuestion",
  "lastAskedAt"}`), `open_chat(record, project, chat_id)`.
- `backend/features/agent/presentation/routes.py` — `make_chats_blueprint(new_chat, list_chats,
  open_chat)`: `POST` ve `GET /api/projects/<proje>/chats`, `GET /api/projects/<proje>/chats/<id>`.

---

## Görev 1: `backend/tests/test_chat_record.py` — yeni

**Dosya:** Oluştur: `queen-editor/backend/tests/test_chat_record.py`

- [ ] **Adım 1: Dosyanın tamamı.**

```python
"""The agent's chats, kept with their project for good (madde 417).

One file in the project's folder that is only ever added to and is folded on read -- the photo
record's way: a session that dies mid-write loses at most the line it was adding. What 420's agent
will write, these tests write through the record's own methods.

The new module is imported inside the tests: it is written after this file, and an import at the
top would stop the whole collection instead of failing these questions.
"""
import os

import pytest

from backend.services.drive.storage import DriveStorage

ASKED = "2026-10-06T10:00:00+00:00"
LATER = "2026-10-06T10:05:00+00:00"
READING = ("3 numaralı kareyi okuyor…", "3 numaralı kareyi okudu")
LOOKING = ("Bir görsele bakıyor…", "Bir görsele baktı")
REFUSED = "Model hata döndü, farklı şekilde dene."


def record_at(path):
    from backend.features.agent.data.chat_record import DriveChatRecord
    return DriveChatRecord(DriveStorage(str(path)))


@pytest.fixture
def record(tmp_path):
    (tmp_path / "düğün").mkdir()
    return record_at(tmp_path)


def asked(record, chat=1, text="Kaç kare var?", at=ASKED):
    """A chat with one question on it."""
    record.add_chat("düğün", chat)
    record.add_question("düğün", chat, text, at)


def step(pair, finished):
    running, done = pair
    return {"running": running, "done": done, "finished": finished}


def test_a_project_with_no_chats_reads_none(record):
    assert record.chats("düğün") == []


def test_a_new_chat_reads_back_with_nothing_asked(record):
    record.add_chat("düğün", 1)

    assert record.chats("düğün") == [{"id": 1, "questions": []}]


def test_a_question_reads_back_with_its_steps_and_its_answer(record):
    asked(record)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.add_step("düğün", 1, *LOOKING)
    record.finish_step("düğün", 1)
    record.answer("düğün", 1, "Projede 12 kare var.")

    assert record.chats("düğün") == [{"id": 1, "questions": [{
        "text": "Kaç kare var?", "askedAt": ASKED,
        "steps": [step(READING, True), step(LOOKING, True)],
        "outcome": {"kind": "answer", "text": "Projede 12 kare var."}}]}]


def test_a_step_still_going_on_reads_unfinished_and_its_question_has_no_outcome(record):
    """No outcome is what a question the agent is still working on looks like (420)."""
    asked(record)
    record.add_step("düğün", 1, *READING)

    question = record.chats("düğün")[0]["questions"][0]
    assert question["steps"] == [step(READING, False)]
    assert question["outcome"] is None


@pytest.mark.parametrize("text", [
    REFUSED,
    "HTTPSConnectionPool(host='api.deepseek.com', port=443): Read timed out. (read timeout=120)",
], ids=["refusal", "technical"])
def test_a_failure_keeps_its_own_text(record, text):
    """The screen draws both as one card (BEHAVIOUR.md, Agent panel); only the words differ."""
    asked(record)
    record.fail("düğün", 1, text)

    assert record.chats("düğün")[0]["questions"][0]["outcome"] == {"kind": "failure", "text": text}


def test_a_stopped_question_says_so(record):
    asked(record)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.stop("düğün", 1)

    question = record.chats("düğün")[0]["questions"][0]
    assert question["outcome"] == {"kind": "stopped"}
    assert question["steps"] == [step(READING, True)]


def test_steps_and_outcomes_land_on_the_chats_latest_question(record):
    asked(record)
    record.answer("düğün", 1, "12 kare.")
    record.add_question("düğün", 1, "Hangisi hata verdi?", LATER)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.answer("düğün", 1, "7 numaralı kare.")

    first, second = record.chats("düğün")[0]["questions"]
    assert first["steps"] == []
    assert first["outcome"] == {"kind": "answer", "text": "12 kare."}
    assert (second["text"], second["askedAt"]) == ("Hangisi hata verdi?", LATER)
    assert second["steps"] == [step(READING, True)]
    assert second["outcome"] == {"kind": "answer", "text": "7 numaralı kare."}


def test_two_chats_written_at_the_same_time_stay_apart(record):
    """Two chats may run at once (BEHAVIOUR.md, Agent panel), so their lines interleave."""
    record.add_chat("düğün", 1)
    record.add_chat("düğün", 2)
    record.add_question("düğün", 1, "Birinci", ASKED)
    record.add_question("düğün", 2, "İkinci", LATER)
    record.add_step("düğün", 2, *LOOKING)
    record.add_step("düğün", 1, *READING)
    record.answer("düğün", 1, "Bir.")
    record.fail("düğün", 2, REFUSED)

    one, two = record.chats("düğün")
    assert one == {"id": 1, "questions": [{
        "text": "Birinci", "askedAt": ASKED, "steps": [step(READING, False)],
        "outcome": {"kind": "answer", "text": "Bir."}}]}
    assert two == {"id": 2, "questions": [{
        "text": "İkinci", "askedAt": LATER, "steps": [step(LOOKING, False)],
        "outcome": {"kind": "failure", "text": REFUSED}}]}


def test_another_projects_chats_are_not_in_this_one(tmp_path, record):
    (tmp_path / "kına").mkdir()
    asked(record)

    assert record.chats("kına") == []


def test_the_record_is_one_file_in_the_projects_own_folder(tmp_path, record):
    """Inside the folder, so a renamed project carries its chats and a deleted one takes them."""
    asked(record)
    record.answer("düğün", 1, "12 kare.")

    assert os.listdir(tmp_path / "düğün") == ["chats.jsonl"]


def test_a_write_only_adds_to_the_end(tmp_path, record):
    """FOUNDATION 1: nothing already written is rewritten."""
    asked(record)
    path = tmp_path / "düğün" / "chats.jsonl"
    before = path.read_text(encoding="utf-8")

    record.answer("düğün", 1, "12 kare.")

    after = path.read_text(encoding="utf-8")
    assert after.startswith(before) and after != before


def test_a_half_written_last_line_hides_nothing_before_it(tmp_path, record):
    asked(record)
    with open(tmp_path / "düğün" / "chats.jsonl", "a", encoding="utf-8") as f:
        f.write('{"chat": 1, "event": "ans')

    assert record.chats("düğün")[0]["questions"][0]["text"] == "Kaç kare var?"


def test_a_fresh_record_reads_what_an_earlier_one_wrote(tmp_path, record):
    """A server restart: nothing is held in memory, the disk is the truth (FOUNDATION 2)."""
    asked(record)
    record.answer("düğün", 1, "12 kare.")

    assert record_at(tmp_path).chats("düğün") == [{"id": 1, "questions": [{
        "text": "Kaç kare var?", "askedAt": ASKED, "steps": [],
        "outcome": {"kind": "answer", "text": "12 kare."}}]}]


def test_a_project_is_its_folder(record):
    assert record.project_exists("düğün") is True
    assert record.project_exists("yok") is False
```

## Görev 2: `backend/tests/test_chat_usecases.py` — yeni

**Dosya:** Oluştur: `queen-editor/backend/tests/test_chat_usecases.py`

- [ ] **Adım 1: Dosyanın tamamı.**

```python
"""What the agent's chat doors decide (madde 417): a new chat, the list, one chat opened.

The record is faked (CODE-STANDARD, Tests). Its chats have the shape the real one folds them into:
{"id", "questions": [{"text", "askedAt", "steps", "outcome"}]}.

The module under test is imported inside the tests: it is written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
import pytest

AT_10 = "2026-10-06T10:00:00+00:00"
AT_11 = "2026-10-06T11:00:00+00:00"
AT_12 = "2026-10-06T12:00:00+00:00"


def usecases():
    from backend.features.agent.domain.usecases import chats
    return chats


def question(text, at):
    return {"text": text, "askedAt": at, "steps": [], "outcome": None}


def chat(chat_id, *questions):
    return {"id": chat_id, "questions": list(questions)}


class FakeChatRecord:
    """The project düğün and the chats it holds. What is added is written down."""

    def __init__(self, *chats):
        self.held = list(chats)
        self.added = []

    def project_exists(self, project):
        return project == "düğün"

    def chats(self, project):
        return list(self.held)

    def add_chat(self, project, chat_id):
        self.added.append((project, chat_id))
        self.held.append(chat(chat_id))


def test_a_new_chat_is_made_when_none_is_waiting():
    record = FakeChatRecord()

    assert usecases().new_chat(record, "düğün") == {"id": 1, "questions": []}
    assert record.added == [("düğün", 1)]


def test_a_new_chat_takes_the_number_after_the_highest():
    record = FakeChatRecord(chat(1, question("a", AT_10)), chat(2, question("b", AT_11)))

    assert usecases().new_chat(record, "düğün") == {"id": 3, "questions": []}
    assert record.added == [("düğün", 3)]


def test_a_waiting_empty_chat_is_returned_instead_of_a_new_one():
    """Yeni sohbet opens the empty chat if one is waiting (BEHAVIOUR.md, Agent panel)."""
    record = FakeChatRecord(chat(1, question("a", AT_10)), chat(2))

    assert usecases().new_chat(record, "düğün") == {"id": 2, "questions": []}
    assert record.added == []


def test_the_list_holds_only_chats_with_a_question_newest_last_question_first():
    first = "Projeyi özetler misin?\nHer kareyi ayrı anlat"
    record = FakeChatRecord(chat(1, question(first, AT_10), question("Peki 7?", AT_12)),
                            chat(2, question("Kaç kare var?", AT_11)),
                            chat(3))

    assert usecases().list_chats(record, "düğün") == [
        # The whole first question: cutting it to one line is the screen's.
        {"id": 1, "firstQuestion": first, "lastAskedAt": AT_12},
        {"id": 2, "firstQuestion": "Kaç kare var?", "lastAskedAt": AT_11},
    ]


def test_a_project_where_nothing_was_asked_lists_nothing():
    assert usecases().list_chats(FakeChatRecord(chat(1)), "düğün") == []


def test_a_chat_opens_with_everything_in_it():
    held = chat(2, {"text": "Kaç kare var?", "askedAt": AT_10,
                    "steps": [{"running": "3 numaralı kareyi okuyor…",
                               "done": "3 numaralı kareyi okudu", "finished": True}],
                    "outcome": {"kind": "answer", "text": "12 kare."}})
    record = FakeChatRecord(chat(1, question("a", AT_11)), held)

    assert usecases().open_chat(record, "düğün", 2) == held


def test_a_chat_that_is_not_there_is_refused():
    module = usecases()

    with pytest.raises(module.ChatMissing) as exc:
        module.open_chat(FakeChatRecord(chat(1)), "düğün", 7)

    assert str(exc.value) == "Sohbet yok: 7"


@pytest.mark.parametrize("door", ["new", "list", "open"])
def test_every_door_refuses_a_project_that_is_not_there_and_writes_nothing(door):
    module, record = usecases(), FakeChatRecord()
    ask = {"new": lambda: module.new_chat(record, "yok"),
           "list": lambda: module.list_chats(record, "yok"),
           "open": lambda: module.open_chat(record, "yok", 1)}[door]

    with pytest.raises(module.ProjectMissing) as exc:
        ask()

    assert str(exc.value) == "Proje yok: yok"
    assert record.added == []
```

## Görev 3: `backend/tests/test_chats_routes.py` — yeni

**Dosya:** Oluştur: `queen-editor/backend/tests/test_chats_routes.py`

- [ ] **Adım 1: Dosyanın tamamı.**

```python
"""The agent's chats over HTTP (madde 417): a new chat, the list, one chat opened -- and no delete.

The door is wired by hand over a temp folder, the wiring main.py does. What 420's agent will write
-- a question, its steps, its outcome -- the tests write through the record itself: no door takes
them yet.

The new modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
from functools import partial

import pytest

from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

ASKED = "2026-10-06T10:00:00+00:00"
CHATS = "/api/projects/düğün/chats"
READING = ("3 numaralı kareyi okuyor…", "3 numaralı kareyi okudu")
LOOKING = ("Bir görsele bakıyor…", "Bir görsele baktı")
WHOLE = {"id": 1, "questions": [{
    "text": "Kaç kare var?", "askedAt": ASKED,
    "steps": [{"running": READING[0], "done": READING[1], "finished": True},
              {"running": LOOKING[0], "done": LOOKING[1], "finished": True}],
    "outcome": {"kind": "answer", "text": "Projede 12 kare var."}}]}
ROW = {"id": 1, "firstQuestion": "Kaç kare var?", "lastAskedAt": ASKED}


def client_with(dist, blueprint):
    return create_app(dist_dir=str(dist), blueprints=[blueprint]).test_client()


def app_over(drive, dist):
    """(client, record) over `drive` -- built again over the same folder, it is a restart."""
    from backend.features.agent.data.chat_record import DriveChatRecord
    from backend.features.agent.domain.usecases.chats import list_chats, new_chat, open_chat
    from backend.features.agent.presentation.routes import make_chats_blueprint
    record = DriveChatRecord(DriveStorage(str(drive)))
    blueprint = make_chats_blueprint(new_chat=partial(new_chat, record),
                                     list_chats=partial(list_chats, record),
                                     open_chat=partial(open_chat, record))
    return client_with(dist, blueprint), record


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


@pytest.fixture
def server(drive, dist):
    return app_over(drive, dist)


def answered(record, project="düğün", chat=1):
    """What 420's agent will write: a question, two finished steps, an answer."""
    record.add_question(project, chat, "Kaç kare var?", ASKED)
    for running, done in (READING, LOOKING):
        record.add_step(project, chat, running, done)
        record.finish_step(project, chat)
    record.answer(project, chat, "Projede 12 kare var.")


def test_a_new_chat_comes_back_empty(server):
    client, _record = server

    response = client.post(CHATS)

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "questions": []}


def test_asking_for_a_new_chat_twice_gives_the_waiting_one(server):
    client, _record = server

    assert client.post(CHATS).get_json()["id"] == 1
    assert client.post(CHATS).get_json()["id"] == 1
    # An empty chat is never listed.
    assert client.get(CHATS).get_json() == {"chats": []}


def test_a_chat_with_a_question_is_listed_and_opens_whole(server):
    client, record = server
    client.post(CHATS)
    answered(record)

    assert client.get(CHATS).get_json() == {"chats": [ROW]}
    response = client.get(f"{CHATS}/1")
    assert response.status_code == 200
    assert response.get_json() == WHOLE


def test_a_new_chat_after_a_question_is_a_new_one(server):
    client, record = server
    client.post(CHATS)
    record.add_question("düğün", 1, "Kaç kare var?", ASKED)

    assert client.post(CHATS).get_json() == {"id": 2, "questions": []}


def test_the_chats_are_still_there_after_a_restart(server, drive, dist):
    client, record = server
    client.post(CHATS)
    answered(record)

    restarted, _record = app_over(drive, dist)

    assert restarted.get(CHATS).get_json() == {"chats": [ROW]}
    assert restarted.get(f"{CHATS}/1").get_json() == WHOLE


def test_another_projects_chats_are_never_visible(server, drive):
    client, record = server
    (drive / "kına").mkdir()
    client.post(CHATS)
    answered(record)

    assert client.get("/api/projects/kına/chats").get_json() == {"chats": []}
    response = client.get("/api/projects/kına/chats/1")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Sohbet yok: 1"}


@pytest.mark.parametrize("method, url", [("post", "/api/projects/yok/chats"),
                                         ("get", "/api/projects/yok/chats"),
                                         ("get", "/api/projects/yok/chats/1")])
def test_an_unknown_project_is_a_404(server, method, url):
    client, _record = server

    response = getattr(client, method)(url)

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: yok"}


def test_a_new_chat_never_creates_a_project(server, drive):
    # Every folder under the root is a project: a write to an unknown name must not conjure one.
    client, _record = server

    client.post("/api/projects/yok/chats")

    assert not (drive / "yok").exists()


def test_an_unknown_chat_is_a_404(server):
    client, _record = server

    response = client.get(f"{CHATS}/7")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Sohbet yok: 7"}


def test_there_is_no_door_to_delete_a_chat(server):
    """A chat is never deleted (madde 417)."""
    client, record = server
    client.post(CHATS)
    answered(record)

    assert client.delete(f"{CHATS}/1").status_code == 405
    assert client.get(f"{CHATS}/1").get_json() == WHOLE


def broken_drive(*_args):
    raise OSError("[Errno 107] Transport endpoint is not connected")


@pytest.mark.parametrize("method, url", [("post", CHATS), ("get", CHATS), ("get", f"{CHATS}/1")])
def test_a_disk_error_answers_in_the_systems_own_words(dist, method, url):
    from backend.features.agent.presentation.routes import make_chats_blueprint
    client = client_with(dist, make_chats_blueprint(new_chat=broken_drive, list_chats=broken_drive,
                                                    open_chat=broken_drive))

    response = getattr(client, method)(url)

    assert response.status_code == 500
    assert response.get_json() == {"error": "[Errno 107] Transport endpoint is not connected"}
```

## Görev 4: `backend/tests/test_composition_root.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_composition_root.py`

- [ ] **Adım 1: `test_the_app_hands_a_reference_run_to_the_use_case`'in arkasına bir test.**

```python
@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_serves_the_agents_chats(import_main, video_model):
    """Madde 417: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main(video_model)

    response = main.app.test_client().get("/api/projects/m417-yok/chats")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m417-yok"}
```

## Görev 5: Koşu — kırmızı, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde kırmızı — üç yeni dosyanın bütün testleri
(`ModuleNotFoundError: backend.features.agent`) ve `test_the_app_serves_the_agents_chats`'in iki
durumu (kapı yok, GET `index.html`'e düşüyor). Öteki her şey yeşil; öteki üç satır yeşil.

**Koşuldu:** `16 failed, 1288 passed, 27 errors` — 42'si yeni testler, beklendiği gibi; biri
`test_version_record`'un `test_every_link_to_a_roadmap_resolves_from_where_it_is_written`'ı: bu
dal `feat/queen-editor-v9`'un ucundan değil, v9'un yol haritası yazılmadan önceki `baa32885`'ten
açıldı, ve spec'in yol haritasına bağlantısı bu dalda çözülmüyor — v9'a birleşince çözülür, kod
değil. · vitest `794 passed (794)` · queen-agent `989 passed` · queen-agent vitest `838 passed (838)`.

- [ ] **Adım 2: Commit** — spec, bu plan ve dört test dosyası; mesaj
  `test(queen-editor): Madde 417 red -- …`, çift tırnaksız, PowerShell'in tek tırnaklı
  here-string'iyle, `Co-Authored-By` satırıyla biter.
