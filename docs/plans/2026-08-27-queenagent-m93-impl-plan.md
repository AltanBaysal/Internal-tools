# Madde 93 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-27-queenagent-m93-yonerge-sona-iner-uygulama-design.md](../specs/2026-08-27-queenagent-m93-yonerge-sona-iner-uygulama-design.md)
**Bu turda yeni test yazılmaz.** `a3ea28a`'nın beş kırmızısı yeşile döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Tek dosya: `backend/features/workspace/domain/usecases/stream_answer.py`

### 1. `_conversation` sadeleşiyor

```python
def _conversation(chat):
    """Every message, and nothing else.

    The skill's instruction used to be dropped in here, in front of the turn it governed. Since
    Madde 93 it does not travel inside the conversation at all -- it rides at the end of the
    request, and `_asked` is what puts it there.
    """
    return [{"role": message.role, "content": message.text} for message in chat.messages]
```

`active` takibi ve "bir cevap skill taşımaz" kuralı düşüyor: ikisi de yönergenin **nereye**
serpileceğini hesaplamak içindi.

### 2. İki yeni yardımcı, `_conversation`'ın altına

```python
def _current_skill(chat):
    """Which skill governs the turn being answered: the newest user message's.

    Walked from the end rather than read off the last message, for the same reason last_sent is: a
    record does not always end with the question that is waiting for an answer.
    """
    for message in reversed(chat.messages):
        if message.role == "user":
            return message.skill
    return ""


def _asked(conversation, instruction):
    """The request as it goes out: the conversation, and the instruction behind all of it.

    Built fresh on every round rather than once, because `conversation` grows -- each round appends
    what the model said and what the tools answered. An instruction placed inside it once would sit
    behind those from the second round on, and the reason this item exists would stop holding after
    the first.
    """
    if not instruction:
        return conversation
    return conversation + [{"role": "system", "content": instruction}]
```

### 3. `stream_answer`

`conversation = _conversation(chat)`'in hemen altına:

```python
    # Read once: the turn being answered is settled before the first round, and no round changes it.
    instruction = instruction_for(_current_skill(chat))
```

ve motora giden çağrı:

```python
                for piece in engine.stream(
                    _asked(conversation, instruction),
                    tools=tools_for(mode),
```

Döngünün `conversation.append(...)` satırları olduğu gibi kalıyor — büyüyen liste konuşmanın
kendisi, ve yönerge ona hiç girmiyor.

## Beklenen yeşil

`a3ea28a`'nın beş kırmızısı. Test turunda yazılıp bugün de yeşil olan bekçi — *motor sırayı
bozmuyor* — yeşil kalır.

**İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`xai_engine.py` açılmaz** — sabit olan zaten başta.
- **`skills.py` açılmaz** — 94'ün işi.
- **`Message.skill`'e dokunulmaz.**
- **Ön yüz açılmaz, `dist` derlenmez.**
