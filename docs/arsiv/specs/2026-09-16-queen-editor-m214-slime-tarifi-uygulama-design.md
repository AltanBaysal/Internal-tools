# Madde 214 · Slime girl — uygulama turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Test turu:**
[tasarım](2026-09-16-queen-editor-m214-slime-tarifi-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Testler `bfd410b6`'de kırmızı duruyor. Bu tur onları yeşile çeviriyor: 21 backend, 32 ön yüz.

## Tarif nerede yazılı

**Ad ve LoRA dizilimi uygulamada, adres ve boyut defterde.** Grafiği yamayan taraf ne yazacağını
bilmek zorunda; indiren taraf nereden alacağını. İkisini bir test eşitliyor
*(`test_every_recipe_the_app_knows_has_a_checkbox_of_its_own`)*, yani biri ötekini geçerse takım
durur.

Yeni modül: `backend/features/photo_generation/domain/recipes.py`

```
RECIPES = [{id, label, checkpoint, loras: [{lora, strength}], trigger}, ...]
```

| id | label | checkpoint | loras | trigger |
|---|---|---|---|---|
| `nova3dcg` | Nova 3DCG XL | `nova3DCGXL_ilV90.safetensors` | USNR 0.8 | — |
| `novaorange` | Nova Orange XL | `novaOrangeXL_rexV10.safetensors` | USNR 0.8 | — |
| `novaanime` | Nova Anime XL | `novaAnimeXL_ilV190.safetensors` | USNR 0.8 | — |
| `slime` | Slime | `nova3DCGXL_ilV90.safetensors` | `translucent_penetration_v5` **0.9** | `translucent penetration` |

İlk üçünün LoRA'sı grafiğin bugünkü hâliyle aynı — tarif seçmek bugünkü çıktıyı değiştirmiyor,
yalnız onu adlandırıyor.

## Liste nereden geliyor

`QE_PHOTO_RECIPES` → [config.py](../../../queen-editor/backend/config.py) → `main.py` →
`list_models(generator, chosen)`.

- `chosen` **doluysa**: o kimliklerin tarifleri, **defterin sırasıyla**, `{"value": "recipe:<id>",
  "label": <label>}`. Tanınmayan kimlik atlanıyor ve ötekileri düşürmüyor — depo defterin gerisinde
  kalmış olabilir, ve bir bilinmeyen ad yüzünden paneli kapatmak kullanıcının elinden gelmeyen bir
  sebeple olurdu.
- `chosen` **boşsa**: bugünkü davranış — sunucunun checkpoint adları, `value == label`. Depoyu
  defter olmadan koşturan her yer *(yerel geliştirme, testler)* burada.

Ortam değişkeni virgülle ayrılmış kimlik listesi; boşluklar kırpılıyor, boş parçalar atılıyor.

## Üretim

[comfy_photo_generator.py](../../../queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py)
`model` değerini üç türlü okuyor:

| Değer | `45` | `27` | Prompt |
|---|---|---|---|
| `""` | dokunulmuyor | dokunulmuyor | dokunulmuyor |
| `<dosya>.safetensors` | yazılıyor | dokunulmuyor | dokunulmuyor |
| `recipe:<id>` | tarifin checkpoint'i | **tarifin LoRA'ları, ötekiler yok** | tetik varsa başa |

`27`'nin yamanması **tam değişim**: node'un `lora_*` anahtarlarının hepsi siliniyor ve tarifin
listesi `lora_1`'den başlayarak yazılıyor. Ekleme değil değiştirme, çünkü maddenin kendisi bu —
kullanıcı USNR **kapalıyken** beğendi.

Tanınmayan bir `recipe:` kimliği `RuntimeError`. Sessizce normale düşmek, kullanıcının seçtiği şeyin
uygulanmadığını hiçbir yerde söylemeyen bir fotoğraf üretirdi.

`27` yalnız tarif seçilmişken aranıyor; `3/4/40/45`'in bugünkü varlık kontrolü olduğu gibi kalıyor.
Her render için şart koşmak, LoRA yükleyicisi olmayan bir grafiği de kırardı.

## Defter

CONFIG'deki kutular tarif kutusu olur — `PHOTO_NOVA3DCG`, `PHOTO_NOVAORANGE`, `PHOTO_NOVAANIME`,
`PHOTO_SLIME` — ve başlık *"Fotoğraf tarifleri"* olur. Model hücresi iki listeye ayrılır:

- `PHOTO_CHECKPOINTS` — dosya başına bir satır: sürüm kimliği, GiB, ad, etiket.
- `PHOTO_RECIPES` — tarif başına bir satır: anahtar, kimlik, checkpoint adı.

Seçilenlerden `CHOSEN_CHECKPOINTS = sorted({...})` çıkıyor; indirme listesi de `PHOTO_GIB` de onu
okuyor. Nova 3DCG ile Slime birlikte seçilince 7 GiB bir kez iniyor ve bir kez sayılıyor.

`flask_env`'e `"QE_PHOTO_RECIPES"` ekleniyor: seçili tariflerin kimlikleri.

Her iki LoRA da foto grubuyla iniyor *(`CIVITAI_PHOTO`)* — tarif yalnız checkpoint'i seçiyor.

## Ön yüz

- [GeneratePanel.jsx](../../../queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx):
  `<option value={row.value}>{row.label}</option>`; ilk satır `rows[0].value`; *"artık kurulu değil"*
  kontrolü artık **değerlere** bakıyor.
- [PhotoDetail.jsx](../../../queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx):
  `useModels()` ile satırları okuyup kaydedilen değerin etiketini buluyor; bulamazsa kaydedilen
  değeri yazıyor. `.safetensors` kırpması olduğu gibi kalıyor.

`useModels` ve `api.js` değişmiyor: ikisi de ne taşıdıklarına bakmıyor.

## Yol haritası düzeltiliyor

Madde 214'ün satırı bugün *"LoRA'nın WAN 2.2 I2V tabanlı olması ve High + Low çifti gelmesi"* diyor.
Referans bir fotoğraf LoRA'sı çıktı; satır verilen kararla değiştirilecek, ve video tarafına
dokunulmadığı yazılacak.

## Bu turda değişmeyen

Grafik. `workflow_api.json` bugünkü hâliyle kalıyor — `nova3dcg` tarifi zaten onun hâli, ve Slime
grafiği çalışma anında yamıyor.
