# Mira Faz 7 (Akış) — Uygulama Planı

**Hedef:** Cevabın parça parça akması (Madde 15) ve hata kartı + **Try again** (Madde 16).

**Mimari:** Akış Faz 6'nın `answer` uç noktasının içinden geçer — ayrılmasının sebebi buydu. Yarım
metin diske yazılmaz; akış başladıktan sonraki arıza durum kodu değil, akışın içinde bir `error`
olayıdır.

**Kaynak spec:** [Faz 7](../specs/2026-08-09-mira-faz-7-akis-design.md)

## Global Kısıtlar

- `ai` mesajı **yalnız akış tamamlanınca** yazılır.
- `done` olayı sohbetin tamamını taşır: ekrandaki birikim tahmin, sunucunun kaydı gerçektir.
- `EventSource` yok (POST yapamaz); `fetch` + `body.getReader()`.
- Testlerde ağ yok; okuyucu da sahte.
- Commit: `git add <yollar>` → `git commit -m <mesaj> -- <aynı yollar>`.

---

### Task 1: Servisin akışı

**Dosyalar:** Değiştir `services/xai/client.py` · Test `backend/tests/test_xai_client.py` (ekleme)

`stream(messages, tools=None)` bir üreteçtir: `data: ` ile başlayan satırları çözer,
`choices[0].delta.content` varsa üretir, `data: [DONE]` görünce durur. Çözülemeyen satır **atlanır** —
tek bozuk kare akışı düşürmemeli.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS

```python
    def stream(self, messages, tools=None):
        request = self._request({"messages": messages, "stream": True}, tools)
        try:
            with self._opener(request) as response:
                for raw in response:
                    text = _delta(raw)
                    if text is DONE:
                        return
                    if text:
                        yield text
        except urllib.error.HTTPError as failure:
            body = failure.read().decode("utf-8", "replace")
            raise XaiFailed(f"{failure.code} {body}") from failure
        except urllib.error.URLError as failure:
            raise XaiFailed(str(failure.reason)) from failure
```

`_delta(raw)` satırı çözer; `[DONE]` için bir sentinel döndürür, çözülemeyen satır için `None`.

---

### Task 2: Akan use case ve rota

**Dosyalar:** Oluştur `domain/usecases/stream_answer.py` · Değiştir `domain/ports.py`,
`data/xai_engine.py`, `presentation/routes.py` · Test `backend/tests/test_stream_answer.py`,
`test_chats_api.py` (güncelleme)

```python
"""Stream an answer: the pieces go out as they arrive, the record is written only at the end."""
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.usecases.append_message import append_message


def stream_answer(chat_store, engine, project_id, chat_id, now):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    pieces = []
    try:
        for piece in engine.stream(
            [{"role": message.role, "content": message.text} for message in chat.messages]
        ):
            pieces.append(piece)
            yield piece
    except Exception as failure:
        # Half an answer is never kept: the design's line is that an answer either exists or does
        # not, and Faz 8's files cannot be born of an unfinished thought.
        raise EngineFailed(str(failure)) from failure
    yield append_message(chat_store, project_id, chat_id, "".join(pieces), now, role="ai")
```

Son `yield` bir `Chat` nesnesidir; rota metin parçalarını `chunk`, `Chat`'i `done` olarak sarar. Tip
ayrımı üzerinden gitmek, ayrı bir "bitti" bayrağı taşımaktan basit.

Rota:

```python
    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/answer")
    def post_answer(project_id, chat_id):
        if chat_store.get(project_id, chat_id) is None:
            # The only failure that can still be a status code: nothing has been sent yet.
            return jsonify({"error": "chat not found"}), 404
        return Response(
            _sse(stream_answer(chat_store, engine, project_id, chat_id, now=_now())),
            mimetype="text/event-stream",
        )
```

`_sse` üreteci sarar: `Chat` gelirse `event: done`, metin gelirse `event: chunk`, `EngineFailed`
yakalanırsa `event: error`.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS

---

### Task 3: Tarayıcı tarafı akış

**Dosyalar:** Oluştur `shared/sse.js` · Değiştir `useChat.js`, `ChatScreen.jsx`, `workspace.css` ·
Test `shared/sse.test.js`, `ChatScreen.test.jsx` (ekleme), `App.test.jsx` (ekleme)

`streamEvents(path, onEvent)` — `fetch` ile POST atar, `body.getReader()` üzerinden okur, tampon
üzerinde `\n\n` ile kareleri ayırır, her kareyi `{event, data}` olarak verir.

`useChat`: `streamingText` state'i tutar. `chunk` → biriktir, `done` → `setChat(data)` ve birikimi
temizle, `error` → `setError(data.error)` ve birikimi temizle.

`ChatScreen`: `streamingText` doluysa onu bir `ai` mesajı gibi çizer; üç nokta yalnız `thinking &&
!streamingText` iken görünür. Hata kartı tasarımın metnini ve **Try again** butonunu taşır.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS · derle

---

## Öz-denetim

**Spec kapsaması.** Dokuz cümle: 1-2 Task 1 · 3-4 Task 2'nin use case testleri · 5-6 Task 2'nin rota
testleri · 7-9 Task 3.

**Ad tutarlılığı.** `stream(messages, tools=None)` serviste, portta ve `XaiEngine`'de aynı. Olay
adları `chunk` / `done` / `error` hem rotada hem `sse.js`'te hem `useChat`'te aynı üç dize.

**Risk.** Flask'ın sync üreteci istek bağlamı dışında çalışır; `_now()` üretecin **içinde** değil,
çağrılırken hesaplanmalı, yoksa zaman damgası akışın bitişine kayar. Bu yüzden `now` parametre olarak
geçiyor — zaten domain kuralı da bu.
