# Madde 498 · Sıra boşken bildirim — plan

**Spec:** [2026-10-27-queen-editor-m498-bosta-bildirim-design.md](../specs/2026-10-27-queen-editor-m498-bosta-bildirim-design.md)

Önce test yazılır ve kırmızı görülür, sonra kod. *(İlk yol, dakikada bir `/api/activity` sormak,
kullanıcının 27 Ekim kararıyla bırakıldı: o kod ve testleri silindi.)*

## Sunucu

1. **`backend/tests/test_idle_watch.py` — kırmızı.** Sahte saatle:
   - açılıştan 600 sn sonra soru, 599'da yok; her 600 sn'de yeniden;
   - Buradayım kapatıp yeniden sayıyor; sorulmamışken yalnız sayımı yeniliyor;
   - iş sürerken soru yok, son işin bitişinden sayılıyor; iki işte sonuncusundan;
   - başlayan iş açık soruyu kapatıyor; hata atan iş de bitiyor;
   - `waiting()` içindeki iş, iş sayılmıyor; bekçinin iş parçacığı dışında `waiting()` bir şey
     değiştirmiyor.

   Gerçek saatle:
   - tutulan soru sınırda ya da eski sürüme hemen cevaplanıyor;
   - geri sayıma, Buradayım'a, başlayan işe ve işin bitişiyle açılan geri sayıma uyanıyor.
2. **`backend/tests/test_idle_routes.py` — kırmızı.** Sahte bekçiyle:
   - `GET /api/idle?after=3` → `changed_since(3, ASK_WAIT_SECONDS)`;
   - `after` yok, boş ya da sözcük → `None`;
   - `ASK_WAIT_SECONDS` 100'ün altında;
   - `POST /api/idle/here` → `here()`.
3. **`backend/tests/test_agent_runner.py` — kırmızı.** Sahte `waiting` ile izin beklerken içinde,
   cevapla da Durdur'la dışında.
4. **`backend/tests/test_composition_root.py` — kırmızı.** Üç işçinin `_spawn`'ı bekçinin `spawn`'ı,
   ajanın `_waiting`'i bekçinin `waiting`'i; `GET /api/idle` başta `{"version": 0, "asking": false}`.
5. **Yeşil.**
   - `features/idle/watch.py`: `IdleWatch`.
   - `features/idle/presentation/routes.py`: `make_idle_blueprint`, `ASK_WAIT_SECONDS = 50`.
   - `features/agent/runner.py`: `waiting=None` → `nullcontext`; `_permit`'in bekleyişi
     `with self._waiting():` içinde.
   - `main.py`: `_idle = IdleWatch()`, üç işçiye `spawn=_idle.spawn`, ajana `waiting=_idle.waiting`,
     `_idle_bp`.

## Ekran

6. **`shared/api.test.js` — kırmızı.** `waitForIdle(1)` → `GET /api/idle?after=1`, `waitForIdle(null)`
   → `GET /api/idle`, `sayHere()` → `POST /api/idle/here`. İstek 60 sn'de kesilmiyor, 100 sn'de
   kesiliyor. Kod: `api.js`, `IDLE_ASK_TIMEOUT_MS = 80_000`.
7. **`features/idle/notification.test.js`.** İzin ve bildirim, ilk yoldan kaldığı gibi.
8. **`features/idle/IdleWatch.test.jsx` — kırmızı.** Sahte `sayHere`, `waitForIdle` ve `Notification`
   ile spec'teki ekran maddeleri. Kod: `useIdleWatch.js` (saymaz, dinler) ve `IdleWatch.jsx`.
9. **`App.test.jsx` — kırmızı, sonra yeşil.** `sayHere` ve `waitForIdle` mock'a eklenir:
   - kutu listede ve projede çıkıyor;
   - ekran değişince tek istek kalıyor.

   Kod: `App.jsx`, `Screen` + `IdleWatch`.
10. **İzin.** `GeneratePanel.test.jsx` ve `LayerPanel.test.jsx`: Kuyruğa ekle izni soruyor;
    `LayerPanel`'in reddettiği basış sormuyor. Kod: iki `handleAdd`.

## Kapanış

11. `npm run build --prefix queen-editor/frontend`. Ardından, tek tek: `python -m pytest queen-editor
    -q`, `npm test --prefix queen-editor/frontend`.
