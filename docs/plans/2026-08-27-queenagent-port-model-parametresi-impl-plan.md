# `Engine` portundaki ölü `model` parametresi · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-27-queenagent-port-model-parametresi-uygulama-design.md](../specs/2026-08-27-queenagent-port-model-parametresi-uygulama-design.md)
**Bu turda yeni test yazılmaz.** `f70a3a9`'un üç kırmızısı yeşile döner.
**Komut:** `python -m pytest queen-agent -q`

---

## Tek dosya: `backend/features/workspace/domain/ports.py`

`Engine` bütünüyle şu hâlini alıyor:

```python
class Engine(Protocol):
    """Something that answers a conversation.

    Which model it answers with is not asked here: there is one, and config.py names it once. That
    belongs to whatever the engine was built with, not to the call.
    """

    def complete(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Answer a conversation. Messages carry the domain's own roles: user and ai."""

    def stream(self, messages: list[dict], tools: list[dict] | None = None, on_open=None):
        """Answer a conversation piece by piece.

        Yields {"text": str} as words arrive and {"tool_calls": [...]} when the model asks for one.

        `on_open` is handed a callable that cuts the connection this answer is reading, as soon as
        there is one to cut. An engine with no connection to cut never calls it.

        Also yields {"usage": {"sent": int, "cached": int, "answered": int}} when the engine says
        what the answer cost -- once, as the stream closes. Should it ever say so more than once,
        each figure is the total for this one call rather than the share since the last, so the
        newest replaces the one before it. An engine that never mentions spending never yields
        this, and every fake in the tests is such an engine.
        """
```

Değişen üç şey: iki imzadan `model`, `complete`'in ikinci paragrafı, ve sınıfa giren docstring.
`stream`'in docstring'i harfi harfine aynı — içindeki *model* geçişleri cevabı veren şeyden
bahsediyor, parametreden değil.

Dosyanın geri kalanı — `ProjectStore`, `ChatStore`, `Stops`, `FileStore` ve modül docstring'i —
açılmıyor.

## Üç kırmızının karşılığı

| Test | Silme |
|---|---|
| `..._asks_for_what_its_adapter_takes[complete]` | `complete`'ten `model` — imza `['self', 'messages', 'tools']` oluyor, `XaiEngine` ile aynı |
| `..._asks_for_what_its_adapter_takes[stream]` | `stream`'den `model` — imza `['self', 'messages', 'tools', 'on_open']` oluyor |
| `..._no_longer_hands_a_model_to_the_call` | *"The model travels with the call..."* cümlesi |

## Doğrulama

```
python -m pytest queen-agent -q
```

**İki kırmızı bu işin değildir:** `test_notebook`'un ikisi. Başka kırmızı beklenmiyor: `model`'i
arka uçta çağıran hiçbir şey yok, yani silinen parametre kimsenin ölçüsünü kırmıyor.

Ön yüz koşulmuyor ve `dist` derlenmiyor: hiçbir ön yüz dosyası değişmiyor.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`xai_engine.py`, `client.py`, `config.py` açılmaz.**
- **`complete` silinmez.**
- **Öteki üç port açılmaz.**
