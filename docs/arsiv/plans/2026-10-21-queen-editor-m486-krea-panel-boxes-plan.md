# Madde 486 · Krea seçiliyken LoRA kutusu Krea'nın LoRA'sını gösterir, negatif gizlenir — plan

**Spec:** [2026-10-21-queen-editor-m486-krea-panel-boxes-design.md](../specs/2026-10-21-queen-editor-m486-krea-panel-boxes-design.md)
· **Dal:** `feat/queen-editor-v10` · Test önce (TDD). Ekran değişir, `dist` yeniden kurulur.

## 1. Katalog ve model listesi

1. `queen-editor/backend/tests/test_photo_usecases.py`:
   - Krea'nın satırı `list_models`'ta `lora: {"value": "snofs", "label": "SNOFS"}` ve
     `negative: False` taşır; Nova ve DaSiWa'nın satırı bugünkü gibi.
2. `queen-editor/backend/tests/test_workflow_asset.py`: Krea grafiğinin `53:15`'i katalogdaki
   `KREA2_LORA`'nın dosyasını yükler.

   Kırmızı.
3. `backend/features/photo_generation/domain/catalog.py`: `KREA2_LORA`, Krea satırında `lora` ve
   `negative`, `own_lora`, `drawn_with`; modül docstring'i.
4. `backend/features/photo_generation/domain/usecases/list_models.py`: satırın iki alanı. Yeşil.

## 2. Krea satırının kaydı

1. `test_photo_usecases.py`:
   - Krea batch'i: satırlar `lora: "snofs"`, `negative: ""`, üreticiye de bunlar gider;
   - Krea batch'i kutuda eskimiş bir LoRA'yla da kuyruğa girer (`InvalidLora` yok);
   - Nova batch'i bugünkü gibi (mevcut testler); bilinmeyen bir model kutuların LoRA'sını ve
     negatifini kaydeder;
   - `regenerate`: Krea karesinden yeni fotoğraf negatifsiz, LoRA `snofs`; 486'dan önce `slime`'la
     planlanmış bir Krea karesi de.
2. `test_fix_photo.py`: Krea satırının düzeltmesi negatifsiz kaydedilir.

   Kırmızı.
3. `domain/usecases/start_batch.py`: doğrulama `own_lora(model) is None` iken; `plan_frames`
   `drawn_with`'in cevabını yazar.
4. `domain/usecases/regenerate.py`, `domain/usecases/fix_photo.py`: `drawn_with`. Yeşil.

## 3. Panel

1. `frontend/src/features/photo_generation/GeneratePanel.test.jsx`:
   - Krea seçilince LoRA kutusu yalnız SNOFS, kapalı; "Negatif prompt" yok;
   - Nova'ya dönünce kutular: seçilen LoRA ve yazılan negatif yerinde;
   - Krea'da istek kutuların kendi değerlerini taşır (ayarlar korunur);
   - kayıtlı Krea ile açılan panel aynı.

   Kırmızı.
2. `GeneratePanel.jsx`: `chosen`, `ownLora`, `takesNegative`. Yeşil.

## 4. Ayrıntı sayfası

1. `PhotoDetail.test.jsx`: Krea karesi LoRA satırında SNOFS, negatif kutusu yok; Nova karesi bugünkü
   gibi (mevcut testler). Kırmızı.
2. `PhotoDetail.jsx`: `madeBy`; LoRA adı modelin kendi LoRA'sından ya da listeden; negatif kutusu
   `madeBy.negative === false` iken çizilmez. Yeşil.

## 5. Bitiş

1. `npm run build --prefix queen-editor/frontend`.
2. Takımlar tek tek: `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`,
   `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`.
