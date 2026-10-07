# Madde 417 — Agent'ın sohbetlerinin kaydı, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Ekran yok, `dist`
> kurulmaz.

**Hedef:** Test turunun kırmızı testlerini kodla yeşile çevirmek — testlerin anlattığı kadar, fazlası
değil.

**Yaklaşım:** Yeni özellik `features/agent/`: kayıt projenin klasöründe yalnız eklenen tek dosya,
okurken katlanır; üç use case; üç kapı; `main.py` bağlar.

**Spec:** [m417 uygulama turu](../specs/2026-10-06-queen-editor-m417-sohbet-kaydi-uygulama-design.md)
· [m417 test turu](../specs/2026-10-06-queen-editor-m417-sohbet-kaydi-testler-design.md)

## Her yere geçerli kurallar

- Kod, yorum, docstring İngilizce; kullanıcının gördüğü metin Türkçe. Yorum neden'i söyler.
- CODE-STANDARD: domain saf; dosya şeması yalnız `data/`'da; özellik özelliği import etmez; somut
  sınıflar yalnız `main.py`'de bağlanır.
- FOUNDATION 1–2: kayıt yalnız eklenir; bellekte tutulmaz.
- Testlere dokunulmaz. `main.py`'de 416'nın DeepSeek satırlarına dokunulmaz.

---

## Görev 1: Paket — `backend/features/agent/`

**Dosyalar:** Oluştur (boş): `queen-editor/backend/features/agent/__init__.py`,
`…/agent/data/__init__.py`, `…/agent/domain/__init__.py`, `…/agent/domain/usecases/__init__.py`,
`…/agent/presentation/__init__.py`

- [ ] **Adım 1:** Beş boş `__init__.py` — öteki özelliklerinki gibi.

## Görev 2: `domain/ports.py`

**Dosya:** Oluştur: `queen-editor/backend/features/agent/domain/ports.py`

```python
"""Ports this feature needs. Implemented in data/, faked in tests -- domain stays pure."""
from typing import Protocol


class ChatRecord(Protocol):
    """A project's chats with the agent, kept with the project for good (madde 417).

    A chat is {"id": int, "questions": [question]}. A question is {"text", "askedAt", "steps",
    "outcome"}; a step is {"running", "done", "finished"} -- its sentence while it goes on, its
    sentence once done, and whether it is. The outcome is None while the agent still works on the
    question, else {"kind": "answer" | "failure", "text"} or {"kind": "stopped"}. A failure's text is
    a refusal's sentence or a technical error's own words.

    A step, its end and an outcome are written to the chat's latest question.
    """

    def project_exists(self, project: str) -> bool:
        ...

    def chats(self, project: str) -> list[dict]:
        """Every chat of the project, in the order they were opened."""
        ...

    def add_chat(self, project: str, chat_id: int) -> None:
        """A chat with nothing asked yet."""
        ...

    def add_question(self, project: str, chat_id: int, text: str, at: str) -> None:
        ...

    def add_step(self, project: str, chat_id: int, running: str, done: str) -> None:
        """A step begins, with both of its sentences; it is not finished yet."""
        ...

    def finish_step(self, project: str, chat_id: int) -> None:
        """The latest step is finished."""
        ...

    def answer(self, project: str, chat_id: int, text: str) -> None:
        ...

    def fail(self, project: str, chat_id: int, text: str) -> None:
        ...

    def stop(self, project: str, chat_id: int) -> None:
        ...
```

## Görev 3: `data/chat_record.py`

**Dosya:** Oluştur: `queen-editor/backend/features/agent/data/chat_record.py`

**Üretir:** `DriveChatRecord(storage)` — Görev 2'nin `ChatRecord`'u.

```python
"""ChatRecord over DriveStorage -- the only place that knows the chat file's name and its lines.

Every chat of a project lives in one file inside the project's own folder (madde 417): a renamed
project carries its chats and a deleted one takes them, and the list, a chat opened and a new chat
each read one file -- a file per chat would have the list open every one of them over Drive.

The file is only ever added to, the photo record's rule: a session that dies mid-write loses at most
the line it was adding, where rewriting a chat could lose all of it. Each line is one event about
one chat, and reading folds them in the order they were written. Nothing is held in memory, so a
restart loses nothing.
"""
import json

FILE = "chats.jsonl"

OPENED = "opened"
QUESTION = "question"
STEP = "step"
STEP_DONE = "stepDone"
ANSWER = "answer"
FAILURE = "failure"
STOPPED = "stopped"


def _rows(lines):
    """Every readable line, in the order written.

    One that will not parse is skipped rather than raised on: the last can be half-written after a
    session death, and it must not hide the chats before it.
    """
    rows = []
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and isinstance(row.get("chat"), int):
            rows.append(row)
    return rows


def _fold(rows):
    """The chats, in the order their first line was written. Any line makes its chat exist, so
    "opened" is only ever needed by a chat with nothing asked yet."""
    chats = {}
    for row in rows:
        chat = chats.setdefault(row["chat"], {"id": row["chat"], "questions": []})
        if row.get("event") == QUESTION:
            chat["questions"].append({"text": row.get("text"), "askedAt": row.get("at"),
                                      "steps": [], "outcome": None})
        elif chat["questions"]:
            _land(chat["questions"][-1], row)
    return list(chats.values())


def _land(question, row):
    """Steps and outcomes belong to the question being worked on, which is the chat's latest."""
    event = row.get("event")
    if event == STEP:
        question["steps"].append({"running": row.get("running"), "done": row.get("done"),
                                  "finished": False})
    elif event == STEP_DONE and question["steps"]:
        question["steps"][-1]["finished"] = True
    elif event in (ANSWER, FAILURE):
        question["outcome"] = {"kind": event, "text": row.get("text")}
    elif event == STOPPED:
        question["outcome"] = {"kind": STOPPED}


class DriveChatRecord:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def chats(self, project):
        return _fold(_rows(self._storage.read_lines(project, FILE)))

    def add_chat(self, project, chat_id):
        self._add(project, chat_id, OPENED)

    def add_question(self, project, chat_id, text, at):
        self._add(project, chat_id, QUESTION, text=text, at=at)

    def add_step(self, project, chat_id, running, done):
        self._add(project, chat_id, STEP, running=running, done=done)

    def finish_step(self, project, chat_id):
        self._add(project, chat_id, STEP_DONE)

    def answer(self, project, chat_id, text):
        self._add(project, chat_id, ANSWER, text=text)

    def fail(self, project, chat_id, text):
        self._add(project, chat_id, FAILURE, text=text)

    def stop(self, project, chat_id):
        self._add(project, chat_id, STOPPED)

    def _add(self, project, chat_id, event, **fields):
        line = json.dumps({"chat": chat_id, "event": event, **fields}, ensure_ascii=False)
        self._storage.append_line(project, FILE, line)
```

## Görev 4: `domain/usecases/chats.py`

**Dosya:** Oluştur: `queen-editor/backend/features/agent/domain/usecases/chats.py`

**Üretir:** `ProjectMissing`, `ChatMissing`, `new_chat(record, project) -> dict`,
`list_chats(record, project) -> list[dict]`, `open_chat(record, project, chat_id) -> dict`.

```python
"""The agent's chats at the door: a new chat, the list, one chat opened (madde 417).

The messages are user-facing Turkish; presentation forwards them untouched. ProjectMissing is this
feature's own, since a feature never imports another, and says what the projects feature says.
"""


class ProjectMissing(Exception):
    """No such project folder (message is the user-facing text)."""


class ChatMissing(Exception):
    """No chat under that id in the project (message is the user-facing text)."""


def _require(record, project):
    # Asked before anything is written: every folder under the root is a project, and a write into
    # an unknown name would make one.
    if not record.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")


def new_chat(record, project):
    """The empty chat waiting in the project, or a new one -- never a second empty chat
    (BEHAVIOUR.md, Agent panel).

    A new chat takes the highest number plus one, and since nothing is deleted no number comes back.
    Two requests at once can both take it: their two lines then fold into one empty chat, which is
    exactly the answer the rule asks for.
    """
    _require(record, project)
    chats = record.chats(project)
    for chat in chats:
        if not chat["questions"]:
            return chat
    chat_id = max((chat["id"] for chat in chats), default=0) + 1
    record.add_chat(project, chat_id)
    return {"id": chat_id, "questions": []}


def list_chats(record, project):
    """The chats with a question, the newest last question first; each with its first question
    whole -- cutting it to one line is the screen's -- and when the last one was asked."""
    _require(record, project)
    rows = [{"id": chat["id"], "firstQuestion": chat["questions"][0]["text"],
             "lastAskedAt": chat["questions"][-1]["askedAt"]}
            for chat in record.chats(project) if chat["questions"]]
    # The times are ISO text in one shape, so their order as text is their order in time.
    return sorted(rows, key=lambda row: row["lastAskedAt"], reverse=True)


def open_chat(record, project, chat_id):
    _require(record, project)
    for chat in record.chats(project):
        if chat["id"] == chat_id:
            return chat
    raise ChatMissing(f"Sohbet yok: {chat_id}")
```

## Görev 5: `presentation/routes.py`

**Dosya:** Oluştur: `queen-editor/backend/features/agent/presentation/routes.py`

**Tüketir:** Görev 4'ün üç use case'i ve iki hatası.

```python
"""/api/projects/<project>/chats -- request/response translation only (madde 417).

There is no door to delete a chat: a chat is never deleted, so a DELETE is Flask's own 405.
"""
from flask import Blueprint, jsonify

from backend.features.agent.domain.usecases.chats import ChatMissing, ProjectMissing


def make_chats_blueprint(new_chat, list_chats, open_chat):
    """Every argument is a use case already bound to the record (see main.py)."""
    bp = Blueprint("agent_chats", __name__)

    @bp.post("/api/projects/<project>/chats")
    def post_chat(project):
        return _answer(lambda: new_chat(project))

    @bp.get("/api/projects/<project>/chats")
    def get_chats(project):
        return _answer(lambda: {"chats": list_chats(project)})

    @bp.get("/api/projects/<project>/chats/<int:chat_id>")
    def get_chat(project, chat_id):
        return _answer(lambda: open_chat(project, chat_id))

    return bp


def _answer(ask):
    try:
        return jsonify(ask())
    except (ProjectMissing, ChatMissing) as exc:
        return jsonify({"error": str(exc)}), 404
    except OSError as exc:
        # The operating system's own words -- never a guessed cause.
        return jsonify({"error": str(exc)}), 500
```

## Görev 6: `backend/main.py`

**Dosya:** Değiştir: `queen-editor/backend/main.py`

- [ ] **Adım 1: İmportlar**, `from backend import config`'in hemen altına:

```python
from backend.features.agent.data.chat_record import DriveChatRecord
from backend.features.agent.domain.usecases.chats import list_chats, new_chat, open_chat
from backend.features.agent.presentation.routes import make_chats_blueprint
```

- [ ] **Adım 2: Paylaşılan depolamanın yorumu doğru kalsın** — `# One storage, shared by both
  features:` → `# One storage, shared by every feature that keeps files:` (kayıt da onu kullanıyor;
  üreticiler kullanmıyor).

- [ ] **Adım 3: Bağlama**, `_producers_bp`'nin altına; `create_app`'in listesi `_chats_bp` ile biter:

```python
# The agent's chats: one record per project, kept in the project's own folder (madde 417).
_chat_record = DriveChatRecord(_storage)
_chats_bp = make_chats_blueprint(new_chat=partial(new_chat, _chat_record),
                                 list_chats=partial(list_chats, _chat_record),
                                 open_chat=partial(open_chat, _chat_record))

app = create_app(blueprints=[_projects_bp, _reference_settings_bp, _photo_bp, _references_bp,
                             _producers_bp, _chats_bp])
```

## Görev 7: Koşu — yeşil, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi.

Beklenen: `queen-editor` pytest'inde test turunun 42 kırmızısı yeşil. Tek kırmızı
`test_every_link_to_a_roadmap_resolves_from_where_it_is_written` kalır — kod değil: bu dalın açıldığı
`baa32885`'te v9'un yol haritası yok; `feat/queen-editor-v9`'a birleşince çözülür. Öteki üç satır
yeşil.

**Koşuldu:** `1 failed, 1330 passed` — tek kırmızı o bağlantı testi, iki spec'in yol haritası
bağlantısı · vitest `794 passed (794)` · queen-agent `989 passed` · queen-agent vitest
`838 passed (838)`.

- [ ] **Adım 2: Commit** — kod, uygulama spec'i ve bu plan; `feat(queen-editor): 417 -- …`.
