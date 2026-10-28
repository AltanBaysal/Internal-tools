# Madde 497 · Drive'a kayıt olmayınca hata verip dursun — plan

**Spec:** [2026-10-27-queen-editor-m497-drive-kayit-kontrolu-design.md](../specs/2026-10-27-queen-editor-m497-drive-kayit-kontrolu-design.md)

Test önce yazılır, kırmızı görülür, sonra kod.

## 1. `queen-editor/backend/tests/test_storage.py` — kırmızı

"the room check" başlığıyla yeni testler; boş yer `storage_module.shutil.disk_usage` yerine konan
sahteyle verilir:

- yer yokken `write_bytes`, `write_text`, `save_file` `StorageError` veriyor; cümle iki sayıyı ve
  hedefin adını taşıyor; eski hedef aynı, klasörde geçici dosya yok;
- yer yokken `append_line` `StorageError` veriyor ve kayıt dosyası aynı kalıyor;
- boş yer yazılacağa tam eşitse kayıt da satır da yazılıyor;
- `disk_usage`'ın kendi `OSError`'ı yükseliyor ve hiçbir şey yazılmıyor;
- boş yer sorulan yol kök.

## 2. `queen-editor/backend/services/storage/storage.py` — yeşil

- `_save(folder, name, size, write)`: `_file`'dan (ad + bağlantı kontrolü) sonra, `mkstemp`'ten önce
  `self._room(size, target)`.
- `_room`: `shutil.disk_usage(self._root).free < size` ise `StorageError("Drive'da yer yok: …")`.
- `write_bytes` boyut olarak `len(data)` verir; `save_file` kaynağı bir kez açar, boyutu
  `os.fstat(handle.fileno()).st_size`'tan alır ve açık dosyadan kopyalar.
- `append_line`: `_file`'dan sonra `self._room(<satır + "\n"'in UTF-8 uzunluğu>, path)`.
- Modülün docstring'i kuralı söyler: her yazma önce yer sorar.

## 3. `queen-editor/backend/tests/test_photo_usecases.py` — bugünkü yolu sabitleyen testler

`FakeStore`'dan, `save`'i kısa, nötr bir `StorageError` veren bir alt sınıf:

- fotoğraf: `run_batch` sonrası `runner.status()` `error`, cümle tam olarak o hata; kare `done`
  değil;
- video: `video_job_project` + `resume_batch` ile aynısı, video katmanında.

## 4. `queen-editor/backend/tests/test_export.py` — export

`on_drive` ile gerçek `Storage` üstünde, `disk_usage` sahte ve dolu: `ExportRunner` ile başlatılan
export `error` durumunda ve cümle "Drive'da yer yok"; exports kökünde hiçbir şey kalmıyor.

## 5. Belgeler

- `queen-editor/CODE-STANDARD.md`, *Services*: kapının kurallarına "every write asks for room
  first", istisnasız; DriveFS'in boş yerinin hesabın kotası olduğu doğrulanmadı diye.
- `queen-editor/FOUNDATION.md` karar 7: kapının her yazmadan önce baktığı ikinci şey, Drive'ın boş
  yeri; hatası kapının kendi cümlesi.

## 6. Frontend — Kuyruğa ekle'nin reddi (QA'dan)

- `GeneratePanel.test.jsx` — kırmızı: reddedilen Kuyruğa ekle "Kuyruğa eklenemedi" başlığının altında
  `error`'daki sunucu cümlesini gösteriyor, "tekrar dene" yok; iki eski test yeni başlığı bekler.
- `ProjectScreen.test.jsx` — kırmızı: `onSaveSettings` Drive'ın cümlesiyle reddedince cümle ekranda,
  `generateBatch` çağrılmıyor.
- `useGeneration.test.jsx` / `GeneratePanel.test.jsx` — kırmızı: reddedilen `generate`
  `{ error: <failureText> }` ile dönüyor; panel, `error` prop'u `null`'a dönünce de reddin cümlesini
  gösteriyor.
- `useGeneration.js` — `generate`'in `catch`'i `{ error: failureText(err) }` döner
  (`failureText` bir kez hesaplanır); `ProjectScreen.handleGenerate`'in ayar reddi de aynı şekli döner.
- `GeneratePanel.jsx` — yeşil: `refused` `null` ya da reddin sözü (`setRefused(result?.error ??
  null)`); sabit `Note` yerine `<StatusErrorCard text="Kuyruğa eklenemedi" raw={refused} />`.
- `GeneratePanel.jsx` — prompt bloğunun `minHeight: 0`'ı `PROMPT_FLOOR` (96 px) olur: kart onu
  ezmez, panel kayar. jsdom yerleşim hesaplamaz; test yok, QA Playwright'ta 1280×720'de bakar.
- Öteki ekran yazmalarının yakalayıcıları gözden geçirilir (spec, 4).

## 7. Doğrulama

`npm run build --prefix queen-editor/frontend`. Sırayla: `python -m pytest queen-editor -q`, sonra
`npm test --prefix queen-editor/frontend`.
