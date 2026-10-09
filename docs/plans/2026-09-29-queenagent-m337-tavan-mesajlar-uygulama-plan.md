# Madde 337 — Tavan ve gösterge yalnız sohbetin mesajlarını ölçer · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 337'nin on altı kırmızı testini yeşile getirmek: tavan ve gösterge yalnız açık satırdaki
mesajların metnini ölçer, ve `Usage.context` kalkar.

**Architecture:** Kural `chat.py`'de (`chat_size`, `is_full`); tur faturayı üç sayıyla toplar; depo
dördüncü anahtarı yazmaz; yol kaydın `context.sent`'ine `chat_size`'ı koyar.

**Tech Stack:** Python, Flask, pytest.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m337-tavan-mesajlar-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel; test dosyaları değişmez.
- Ölçü: `sum(len(message.text) for message in active_messages(chat)) * 3 // 10`. Tavan 50.000.
- Ön uca dokunulmaz, `dist` derlenmez. Kaydın anahtarı `context.sent` kalır.
- Yorumlar İngilizce, *neden*'i ve bugün doğru olanı söyler.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Ölçü, fatura, depo ve yol — yeşil

**Files:**
- Modify: `queen-agent/backend/features/workspace/domain/chat.py` — `Usage`, `CONTEXT_CEILING`'in açıklaması, `last_context` → `chat_size`, `is_full`
- Modify: `queen-agent/backend/features/workspace/domain/usecases/stream_answer.py` — iki `Usage(...)`
- Modify: `queen-agent/backend/features/workspace/data/file_chat_store.py` — `_message_json`, `_as_usage`
- Modify: `queen-agent/backend/features/workspace/presentation/routes.py` — import, `_chat_json`

**Interfaces:**
- Produces: `chat_size(chat) -> int`; `is_full(chat) -> bool`; `Usage(sent=0, cached=0, answered=0)`.

- [ ] **Step 1: `chat.py` — `Usage`'ın son alanı silinir**

```python
    answered: int = 0
```

(`context: int = 0` ve üstündeki beş satırlık yorum gider.)

- [ ] **Step 2: `chat.py` — tavan ve ölçü**

`CONTEXT_CEILING`'den dosyanın sonuna kadar:

```python
CONTEXT_CEILING = 50_000
"""How big one chat's messages may grow before it stops taking new turns.

Not a capacity limit -- the window is 256k, so this is a fifth of it. It is a quality one: models
get worse as the input grows and what sits in the middle of a long request goes unread, so fitting
is not the same as being read. Above 200k the input also costs twice as much.
"""


def chat_size(chat):
    """How big the conversation is, in tokens: its messages' text and nothing else (Madde 337).

    That is all a chat sends the model of itself. A message's steps, files and bill stay on disk;
    the system prompt, the tool descriptions, the skill's instruction and the opened-files box come
    back the same in a new chat, so closing this one over them would win nothing.

    The open line, because a line nobody is standing on is not sent (Madde 195). An estimate rather
    than a count: the app ships no tokenizer -- Flask is its one dependency -- and DeepSeek's own
    rough measure is that an English character is about 0.3 of a token. Whole numbers, so the
    ceiling's edge is not moved a character by rounding.
    """
    characters = sum(len(message.text) for message in active_messages(chat))
    return characters * 3 // 10


def is_full(chat):
    """Whether this chat has reached the ceiling and may not take another turn."""
    return chat_size(chat) >= CONTEXT_CEILING
```

- [ ] **Step 3: `stream_answer.py` — turun faturası**

```python
            if round_spent:
                spent = Usage(
                    spent.sent + round_spent["sent"],
                    spent.cached + round_spent["cached"],
                    spent.answered + round_spent["answered"],
                )
```

```python
                if result.spent:
                    # A second request, paid for inside this turn, and the stamp is the only place
                    # anybody would look for it.
                    spent = Usage(
                        spent.sent + result.spent.get("sent", 0),
                        spent.cached + result.spent.get("cached", 0),
                        spent.answered + result.spent.get("answered", 0),
                    )
```

- [ ] **Step 4: `file_chat_store.py`**

`_message_json`'da `usage` üç anahtarla:

```python
        stored["usage"] = {
            "sent": message.usage.sent,
            "cached": message.usage.cached,
            "answered": message.usage.answered,
        }
```

`_as_usage`:

```python
def _as_usage(raw):
    # Field by field rather than **raw: a chat on disk can be edited by hand, and a key this app
    # does not know would turn a stray edit into a crash instead of something ignored. The chats
    # answered between Madde 133 and 337 carry one such key, `context`, and it drops the next time
    # the chat is written.
    if not raw:
        return Usage()
    return Usage(raw.get("sent", 0), raw.get("cached", 0), raw.get("answered", 0))
```

- [ ] **Step 5: `routes.py`**

Import'ta `last_context` yerine `chat_size` (alfabetik, `active_messages`'tan sonra). `_chat_json`:

```python
        # The ceiling travels with the number: the gauge draws a share, and a share needs its
        # denominator. A second copy of the ceiling living in the browser is what would go stale.
        #
        # The key stays `sent` while the number behind it became the chat's messages (Madde 337):
        # it is still what the chat sends of itself, and renaming it would rebuild the frontend to
        # say the same thing. The gauge is handed the number the ceiling actually stops on -- a
        # gauge measuring something else cannot warn about the wall it is not watching.
        "context": {"sent": chat_size(chat), "ceiling": CONTEXT_CEILING},
```

- [ ] **Step 6: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `python -m pytest queen-agent -q` 932 geçti. queen-editor'ün arka ucunda yalnız 377'nin iki
kırmızısı. Ön uçlar yeşil (652, 749).

- [ ] **Step 7: Commit**

```powershell
git add queen-agent/backend/features/workspace/domain/chat.py queen-agent/backend/features/workspace/domain/usecases/stream_answer.py queen-agent/backend/features/workspace/data/file_chat_store.py queen-agent/backend/features/workspace/presentation/routes.py docs/specs/2026-09-29-queenagent-m337-tavan-mesajlar-uygulama-design.md docs/plans/2026-09-29-queenagent-m337-tavan-mesajlar-uygulama-plan.md
git commit -m @'
feat: Madde 337 -- the ceiling and the gauge measure the chat's messages alone, and a turn's tools and opened files no longer fill it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
