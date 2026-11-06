# Madde 511 · Sıra kapanırken eklenen iş de başlar — plan

**Spec:** [2026-10-29-queen-editor-m511-sira-kapanirken-is-design.md](../specs/2026-10-29-queen-editor-m511-sira-kapanirken-is-design.md)

Önce test yazılır ve kırmızı görülür, sonra kod. Yalnız sunucu; ekran ve `dist` değişmez.

## Sunucu

1. **`backend/tests/test_photo_usecases.py` — kırmızı.**
   - `ClosingPlanStore`: döngünün borç bulmadığı okumanın hemen ardından bir basışı içeri alan sahte
     plan. `test_a_job_queued_as_the_queue_closes_still_starts`: işi bekleten (`spawn=jobs.append`)
     ve bitişi dinleyen bir `PhotoRunner`; "ilk" işlenir, kapanırken "ikinci" kuyruğa eklenir. İkisi
     de üretiliyor, borçlu iş yok, ikinci işçi yok, bitiş bir kez `done`. Eski kodda yalnız `['ilk']`.
   - `Overtaken`: `status()` cevap verdikten sonra, `start()` çalışmadan önce öteki basışın alışını
     içeri alan işçi. Aynı projenin basışı: bu basış `Busy` almıyor, katılıyor. Başka projenin basışı:
     bu basış `Busy` alıyor, tutucu `"başka"`da kalıyor. Eski kodda ilki `Busy`, ikincisi `"düğün"`.
2. **`backend/tests/test_photo_runner.py` — kırmızı.** `deferred_runner` ile:
   - koşu sürerken `start`: başka projede `False`, bu projede `True`, tek `spawn`, tutucu yerinde;
   - kapanırken katılım olan koşu bir geçiş daha dönüyor, bitiş bir kez ve son geçişin özetiyle;
   - `done`, `paused`, `error`, `waiting` ile biten koşu katılım varsa bir geçiş daha dönüyor;
   - katılım durdurma isteğini indirmiyor;
   - sürerken yeniden adlandırılan koşunun bitişi yeni adla yayımlanıyor ve söyleniyor.
3. **Yeşil.**
   - `features/photo_generation/runner.py`: `start` kilitte tek adım — başka proje `False`, bu proje
     `_joined` ve `True`, boşta alış ve `_stop` iner; kilitten sonra `named.took` ve `spawn`;
     `join` gider. `_run(job)` geçişleri döndürür; `_finish(summary)` kilitte: `_joined`
     kalkıksa indirir ve `None`, değilse durumu o anki adla yazar ve döner. Modülün yorumu neden her
     bitiş olduğunu söyler.
   - `features/photo_generation/domain/run_loop.py`: `make_job` `named.took(project)` çağırmaz ve
     `project` parametresi gider; yorumu nedenini söyler.
   - `features/photo_generation/domain/usecases/run_queue.py`: `job = make_job(...)` (adsız), sonra
     `if not runner.start(project, job): raise Busy(...)`.
4. **`make_job`'u kendisi çalıştıran testler** (`test_photo_usecases`, `test_failed_attempts`,
   `test_happy_ending`, `test_export_total`, `test_variant_batch`, `test_video_length`,
   `test_producer_contract`) projenin adını vermez; adı `named=RunningName("düğün")` taşır, ya da
   `test_producer_contract`'ta sahte `Runner`'ın tutucusu `RunningName("düğün")`.
5. **`queen-editor/BACKLOG.md`:** aynı anda gelen basış ve yeniden adlandırmanın bir işi
   bekletebildiği, Diğer'e; spec'in Sınırlar'ı ona bağlanır.

## Kapanış

6. Tek tek: `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
