# Madde 509 · "Orada mısın?" kalkar, sıra bitince bildirim gelir — plan

**Spec:** [2026-10-29-queen-editor-m509-sira-bitince-bildirim-design.md](../specs/2026-10-29-queen-editor-m509-sira-bitince-bildirim-design.md)

[518](../specs/2026-10-30-queen-editor-m518-acik-sayfa-isi-gorur-design.md) bu bekçiyi `features/queue_watch/` (`QueueWatch`, `GET /api/queue/watch`) olarak genişletti.

Önce test yazılır ve kırmızı görülür, sonra kod. 498'in yalnız sayıma ve kutuya hizmet eden testleri
kodlarıyla birlikte silinir. Kalan dosyalar spec'teki yeni adlarına `git mv` ile taşınır.

## Sunucu

1. **`backend/tests/test_ended_watch.py` (eski `test_idle_watch.py`) — baştan, kırmızı.** Sayım,
   Buradayım, `spawn` ve `waiting` testleri gider. Kalan:
   - sayaçsız istek hemen `{"ended": 0, "last": None}`; iki `ended()` → sayaç 2, `last` sonuncusu;
   - eski sayaçtan istek hemen; güncel sayaçtan istek sınırda (gerçek saat, saniyenin kesri);
   - tutulan istek `ended()`'a hemen uyanıyor.
2. **`backend/tests/test_ended_routes.py` (eski `test_idle_routes.py`) — kırmızı.** Kapı
   `GET /api/queue/ended`; sahte bekçi `{"ended": 3, "last": {…}}` döner; Buradayım testi gider.
3. **`backend/tests/test_photo_runner.py` — kırmızı.** `ended` sahtesiyle:
   - `done`, `error` ve `waiting` özetinde bir kez, yayımlanan durumla, ve çağrıldığı anda durum
     zaten yazılı;
   - hata atan işte `error` ve işin kendi sözüyle;
   - `paused`'da hiç;
   - `ended` verilmeyen işçi sorunsuz.
4. **`backend/tests/test_agent_runner.py`.** `paused` fikstürü ve izin bekleyen ajanın bekçiye
   söylendiği test gider.
5. **`backend/tests/test_composition_root.py` — kırmızı.** Üç işçi testinin yerine: sıranın işçisinin
   `_ended`'ı bekçinin `ended`'ı; export ve ajanın `_spawn`'ı bekçinin değil. `GET /api/queue/ended`
   başta `{"ended": 0, "last": None}`.
6. **Yeşil.**
   - `features/queue_ended/watch.py`: `EndedWatch` — `ended`, `changed_since`.
   - `features/queue_ended/presentation/routes.py`: `make_ended_blueprint`, yalnız
     `GET /api/queue/ended`.
   - `features/photo_generation/runner.py`: `ended=None`, `TOLD`; `_run` durumu yazar, `TOLD`'daysa
     `ended(state)`; `start`'ın yorumundaki durumlar döngününkiler (`done`, `paused`, `waiting`,
     `error`).
   - `features/agent/runner.py`: `waiting` parametresi ve `with self._waiting():` gider.
   - `main.py`: `_ended = EndedWatch()`, `PhotoRunner(ended=_ended.ended)`, `ExportRunner()`,
     `AgentRunner(_chat_record)`.

## Ekran

7. **`shared/api.test.js` — kırmızı.** `sayHere` testi gider; `waitForEnded` (eski `waitForIdle`)
   `/api/queue/ended`'i sorar, 80 sn kalır. Kod: `api.js`'den `sayHere` çıkar,
   `ENDED_ASK_TIMEOUT_MS`.
8. **`features/notification/notification.test.js` — kırmızı.** Başlık **Queen Editor**, `tag`
   `queen-editor-queue`. Kod: `TITLE`, `TAG`, ve modülün yorumu (kutu yok).
9. **`features/notification/useEndedNotification.test.jsx` — yeni, kırmızı.** `renderHook`, sahte
   `waitForEnded` ve `Notification` ile spec'teki ekran maddeleri; `done`, `error` ve `waiting`'in
   cümleleri, `waiting`'de üç türün sözcüğü (bozuk bir eşlemede kırmızı görülür).
   `IdleWatch.test.jsx` silinir. Kod: `useEndedNotification.js` (eski `useIdleWatch.js`)
   durum tutmaz, cümleyi `last`'tan seçer; `IdleWatch.jsx` silinir. `GeneratePanel` ve `LayerPanel`
   `askPermission`'ı `../notification/notification.js`'ten alır.
10. **`App.test.jsx` — kırmızı, sonra yeşil.** `sayHere` mock'tan çıkar; listede bildirim çalıyor,
    ekran değişince tek istek kalıyor, "Orada mısın?" hiç yok. Kod: `App.jsx`
    `useEndedNotification()`'ı çağırır ve `<Screen />`'i çizer.

## Belgeler

11. `queen-editor/BACKLOG.md`, *"Boşta Colab kapansın"*: bugün ne olduğunu söyleyen cümle 509'a göre.

## Kapanış

12. `npm run build --prefix queen-editor/frontend`. Ardından, tek tek: `python -m pytest queen-editor
    -q`, `npm test --prefix queen-editor/frontend`.
