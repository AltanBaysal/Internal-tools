# Madde 510 · Videonun sesi kare sayfasından kapatılabilir — plan

**Spec:** [2026-10-29-queen-editor-m510-ses-kapatma-design.md](../specs/2026-10-29-queen-editor-m510-ses-kapatma-design.md)

Önce test yazılır ve kırmızı görülür, sonra kod.

## Sunucu

1. **`backend/tests/test_mute.py` — yeni, kırmızı.**
   - **Store** (gerçek `Storage` bir klasör üstünde):
     - dosya yoksa `[]`;
     - `put` ekler ve çıkarır;
     - aynı durumda yazmaz;
     - bozuk dosyada `read` ve `put` `OSError` verir ve dosya aynı kalır;
     - iki iş parçacığında iki `put` ikisini de bırakır.
   - **Kapı** (`client_over`, `test_happy_ending`'in yolu): `GET`, `PUT true`/`false`, sesi olmayan ve
     sesi kırmızı kare, geçersiz değer, olmayan proje.
   - **Export:** `test_export`'un `ExportStore`'u ve `FakeExporter`'ı, `silent` eklenmiş haliyle:
     - kapalı kare `silent`'le, öteki `piece`'le;
     - sesi olmayan kare listede olsa da `piece(…, None, …)`;
     - birleşik export'ta parçaların sırası;
     - liste bir kez okunur;
     - liste okunamazsa export klasörü açılmaz.
   - **Özet:** `muted` ve `silent` ayrık.
   - **`FfmpegVideoExporter.silent`:** komut `-i video -c copy -an hedef`.
2. **`backend/tests/test_export.py`, `backend/tests/test_export_total.py`.** `run_export` ve
   `export_summary`'yi çağıran yardımcılara `mutes=` eklenir (boş liste). `FakeExporter`'a `silent`
   eklenir.
3. **`backend/tests/test_composition_root.py` — kırmızı.**
   - export ve özet `main._mutes`'u alıyor;
   - `GET /api/projects/m510-yok/muted` 404.
4. **Yeşil.**
   - `features/photo_generation/domain/mute.py`: `holds_sound`, `silenced`, `require_sound`,
     `check`, `InvalidMute`, `NoSound`. `export_summary`'nin `silent`'i ve `run_export`'un
     `_audio_of`'u `holds_sound`'u sorar.
   - `features/photo_generation/domain/ports.py`: `MuteStore`.
   - `features/photo_generation/data/mute_store.py`: `DriveMuteStore` — `project_exists`, `read`,
     `put`, kilit.
   - `features/photo_generation/domain/usecases/mute.py`: `get_muted`, `set_muted`.
   - `features/photo_generation/presentation/mute_routes.py`: `make_mute_blueprint`.
   - `features/photo_generation/domain/usecases/run_export.py`: `mutes` argümanı, klasörden önce bir
     okuma, `silenced` karede `exporter.silent`.
   - `features/photo_generation/domain/usecases/export_summary.py`: `mutes`, `muted` sayısı.
   - `features/photo_generation/data/ffmpeg_video_exporter.py`: `silent(video, target)`.
   - `backend/main.py`: `_mutes`, iki `mutes=`, kapı, blueprint listesi.

## Ekran

5. **`frontend/src/features/photo_generation/useMuted.test.jsx` — yeni, kırmızı.**
   - açılışta tek `getMuted`;
   - `mute` listeyi hemen değiştirir ve `saveMuted` gider; cevaptan yalnız o kare alınır;
   - reddedilen basış eski haline döner ve reddi geçirir;
   - aynı karede eski basışın geç cevabı ve reddi uygulanmaz;
   - iki karede basış, ikincinin cevabı önce: ikisi de kapalı kalır;
   - iki karede basış, birinci reddedilir: yalnız birinci geri alınır ve reddi söylenir.
6. **`LayerPlayer.test.jsx` — kırmızı.**
   - `onMute` yokken düğme yok;
   - varken **Sesi kapat**, `silent`'te **Sesi aç**;
   - basış `onMute`'u çağırır, oynatmaz;
   - `silent`'te video ve wav `muted`;
   - sesi olmayan Video sekmesinde video susmaz.
7. **`PhotoDetail.test.jsx` — kırmızı.**
   - api sahtesine `getMuted`, `saveMuted`;
   - Video ve Ses sekmelerinde düğme;
   - sesi olmayan ve sesi kırmızı karede düğme yok;
   - basış ve geri basış;
   - açılışta kapalı gelen kare;
   - ret kartı;
   - başka kareye geçince kart gider.
8. **`ExportScreen.test.jsx` — kırmızı.** *⚠ 2 videonun sesi kapalı*; sıfırda satır yok.
9. **Yeşil.**
   - `shared/api.js`: `getMuted`, `saveMuted`.
   - `features/photo_generation/useMuted.js`.
   - `features/photo_generation/glyphs.jsx`: `SpeakerGlyph`, `SpeakerOffGlyph`.
   - `LayerPlayer.jsx`: `silent`, `onMute`, sağ üstte düğme.
   - `PhotoDetail.jsx`: `useMuted`, `onMute`/`silent`, ret kartı.
   - `ExportScreen.jsx`: satır.
10. **Başka ekranlar.** `PhotoDetail`'i çizen testlerin (`App.test.jsx`) api sahtelerine `getMuted`
    eklenir.

## Reviewer'dan sonra

- `queen-editor/BACKLOG.md`, Diğer: *"Kare sayfasında geç gelen bir ret başka karede görünüyor"*.

## Bitiş

11. `python -m pytest queen-editor -q`, sonra `npm test --prefix queen-editor/frontend`, tek tek.
12. `npm run build --prefix queen-editor/frontend`; `dist` değişikliğiyle birlikte bırakılır, commit
    ana ajanın.
