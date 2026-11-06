# Madde 512 · Aynı anda basılan iki Kuyruğa ekle'nin ikisi de sırada kalır — plan

**Spec:** [2026-10-29-queen-editor-m512-ayni-anda-iki-basis-design.md](../specs/2026-10-29-queen-editor-m512-ayni-anda-iki-basis-design.md)

Önce test yazılır ve kırmızı görülür, sonra kod. Yalnız sunucu; ekran ve `dist` değişmez.

## Sunucu

1. **`backend/tests/test_photo_usecases.py`:** `FakePlanStore` gerçek bir `RLock` ile `held(project)`
   verir, `DrivePlanStore` gibi.
2. **`backend/tests/test_plan_hold.py` — kırmızı.** `Contention`: ikinci basışı başka bir iş
   parçacığında, birincinin ilk yazmasının hemen önünde başlatır ve onu kısa bir süre (`WINDOW`)
   bekler. Testler:
   - gerçek `Storage` üstünde `DrivePlanStore`: okuma ile yazma arasına giren `append` kaybolmuyor;
     sekiz `append` aynı anda hepsi planda ve hatasız; bir projenin planı tutulurken başka projeye
     `append` beklemiyor;
   - her ad veren kapıda aynı anda iki basış: `start_batch`, `queue_references`, `queue_layer`
     (iki varyant), `regenerate` (aynı söz), `fix_photo` (`test_fix_photo.Project`), `copy_frames`.
3. **Yeşil.**
   - `features/photo_generation/data/plan_store.py`: proje başına `RLock`, bir sözlükte, sözlüğün
     kilidiyle; `held(project)` bağlam yöneticisi; `append` okumasını ve yazmasını `held` içinde
     yapar. Modülün yorumu neden olduğunu söyler.
   - `features/photo_generation/domain/ports.py`: `PlanStore.held`.
   - `start_batch.py`, `queue_references.py`, `queue_layer.py`, `regenerate.py`, `fix_photo.py`,
     `copy_frames.py`: adları okumaktan yazmaya kadar `with plan_store.held(project):`, `run_queue`
     dışarıda. Her birinde bir satır neden olduğunu söyler.
4. **Reviewer'ın bulduğu: kare kapatan kapılar ve sürükleme.**
   - `test_plan_hold.py` — kırmızı: silme ile aynı anda kopya (`remove_frames` + `copy_frames`),
     fotoğraf katmanı silinirken video basışı (`remove_layer` + `queue_layer`), sürükleme ile aynı
     anda kopya (`save_order` + `copy_frames`).
   - Yeşil: `remove_frames.py`, `remove_layer.py`, `save_order.py` ilk okumadan son yazmaya kadar
     `with plan_store.held(project):`.
   - `ports.py` ve `plan_store.py`'nin yorumları kilidin ne olduğunu söyler: kare adlandıran ya da
     kapatan kapıların yazma kapısı (plan, kayıt ve sıra birlikte), döngü kaydı dışında yazar.
5. **QA'nın bulduğu: kopya önce, sürükleme sonra.**
   - `test_plan_hold.py` — kırmızı: kopya düştükten sonra kopyayı bilmeyen bir liste ile sürükleme
     (`['0_a', '1_a']`, ikiz yok); listenin atladığı yan yana kareler kendi sıralarını koruyor.
   - Yeşil: `domain/gallery_order.py`'ye `keep_unnamed(named, gallery)` — listenin adlandırmadığı her
     kare, galeride hemen altındaki karenin üstüne, alttan yukarı; `save_order.py` kilit altında
     ekranın süzülmüş listesini `list_frames`'in sırasıyla ona verir. Modülün yorumu değişir: listenin
     unuttuğu kare artık tepeye çıkmaz.
6. **`queen-editor/BACKLOG.md`, Diğer:** *"Windows'ta okunan bir dosyanın üstüne kayıt düşebilir"*,
   *"Referans sırası ve arşiv işaretleri aynı anda iki yazmada birini kaybedebilir"* ve *"Fotoğraf
   kaydına aynı anda iki satır yazılabilir"*; spec'in Sınırlar'ı onlara bağlanır.

## Kapanış

7. Tek tek: `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
