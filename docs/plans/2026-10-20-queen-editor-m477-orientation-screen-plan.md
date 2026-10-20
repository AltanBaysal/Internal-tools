# Madde 477 — Üretimin yönü, ekran, plan

> **Koşum:** bu oturumda, ana klasörde, `feat/queen-editor-v10` dalında, adım adım, test önce (TDD).
> Adımlar `- [ ]` ile işaretlenir. Commit ana ajanın.

**Hedef:** fotoğraf üretiminin başladığı her formda *Yön: Yatay | Dikey*, varsayılan *Yatay*; seçilen
yön o üretimle gider. Fotoğraf panelinde ve Referanstan'da projeyle saklanır, *Yeniden üret*te karenin
kendi yönüyle açılır.

**Spec:** [m477](../specs/2026-10-20-queen-editor-m477-orientation-screen-design.md)

**Araçlar:** pytest, vitest, vite build.

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce**, ekrandaki metin **Türkçe**.
- Dosyalar Read / Edit / Write ile değişir. Kabuk yalnız pytest, npm ve git status / diff için.
- İki suite birer birer koşulur.

---

## Görev 1: kayıtlar (backend)

- [ ] `test_settings_store.py`: boş kayıtta `orientation` `""`; gidip gelen kayıtta `dikey`; alanı
  olmayan eski kayıt `""`; metin olmayan değer `""`.
- [ ] `test_project_usecases.py`: `save_settings` `orientation`'ı yazıyor.
- [ ] `test_projects_routes.py`: `GET`/`PUT …/settings` alanı taşıyor; yanlış tip `""`.
- [ ] `test_reference_settings.py`: aynıları `reference_settings.json` için.
- [ ] Kırmızı → `settings_store.py`, `save_settings.py`, `projects/presentation/routes.py`,
  `reference_settings_store.py`, `save_reference_settings.py`, `reference_settings_routes.py` → yeşil.

## Görev 2: `api.js` ve `useGeneration`

- [ ] `api.test.js`: `generateBatch`, `saveSettings`, `regenerateFrame`, `produceFromReferences`,
  `saveReferenceSettings` gövdelerinde `orientation`.
- [ ] `useGeneration.test.jsx`: havuzdan üretim yönü `produceFromReferences`'a veriyor.
- [ ] Kırmızı → `api.js`, `useGeneration.js` (`queueLayer`'ın ve `regenerate`'in son argümanı) → yeşil.

## Görev 3: `orientation.jsx`

- [ ] Yeni dosya: `LANDSCAPE`, `PORTRAIT`, `FIRST_ORIENTATION`, `shapeOf`, `OrientationSegment`. Panellerin
  testleri üzerinden sınanır.

## Görev 4: fotoğraf paneli

- [ ] `GeneratePanel.test.jsx`: *Yatay* açılış, negatifin altında, dokunulmazsa `yatay`, *Dikey*
  seçilince `dikey`, kaydın `dikey`'i, alan hatasını temizleme, taslakta hatırlama.
- [ ] `ProjectScreen.test.jsx`: *Kuyruğa ekle* yönü kayda ve `generateBatch`'e veriyor.
- [ ] Kırmızı → `GeneratePanel.jsx` (`opening`, state, `REMEMBERED`, segment, gönderim),
  `ProjectScreen.jsx` (`handleGenerate`) → yeşil.

## Görev 5: *Yeniden üret*

- [ ] `PhotoDetail.test.jsx`: satırın yönüyle / *Yatay*'la açılış; resmin şekli gelince onu izleme
  (`naturalWidth` / `naturalHeight` elemana konur, `load` ateşlenir); seçimin önceliği ve gönderimi;
  Video sekmesinde yok; başka karede düşme. Video'nun dört beklentisine yedinci `undefined`.
- [ ] Kırmızı → `PhotoDetail.jsx` (`newOrientation`, `{ file, facing }`, `learnShape`, segment,
  `handleRegenerate`) → yeşil.

## Görev 6: *Referanstan*

- [ ] `LayerPanel.test.jsx`: yalnız Referanstan'da, *Yatay* / kaydın yönüyle açılış, kayda ve kuyruğa
  gitme, yeniden kurulunca taslakta kalma. Sekme düzeninin iki listesine `Yön`; havuzdan gönderimin
  üç beklentisine `"yatay"`. `ProjectScreen.test.jsx`'in havuz beklentisine `"yatay"`.
- [ ] Kırmızı → `LayerPanel.jsx` (`poolOrientation`, kayıt, taslak, segment, gönderim) → yeşil.

## Görev 7: Bitiş

- [ ] `npm run build --prefix queen-editor/frontend`.
- [ ] `python -m pytest queen-editor -q`, sonra `npm test --prefix queen-editor/frontend`.
- [ ] `git status` / `git diff` ile değişen dosyaları gözden geçir.
