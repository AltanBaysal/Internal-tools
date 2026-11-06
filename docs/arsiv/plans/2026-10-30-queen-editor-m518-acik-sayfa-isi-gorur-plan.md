# Madde 518 · Açık sayfa dışarıdan eklenen işi görür — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-17), 518 · v11-17 ·
**Spec:** [2026-10-30-queen-editor-m518-acik-sayfa-isi-gorur-design.md](../specs/2026-10-30-queen-editor-m518-acik-sayfa-isi-gorur-design.md)

Önce test: testler yeni kuralı söyler (kırmızı), sonra kod (yeşil).

## 1. Taşımalar (`git mv`)

- `backend/features/queue_ended/` → `backend/features/queue_watch/`.
- `backend/tests/test_ended_watch.py` → `test_queue_watch.py`, `test_ended_routes.py` →
  `test_queue_watch_routes.py`.

## 2. Testler

**Sunucu**
- `test_queue_watch.py`: `QueueWatch`; açılış `{started: 0, ended: 0, last: None}`; başlamalar ve bitişler
  ayrı sayılır; tutulan istek bir başlamayı ve bir bitişi hemen duyar; sorulan çift durduğu gibiyse süre
  dolar; eski bir çift hemen cevaplanır.
- `test_queue_watch_routes.py`: `GET /api/queue/watch?started=S&ended=E` çifti kapının süresiyle verir;
  biri eksik ya da sayı değilse `None`.
- `test_photo_runner.py`: işçiyi alan basış `started()` der — `running` yazıldıktan sonra, iş başlamadan
  önce; katılma ve reddedilen basış demez.
- `test_composition_root.py`: işçi gözcünün `started`'ını ve `ended`'ını taşır; uygulama
  `/api/queue/watch`'ta `{started: 0, ended: 0, last: None}` ile kalkar.
- `test_photo_usecases.py`: `test_progress_reports_name_the_frames_still_waiting` → raporlarda `pending`
  yok. `test_variant_batch.py`: `pending` satırı çıkar.

**Ekran**
- `shared/queue_watch.test.jsx` (yeni): bugün `useEndedNotification.test.jsx`'teki dinleme testleri buraya
  gelir (çift ile); açılışın cevabı ve aynı çift söylenmez; bir başlama, bir bitiş, ve yeniden başlayan
  sunucunun ardından gelen başlama (`started` aynı, `ended` farklı) söylenir; çıkan dinleyiciye söylenmez.
- `useEndedNotification.test.jsx`: `useQueueWatch` ile birlikte kurulur; `ended` arttıkça çalar,
  başlamada çalmaz.
- `useGeneration.test.jsx`: boşta açılan sayfa bir dakika sormaz; tutulan istek bir başlama getirince
  galeriyi ve durumu sorar, yeni kareyi gösterir ve 2 sn sonra yeniden sorar; yalnız bitiş sordurmaz;
  yeniden başlayan sunucunun ardından gelen başlama (`started` aynı, `ended` küçük) sordurur.
- `App.test.jsx`: `waitForQueue`; açık proje sayfası başka yerden eklenen kareyi gösterir.
- `api.test.js`: `waitForQueue` adresi ve süresi.
- Kırmızılar çalıştırılıp görülür.

## 3. Kod

- `queue_watch/watch.py`: `QueueWatch` — `started()`, `ended(state)`, `changed_since(seen, timeout)`.
- `queue_watch/presentation/routes.py`: `make_watch_blueprint`, `GET /api/queue/watch`.
- `photo_generation/runner.py`: `started` parametresi; almadan sonra, `spawn`'dan önce.
- `photo_generation/domain/run_loop.py`: iki rapordan `pending` çıkar.
- `main.py`: `_queue_watch`, `PhotoRunner(started=…, ended=…)`, `_queue_watch_bp`.
- `frontend/src/shared/api.js`: `waitForQueue`, `QUEUE_ASK_TIMEOUT_MS`.
- `frontend/src/shared/queue_watch.js`: `useQueueWatch`, `onQueueMoved`.
- `features/notification/useEndedNotification.js`: dinleyici.
- `features/photo_generation/useGeneration.js`: dinleyici; `started` değişince ya da `ended` küçülünce
  `poll`.
- `App.jsx`: `useQueueWatch()`.
- `npm test --prefix queen-editor/frontend`, `npm run build --prefix queen-editor/frontend`,
  `python -m pytest queen-editor -q`.

## 4. BACKLOG

- `queen-editor/BACKLOG.md`: *"Açık ve boştaki bir sayfa dışarıdan eklenen işi görmüyor"* silinir.
