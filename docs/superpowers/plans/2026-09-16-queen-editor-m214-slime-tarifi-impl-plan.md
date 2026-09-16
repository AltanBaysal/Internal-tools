# Madde 214 · Slime girl — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-16-queen-editor-m214-slime-tarifi-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı: `bfd410b6` — 21 backend, 32 ön yüz.

## Adımlar

**1 · `recipes.py`.** `RECIPES` listesi ve kimlikten tarife bakan bir yardımcı. Tek bilgi kaynağı:
ad, checkpoint, LoRA dizilimi, tetik.

**2 · `config.py`.** `PHOTO_RECIPES = [...]` — `QE_PHOTO_RECIPES`'in virgülle ayrılmış değeri,
kırpılmış, boşları atılmış.

**3 · `list_models.py`.** İkinci argüman `chosen`. Doluysa tarif satırları *(sıra `chosen`'ın
sırası)*, boşsa bugünkü davranış. `main.py` bağlamayı `partial(list_models, _photo_generator,
config.PHOTO_RECIPES)` yapar.

**4 · `comfy_photo_generator.py`.** `LORA_NODE = "27"`. `generate` değeri üçe ayırır; tarif
seçildiğinde `27`'nin `lora_*` anahtarları silinip tarifin listesi `lora_1`'den yazılır, tetik
prompt'un başına geçer. `_load`'un varlık kontrolü bugünkü dörtlüde kalır; `27` yalnız tarif
kullanılırken aranır ve yoksa adıyla söylenir.

**5 · Defter.** CONFIG kutuları tarif kutusuna döner ve başlık *"Fotoğraf tarifleri"* olur. Model
hücresi `PHOTO_CHECKPOINTS` + `PHOTO_RECIPES` + `CHOSEN_CHECKPOINTS` olur; indirme listesi ve
`PHOTO_GIB` o tekilleştirilmiş adı okur. `CIVITAI_PHOTO`'ya translucent LoRA eklenir. `flask_env`'e
`"QE_PHOTO_RECIPES"` eklenir.

**6 · `model_groups.py`.** Foto grubuna `translucent_penetration_v5.safetensors` satırı.

**7 · Ön yüz.** `GeneratePanel.jsx` satır çizer *(etiket metin, değer `value`)*; ilk satır
`rows[0].value`; *"artık kurulu değil"* değerlere bakar. `PhotoDetail.jsx` `useModels()` ile etiketi
bulur, bulamazsa kaydedilen değeri yazar.

**8 · Takım koşulur**, dördü de — hepsi yeşil beklenir:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

**9 · `dist` derlenir.** Ön yüz değişti, ve defter depoyu klonlayıp derlemiyor:

```
npm run build --prefix queen-editor/frontend
```

**10 · Yol haritası** düzeltilir: 214'ün satırı verilen kararı yazar, WAN şartı kalkar.

**11 · Tek commit** — kaynak ve `dist` birlikte.

## Değişen dosyalar

`queen-editor/backend/features/photo_generation/domain/recipes.py` *(yeni)*,
`queen-editor/backend/config.py`,
`queen-editor/backend/main.py`,
`queen-editor/backend/features/photo_generation/domain/usecases/list_models.py`,
`queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py`,
`queen-editor/backend/features/producers/domain/model_groups.py`,
`queen-editor/queeneditor.ipynb`,
`queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx`,
`queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`,
`queen-editor/frontend/dist/**`,
`docs/superpowers/roadmaps/2026-09-11-queen-editor-v5-roadmap.md`.
