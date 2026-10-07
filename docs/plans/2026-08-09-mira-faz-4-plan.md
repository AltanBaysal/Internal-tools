# Mira Faz 4 (Composer ve sohbet kaydı) — Uygulama Planı

**Hedef:** Composer'ın taslak kuralları (Madde 8) ve sohbetin ilk mesajıyla diske düşmesi (Madde 9).

**Mimari:** Taslak composer'ın içinde yaşar, dışarıya yalnız `onSubmit(text)` çıkar. Sunucu tarafında
sohbet `workspace` feature'ının ikinci deposudur: `ChatStore` portu, `FileChatStore` uygulaması ve üç
rota. `start_chat` projenin varlığını proje deposundan doğrular.

**Kaynak spec:** [Faz 4](../specs/2026-08-09-mira-faz-4-sohbet-kaydi-design.md)

## Global Kısıtlar

- Mesaj **diske yazılmadan** hiçbir cevap dönülmez.
- `at` tam ISO damgasıdır; `11:04`'e çevirmek tarayıcının işi.
- Sohbet listesi yeniden eskiye, proje listesi eskiden yeniye — ikisi ayrı sorulara cevap veriyor.
- Liste yanıtı mesaj taşımaz.
- Komutlar sabit: `python -m pytest d:\code\github\internal-tools\mira -q` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend test` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend run build`

---

### Task 1: Sohbet domain'i

**Dosyalar:** Oluştur `domain/chat.py`, `domain/errors.py`, `domain/usecases/start_chat.py`,
`domain/usecases/list_chats.py` · Değiştir `domain/ports.py`, `domain/usecases/edit_project.py` ·
Test `backend/tests/test_start_chat.py`

`errors.py` mevcut iki istisnayı toplar (`ProjectNotFound`, `InvalidProjectName`) ve iki yenisini
ekler (`EmptyMessage`). Gerekçe: `start_chat`'in `edit_project`'ten istisna ithal etmesi ters bir
bağımlılık okuması olurdu. `edit_project` bunları `errors`'tan ithal ettiği için mevcut testlerin
ithal yolu bozulmuyor.

- [ ] **Adım 1: Test yaz** — `test_start_chat.py`:

```python
import pytest

from backend.features.workspace.domain.chat import TITLE_LIMIT, chat_title
from backend.features.workspace.domain.errors import EmptyMessage, ProjectNotFound
from backend.features.workspace.domain.usecases.list_chats import list_chats
from backend.features.workspace.domain.usecases.start_chat import start_chat


class FakeProjectStore:
    def __init__(self, ids=("p1",)):
        self.ids = set(ids)

    def get(self, project_id):
        return object() if project_id in self.ids else None


class FakeChatStore:
    def __init__(self):
        self.saved = []

    def add(self, project_id, chat):
        self.saved.append((project_id, chat))

    def list_for(self, project_id):
        return [chat for pid, chat in self.saved if pid == project_id]


def _start(text, chat_store=None, new_id="c1", now="2026-08-09T11:04:00+00:00"):
    return start_chat(
        chat_store or FakeChatStore(), FakeProjectStore(), "p1", text, new_id=new_id, now=now
    )


def test_a_short_message_is_the_title_as_it_is():
    assert chat_title("Write the intro") == "Write the intro"


def test_a_long_message_is_cut_and_marked():
    title = chat_title("x" * 60)
    assert title == "x" * TITLE_LIMIT + "…"


def test_a_message_of_exactly_the_limit_gets_no_ellipsis():
    # Nothing was cut off, so nothing should claim it was.
    assert chat_title("x" * TITLE_LIMIT) == "x" * TITLE_LIMIT


def test_the_chat_is_born_with_its_first_message():
    chat = _start("Hello there")
    assert chat.title == "Hello there"
    assert [(m.role, m.text) for m in chat.messages] == [("user", "Hello there")]
    assert chat.messages[0].at == "2026-08-09T11:04:00+00:00"


def test_the_chat_is_handed_to_the_store():
    store = FakeChatStore()
    chat = _start("Hello", chat_store=store)
    assert store.saved == [("p1", chat)]


@pytest.mark.parametrize("blank", ["", "   ", "\n\t"])
def test_an_empty_message_starts_nothing(blank):
    store = FakeChatStore()
    with pytest.raises(EmptyMessage):
        _start(blank, chat_store=store)
    assert store.saved == []


def test_an_unknown_project_starts_nothing():
    with pytest.raises(ProjectNotFound):
        start_chat(
            FakeChatStore(), FakeProjectStore(), "nope", "hi", new_id="c1", now="2026-08-09T11:04:00+00:00"
        )


def test_chats_come_back_newest_first():
    store = FakeChatStore()
    _start("first", chat_store=store, new_id="c1", now="2026-08-09T10:00:00+00:00")
    _start("second", chat_store=store, new_id="c2", now="2026-08-09T12:00:00+00:00")
    assert [c.id for c in list_chats(store, "p1")] == ["c2", "c1"]
```

- [ ] **Adım 2:** koş → FAIL

- [ ] **Adım 3: Yaz**

`domain/chat.py`:

```python
"""Chat and Message -- what was said in one conversation."""
from dataclasses import dataclass

TITLE_LIMIT = 42


@dataclass(frozen=True)
class Message:
    role: str  # "user" or "ai"
    at: str  # ISO 8601; the browser turns it into 11:04
    text: str


@dataclass(frozen=True)
class Chat:
    id: str
    title: str
    created_at: str
    messages: tuple = ()

    @property
    def last_activity(self):
        return self.messages[-1].at if self.messages else self.created_at


def chat_title(text):
    """A chat is named after the message that started it."""
    trimmed = text.strip()
    if len(trimmed) <= TITLE_LIMIT:
        return trimmed
    # Only a message that actually lost something is marked as cut.
    return trimmed[:TITLE_LIMIT] + "…"
```

`domain/errors.py`:

```python
"""Errors the workspace domain raises. The routes turn them into status codes."""


class ProjectNotFound(Exception):
    """No project carries this id."""


class InvalidProjectName(Exception):
    """A project cannot be left without a name."""


class EmptyMessage(Exception):
    """A message with nothing in it does not start a chat."""


class ChatNotFound(Exception):
    """No chat carries this id inside that project."""
```

`edit_project.py` kendi istisna tanımlarını siler ve `from backend.features.workspace.domain.errors
import InvalidProjectName, ProjectNotFound` ile ithal eder.

`domain/usecases/start_chat.py`:

```python
"""Start a chat -- a chat is born with its first message; there is no empty chat."""
from backend.features.workspace.domain.chat import Chat, Message, chat_title
from backend.features.workspace.domain.errors import EmptyMessage, ProjectNotFound


def start_chat(chat_store, project_store, project_id, text, new_id, now):
    if project_store.get(project_id) is None:
        raise ProjectNotFound(project_id)
    trimmed = text.strip()
    if not trimmed:
        raise EmptyMessage()
    chat = Chat(
        id=new_id,
        title=chat_title(trimmed),
        created_at=now,
        messages=(Message(role="user", at=now, text=trimmed),),
    )
    chat_store.add(project_id, chat)
    return chat
```

`domain/usecases/list_chats.py`:

```python
"""List chats newest first -- both the sidebar and the project screen show the latest on top."""


def list_chats(chat_store, project_id):
    # Newest by last activity, not by creation: a chat that was answered a minute ago belongs at the
    # top even if it started yesterday. The id breaks ties so the order never wobbles.
    return sorted(
        chat_store.list_for(project_id),
        key=lambda chat: (chat.last_activity, chat.id),
        reverse=True,
    )
```

`ports.py` — `ChatStore` protokolü eklenir (`add`, `get`, `list_for`).

- [ ] **Adım 4:** koş → PASS

---

### Task 2: Sohbet deposu ve rotalar

**Dosyalar:** Oluştur `data/file_chat_store.py` · Değiştir `presentation/routes.py`, `main.py` ·
Test `backend/tests/test_file_chat_store.py`, `backend/tests/test_chats_api.py`

`make_workspace_bp(project_store, chat_store)` iki depo alır; `test_projects_api.py`'nin `_client`
yardımcısı da güncellenir.

- [ ] **Adım 1: Testleri yaz** (özet — tam hâli uygulamada):
  `test_file_chat_store.py`: sohbet yeni bir depo örneğinden okunuyor · id dosya adından geliyor ve
  dosyanın içinde tekrar edilmiyor · `.json` olmayan girdiler atlanıyor · olmayan sohbet `None`.
  `test_chats_api.py`: `POST` 201 ve sohbeti döndürüyor · boş metin 400 · bilinmeyen proje 404 ·
  `GET` listesi yeniden eskiye ve **mesaj taşımıyor** · tek sohbet mesajları taşıyor · bilinmeyen
  sohbet 404 · sohbet kurulunca proje kartının `chats` sayısı 1 oluyor.

- [ ] **Adım 2:** koş → FAIL

- [ ] **Adım 3:** `FileChatStore` ve üç rotayı yaz; `main.py`'de bağla.

- [ ] **Adım 4:** koş → PASS

---

### Task 3: Composer kuralları

**Dosyalar:** `ComposerShell.jsx` → `Composer.jsx` (kontrollü) · Değiştir `HomeScreen.jsx`,
`ProjectScreen.jsx`, `workspace.css` · Test `Composer.test.jsx`

Öneri baloncukları composer'ın içine taşınır (isteğe bağlı `suggestions` prop'u). Gerekçe: öneri
taslağı dolduruyor, yani taslağa erişmesi gerekiyor — dışarıda bırakmak taslağı yukarı kaldırmayı
zorunlu kılardı ve kutu artık kendi hâlinin sahibi olmazdı.

- [ ] **Adım 1: Test yaz** — `Composer.test.jsx`: boş taslakta pasif · yalnız boşlukta pasif ·
  yazınca canlanıyor · Enter gönderiyor · Shift+Enter göndermiyor · gönderince taslak boşalıyor ·
  öneri dolduruyor ama göndermiyor · `onSubmit` yokken Enter çökmüyor.

- [ ] **Adım 2:** koş → FAIL

- [ ] **Adım 3:** `Composer.jsx`'i yaz, iki ekranı ona bağla, `.composer__send--ready` stilini ekle.

- [ ] **Adım 4:** koş → PASS · derle

---

## Öz-denetim

**Spec kapsaması.** On bir cümle: 1 Task 1'in üç başlık testi · 2 Task 2'nin depo testi · 3 Task 1
`test_an_empty_message_starts_nothing` + Task 2'nin 400 testi · 4 Task 2'nin 404 testi · 5 Task 1
`test_chats_come_back_newest_first` · 6 Task 2'nin liste/tek sohbet testleri · 7-11 Task 3'ün sekiz
testi.

**Ad tutarlılığı.** `Chat(id, title, created_at, messages)` ve `Message(role, at, text)` domain'de;
diskteki ve HTTP'deki karşılıkları `createdAt` ve `messages[].at`, çeviri yalnız `file_chat_store.py`
ve `routes.py` sınırlarında. `start_chat(chat_store, project_store, project_id, text, new_id, now)`
imzası Task 1 ve Task 2'de aynı. Ön yüzdeki `onSubmit(text)` tek argüman alıyor.

**Risk.** `make_workspace_bp` imzası değişiyor; `test_projects_api.py` de bu yüzden dokunuluyor.
Değişiklik tek yerde (kompozisyon kökü) bağlandığı için başka çağıran yok.
