# Madde 462 · Ekran sunucunun durumunu çizer — plan

**Spec:** [2026-10-10-queen-agent-m462-ekran-sunucu-durumu-design.md](../specs/2026-10-10-queen-agent-m462-ekran-sunucu-durumu-design.md)

Her adımda önce test yazılır ve kırmızı görülür, sonra kod. Backend yolları `queen-agent/backend/`,
frontend yolları `queen-agent/frontend/src/` altında.

## Backend

1. **`features/workspace/data/live_turns.py`** — `release(proje, sohbet, tur, error="")` bırakır, sonra
   o turu bitirir; `LiveTurn.end` bir kez işler; `_run`'ın `finally`'si `release(…, error)`.
   `domain/ports.py`'de `Turns.release`'in belgesi. Test: `tests/test_live_turns.py` — bırakılan tur
   bitmiş; ikinci `end` ilkinin sözünü değiştirmiyor.
2. **`domain/usecases/run_turn.py`** — `now` yerine `clock`; cevap son yazıda `clock()`. Test:
   `tests/test_run_turn.py` — üç çağrı `lambda: NOW`; cevabın saati yazıldığı an, saat bir kez soruluyor.
3. **`domain/usecases/advance_chat.py`** — `clock`; soru `clock()` anında; `Nothing(chat)` okunan kaydı
   taşır; `NO_TEXT`'in belgesi (yalnız retry kapısı). Test: `tests/test_advance_chat.py`.
4. **`domain/usecases/read_chat.py`** (yeni) — `(chat, snapshot)`, önce tur sonra kayıt. Test:
   `tests/test_read_chat.py`.
5. **`domain/turn.py`** — `status_of`'un belgesi: canlı turda kayıt okunmaz. Test: `tests/test_turn.py`.
6. **`domain/usecases/retry_turn.py`** — belge: canlı turun Try again'i kapıda yeniden bağlanır.
7. **`presentation/routes.py`** — `_turn_json`, `_chat_state`, `_listened`, `_told(snapshot)`,
   `_frame(data)`, `EVENT_HEADERS`; `get_chat` `read_chat`'le; `get_events`; mesaj kapısı 202 / 409 +
   tur, metinsiz istek boş mesaj; `post_retry`; Stop ve izin kimlikle, cevap `{turn}`; köprü (`_sse`,
   eski `_told`) gider. Test: `tests/test_chats_api.py` yeniden yazıldı (yardımcılar `_listen`,
   `_heard`, `_sent`, `_retried`, `_until_asked`, `_laid`, `_laid_turn`); `tests/test_pin_archive.py`
   ve `tests/test_last_activity.py` turun sonunu olay kapısından bekler.

## Frontend

8. **`test-setup.js`** — testin konuşturduğu sahte `EventSource` (`emit`, `drop`, `refuse`, `opened`).
9. **`shared/failure.js`** — `failure.body`; **`shared/api.js`** — `reach(path)`. Test:
    `shared/api.test.js`.
10. **`features/workspace/useChat.js`** — yeniden yazım: `chat` (kapının ya da okumanın verdiği hâl),
    `pending`, `decided` (ulaşmayan cevapta geri), `early` (kapıdan önce basılan Stop); tur başına bir
    akış, kendi turu bitene kadar açık; `follow`, `heard`, `finished`, `gaveUp` (işlemiş akış okumadan
    yeniden; işlememişte okuma, `reach`, bir kez daha dinleme, kart), `took`; sekmeye dönünce bir okuma;
    `send`, `retry`, `stop`, `answer` kimliklerle; türetilen ekran adları. Test:
    `features/workspace/useChat.test.jsx` (yeni).
11. **`features/workspace/Composer.jsx`** — Stop görünürken Enter göndermez. Test: `Composer.test.jsx`.
12. **`features/workspace/ChatScreen.jsx`** — reddedilen düzenleme alanına döner; bekleyişin saati
    açık hattın son mesajından. Test: `ChatScreen.test.jsx`.
13. **`App.jsx`** — `onTurnEnd` argümansız. Test: `App.test.jsx` — akış testleri yeni
    protokolle (`started`, `live`, `hear`, `OVER`, `retryPosts`); yeni: cevapsız soru kartsız,
    durdurulmuş cevapta Try again yok, tur sürerken ve izin beklerken yenileme.
14. **Silinenler** — `shared/sse.js`, `shared/sse.test.js`, `features/workspace/chatTitle.js`,
    `features/workspace/chatTitle.test.js`.
15. **`dist`** — `npm run build --prefix queen-agent/frontend`.

## Son

16. Dört suite sırayla: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
    `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
17. Gerçek sunucuyla kısa deneme, kullanıcının kökünden uzakta: `tmp/m462/serve.py` (yavaş sahte motor,
    kök `tmp/m462/root`).
