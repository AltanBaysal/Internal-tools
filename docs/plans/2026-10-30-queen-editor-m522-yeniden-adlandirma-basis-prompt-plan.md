# Madde 522 · Yeniden adlandırma bir basışı ya da prompt'u kaybettirmez — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-21), 522 · v11-21 ·
**Spec:** [2026-10-30-queen-editor-m522-yeniden-adlandirma-basis-prompt-design.md](../specs/2026-10-30-queen-editor-m522-yeniden-adlandirma-basis-prompt-design.md)

Önce testler, eski kodda kırmızı; sonra seçenekler ana ajana (1. seçenek onaylandı); sonra kod (yeşil).
Ekrana dokunulmaz, `dist` derlenmez.

## 1. Testler — `backend/tests/test_rename_under_queue.py` (yeni)

- `Project`: gerçek geçici klasörde `düğün`, `Storage` üstünde dört depo; `rename(runner)` yeniden
  adlandırmayı (`follow_rename`) bir iş parçacığında başlatıp `WINDOW` kadar bekler.
- `RenamedBeforeItsClaim(PhotoRunner)`: `start`'tan hemen önce yeniden adlandırmayı sokar, koşuyu
  saklar.
- `test_a_press_on_an_idle_worker_as_the_project_is_renamed_still_makes_its_job`,
  `test_a_press_joining_a_run_as_the_project_is_renamed_joins_it`.
- `Gate(FakePlanStore)` kapının tutulup tutulmadığını bilir, `Claims(PhotoRunner)` her alışta onu yazar:
  `test_every_door_that_queues_work_claims_the_worker_under_its_gate`, sekiz kapı.
- `after_first(obj, method, then)`: bir okumanın ilk cevabından hemen sonra yeniden adlandırmayı sokar.
  `test_a_rename_between_the_source_read_and_the_written_prompt_never_makes_an_empty_prompt`,
  `…_and_the_frames_words_never_asks_with_none`,
  `test_a_rename_between_the_frames_words_and_its_written_prompt_never_asks_again`.
- `test_made_once.py`: `follow_rename` çağrısı `plan`'ı da verir.

## 2. Kod

- `domain/usecases/follow_rename.py`: `plan_store` parametresi; taşıma ve `runner.rename`
  `plan_store.held(old)` içinde.
- `main.py`: `partial(follow_rename, _photo_runner, _plan_store)`.
- `domain/usecases/start_batch.py`, `queue_layer.py`, `regenerate.py`, `queue_references.py`,
  `fix_photo.py`: `run_queue` (`fix_photo`'da `try/except Busy` ile) `with plan_store.held` içine.
- `domain/usecases/retry_frame.py`, `retry_failed.py`, `resume_batch.py`: varlık bakışından `run_queue`'ya
  kadar `with plan_store.held(project)`.
- Reviewer'dan sonra: `start_batch.py` ve `queue_references.py` varlık bakışını kapının içine alır;
  `queue_references` havuz bakışını ve `video_settings.carried`'ı da. Test:
  `test_a_press_the_rename_lands_just_before_is_told_the_project_is_gone` (eski kodda
  `FileNotFoundError … plan.json`). `test_reference_usecases.run` kapı için bir `FakePlanStore` verir.
- `domain/usecases/run_queue.py`: docstring — kapının içinde çağrılır, neden.
- `data/plan_store.py`: modül docstring'i — kapıyı kuyruğa iş koyan kapılar işçinin alınışına kadar,
  yeniden adlandırma taşıma boyunca tutar.
- `domain/run_loop.py`: `snapshot(project)` adı almaz, verilen adla okur; `summary` kendi tutuşunu alır.
  Turun başında birinci tutuş: `snapshot` + `_unwritten`. `try`'ın içinde ikinci tutuş: `_source_for`,
  `_end_for`, `_prompts_of` ya da yazılmış prompt ve havuz. Yazar ve render dışarıda; iki `report` de
  tutuşların dışında. "Hayalet proje" yorumları doğru nedenle yeniden yazılır.
- `domain/running_name.py`: modül docstring'i ve `steady`, `moved`, `now`, yeniden girilebilirlik
  yorumları — okumalar da kilitte, hayalet klasör nedeni 472'den beri yanlış.

## 3. Bitiş

- BACKLOG: iki iş silinir; *"Proje silinirken gelen bir basış silinecek klasörde koşu başlatabilir"*
  eklenir.
- Takımlar sırayla: `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
