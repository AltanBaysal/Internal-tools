# Madde 89 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-27-queenagent-m89-sohbetin-sekli-tek-yerde-uygulama-design.md](../specs/2026-08-27-queenagent-m89-sohbetin-sekli-tek-yerde-uygulama-design.md)
**Bu turda yeni test yazılmaz.** Yedi kırmızı *(`e1e16d1`)* yeşile döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
`npm run build --prefix queen-agent/frontend`

---

## 1. `presentation/routes.py`

`_sse`'nin son dalı:

```python
            else:
                # The record has one home since Madde 89, and it is get_chat. This frame says the
                # turn is over; what it wrote is a question asked separately.
                yield _frame("done", {})
```

`_chat_json`'a dokunulmuyor — çağıranı teke iniyor, kendisi aynı.

## 2. `frontend/src/features/workspace/useChat.js`

`send`'in `try` bloğunun sonuna, `streamEvents` çağrısından hemen sonra:

```js
        // The record has one home since Madde 89, so the turn ends by reading it. Before the
        // finally below clears what streamed, or the transcript blinks empty between the two.
        //
        // Whatever the turn ended as: a fault still leaves the user's own sentence on disk, and it
        // has to stay on the screen.
        const landed = streamingInto.current ?? chatId;
        if (landed) {
          try {
            setChat(await getJson(`/api/projects/${projectId}/chats/${landed}`));
          } catch (unreadable) {
            // A fault already reported is the turn's real one; replacing it with this would show
            // the wrong cause. Otherwise the read speaks for itself -- the answer was written, and
            // what was lost is the showing of it.
            setError((current) => current ?? unreadable.message);
          }
        }
```

`setError`'ın fonksiyon hâli, akıştaki `error` karesinin zaten koyduğu mesajı korumak için: o
karenin sebebi turun asıl arızası.

## 3. Ölçüsü değişen testin sahtesi

Test turunda yazıldı ve dokunulmuyor.

## Beklenen yeşil

Yedi kırmızının hepsi. **İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`_chat_json` ve `_chat_summary` açılmaz.**
- **`stream_answer.py` açılmaz.**
- **`/stop` ucuna dokunulmaz.** 90'ın işi.
