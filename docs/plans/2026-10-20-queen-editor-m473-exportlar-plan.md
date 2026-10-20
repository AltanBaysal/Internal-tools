# Madde 473 — `Exportlar` klasörü, plan

> **Koşum:** bu oturumda, ana klasörde, `feat/queen-editor-v10` dalında, adım adım, test önce (TDD).
> Adımlar `- [ ]` ile işaretlenir. Commit ana ajanın.

**Hedef:** yeni export'lar `queenEditor/Exportlar/<tarih> <proje>/`'ye gider; `Exportlar` proje
olarak listelenmez ve proje adı olamaz; eski export'lara dokunulmaz.

**Spec:** [m473](../specs/2026-10-20-queen-editor-m473-exportlar-design.md)

**Araçlar:** pytest, vitest.

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce**, yalnız bugün doğru olanı söyler; ekrana giden cümleler
  Türkçe.
- Dosyalar Read / Edit / Write ile değişir; kabuk yalnız pytest, npm ve git status / diff için.
- İki satır birer birer koşulur, hiçbir zaman ikisi birlikte.
- `Storage`, notebook ve frontend kodu değişmez; `dist` yeniden kurulmaz.

---

## Görev 1: Ayrılmış ad — `name_rules` ve `project_store`

- [ ] `backend/tests/test_name_rules.py`: `Exportlar`, `exportlar`, `EXPORTLAR` → ayrılmış cümlesi;
  `validate(name_rules.EXPORTS_DIR)` ayrılmış.
- [ ] `backend/tests/test_project_store.py`: kökte `Exportlar/` varken `list()` onu göstermiyor.
- [ ] `backend/tests/test_projects_routes.py`: `POST /api/projects {"name": "Exportlar"}` ve yeniden
  adlandırma `400`, "ayrılmış".
- [ ] Kırmızı.
- [ ] `features/projects/domain/name_rules.py`: `EXPORTS_DIR = "Exportlar"`; `validate` ikisini de
  `casefold` ile karşılaştırır.
- [ ] `features/projects/data/project_store.py`: `list()` `EXPORTS_DIR`'i de atlar.
- [ ] Yeşil.

## Görev 2: `photo_store` — yeni yer

- [ ] `backend/tests/test_photo_store.py`: `store_at` `DrivePhotoStore(Storage(...),
  name_rules.EXPORTS_DIR)`; `export_folder` yardımcısı `<kök>/Exportlar/<STAMP> düğün`. Testler:
  - `open_export` yokken `Exportlar`'ı açıyor, dakikalık klasörü açmıyor, yolunu dönüyor; varken
    içindekilere dokunmuyor;
  - kök Errno 107 / yokken `open_export` `StorageError`, hiçbir şey açılmıyor;
  - `export_dir()` `<kök>/Exportlar`, bir şey açmıyor;
  - `copy_photo` / `copy_video` / `copy_export` / `remove_export` yeni yerde; proje klasöründe
    `export/` açılmıyor; `remove_export` `Exportlar`'ı bırakıyor;
  - eski `<proje>/export/<tarih>/` dokunulmadan kalıyor.
- [ ] `test_photo_routes.py`, `test_reference_routes.py`: kurucuya ikinci argüman.
- [ ] Kırmızı.
- [ ] `features/photo_generation/data/photo_store.py`: kurucu `exports`; `EXPORT_DIR` gider;
  `export_dir()`, `open_export(project, stamp)`, `_dated`.
- [ ] Yeşil.

## Görev 3: `run_export`, `export_summary`, `main.py`

- [ ] `backend/tests/test_export.py`: sahte store `open_export` tutar ve sırayı yazar; `open_export`
  `make_pieces_dir`'den önce; `FOLDER` yeni yol.
- [ ] `backend/tests/test_photo_usecases.py`: sahte `export_dir()`; özetin `folder`'ı.
- [ ] `backend/tests/test_photo_routes.py`: export `drive/Exportlar/2026-08-12 14-32 düğün/video/01.mp4`'e
  iniyor, `drive/düğün/export` yok; özetin `folder`'ı `Exportlar` ile bitiyor; birleşik export da
  aynı yere.
- [ ] `backend/tests/test_composition_root.py`: `main._photo_store.export_dir()` =
  `<kök>/name_rules.EXPORTS_DIR`.
- [ ] Kırmızı.
- [ ] `run_export.py`: `store.open_export(project, stamp)`, `make_pieces_dir`'den önce.
- [ ] `export_summary.py`: `store.export_dir()`.
- [ ] `main.py`: `DrivePhotoStore(_storage, name_rules.EXPORTS_DIR)`.
- [ ] Yeşil.

## Görev 4: Frontend test verisi, yorumlar, belgeler

- [ ] `ExportScreen.test.jsx`: sahte özetin ve `target`'ın yolu sunucunun yeni cevabı.
- [ ] `rename_project.py` docstring'i.
- [ ] CODE-STANDARD: kökün klasörleri ve ayrılmış iki ad.

## Görev 4b: Reviewer'ın bulguları — ayrılmış klasör URL'den proje değil

- [ ] `test_name_rules.py`: `is_reserved`, her harf biçimiyle.
- [ ] `test_project_store.py`: arşiv işareti taşıyan ayrılmış klasör hiçbir listede yok.
- [ ] `test_projects_routes.py`: `Exportlar` ve `arsiv` için silme, yeniden adlandırma, arşivleme
  404; klasör yerinde, halt çağrılmamış, iki liste boş.
- [ ] Kırmızı.
- [ ] `name_rules.is_reserved`; `project_store.list` / `list_archived`; `delete_project`,
  `rename_project`, `archive_project` `ProjectMissing`.
- [ ] CODE-STANDARD'ın `make_dir` satırı; `ARCHIVE_DIR` yorumu; üç yerde yazılan "adı projects
  verir" cümlesi yalnız `name_rules`'ta.
- [ ] Yeşil.

## Görev 4c: QA'nın bulgusu — ayarların kapıları

- [ ] `test_projects_routes.py`, `test_reference_settings.py`: `Exportlar` ve `arsiv` için `GET` ve
  `PUT` `…/settings` ve `…/reference-settings` 404, klasöre dosya yazılmıyor.
- [ ] Kırmızı.
- [ ] `get_settings`, `save_settings`, `save_reference_settings`: varlık sorusunun yanında
  `is_reserved`.
- [ ] Yeşil.

## Görev 5: Bitiş

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend`
- [ ] `git status` / `git diff` — yalnız spec'in andığı dosyalar.
