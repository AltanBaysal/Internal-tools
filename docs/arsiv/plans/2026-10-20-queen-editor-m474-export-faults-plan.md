# Madde 474 — Export'un iki eski hatası, plan

> **Koşum:** bu oturumda, ana klasörde, `feat/queen-editor-v10` dalında, adım adım, test önce (TDD).
> Adımlar `- [ ]` ile işaretlenir. Commit ana ajanın.

**Hedef:** birleşik dosya makinede sabit bir adla (`birlesik.mp4`) kesilir; düşen bir export yalnız
kendi videolarını siler, `foto/`'yu başka hiçbir export ona ihtiyaç duymuyorsa, sonra boş klasörleri.

**Spec:** [m474](../specs/2026-10-20-queen-editor-m474-export-faults-design.md)

**Araçlar:** pytest, vitest.

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce**, yalnız bugün doğru olanı söyler.
- Dosyalar Read / Edit / Write ile değişir; kabuk yalnız pytest, npm ve git status / diff için.
- İki satır birer birer koşulur.
- Frontend ve notebook değişmez; `dist` yeniden kurulmaz.

---

## Görev 1: `Storage.remove_empty_dir`

- [ ] `backend/tests/test_storage.py`: `CALLS`'a `remove_empty_dir`; boş klasörü siliyor (`True`),
  dolu ve olmayan için `False` ve dokunmuyor, `()` `NameRefused`.
- [ ] Kırmızı.
- [ ] `backend/services/storage/storage.py`: `remove_empty_dir(folder)` — `os.rmdir`;
  `FileNotFoundError`, `ENOTEMPTY`, `EEXIST` → `False`.
- [ ] Yeşil.

## Görev 2: `ExportRunner.others_writing`

- [ ] `backend/tests/test_export.py`: öteki mod koşuyor ve `target` aynı → `True`; kendi modu,
  başka `target`, dinlenen öteki mod → `False`.
- [ ] Kırmızı → `export_runner.py`'ye yöntem → yeşil.

## Görev 3: `photo_store.remove_export(project, stamp, videos, in_use)`

- [ ] `backend/tests/test_photo_store.py` (gerçek klasörlerle):
  - kendi videoları gider, aynı dakikadaki birleşik dosya ve `foto/` kalır;
  - videosu olmayan (birleşik) düşen export: başka export'un `video/`'su ve `foto/` kalır;
  - `in_use` iken `foto/` kalır;
  - tek başına: `foto/`, `video/` ve dakikalık klasör gider, `Exportlar` kalır;
  - var olan iki testin çağrısı yeni imzaya.
- [ ] Kırmızı → `photo_store.py` → yeşil.

## Görev 4: `run_export`

- [ ] `backend/tests/test_export.py`:
  - sahte `ExportStore.remove_export` yeni imzayı kaydeder (`cleanups`); `DriveGoneAtCleanup` de;
  - ayrı export 02'de düşünce temizlik `["01.mp4"]` ve `in_use=False` alıyor; birleşik `[]`;
  - öteki mod aynı klasöre yazarken düşen export `in_use=True` veriyor;
  - birleşen dosya `PIECES/birlesik.mp4`, Drive'a `düğün.mp4`; var olan üç testin beklediği ad;
  - gerçek `Storage` ile: adı `01` olan projenin birleşik dosyası doğru (sahte ffmpeg çıktıyı önce
    açar, `-y` gibi), Drive'da `01.mp4`;
  - gerçek `Storage` ile: aynı dakikada bitmiş birleşik export varken ayrı export düşüyor, birleşik
    dosya ve `foto/` kalıyor, `video/` gidiyor.
- [ ] Kırmızı.
- [ ] `run_export.py`: `JOINED`; `own` listesi `_write`'a; `_clean` yeni çağrı; docstring'ler.
- [ ] Yeşil.

## Görev 5: Bitiş

- [ ] `python -m pytest queen-editor -q`, sonra `npm test --prefix queen-editor/frontend`.
- [ ] `git status` / `git diff` ile değişen dosyaları gözden geçir.
