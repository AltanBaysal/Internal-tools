# Madde 482 · Krea 2 Turbo, fotoğraf üretiminde bir seçenek — plan

**Spec:** [2026-10-21-queen-editor-m482-krea2-photo-option-design.md](../specs/2026-10-21-queen-editor-m482-krea2-photo-option-design.md)
· **Dal:** `feat/queen-editor-v10` · Test önce (TDD). Ekran değişmez, `dist` derlenmez.

## 1. Grafik

1. `Unsaved Workflow.json` → `queen-editor/assets/workflow_photo_krea2_api.json`, bayt bayt.
2. `backend/config.py`: `KREA2_WORKFLOW_PATH`.
3. `backend/tests/test_workflow_asset.py`:
   - gönderilen grafikler dört;
   - Krea grafiği API biçiminde, yazılan üç düğümüyle;
   - cfg 1 ve negatifi `ConditioningZeroOut`;
   - SNOFS açık;
   - yüklediği her model fotoğraf grubunun Krea seçeneğinde;
   - Krea'nın boyutları videoyla birebir aynı oranda, 16'nın katı, adı neyse şekli o.

## 2. Krea üreticisi

1. `backend/tests/test_comfy_krea_photo_generator.py`:
   - prompt, seed ve boyut yazılır; negatif, LoRA ve tetik yazılmaz;
   - dosya değişmez;
   - UI biçimi ve eksik düğüm durur;
   - `None` grafiğin boyutunu bırakır.

   Kırmızı.
2. `backend/features/photo_generation/data/comfy_krea_photo_generator.py`. Yeşil.

## 3. Modele göre kapı

1. `backend/tests/test_photo_by_model.py`:
   - `krea2` Krea'ya, öteki her değer (boş, `recipe:…`, dosya adı, `nova3dcg`) bugünkü üreticiye;
   - `fits_batch` modelin üreticisine sorulur, Krea'da `False`;
   - `generate_batch` geçer.

   Kırmızı.
2. `backend/features/photo_generation/data/photo_by_model.py`. Yeşil.
3. `domain/ports.py`: `fits_batch(count, model="")`. `domain/run_loop.py`: `_made_together` grubun
   modelini verir. `data/comfy_photo_generator.py`: `fits_batch(count, model="")`, `model` yok sayılır.
   `tests/test_variant_batch.py`: sahte `fits_batch` modeli alır, yeni test: soru modeli taşır.
4. `domain/catalog.py`: `KREA2` ve Krea satırı. `tests/test_photo_usecases.py`: model listesi üç.
5. `backend/main.py`: `PhotoByModel`.
6. `tests/test_producer_contract.py`: config'in grafikleri dört; gerçek döngü, Krea karesi gerçek Krea
   grafiğiyle yatay 1280 × 720; `tests/test_composition_root.py`: fotoğraf üreticisi `PhotoByModel`.

## 4. Üreticiler paneli

1. `backend/tests/test_producers.py`:
   - `any` satırı: seçeneklerden biri tam ise kurulu, yarım seçenek değil;
   - yalnız Krea'lı makine kurulu;
   - biçim testi üçüncü biçimi alır;
   - fotoğraf grubunun satırları.

   Kırmızı.
2. `domain/model_groups.py`: `KREA2_FILES`, `any` satırı. `domain/usecases/list_producers.py`:
   `_here`. Yeşil.

## 5. Notebook

1. `backend/tests/test_notebook_installs_the_producer_groups.py`:
   - panelin saydığı her dosya, iç içe olanlar da, defterde;
   - Krea'nın üç HF dosyası Comfy-Org'dan, SNOFS 3390681'le aynadan;
   - Krea'nın listeleri kutusunun arkasında;
   - disk Krea'yı sayar;
   - klon dördüncü grafiği arar;
   - checkpoint'i olan modellerin testi Krea'yı atlar.

   Kırmızı.
2. `queen-editor/queeneditor.ipynb`:
   - CONFIG: kutu ve kontrol;
   - model hücresi: `PHOTO_MODELS`, `HF_KREA2`, `CIVITAI_KREA2`, `PHOTO_GIB`, `FOLDERS`;
   - klon hücresi.

   Yeşil.

## 6. Takımlar

Tek tek: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
`python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
