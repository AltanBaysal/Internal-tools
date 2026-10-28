# Madde 345 — Sohbet baştan kırpılabilir · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `8afa8342`'nin on altı kırmızısını, yalnız onların tuttuğunu yazarak yeşile döndürmek.

**Architecture:** Kural `chat.py`'de (`Message.trimmed`, `TRIM_KEEPS`, `sent_from`, `sent_messages`,
`trim_point`); kırpma yeni use case `trim_chat.py`'de; modele giden `stream_answer`'ın
`_conversation`'ında; alan `file_chat_store.py`'de; kapı ve kayıt `routes.py`'de.

**Tech Stack:** Python, Flask, pytest.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m345-kirpma-uygulama-design.md)

## Global Constraints

- Ölçü 337'ninki: harf × 3 ÷ 10. Tavan 50.000; `TRIM_KEEPS = 10_000`.
- Kapı `POST /api/projects/<p>/chats/<c>/trim`: `{}`, `400 {"error": "this chat is not full"}`,
  `404 {"error": "chat not found"}`. Kayıtta her zaman `"trimmed"`.
- Diskte `"trimmed"` yalnız sıfır değilse.
- Ön uca dokunulmaz, `dist` derlenmez. Kod ve yorum İngilizce; yorum *neden*'i söyler.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Kural, use case, veri, kapı — yeşil

**Files:**
- Modify: `queen-agent/backend/features/workspace/domain/chat.py`
- Modify: `queen-agent/backend/features/workspace/domain/errors.py`
- Create: `queen-agent/backend/features/workspace/domain/usecases/trim_chat.py`
- Modify: `queen-agent/backend/features/workspace/domain/usecases/stream_answer.py`
- Modify: `queen-agent/backend/features/workspace/data/file_chat_store.py`
- Modify: `queen-agent/backend/features/workspace/presentation/routes.py`
- Modify: `queen-agent/CODE-STANDARD.md` — store tablosunun `chats/<id>.json` satırı

**Interfaces:**
- Consumes: test turunun adları — `Message.trimmed`, `TRIM_KEEPS`, `sent_from`, `sent_messages`,
  `trim_point`; kapının yolu ve sözleri.

- [ ] **Step 1: `chat.py`**

`Message`'ın sonuna:

```python
    # How many messages at the start of its line stopped going to the model when the chat was
    # trimmed with this one last (Madde 345). On the message rather than the chat, because a chat
    # holds several lines: a version opened after this message carries it in front of it and stays
    # trimmed, and one cut before it never filled and carries nothing. Zero is untrimmed.
    trimmed: int = 0
```

`chat_size` yalnız gideni ölçer, harf toplamı `_size`'a çıkar; `is_full`'dan sonra kırpmanın kuralı:

```python
def chat_size(chat):
    """...(337'nin metni)... What is sent since Madde 345: a trimmed chat's oldest turns stay in the
    record and stop counting."""
    return _size(sent_messages(chat))


def _size(messages):
    characters = sum(len(message.text) for message in messages)
    return characters * 3 // 10


TRIM_KEEPS = 10_000
"""The most a trim leaves the model of a full chat -- the owner's number (Madde 345)."""


def sent_from(chat):
    """Where the model starts reading the open line: its newest trim, or 0 (Madde 345)."""
    for message in reversed(active_messages(chat)):
        if message.trimmed:
            return message.trimmed
    return 0


def sent_messages(chat):
    """What the chat sends the model of itself: the open line from its trim on."""
    return active_messages(chat)[sent_from(chat) :]


def trim_point(chat):
    """Where a trim cuts the open line: before the first question after which TRIM_KEEPS at most
    is left. (Ayrıntısı spec'te: yalnız sorunun önü; yetmezse son soru.)"""
    said = active_messages(chat)
    questions = [index for index in range(1, len(said)) if said[index].role == "user"]
    for index in questions:
        if _size(said[index:]) <= TRIM_KEEPS:
            return index
    return questions[-1] if questions else 0
```

- [ ] **Step 2: `errors.py`**

```python
class ChatNotFull(Exception):
    """Only a full chat is trimmed."""
```

- [ ] **Step 3: `usecases/trim_chat.py`**

```python
from dataclasses import replace

from backend.features.workspace.domain.chat import active_messages, is_full, trim_point
from backend.features.workspace.domain.errors import ChatNotFound, ChatNotFull


def trim_chat(chat_store, project_id, chat_id):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    if not is_full(chat):
        raise ChatNotFull(chat_id)
    marked = replace(active_messages(chat)[-1], trimmed=trim_point(chat))
    chat_store.replace(project_id, _with_last(chat, marked))


def _with_last(chat, message):
    if not chat.active:
        return replace(chat, messages=chat.messages[:-1] + (message,))
    return replace(
        chat,
        versions=tuple(
            replace(version, messages=version.messages[:-1] + (message,))
            if version.id == chat.active
            else version
            for version in chat.versions
        ),
    )
```

- [ ] **Step 4: `stream_answer.py`** — `_conversation` `sent_messages(chat)`'i gönderir; import'a
  `sent_messages`.

- [ ] **Step 5: `file_chat_store.py`** — `_message_json`'da `if message.trimmed: stored["trimmed"] =
  message.trimmed`; `_as_message`'da `trimmed=message.get("trimmed", 0)`.

- [ ] **Step 6: `routes.py`** — import'lara `ChatNotFull`, `sent_from`, `trim_chat`; `post_version`'ın
  arkasına:

```python
    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/trim")
    def post_trim(project_id, chat_id):
        try:
            trim_chat(chat_store, project_id, chat_id)
        except ChatNotFound:
            return jsonify({"error": "chat not found"}), 404
        except ChatNotFull:
            return jsonify({"error": "this chat is not full"}), 400
        return jsonify({})
```

  `_chat_json`'a `"trimmed": sent_from(chat)`; *There is no PATCH here* yorumu iki kapıyı sayar.

- [ ] **Step 7: `CODE-STANDARD.md`** — `chats/<id>.json`'ın *Written when*'i: `after each message, on a
  model or skill choice, and on a trim`.

- [ ] **Step 8: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent arka ucu 963 geçer (947 + 16); öteki üç satır taban çizgisinde.

- [ ] **Step 9: Farkı oku ve commit'le**

`git diff c0b65cf5..HEAD`'i madde, FOUNDATION, CODE-STANDARD ve CLAUDE.md'nin *Style*'ına karşı oku.

```powershell
git add queen-agent/backend/features/workspace docs/specs/2026-09-29-queenagent-m345-kirpma-uygulama-design.md docs/plans/2026-09-29-queenagent-m345-kirpma-uygulama-plan.md queen-agent/CODE-STANDARD.md
git commit -m @'
feat: Madde 345 -- a full chat can be trimmed from the start; only what follows the cut is sent and measured

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
