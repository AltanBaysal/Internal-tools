# Madde 523 · Referans sırası ve arşiv işaretleri aynı anda yazılınca kaybolmaz — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-22), 523 · v11-22 ·
**Spec:** [2026-10-30-queen-editor-m523-referans-arsiv-ayni-anda-design.md](../specs/2026-10-30-queen-editor-m523-referans-arsiv-ayni-anda-design.md)

Önce testler, eski kodda kırmızı; sonra kod (yeşil). Ekrana dokunulmaz, `dist` derlenmez.

## 1. Testler — `backend/tests/test_written_at_once.py` (yeni)

- `Meanwhile.after_first(obj, method, second)`: bir yöntemin ilk cevabından hemen sonra ikinci yazmayı
  bir iş parçacığında başlatıp `WINDOW` kadar bekler; `done()` onu bekler ve hatasını teste verir.
- `Pool`: gerçek klasörde `düğün`'ün havuzu (`DrivePhotoStore`, `DriveReferenceStore`,
  `DriveReferenceOrderStore`, `DrivePlanStore`).
  - `test_two_uploads_of_one_name_at_once_keep_both_files` (`pool.items`'tan sonra).
  - `test_an_upload_in_the_middle_of_another_write_keeps_its_place`, üç birinci kapı: yükleme, çıkarma,
    sürükleme (`orders.read`'den sonra).
- `Projects`: gerçek kökte üç proje, `DriveProjectStore`.
  `test_an_archive_in_the_middle_of_another_mark_change_is_kept`, dört birinci değişiklik: arşive
  kaldırma, geri alma, silme, yeniden adlandırma (`storage.read_text`'ten sonra).
- `test_a_press_as_the_project_is_deleted_starts_no_run`: silmenin işaret okumasından sonra bir
  `start_batch`. Kırmızı eski bağlantıyla (`halt_project` portu) görüldü, sonra `follow_delete`'e çevrildi.
- `test_photo_usecases.py`: `test_a_delete_stops_the_projects_run_before_its_folder_goes`.

## 1b. Reviewer'dan sonra — testler önce, kırmızı

- `test_reference_usecases.py`: `GatedClips`, `GatedPool` (kapının tutulup tutulmadığını yazar; `Gate`
  522'nin testinden) — `test_an_upload_reads_its_lengths_and_writes_its_bytes_before_the_gate`;
  `test_an_upload_the_pool_refuses_leaves_no_bytes_behind`;
  `test_a_drag_from_a_tab_that_never_saw_an_upload_keeps_it_where_it_stood`. `FakeReferenceStore`
  `stage`, `place`, `discard` öğrenir (`save` testin kendi tohumlaması için kalır).
- `test_written_at_once.py`: `Meanwhile.after_first(…, nth=)`; silme iki okumasının ikisiyle de
  denenir; `test_an_upload_the_pool_refuses_leaves_no_hidden_file_behind` (gerçek klasör).
- `test_project_store.py`: `test_a_delete_that_fails_half_way_leaves_an_archived_project_archived`.
- `test_storage.py`: `stage_bytes`, `rename_file` mount listesine; gizli yazma, yarıda kalan yazma,
  proje klasörünü açmama.
- `test_reference_store.py`: `put` (stage + place), gizli dosya listede yok, `discard` hata atmaz.

## 2. Kod

- `domain/usecases/add_references.py`, `remove_reference.py`, `save_reference_order.py`: `plan_store`
  parametresi; projeye bakıştan cevaba kadar `with plan_store.held(project)`. Sürüklemenin gövde
  denetimi dışarıda.
- `features/projects/data/project_store.py`: `self._lock`; `archive`, `restore`, `rename` okuma-yazmayı
  kilitte yapar; `delete` işaretleri kilitsiz okur, klasörü siler, sonra kilitte yeniden okuyup yazar.
- Reviewer'dan sonra:
  - `services/storage/storage.py`: `_save`'in gizli dosyayı yazan kısmı `_staged`'e; yeni `stage_bytes`,
    `rename_file`.
  - `data/reference_store.py`: `save` yerine `stage`, `place`, `discard` (hata atmaz).
  - `domain/usecases/add_references.py`: `_weighed` (tür, satır, süre, basışın tek başına sınırları)
    ve `pool.stage` kapıdan önce; kapıda boş adlar, havuzla sınırlar, `pool.place`, sıra; `finally`
    yerine konmamışları `discard` eder.
  - `domain/usecases/save_reference_order.py`: her tür için `gallery_order.keep_unnamed`.
  - İkinci okumadan sonra: `Storage.sweep_staged(folder, age)`, `DriveReferenceStore.sweep`
    (`STAGED_FOR` = 3600 s), `add_references` kapıda `pool.sweep`. Testler önce, kırmızı:
    `test_storage.py` (eski gizli dosya gider, genç ve görünür kalır; olmayan klasör; mount listesi),
    `test_written_at_once.py` `test_an_upload_sweeps_what_earlier_uploads_left_staged_an_hour_ago`,
    `GatedPool` süpürmenin kapıda olduğunu yazar. `project_store.delete`'in ilk okumasına yorum.
- `domain/usecases/follow_delete.py` (yeni): G'de `halt_project` ve `remove()`.
- `features/projects/domain/usecases/delete_project.py`: `halt` yerine `end(name, remove)` portu.
- `main.py`: `partial(follow_delete, _photo_runner, _plan_store, _comfy_client.interrupt, time.sleep)`;
  havuzun üç kapısına `_plan_store`.
- `data/plan_store.py` modül docstring'i ve `domain/ports.py` `PlanStore.held`: kapıyı havuzun
  yazarları ve silme de tutar.

## 2b. QA'dan sonra (c8e0bd23'ün üstüne) — testler önce, kırmızı

- Testler:
  - `test_written_at_once.py`: `Meanwhile.now`; `test_an_upload_during_a_slow_removal_never_brings_the_project_back`
    (yavaş silme: önce dosyalar, araya yükleme, sonra klasörler); `test_an_upload_whose_project_is_deleted_before_its_bytes_go_is_told_it_is_gone`.
    Silmenin iki okumalı denemesi kalktı (artık tek okuma).
  - `test_reference_usecases.py`: `test_an_upload_lists_the_pool_once_under_the_gate`,
    `test_a_drag_lists_the_pool_once_under_the_gate`.
  - `test_project_store.py`: çöpü silinemeyen silme proje bırakmaz; çöpe taşıması düşen silme arşivi
    korur; `clear` eski çöpleri süpürür.
  - `test_storage.py`: `trash_dir`, `sweep_trash` (mount listesine de).
  - `test_project_usecases.py`: `RecordingStore.clear`; çöp port döndükten sonra silinir.
- Kod:
  - `services/storage/storage.py`: `trash_dir`, `sweep_trash`, `_trashed_at`; `list_dirs` önekli
    klasörleri atlar.
  - `features/projects/data/project_store.py`: `delete` M'de okur, çöpe taşır, yazar, çöpü döner;
    `clear(trash)` (hata atmaz) siler ve süpürür (`STALE`).
  - `features/projects/domain/usecases/delete_project.py`: port döndükten sonra `store.clear`.
  - `domain/usecases/follow_delete.py`: docstring.
  - `domain/usecases/add_references.py`: baytlarda `FileNotFoundError` → yeniden bakış → "Proje yok";
    cevap `references.placed(order, held + arriving)`.
  - `domain/usecases/save_reference_order.py`: cevap `references.placed(order_now, standing)`.

- Reviewer'dan sonra: `Storage.dir_exists` gizli adlı (`TEMP_PREFIX`) bir klasöre `False` der.
  Testler önce, kırmızı: `test_storage.py`
  `test_a_folder_in_the_trash_is_not_there_for_anyone_who_asks_by_name`, `test_written_at_once.py`
  `test_an_upload_into_the_trash_by_name_is_told_there_is_no_project`.

## 3. Eski testlerin yeni imzası

- `test_reference_usecases.py`: üç kapının çağrıları `FakePlanStore()` verir.
- `test_reference_store.py`: `save` yerine `put` (stage + place).
- `test_reference_routes.py`: `partial`'lar `plan_store`'u verir.
- `test_project_usecases.py`: `ending(log)` portu (durdurur, verilen silmeyi çalıştırır).
- `test_projects_routes.py`: silme portu verilen silmeyi çalıştırır.

## 4. BACKLOG

- Silinir: *"Referans sırası ve arşiv işaretleri aynı anda iki yazmada birini kaybedebilir"*, *"Proje
  silinirken gelen bir basış silinecek klasörde koşu başlatabilir"*.
- Eklenir: *"Arşive kaldırma ile silme aynı anda gelince silinen projenin işareti kalabilir"*,
  *"Referans yüklenirken başlayan bir video referansları bir an ada göre sıralı okuyabilir"*.

## 5. Suitler

`python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend` (sırayla); queen-agent'ın
ikisi de, sırayla.
