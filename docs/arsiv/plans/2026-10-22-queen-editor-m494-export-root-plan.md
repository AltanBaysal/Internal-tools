# Madde 494 — export'ların kendi kökü, plan

> **Koşum:** bu oturumda, ana klasörde, `feat/queen-editor-v10` dalında, adım adım, test önce (TDD).
> Adımlar `- [ ]` ile işaretlenir. Commit ana ajanın.

**Hedef:** export'lar `MyDrive/queenEditorExport/<tarih> <proje>/`'ye, kendi `Storage`'ından geçerek
gider; `queenEditor`'de `Exportlar` açılmaz ve ayrılmış ad olmaktan çıkar.

**Spec:** [m494](../specs/2026-10-22-queen-editor-m494-export-root-design.md)

**Araçlar:** pytest, vitest.

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce**, yalnız bugün doğru olanı söyler; ekrana giden cümleler
  Türkçe.
- Dosyalar Read / Edit / Write ile değişir; kabuk yalnız pytest, npm ve git status / diff için.
- Suite'ler birer birer koşulur.
- Frontend kodu değişmez; `dist` yeniden kurulmaz. Notebook'un `BRANCH` satırına dokunulmaz.

---

## Görev 1: `photo_store` — export'ların `Storage`'ı

- [ ] `backend/tests/test_photo_store.py`: `store_at(path)` iki kök kurar — `path/"projeler"` ve
  `path/"export"` — ve `DrivePhotoStore(Storage(projeler), Storage(export))`. Testler:
  - `open_export` dakikalık klasörü export kökünde açıyor, yolunu dönüyor; projeler kökünde bir şey
    açılmıyor; varsa içine dokunulmuyor;
  - export kökünün stat'ı düşünce `StorageError`, hiçbir şey açılmıyor;
  - export kökü yokken `StorageError`, kök açılmıyor;
  - `export_dir()` export kökü, bir şey açmıyor;
  - `open_export`'suz bir kayıt dakikalık klasörü açmıyor;
  - `copy_*` / `remove_export` yeni yerde; temizlik export kökünü bırakıyor;
  - `in_use` doğruyken boş dakikalık klasör kalıyor.
- [ ] Kırmızı.
- [ ] `photo_store.py`: `exports` bir `Storage`; `_dated` tek parça; `open_export` dakikalık klasörü
  `make_dir`'le açar; export yazmaları `self._exports`'tan; `remove_export` klasörü `in_use`
  yanlışken siler.
- [ ] Yeşil.

## Görev 2: Route ve koşu testleri, `main.py`, `config.py`

- [ ] `test_photo_routes.py`, `test_reference_routes.py`, `test_export.py` (`on_drive`): ikinci
  `Storage` export köküne; beklenen yollar `<export kökü>/<tarih> <proje>`; projeler kökünde
  `Exportlar` yok. Sahte yollar `/fake/queenEditorExport/…`.
- [ ] `test_composition_root.py`: `QE_EXPORT_ROOT` verilince `main._photo_store.export_dir()` o.
- [ ] Kırmızı.
- [ ] `config.py`: `EXPORT_ROOT`. `main.py`: `Storage(config.EXPORT_ROOT)`, `DrivePhotoStore`'a;
  `__main__`'in çıktısında export kökü.
- [ ] Yeşil.

## Görev 3: `Exportlar` ayrılmış ad olmaktan çıkar

- [ ] `test_name_rules.py`: `Exportlar` geçerli, `is_reserved("Exportlar")` yanlış; `EXPORTS_DIR`
  testi gider.
- [ ] `test_project_store.py`: kökteki `Exportlar` bir proje olarak listeleniyor; arşiv işaretli
  ayrılmış klasör testi `arsiv`'in bir harf biçimiyle.
- [ ] `test_projects_routes.py`, `test_reference_settings.py`: parametreler yalnız `ARCHIVE_DIR`;
  `Exportlar` yaratma testi geçerli bir proje olarak.
- [ ] Kırmızı.
- [ ] `name_rules.py`: `EXPORTS_DIR` gider. Yorumlar: `project_store`, `delete_project`,
  `rename_project`.
- [ ] Yeşil.

## Görev 4: `Storage`'ın cümleleri

- [ ] `test_composition_root.py`, `test_storage_routes.py`: "Kök klasöre ulaşılamıyor".
- [ ] Kırmızı.
- [ ] `storage.py`: üç cümle.
- [ ] Yeşil.

## Görev 5: Notebook

- [ ] Yeni `backend/tests/test_notebook_opens_the_export_root.py`: bağlama hücresi
  `EXPORT_FOLDER`'dan export kökünü açıyor; sunucu hücresi `QE_EXPORT_ROOT` veriyor.
- [ ] Kırmızı.
- [ ] `queeneditor.ipynb`: CONFIG `EXPORT_FOLDER`, bağlama hücresi, sunucu hücresi, ilk markdown.
- [ ] Yeşil.

## Görev 6: Frontend test verisi, belgeler

- [ ] `ExportScreen.test.jsx`: `/drive/Exportlar` → `/drive/queenEditorExport`.
- [ ] CODE-STANDARD: kökün tek istisnası `arsiv`; export kökü; `Storage` kök başına bir örnek;
  `make_dir` satırı.
- [ ] FOUNDATION 7: iki klasör, tek yerde adlandırılmış.

## Görev 7: Bitiş

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend`
- [ ] `git status` / `git diff` — yalnız spec'in andığı dosyalar.
