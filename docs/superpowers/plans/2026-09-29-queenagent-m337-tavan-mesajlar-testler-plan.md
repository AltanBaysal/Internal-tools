# Madde 337 — Tavan ve gösterge yalnız sohbetin mesajlarını ölçer · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tavanın ve göstergenin yalnız açık satırdaki mesajların metnini ölçtüğünü, ve `Usage.context`'in
kalktığını tutan testler, kırmızı.

**Architecture:** Dört arka uç test dosyası. Ölçü alanın kuralı olarak `chat.py`'nin `chat_size(chat)`'i;
kapı ve kayıt `test_chats_api.py`'de; harcananın üç sayıya inmesi `test_stream_answer.py` ve
`test_file_chat_store.py`'de.

**Tech Stack:** pytest.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m337-tavan-mesajlar-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Ölçü: harf sayısı × 3 ÷ 10, aşağı yuvarlanır — 1.000 harf 300; 166.667 harf 50.000, 166.666 harf 49.999.
- Tavan 50.000 kalır.
- Kod, yorum ve test adı İngilizce. Ön uca ve üretim koduna bu turda dokunulmaz.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Dört dosyada testler, kırmızı

**Files:**
- Modify: `queen-agent/backend/tests/test_chat.py` — import'a `ToolCall`; *the ceiling* bölümü baştan; `_said`; açık satır testi
- Modify: `queen-agent/backend/tests/test_chats_api.py` — *the ceiling* bölümü
- Modify: `queen-agent/backend/tests/test_stream_answer.py` — *what the answer spent* bölümü
- Modify: `queen-agent/backend/tests/test_file_chat_store.py` — harcananın diske gidişi

**Interfaces:**
- Produces: uygulama turunun karşılayacağı — `chat.py`'de `chat_size(chat) -> int`; `is_full(chat)`
  `chat_size`'ı okur; `Usage(sent, cached, answered)`, `context` alanı yok; diskte `usage`'da `context`
  anahtarı yazılmaz, okunurken yok sayılır; `/chats/<id>`'nin `context.sent`'i `chat_size`.

- [ ] **Step 1: `test_chat.py`**

Import satırı:

```python
from backend.features.workspace.domain.chat import Chat, Message, ToolCall, Usage
```

*the ceiling* bölümü (`_answered`'dan `test_a_chat_is_full_at_the_ceiling_and_not_before`'a kadar) şu olur:

```python
# --- the ceiling on a chat's context (Madde 92; the messages alone since Madde 337) -------------

AT = "2026-08-09T11:04:00.000+00:00"


def _answered(question, answer, **rest):
    """A chat of one question and its answer; the answer carries whatever else it is given."""
    return Chat(
        id="c1",
        title="hi",
        created_at=AT,
        messages=(
            Message(role="user", at=AT, text=question),
            Message(role="ai", at=AT, text=answer, **rest),
        ),
    )


def test_a_chats_size_is_the_text_of_its_messages():
    # Madde 337. What a chat sends the model of itself is each message's text and nothing else, so
    # that is what fills it. An estimate rather than a count, by DeepSeek's own rough measure: an
    # English character is about 0.3 of a token.
    from backend.features.workspace.domain.chat import chat_size

    assert chat_size(_answered("a" * 600, "a" * 400)) == 300


def test_an_empty_chat_has_no_size():
    from backend.features.workspace.domain.chat import chat_size

    assert chat_size(Chat(id="c1", title="hi", created_at=AT)) == 0


def test_what_a_turn_spent_and_did_is_not_the_chats_size():
    # Madde 337, the row's own words: a turn that calls many tools or opens a big file does not grow
    # the gauge. The steps, the files and the bill ride on the message but never reach the model as
    # the chat -- and the opened-files box is not a message at all.
    from backend.features.workspace.domain.chat import chat_size, is_full

    busy = _answered(
        "a" * 600,
        "a" * 400,
        usage=Usage(120_000, 0, 5),
        calls=tuple(ToolCall("read_file", "scene.json", "900 lines") for _ in range(16)),
        files=("scene.json",),
    )
    assert chat_size(busy) == 300
    assert not is_full(busy)


def test_the_ceiling_is_fifty_thousand():
    # The reason is quality rather than capacity: the window is 256k, so this is a fifth of it.
    # Models get worse as the input grows and what sits in the middle goes unread -- fitting is not
    # the same as being read.
    from backend.features.workspace.domain.chat import CONTEXT_CEILING

    assert CONTEXT_CEILING == 50_000


def test_a_chat_is_full_when_its_messages_reach_the_ceiling_and_not_before():
    from backend.features.workspace.domain.chat import CONTEXT_CEILING, chat_size, is_full

    reached = _answered("", "a" * 166_667)
    below = _answered("", "a" * 166_666)
    assert chat_size(reached) == CONTEXT_CEILING
    assert is_full(reached)
    assert not is_full(below)


def test_a_usage_carries_no_context():
    # Madde 337 took the ceiling off the engine's numbers, and the ceiling was the only reader of the
    # last round's size. A field written every turn and read by nothing is a question every later
    # reader has to answer for themselves.
    assert "context" not in [field.name for field in fields(Usage)]
```

`_said` şu olur:

```python
def _said(role, text):
    return Message(role=role, at=AT, text=text)
```

`test_the_ceiling_is_measured_on_the_open_line` şu olur:

```python
def test_the_ceiling_is_measured_on_the_open_line():
    # A turn that only exists on a line nobody is on is not sent any more, and what is not sent
    # cannot fill the chat. Measuring it would close a conversation over work it has walked away
    # from.
    from backend.features.workspace.domain.chat import is_full

    chat = Chat(
        id="c1",
        title="hi",
        created_at=AT,
        messages=(_said("user", "hi"), _said("ai", "a" * 200_000)),
        versions=(_version("l2", "", 1),),
        active="l2",
    )
    assert not is_full(chat)
    assert is_full(replace(chat, active=""))
```

- [ ] **Step 2: `test_chats_api.py`**

*the ceiling* bölümü (`_spending`'den `test_the_record_says_how_much_of_the_ceiling_it_has_used`'a
kadar) şu olur:

```python
# --- the ceiling on a chat's context (Madde 92; the messages alone since Madde 337) -------------

# 170,000 characters: 51,000 tokens by the chat's measure, past the ceiling.
LONG = "a" * 170_000


def _answering(tmp_path, answer, sent=0):
    """A client whose one answer says this, and reports having sent this many tokens."""
    engine = ScriptedEngine(
        [[{"text": answer}, {"usage": {"sent": sent, "cached": 0, "answered": 5}}]]
    )
    return _client(tmp_path, engine)


def test_a_full_chat_refuses_a_new_sentence(tmp_path):
    # The ceiling stops the turn before anything is written: a refused sentence that reached the
    # disk would leave the chat waiting for an answer nobody can give it.
    client = _answering(tmp_path, LONG)
    pid, cid = _started(client)
    before = len(_record(client, pid, cid)["messages"])
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"})
    assert refused.status_code == 400
    assert "ceiling" in refused.get_json()["error"]
    assert len(_record(client, pid, cid)["messages"]) == before


def test_a_full_chat_refuses_a_second_attempt_too(tmp_path):
    # Trying again is sending the same oversized request a second time. The reason has to be the
    # ceiling rather than whatever else the door might have said first -- otherwise the screen
    # tells the user something true and useless.
    client = _answering(tmp_path, LONG)
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid})
    assert refused.status_code == 400
    assert "ceiling" in refused.get_json()["error"]


def test_a_turn_that_spent_a_lot_but_said_little_does_not_fill_the_chat(tmp_path):
    # Madde 337. Sixty thousand is what the old ceiling read: the whole last request, with its
    # instructions, its tool steps and its opened files. None of that is the conversation.
    client = _answering(tmp_path, "Done.", sent=60_000)
    pid, cid = _started(client)
    kept = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"})
    assert kept.status_code == 200
    kept.get_data()
    said = [message["text"] for message in _record(client, pid, cid)["messages"]]
    assert said[:3] == ["hello", "Done.", "and more"]


def test_the_record_says_how_much_of_the_ceiling_it_has_used(tmp_path):
    # Both numbers, because the gauge draws a share and a share needs its denominator. A second
    # copy of the ceiling living in the browser is the thing that would go stale. "hello" and 995
    # characters of answer are a thousand characters: 300 tokens.
    from backend.features.workspace.domain.chat import CONTEXT_CEILING

    client = _answering(tmp_path, "a" * 995, sent=41_000)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["context"] == {"sent": 300, "ceiling": CONTEXT_CEILING}
```

- [ ] **Step 3: `test_stream_answer.py`**

`test_the_answer_remembers_what_it_spent`:

```python
def test_the_answer_remembers_what_it_spent(tmp_path):
    chats, _, _, _ = _run(tmp_path, [[{"text": "Hello"}, spent(1200, 900, 42)]])
    assert _kept(chats).usage == Usage(1200, 900, 42)
```

`test_what_two_rounds_spent_is_added_up`'ın son satırı:

```python
    assert _kept(chats).usage == Usage(2500, 1800, 30)
```

`test_counts_repeated_inside_one_round_are_not_added_twice` ve
`test_a_stopped_answer_still_says_what_it_spent`'in son satırları, dördüncü sayıyı anlatan
yorumlarıyla birlikte:

```python
    assert _kept(chats).usage == Usage(1200, 900, 2)
```

```python
    assert _kept(chats).usage == Usage(1200, 900, 5)
```

`test_the_turn_remembers_what_its_last_round_carried` ve
`test_a_tools_request_does_not_change_how_big_the_conversation_got` silinir.

- [ ] **Step 4: `test_file_chat_store.py`**

`test_the_size_the_last_round_carried_survives_a_round_trip` silinir.
`test_a_stored_usage_from_before_the_field_reads_zero` yerine:

```python
def test_what_an_answer_spent_is_written_as_three_numbers(tmp_path):
    # Madde 337: the ceiling reads the messages now, and nothing reads the last round's size.
    raw = Store(str(tmp_path))
    chat = replace(
        _chat(),
        messages=(
            Message(
                role="ai",
                at="2026-08-09T11:05:00+00:00",
                text="Here it is.",
                usage=Usage(sent=12400, cached=9100, answered=842),
            ),
        ),
    )
    FileChatStore(raw).add("p1", chat)
    stored = json.loads(raw.read_text("p1/chats/c1.json"))["messages"][0]["usage"]
    assert stored == {"sent": 12400, "cached": 9100, "answered": 842}


def test_a_chat_written_with_the_last_rounds_size_still_reads(tmp_path):
    # Every chat answered between Madde 133 and 337 carries the key. No migration: it is ignored,
    # and it drops the next time the chat is written.
    raw = Store(str(tmp_path))
    raw.write_text(
        "p1/chats/old.json",
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00", "messages": ['
        '{"role": "ai", "at": "2026-08-09T11:05:00+00:00", "text": "hi",'
        ' "usage": {"sent": 12400, "cached": 9100, "answered": 842, "context": 11400}}]}',
    )
    assert FileChatStore(raw).get("p1", "old").messages[0].usage == Usage(12400, 9100, 842)
```

- [ ] **Step 5: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen `python -m pytest queen-agent -q`'de kırmızılar: `test_chat.py`'de `chat_size` import'u
düşenler (1, 2, 3, 5), `test_a_usage_carries_no_context`, açık satır testi; `test_chats_api.py`'de
reddetmeyen iki kapı, kabul etmeyen kapı ve 300 yerine 41.000 diyen kayıt; `test_stream_answer.py`'de
dördüncü alanı 0 olmayan dört `Usage`; `test_file_chat_store.py`'de `context` yazan ve okuyan iki
test. queen-editor'ün arka ucu 377'nin iki kırmızısı; ön uçlar yeşil.

- [ ] **Step 6: Kırmızıyı commit'le**

```powershell
git add queen-agent/backend/tests/test_chat.py queen-agent/backend/tests/test_chats_api.py queen-agent/backend/tests/test_stream_answer.py queen-agent/backend/tests/test_file_chat_store.py docs/superpowers/specs/2026-09-29-queenagent-m337-tavan-mesajlar-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m337-tavan-mesajlar-testler-plan.md
git commit -m @'
test(queen-agent): Madde 337 red -- the ceiling and the gauge measure the chat's messages alone, and a usage carries no context

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
