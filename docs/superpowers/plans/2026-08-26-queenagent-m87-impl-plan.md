# Madde 87 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-26-queenagent-m87-mesaj-tek-kapidan-uygulama-design.md](../specs/2026-08-26-queenagent-m87-mesaj-tek-kapidan-uygulama-design.md)
**Bu turda yeni test yazılmaz.** Commit'lenmiş on üç kırmızı *(`4c8de91`)* yeşile döner; test
dosyalarında değişen tek şey kodun şeklini takip eden fixture'lar.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
`npm run build --prefix queen-agent/frontend`

---

## 1. `domain/usecases/append_message.py` — yaratmayı devralır

Docstring, imza ve yaratma dalı:

```python
"""Write a message into a chat, making the chat if there is not one yet.

Madde 87 folded start_chat in here. Both jobs are the same three steps -- check the text, write the
message, hand the record back -- and splitting them meant the caller had to know which one it was
doing. An empty chat_id means there is no chat yet; a chat_id that names nothing is an error, not an
invitation to make one, or a typo would quietly become a second chat.

project_store and new_id sit at the end with defaults because only the creating branch needs them:
stream_answer writes an answer into a chat that is already there and says nothing about either.
"""
from dataclasses import replace

from backend.features.workspace.domain.chat import Chat, Message, Usage, chat_title
from backend.features.workspace.domain.errors import ChatNotFound, EmptyMessage, ProjectNotFound


def append_message(
    chat_store,
    project_id,
    chat_id,
    text,
    now,
    role="user",
    files=(),
    skill="",
    calls=(),
    stopped=False,
    usage=Usage(),
    project_store=None,
    new_id="",
):
    making = not chat_id
    if making:
        if project_store.get(project_id) is None:
            raise ProjectNotFound(project_id)
    else:
        chat = chat_store.get(project_id, chat_id)
        if chat is None:
            raise ChatNotFound(chat_id)
    trimmed = text.strip()
    # A message has to carry something -- a word said, a file made, or a stop. The user's own
    # message never carries a file or that flag, so an empty one they typed is still refused. The
    # second case is the answer of a model that worked without speaking, and what it made is the
    # answer; the third is an answer somebody cut before it said anything, and the cut is what
    # happened. Calls are deliberately not on this list: looking at files and saying nothing is not
    # an answer.
    #
    # Checked before anything is written, so a refused first sentence leaves no empty chat behind.
    if not trimmed and not files and not stopped:
        raise EmptyMessage()
    message = Message(
        role=role,
        at=now,
        text=trimmed,
        files=tuple(files),
        skill=skill,
        calls=tuple(calls),
        stopped=stopped,
        usage=usage,
    )
    if making:
        # The title belongs to the message that started the chat and never moves.
        made = Chat(id=new_id, title=chat_title(trimmed), created_at=now, messages=(message,))
        chat_store.add(project_id, made)
        return made
    updated = replace(chat, messages=chat.messages + (message,))
    chat_store.replace(project_id, updated)
    return updated
```

## 2. `domain/usecases/start_chat.py`

Dosya silinir: `git rm`.

## 3. `presentation/routes.py`

**Import** — `start_chat` satırı gider. `ProjectNotFound` zaten import edilmiş *(bakıldı)*.

**`post_chat` bütünüyle gider** (66-83. satırlar).

**`post_message` adres ve gövde değiştirir.** Eski hâli (98-114) yerine:

```python
    # One door for every sentence a user says. Which chat it lands in is a field in the body rather
    # than a piece of the address, because it is allowed to be empty -- and an empty piece of a path
    # is a different address, not an empty value.
    @workspace_bp.post("/api/projects/<project_id>/messages")
    def post_message(project_id):
        payload = request.get_json(silent=True) or {}
        wanted = payload.get("chat", "")
        try:
            chat = append_message(
                chat_store,
                project_id,
                wanted,
                payload.get("text", ""),
                now=_now(),
                skill=payload.get("skill", ""),
                project_store=project_store,
                new_id=_new_id("c"),
            )
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        except EmptyMessage:
            return jsonify({"error": "a message needs text"}), 400
        # A chat that was just born is a creation; a sentence added to one is not.
        return jsonify(_chat_json(chat)), 201 if not wanted else 200
```

Uç, sohbet yaratılmayacak olsa bile bir id mintliyor. Ucuz, ve alternatifi kuralın içinde bir dal
daha açmak.

## 4. `frontend/src/features/workspace/useChatLists.js`

```js
export function startChatInProject(projectId, text, skill = "") {
  // No chat named: Madde 87's way of saying there is not one yet.
  return postJson(`/api/projects/${projectId}/messages`, { text, skill });
}
```

## 5. `frontend/src/features/workspace/useChat.js`

`send`'in içindeki istek satırı:

```js
        setChat(
          await postJson(`/api/projects/${projectId}/messages`, { chat: chatId, text, skill }),
        );
```

## 6. Fixture'lar — `test_chats_api.py`

`_started` yeni kapıya gider:

```python
def _started(client, text="hello"):
    # Every chat is born inside a project now, so both ids come back together.
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": text}).get_json()["id"]
    return pid, cid
```

Ve eski kapıya **doğrudan** giden testler taşınır. `_started` kullanmayan çağrı yerleri şunlar
*(bakıldı)* ve hepsinde `/chats` → `/messages` oluyor, gövde aynı kalıyor:

- silinen sohbet testi ve dosyalarını bırakan testi
- iki sohbetin listelenmesi ve sıralanması testleri
- listeye bakan test

`/answer` ve `/stop` çağrılarına **dokunulmuyor** — o adresler sohbet id'sini yolda taşımaya devam
ediyor.

## 7. Fixture'lar — `test_append_message.py`

`start_chat` importu düşer, `_chat` kuralın kendi yaratma dalını çağırır:

```python
def _chat(projects, chats, project_id, chat_id, text, now):
    # A chat always lives in a project, so the project is made first.
    create_project(projects, new_id=project_id, now=now)
    return append_message(
        chats, project_id, "", text, now, project_store=projects, new_id=chat_id
    )
```

## Beklenen yeşil

| Nerede | Ne yeşile döner |
|---|---|
| `test_chats_api.py` | Tek kapı yaratıyor · tek kapı ekliyor · eski yaratma ucu 405 · eski ekleme ucu 404 · tanınmayan sohbet 404 · boş metin iki yoldan da 400 · tanınmayan proje 404 · `start_chat` modülü yok · mesajın skill'i |
| `test_append_message.py` | Kural sohbeti yaratıyor · yaratırken boş metni reddediyor |
| `App.test.jsx` | Taslak tek kapıya sohbetsiz · cevap aynı kapıya sohbetiyle |

**İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.** Değişen tek şey fixture'ların adresi.
- **`stream_answer.py` açılmaz.** Çağrısı aynı kalıyor.
- **İki frontend çağıranı birleştirilmez.** 88'in işi.
- **`/answer` ve `/stop` adresleri değişmez.**
