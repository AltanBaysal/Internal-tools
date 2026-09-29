# Madde 345 — Sohbet baştan kırpılabilir · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dolu bir sohbetin baştan kırpılabildiğini — modele ve ölçüye yalnız kesimden sonrası
gider, bütün mesajlar kayıtta kalır, sohbet yeniden tur alır — tutan testler, kırmızı.

**Architecture:** Dört arka uç test dosyası. Kural `chat.py`'de (`sent_from`, `sent_messages`,
`trim_point`, `TRIM_KEEPS`, `Message.trimmed`); kapı ve kayıt `test_chats_api.py`'de; modele gidenin
kesildiği `test_stream_answer.py`'de; diskteki alan `test_file_chat_store.py`'de.

**Tech Stack:** pytest.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m345-kirpma-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Ölçü 337'ninki: harf sayısı × 3 ÷ 10, aşağı yuvarlanır. Tavan 50.000; kırpma 10.000'i geçmeyeni bırakır.
- Kesim yalnız bir sorunun önüne düşer; hiçbiri yetmezse son sorunun önüne.
- Kapı `POST /api/projects/<p>/chats/<c>/trim`: `200 {}`, `400 {"error": "this chat is not full"}`,
  `404 {"error": "chat not found"}`. Kayıtta her zaman `trimmed`.
- Kod, yorum ve test adı İngilizce. Ön uca ve üretim koduna bu turda dokunulmaz.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Dört dosyada testler, kırmızı

**Files:**
- Modify: `queen-agent/backend/tests/test_chat.py` — dosyanın sonuna *the trim* bölümü
- Modify: `queen-agent/backend/tests/test_chats_api.py` — *the ceiling* bölümünün arkasına *trimming* bölümü
- Modify: `queen-agent/backend/tests/test_stream_answer.py` — dosyanın sonuna *a trimmed chat* bölümü
- Modify: `queen-agent/backend/tests/test_file_chat_store.py` — dosyanın sonuna *the trim* bölümü

**Interfaces:**
- Produces: uygulama turunun karşılayacağı — `chat.py`'de `Message.trimmed: int = 0`,
  `TRIM_KEEPS = 10_000`, `sent_from(chat) -> int`, `sent_messages(chat) -> tuple`,
  `trim_point(chat) -> int`; `chat_size` yalnız `sent_messages`'ı ölçer; `_conversation` yalnız
  `sent_messages`'ı gönderir; diskte mesajın `"trimmed"` anahtarı yalnız sıfır değilse; kapı ve
  kaydın `trimmed`'ı yukarıdaki gibi.

- [ ] **Step 1: `test_chat.py`** — dosyanın sonuna:

```python
# --- the trim: the oldest turns stop going to the model (Madde 345) -----------------------------


def _marked(chat, count):
    """The chat with its first line's last message carrying a trim of this many messages."""
    last = replace(chat.messages[-1], trimmed=count)
    return replace(chat, messages=chat.messages[:-1] + (last,))


def _turns(*pairs):
    """A chat whose first line is these (question, answer) turns, in order."""
    return _trunk(*[text for pair in pairs for text in pair])


def test_a_chat_nobody_trimmed_sends_its_whole_open_line():
    from backend.features.workspace.domain.chat import active_messages, sent_from, sent_messages

    chat = _trunk("hi", "Done.", "again", "Done twice.")
    assert sent_from(chat) == 0
    assert sent_messages(chat) == active_messages(chat)


def test_a_trimmed_line_sends_and_measures_only_what_follows_the_cut():
    # Madde 345, the row's own words: the oldest messages stop going to the model, and the ring
    # reads what is still sent. They stay in the record -- only what is sent moves.
    from backend.features.workspace.domain.chat import (
        active_messages,
        chat_size,
        sent_from,
        sent_messages,
    )

    chat = _marked(_trunk("a" * 600, "a" * 400, "b" * 60, "b" * 40), 2)
    assert sent_from(chat) == 2
    assert [m.text for m in sent_messages(chat)] == ["b" * 60, "b" * 40]
    assert len(active_messages(chat)) == 4
    assert chat_size(chat) == 30


def test_the_newest_trim_on_the_line_is_the_one_that_holds():
    # A trimmed chat fills again and is trimmed again; the second cut is further on, and it is the
    # one the line reads from.
    from backend.features.workspace.domain.chat import sent_from

    first = _marked(_trunk("hi", "Done.", "again", "Done twice."), 2)
    grown = replace(first, messages=first.messages + (_said("user", "more"), _said("ai", "More.")))
    assert sent_from(_marked(grown, 4)) == 4


def test_a_version_split_before_the_trim_is_not_trimmed_and_one_after_it_is():
    # The mark sits on the message that was last when the chat was trimmed -- the answer that filled
    # it. A version cut before that answer never filled, so nothing on it is trimmed; one opened
    # after it carries the mark in front of it and stays trimmed (the design's BEHAVIOUR.md).
    from backend.features.workspace.domain.chat import sent_from

    chat = _marked(_trunk("hi", "Done.", "again", "Done twice."), 2)
    before = replace(chat, versions=(_version("l2", "", 2, "again, shorter"),), active="l2")
    after = replace(chat, versions=(_version("l2", "", 4, "and more"),), active="l2")
    assert sent_from(before) == 0
    assert sent_from(after) == 2


def test_a_trimmed_chat_that_grows_back_to_the_ceiling_is_full_again():
    # 29 September: a trimmed chat that fills again shows the notice again. The measure counts from
    # the cut, so what is past it is what fills the chat.
    from backend.features.workspace.domain.chat import is_full

    trimmed = _marked(_trunk("a" * 200_000, "Done.", "hi", "Done."), 2)
    assert not is_full(trimmed)
    grown = replace(
        trimmed,
        messages=trimmed.messages + (_said("user", "go on"), _said("ai", "a" * 166_667)),
    )
    assert is_full(grown)


def test_a_trim_keeps_ten_thousand():
    # The owner's number, 28 September: "10k contexte kadar".
    from backend.features.workspace.domain.chat import TRIM_KEEPS

    assert TRIM_KEEPS == 10_000


def test_a_trim_drops_whole_turns_from_the_start_until_ten_thousand_is_left():
    # Seventeen turns of 3,000 each: 51,000, full. Three of them are 9,000 and four are 12,000, so
    # the cut stands before the fifteenth question -- message 28.
    from backend.features.workspace.domain.chat import chat_size, trim_point

    chat = _turns(*[("a" * 1000, "a" * 9000)] * 17)
    assert trim_point(chat) == 28
    assert chat_size(_marked(chat, 28)) == 9000


def test_a_trim_never_cuts_between_a_question_and_its_answer():
    # The last turn weighs 10,800 -- more than a trim keeps -- and its answer alone would fit. The
    # cut still stands before the question: the model is never handed an answer to nothing, and the
    # last turn stays whatever it weighs.
    from backend.features.workspace.domain.chat import trim_point

    chat = _turns(("a" * 100, "a" * 100), ("a" * 30_000, "a" * 6_000))
    assert trim_point(chat) == 2
```

- [ ] **Step 2: `test_chats_api.py`** — *the ceiling* bölümünden sonra, *the mode* bölümünden önce:

```python
# --- trimming a full chat from the start (Madde 345) ---------------------------------------------

# 20,000 characters: 6,000 tokens. Nine such answers fill a chat; eight do not.
PAGE = "a" * 20_000


def _filled(tmp_path):
    """A client and a chat of nine turns that has just filled, with one more answer left to give."""
    engine = ScriptedEngine([[{"text": PAGE}]] * 9 + [[{"text": "Done."}]])
    client = _client(tmp_path, engine)
    pid, cid = _started(client)
    for _ in range(8):
        client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "go on"}).get_data()
    return client, pid, cid


def test_a_full_chat_is_trimmed_from_the_start_and_keeps_every_message(tmp_path):
    # "hello" and "go on" are five characters, so each turn is 20,005: nine are 54,013 and full. One
    # turn is 6,001 and two are 12,003, so the cut stands before the ninth question -- message 16 --
    # and the ring reads the one turn still sent.
    client, pid, cid = _filled(tmp_path)
    trimmed = client.post(f"/api/projects/{pid}/chats/{cid}/trim")
    assert trimmed.status_code == 200
    assert trimmed.get_json() == {}
    record = _record(client, pid, cid)
    assert record["trimmed"] == 16
    assert len(record["messages"]) == 18
    assert record["context"]["sent"] == 6001


def test_a_trimmed_chat_takes_turns_again(tmp_path):
    client, pid, cid = _filled(tmp_path)
    client.post(f"/api/projects/{pid}/chats/{cid}/trim")
    kept = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"})
    assert kept.status_code == 200
    kept.get_data()
    said = [message["text"] for message in _record(client, pid, cid)["messages"]]
    assert said[-2:] == ["and more", "Done."]


def test_a_chat_that_is_not_full_is_not_trimmed(tmp_path):
    # Continue here is offered only on a full chat (the owner's decision, 28 September), and the rule
    # lives here rather than in the button.
    client = _client(tmp_path)
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/chats/{cid}/trim")
    assert refused.status_code == 400
    assert refused.get_json() == {"error": "this chat is not full"}
    assert _record(client, pid, cid)["trimmed"] == 0


def test_trimming_a_chat_that_is_not_there_is_a_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    refused = client.post(f"/api/projects/{pid}/chats/nope/trim")
    assert refused.status_code == 404
    assert refused.get_json() == {"error": "chat not found"}


def test_a_chat_nobody_trimmed_says_so(tmp_path):
    # Always present, like the messages' calls: the line on screen (v9-1d) reads it, and a field
    # that comes and goes makes every reader check for it first.
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["trimmed"] == 0
```

- [ ] **Step 3: `test_stream_answer.py`** — dosyanın sonuna:

```python
# --- a trimmed chat (Madde 345) ------------------------------------------------------------------


def test_a_trimmed_chat_sends_only_what_follows_the_cut(tmp_path):
    # The row's own words: in a trimmed chat only the newest part goes to the model, while every
    # message stays in the record.
    chats, files = _seeded(tmp_path)
    append_message(chats, "p1", "c1", "Done.", NOW, role="ai")
    append_message(chats, "p1", "c1", "again", NOW)
    chat = chats.get("p1", "c1")
    marked = replace(chat.messages[-1], trimmed=2)
    chats.replace("p1", replace(chat, messages=chat.messages[:-1] + (marked,)))
    engine = ScriptedEngine([[{"text": "Done again."}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    assert [
        message["content"] for message in engine.seen[0] if message["role"] in ("user", "ai")
    ] == ["again"]
    assert len(chats.get("p1", "c1").messages) == 4
```

- [ ] **Step 4: `test_file_chat_store.py`** — dosyanın sonuna:

```python
# --- the trim (Madde 345) ------------------------------------------------------------------------


def _trimmed(count):
    return replace(
        _chat(),
        messages=(
            Message(role="ai", at="2026-08-09T11:05:00+00:00", text="Here it is.", trimmed=count),
        ),
    )


def test_a_trim_survives_a_round_trip(tmp_path):
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _trimmed(4))
    assert FileChatStore(Store(str(tmp_path))).get("p1", "c1") == _trimmed(4)
    assert json.loads(raw.read_text("p1/chats/c1.json"))["messages"][0]["trimmed"] == 4


def test_a_message_that_trimmed_nothing_writes_no_field_and_reads_zero(tmp_path):
    # The rule every other field on the record keeps, and no migration: every chat on disk today
    # reads as untrimmed.
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _chat())
    assert "trimmed" not in raw.read_text("p1/chats/c1.json")
    assert FileChatStore(raw).get("p1", "c1").messages[0].trimmed == 0
```

- [ ] **Step 5: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen `python -m pytest queen-agent -q`'de on altı kırmızı: `test_chat.py`'nin sekiz yeni testi
(yok olan adlar ve `trimmed` alanı), `test_chats_api.py`'nin beşi (kapı yok, kayıtta `trimmed` yok),
`test_stream_answer.py`'nin biri, `test_file_chat_store.py`'nin ikisi. Öteki testler ve öteki üç satır
yeşil.

- [ ] **Step 6: Kırmızıyı commit'le**

```powershell
git add queen-agent/backend/tests/test_chat.py queen-agent/backend/tests/test_chats_api.py queen-agent/backend/tests/test_stream_answer.py queen-agent/backend/tests/test_file_chat_store.py docs/superpowers/specs/2026-09-29-queenagent-m345-kirpma-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m345-kirpma-testler-plan.md
git commit -m @'
test(queen-agent): Madde 345 red -- a full chat is trimmed from the start, and only what follows the cut is sent and measured

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
