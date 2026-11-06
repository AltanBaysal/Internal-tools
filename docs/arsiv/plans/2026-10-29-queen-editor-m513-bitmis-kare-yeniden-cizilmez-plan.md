# Madde 513 · Bitmiş bir kare yeniden çizilmez — plan

**Spec:** [2026-10-29-queen-editor-m513-bitmis-kare-yeniden-cizilmez-design.md](../specs/2026-10-29-queen-editor-m513-bitmis-kare-yeniden-cizilmez-design.md)

Önce test yazılır ve kırmızı görülür, sonra kod. Yalnız sunucu; ekran ve `dist` değişmez.

## Sunucu

1. **`backend/tests/test_made_once.py` — kırmızı.**
   - Yeniden adlandırma: gerçek `Storage` üstünde `DrivePlanStore`, `DrivePhotoRecord`,
     `DrivePhotoStore`; planın okunmasının hemen ardından başka bir iş parçacığında `follow_rename`,
     kısa bir süre (`WINDOW`) beklenir.
   - İkinci video basışı: döngü bir iş parçacığında, render basışın ilk kayıt okumasını bekler
     (`WaitsForTheLook`); kayıt (`LandsAfterFirstLook`) basışı o okumanın ardından inişe kadar tutar. Yer
     yazılmamışken ve `removed`'dan yeniden açılmışken.
   - Tekrar dene: fotoğrafı bitmiş kare; aynı anda iki basış (`retry_frame`, `retry_failed`), B ilk
     okumasından sonra tutulur, A ve döngü bu arada çalışır (`PausesAfterItsLook`).
2. **Bekle, soru:** iki seçenek ana ajana soruldu; karar, reviewer'ın tasarımı: kaydın katlanması sıradan
   bağımsız olur, yeni kilit yok.
3. **Katlama — testler önce.** `test_made_once.py`'ye gerçek `DrivePhotoRecord` üstünde: başka durumun
   üstüne verilen karar geçilir, aynı durumun üstüne verilen uygulanır, `from`'suz satır eskisi gibi,
   `done` her zaman, çıkarmadan sonra inen `failed` geçilir; `list` ve `written_prompts` geçilen satırı
   saymaz. Kapı testleri: sırada videosu olan kareye basış hiçbir şey eklemez; sıra temizlenirken ve
   beklenen kare silinirken inen fotoğraf `done` kalır (`LandsAtFirstLook`).
4. **Yeşil.**
   - `features/photo_generation/domain/queue.py`: `applies(now, seen)`.
   - `features/photo_generation/data/photo_record.py`: `mark(..., seen=)` satıra `from` yazar;
     `_applied(rows)` `slots`, `list` ve `written_prompts`'un yürüdüğü satırlar.
   - `features/photo_generation/domain/ports.py`: `PhotoRecord.mark` ve `slots`'un sözü.
   - `features/photo_generation/domain/run_loop.py`: `snapshot()` `named.steady()` içinde ve adı
     döndürür; tur o adı kullanır; `failed` işi aldığı durumu `seen` olarak verir.
   - `domain/usecases/queue_layer.py`: karenin kendi yeri kayıttaki durumdan; `queued` yalnız
     `removed`/`deleted`'ın üstüne, `seen` ile.
   - `domain/usecases/retry_frame.py`, `retry_failed.py`: `seen=failed`; fotoğraf dalı yalnız dolu
     olmayan fotoğrafa.
   - `domain/usecases/cancel_generation.py`, `remove_frames.py`, `remove_layer.py`, `fix_photo.py`:
     okudukları durumu `seen` olarak verir; `remove_frames` inmiş katmana `removed` yazmaz.
   - `backend/tests/test_photo_usecases.py`: `FakeRecord` `seen` alır ve aynı katlamayı yapar;
     `backend/tests/test_producer_contract.py`: `Record.mark` `seen` alır.
5. **Kırmızı kontrol:** `cancel_generation` ve `remove_frames` eski haline alınınca iki kapı testi
   kırmızı; geri konur.
6. **Reviewer'ın bulguları.**
   - `mark`'ın `seen`'i zorunlu ve yalnız adıyla (`*, seen`), port'ta, `DrivePhotoRecord`'da ve
     sahtelerde; testlerin her `mark`'ı kastettiği durumu verir; `from`'suz satır testi satırı elle
     ekler.
   - `remove_layer`: dolu okunan yer düşürülecekler listesine girmez.
   - `FakeRecord`, `photo_record._applied`'i kendi satırları üstünde çağırır.
   - `retry_frame`: kopya kare dosyayı tutarken fotoğraf yeniden istenmez — önce kırmızı test
     (`test_tekrar_dene_never_makes_a_photo_over_the_picture_a_copy_still_holds`).
   - Spec Sınırlar: eski bir commit'in 513'ün kaydını okuması.
   - `queue_layer`: döngünün kaydedeceği adı başka bir karenin dolu yeri tutuyorsa yer dolu sayılır —
     önce kırmızı test (`test_a_video_press_never_saves_over_the_video_a_copy_still_holds`, iki
     kapsamda); tarama `layers.held_elsewhere`'de, `retry_frame` ile ortak.
   - QA'nın bulduğu: planda borçlu ve kayıtta yazılmamış iş de sırada sayılır — önce kırmızı test
     (`test_a_second_video_press_before_the_first_is_made_does_not_add_the_frames_own_job_again`).
7. **`queen-editor/BACKLOG.md`, Diğer:** *"Fotoğraf kaydına aynı anda iki satır yazılabilir"*'e
   513'ün de satır sırasına dayandığı eklenir; yeni madde *"Yeniden adlandırma bir videoyu boş
   prompt'la ürettirebilir"*.

## Kapanış

8. Tek tek: `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
