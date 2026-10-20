# Madde 472 — Tek kapı `Storage`, plan

> **Koşum:** bu oturumda, ana klasörde, `feat/queen-editor-v10` dalında, adım adım, test önce (TDD).
> Adımlar `- [ ]` ile işaretlenir. Commit ana ajanın.

**Hedef:** Drive'a giden her okuma ve yazma `backend/services/storage/`'daki `Storage`'dan geçer; bir
kayıt ancak dosya bütün olarak yerine konunca başarılı döner.

**Spec:** [m472](../specs/2026-10-20-queen-editor-m472-storage-design.md)

**Araçlar:** pytest, vitest.

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce**, yalnız bugün doğru olanı söyler; ekrana giden cümleler
  Türkçe.
- Dosyalar Read / Edit / Write ile değişir; kabuk yalnız pytest, npm ve git status / diff için.
- İki satır birer birer koşulur, hiçbir zaman ikisi birlikte; `skip` / `xfail` yok.
- Store'ların dosya adları ve şemaları, domain'in kuralları değişmez. Frontend'de yalnız Görev 6b
  değişir, ve `dist` onunla yeniden kurulur.

---

## Görev 1: `Storage` — test önce

- [ ] `backend/tests/test_storage.py` (yeni; `test_drive_storage.py`'nin yerine). Bugünkü soruların
  yeni adreste olanları, ve yeniler:
  - kurulum diske dokunmuyor (olmayan bir kökle kurulur, hata vermez);
  - kök stat'ı Errno 107 → `StorageError`, cümlesinde OS'un metni; kök yok → `StorageError`;
    aygıt değişti → `StorageError`; yazma bu üçünde hiçbir şey bırakmıyor;
  - aygıt ilk kullanımda kaydediliyor, kurulumda değil;
  - ad sınırı: `""`, `"."`, `".."`, `"a/b"`, `"a\\b"`, `"a\0b"` — klasörde, demetin bir parçasında,
    dosya adında — diske dokunmadan `StorageError`; `delete_dir(())` reddediliyor;
  - kayıt: hedef `os.replace` ile yerine konuyor; yazma yarıda düşünce eski içerik duruyor ve
    geçici dosya kalmıyor; `list_files` `.qe-tmp-` önekini atlıyor;
  - örtük klasör yok: proje yokken `write_text` / `write_bytes` / `append_line` / `save_file`
    `FileNotFoundError`, ve klasör açılmamış; proje varken `(proje, "referans")`'a yazmak
    `referans/`'ı açıyor; `rename_dir("a", "x/y")` reddediliyor;
  - "yok" yalnız `FileNotFoundError`: `read_text`, `read_bytes`, `list_files`, `dir_exists`, `stamp`
    başka bir `OSError`'ı yükseltiyor;
  - `save_file` makinedeki bir dosyayı kaydediyor; `path` sınırdan ve kontrolden geçiyor.
- [ ] Kırmızıyı gör.
- [ ] `backend/services/storage/__init__.py`, `backend/services/storage/storage.py` · `Storage`,
  `StorageError`. `backend/services/drive/` silinir.
- [ ] Yeşil.

## Görev 2: Yeniden adlandırma — 18 test dosyası ve 12 store

- [ ] Store'lar: `from backend.services.drive.storage import DriveStorage` yoktu (store'lar sınıfı
  içe aktarmıyor); docstring'lerdeki "over DriveStorage" → "over Storage".
- [ ] `main.py`: `from backend.services.storage.storage import Storage`; `Storage(config.DRIVE_ROOT)`.
- [ ] Test dosyaları (`DriveStorage` kuranlar): `test_agent_routes`, `test_chat_record`,
  `test_chats_routes`, `test_export_total`, `test_happy_ending`, `test_photo_record`,
  `test_photo_routes`, `test_plan_store`, `test_photo_store`, `test_projects_routes`,
  `test_reference_routes`, `test_video_length`, `test_project_store`, `test_settings_store`,
  `test_reference_settings` — içe aktarma ve kurucu.
- [ ] Proje klasörünü açmadan yazan testlere klasör açılır (örtük klasör yok) — kırmızılardan okunur.
- [ ] `test_composition_root`: kök vermeyen altı test kökü `tmp_path` yapar (kontrol yoksa 503 olur).

## Görev 3: `project_store` ve `plan_store` — katı okuma

- [ ] Test: bozuk `arsiv.json`'la `archive`, `restore`, `delete`, `rename` `OSError`; dosya olduğu
  gibi; `delete` ve `rename` klasöre dokunmamış. Liste bugünkü gibi çiziliyor.
- [ ] Test: bozuk `plan.json`'a `append` `OSError`; dosya olduğu gibi. `read` bugünkü gibi boş.
- [ ] Kırmızı → `project_store`: `()` kök; `_marks` (hoşgörülü) ve `_held_marks` (katı); `delete` /
  `rename` önce işareti okur. `plan_store`: `_parse` ayrılır, `append` katı. → Yeşil.

## Görev 4: `reference_store`

- [ ] Test (`test_reference_store.py`, yeni): ffprobe'a verilen yol ve `dir_path`'in cevabı
  `Storage.path`'ten; havuz klasörü ilk dosyayla açılıyor, proje açılmıyor; `..` reddediliyor.
- [ ] `_subdir` → `(project, REFERENCE_DIR)`; `os` içe aktarması gider.

## Görev 5: `photo_store` ve `run_export`

- [ ] `test_photo_store`: `export_folder` hiçbir şey açmıyor; `copy_photo(project, photo, stamp,
  name)` hedefte varsa yazmıyor; `copy_video` ve `copy_export` kayıt olarak koyuyor ve geride
  geçici dosya bırakmıyor; `remove_export` dakikalık klasörü siliyor; `remove_pieces` makinedekini.
- [ ] `test_export`: `ExportStore` yeni yüzeye; ayrı modda parçalar makinede kesiliyor, her biri
  `copy_video` ile gidiyor, bitince parça klasörü siliniyor; Drive'daki videolar silinmiyor;
  birleşik mod bugünkü gibi; düşen / iptal edilen koşu `remove_export` + `remove_pieces`.
- [ ] Kırmızı → `photo_store`, `run_export`, `export_summary` (`export_dir`). → Yeşil.

## Görev 6: Route'lar ve tek hata işleyicisi

- [ ] Test (`test_static` ya da app testi): bir route `OSError` yükseltince 503 ve `{"error": …}`.
- [ ] Route testleri: `DELETE /api/projects/..`, `/%2E%2E`, `/.`; `POST /api/projects/../archive`;
  `GET /photos/../<dosya>`, `/photos/%2E%2E/<dosya>`; `GET /references/../<dosya>` — reddediliyor,
  kökün dışındaki dosyalar yerinde, hiçbir şey sunulmuyor.
- [ ] Var olan 500 bekleyen testler 503'e.
- [ ] `web/app.py`'ye işleyici; on dört `except OSError` bloğu gider; `serve_photo` /
  `serve_reference` klasörü `Storage.path`'ten alır (`photo_dir`, `reference_dir` üstünden). → Yeşil.

## Görev 6b: Galerinin okuma hatası ekranda kalır (QA'nın bulduğu)

- [ ] Test önce: `useGeneration.test.jsx` — `/frames` düşer, `/status` başarılı: `framesError`
  sunucunun cümlesi; bir sonraki başarılı okuma onu kaldırır. `Gallery.test.jsx` — `failure` varken
  cümle çiziliyor, ne liste ne "henüz kare yok" ne dönen işaret. `ProjectScreen.test.jsx` — ikisi
  birlikte, ekranda.
- [ ] `useGeneration.js`: `framesError` durumu; `ProjectScreen.jsx`: `Gallery`'ye `failure`;
  `Gallery.jsx`: `failure` varken cümle.
- [ ] `npm run build --prefix queen-editor/frontend`.

## Görev 7: Belgeler

- [ ] CODE-STANDARD *Services*: `storage/` ve kapının kuralları.
- [ ] FOUNDATION karar 7: tek kapı ve kaydın başarısı.

## Görev 8: Tarama ve koşu

- [ ] `queen-editor/backend` altında (testler hariç) `services/storage/` dışında `os.makedirs`,
  `shutil`, `open(`, `os.replace` aranır: kalanlar yalnız makinenin geçici alanı ve ComfyUI'nin
  dosyaları.
- [ ] `python -m pytest queen-editor -q`, sonra `npm test --prefix queen-editor/frontend`.

## Görev 9: Colab denemesi — kullanıcının

- [ ] Spec'in *Bitti sayılır* 4'ü: `order.json` 20 kez; Drive'ın web'i ve çöp kutusu. Ana ajan
  kullanıcıya sorar.

## Görev 10: Commit — ana ajanın
