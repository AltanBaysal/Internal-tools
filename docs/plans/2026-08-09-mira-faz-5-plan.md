# Mira Faz 5 (Sohbet ekranı) — Uygulama Planı

**Hedef:** Sohbet ekranı ve gönderme (Madde 10) · Home'dan otomatik proje + sohbet (Madde 11) · iki
sohbet listesi (Madde 12).

**Mimari:** Home'un "proje ve sohbeti birlikte aç" kuralı **tek bir uç noktada** yaşar — tarayıcının
iki isteği arka arkaya atması kuralı ön yüze taşır ve yarıda kalabilir bir işlem üretirdi. Yeni use
case'ler mevcutları besteler, kopyalamaz. Zaman biçimlendirmesi tamamen tarayıcıda.

**Kaynak spec:** [Faz 5](../specs/2026-08-09-mira-faz-5-sohbet-ekrani-design.md)

## Global Kısıtlar

- Kullanıcı balonu istek dönmeden görünür; sunucu reddederse geri alınır.
- Göreli zaman ve `HH:MM` tarayıcıda üretilir; sunucu yalnız ISO damga verir.
- `start_chat_in_new_project` `create_project` + `edit_project` + `start_chat` besteler; varsayılan
  değerler ikinci kez yazılmaz.
- Commit **açık yollarla**: `git add mira docs/...mira-faz-5...` sonra `git commit -- <aynı yollar>`.
- Komutlar sabit: `python -m pytest d:\code\github\internal-tools\mira -q` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend test` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend run build`

---

### Task 1: Mesaj ekleme ve otomatik proje (domain)

**Dosyalar:** Oluştur `domain/usecases/append_message.py`, `domain/usecases/start_chat_in_new_project.py`,
`domain/usecases/list_recent_chats.py` · Değiştir `domain/ports.py` · Test
`backend/tests/test_append_message.py`

- [ ] **Adım 1: Test yaz** — kanıtlanacaklar: mesaj sona ekleniyor ve başlık değişmiyor · boş metin
  reddediliyor ve sohbet dokunulmadan kalıyor · bilinmeyen sohbet `ChatNotFound` · yeni projeli
  başlangıç projeyi ve sohbeti aynı adla kuruyor · boş metin proje de kurmuyor · `list_recent_chats`
  bütün projelerin sohbetlerini yeniden eskiye veriyor.
- [ ] **Adım 2:** koş → FAIL
- [ ] **Adım 3: Yaz**

```python
"""Append a message to an existing chat."""
from dataclasses import replace

from backend.features.workspace.domain.chat import Message
from backend.features.workspace.domain.errors import ChatNotFound, EmptyMessage


def append_message(chat_store, project_id, chat_id, text, now, role="user"):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    trimmed = text.strip()
    if not trimmed:
        raise EmptyMessage()
    # The title belongs to the message that started the chat and never moves.
    updated = replace(chat, messages=chat.messages + (Message(role=role, at=now, text=trimmed),))
    chat_store.replace(project_id, updated)
    return updated
```

```python
"""A message sent from home opens both a project and a chat."""
from backend.features.workspace.domain.chat import chat_title
from backend.features.workspace.domain.errors import EmptyMessage
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.start_chat import start_chat


def start_chat_in_new_project(project_store, chat_store, text, new_project_id, new_chat_id, now):
    trimmed = text.strip()
    if not trimmed:
        raise EmptyMessage()
    # Composed rather than copied: the defaults a new project is born with have one home, and the
    # name is then set from the message with the same rule that names the chat.
    create_project(project_store, new_id=new_project_id, now=now)
    project = edit_project(project_store, new_project_id, name=chat_title(trimmed))
    chat = start_chat(chat_store, project_store, new_project_id, trimmed, new_id=new_chat_id, now=now)
    return project, chat
```

```python
"""Every chat in the workspace, newest first -- what the sidebar's Recent chats shows."""


def list_recent_chats(chat_store):
    return sorted(
        chat_store.list_all(),
        key=lambda pair: (pair[1].last_activity, pair[1].id),
        reverse=True,
    )
```

`ports.py`: `ChatStore` `replace(project_id, chat)` ve `list_all() -> list[tuple[str, Chat]]` kazanır.

- [ ] **Adım 4:** koş → PASS

---

### Task 2: Depo ve rotalar

**Dosyalar:** Değiştir `data/file_chat_store.py`, `presentation/routes.py` · Test
`backend/tests/test_chats_api.py` (ekleme)

`FileChatStore.replace` `_write`'a düşer. `list_all` kökteki her dizini gezer ve o dizinin
sohbetlerini `(project_id, chat)` çifti olarak toplar.

Rotalar: `POST /api/chats` `{text}` → `{project, chat}` (201) · `POST /api/projects/<pid>/chats/<cid>/messages`
`{text}` → güncel sohbet · `GET /api/chats` → her satırda `projectId` + sohbet özeti.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS

---

### Task 3: Zaman biçimlendirme

**Dosyalar:** Oluştur `shared/time.js` · Test `shared/time.test.js`

`clockTime(iso)` → `HH:MM` (yerel saat). `relativeTime(iso, now)` → `just now` (60sn altı) ·
`Nm ago` · `Nh ago` · `yesterday` · `N days ago` · 7 günden sonra tarih. `now` parametre olarak
girer, böylece test sahte saat kurmadan çalışır.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS

---

### Task 4: Sohbet ekranı ve listeler

**Dosyalar:** Oluştur `features/workspace/ChatScreen.jsx`, `features/workspace/useChat.js`,
`features/workspace/useRecentChats.js` · Değiştir `Sidebar.jsx`, `ProjectScreen.jsx`,
`HomeScreen.jsx`, `App.jsx`, `workspace.css` · Test `ChatScreen.test.jsx`, `App.test.jsx` (ekleme)

`useChat(projectId, chatId)` sohbeti çeker ve `send(text)` verir. `send` mesajı **önce** yerel
listeye ekler (`pending` işaretiyle), sonra isteği atar; başarıda sunucunun sohbetiyle değiştirir,
başarısızlıkta iyimser mesajı çıkarır ve hatayı yazar.

`App.jsx`:
- Home'un `onSend`'i `POST /api/chats` çağırır, dönen `{project, chat}` ile `/p/<pid>/c/<cid>`'ye gider
  ve proje listesini tazeler.
- Proje ekranının `onSend`'i `POST /api/projects/<pid>/chats` çağırır ve aynı adrese gider.
- `route.view === "chat"` dalında `<ChatScreen …/>`.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS · derle

---

## Öz-denetim

**Spec kapsaması.** On iki cümle: 1-3 Task 1-2 · 4 Task 1 · 5 Task 2 · 6-7 Task 4 (`ChatScreen.test`)
+ Task 3 · 8-10 Task 4 (`App.test`) · 11 Task 4 (`Sidebar` testi) · 12 Task 3.

**Ad tutarlılığı.** `append_message(chat_store, project_id, chat_id, text, now, role)` — Faz 6 aynı
imzayı `role="ai"` ile çağıracak, o yüzden `role` bugünden parametre. `start_chat_in_new_project`
`(project, chat)` çifti döndürüyor; rota bunu `{"project": …, "chat": …}` olarak sarıyor ve ön yüz
aynı iki anahtarı okuyor. `list_all()` çift döndürüyor, `list_recent_chats` aynı çifti sıralıyor,
rota `projectId`'yi oradan alıyor.

**Risk.** İyimser balon iki yerde tutulabilir hâle gelmemeli: tek kaynak `useChat`'in kendi
dizisidir, `ChatScreen` yalnız çizer.
