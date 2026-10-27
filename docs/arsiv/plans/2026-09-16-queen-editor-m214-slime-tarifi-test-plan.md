# Madde 214 · Slime girl — test turunun planı

**Spec:** [test turu](../specs/2026-09-16-queen-editor-m214-slime-tarifi-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. Testler henüz olmayan iki şeye göre yazılır, ve uygulama turu
onları o hâliyle karşılar:

- `backend/features/photo_generation/domain/recipes.py` → `RECIPES`, kimlikten tarife bakan bir liste.
  Her tarif: `id`, `label`, `checkpoint`, `loras` *(`[{"lora", "strength"}]`)*, `trigger`.
- `list_models(generator, chosen)` → `[{"value", "label"}]`. `chosen` boşsa bugünkü davranış:
  sunucunun checkpoint adları, her biri hem değer hem etiket.

## Adımlar

**1 · `test_photo_usecases.py` — liste (olgular 1–5).** `FakeGenerator` duruyor; değişen yalnız
`list_models`'ın ikinci argümanı ve dönen biçim.

| Test | Kurulum | Ne bekler |
|---|---|---|
| `the recipes the notebook chose are what the panel lists` | `chosen=["nova3dcg", "slime"]` | iki satır, defterdeki sırada, etiketleri `Nova 3DCG XL` ve `Slime` |
| `a recipe the notebook did not choose is not offered` | `chosen=["slime"]`, üretici `nova3DCGXL…` sayıyor | tek satır, `Slime`; Nova yok |
| `a recipe is picked by its id, not by a file name` | `chosen=["slime"]` | `value == "recipe:slime"` |
| `with no recipes named the list is the renderer's own answer` | `chosen=[]` | bugünkü iki ad, `value == label` |
| `an unknown id is dropped and takes nothing with it` | `chosen=["yok", "slime"]` | tek satır, `Slime` |

Dördüncüsü yeşil doğar — bugünkü davranışın çivisi, ve uygulama turunda kırılmaması gereken şey.

**2 · `test_comfy_photo_generator.py` — üretim (olgular 6–13).** `write_graph`'a `27` numaralı node
eklenir *(`Power Lora Loader (rgthree)`, `lora_1` = USNR 0.8 açık)*, çünkü gerçek grafikte o var ve
testin taklidi grafiği yanlış tarif ediyor. `27`'siz grafik yalnız 13. olgunun kurulumu.

| Test | Çağrı | Ne bekler |
|---|---|---|
| `a recipe renders with its own checkpoint` | `model="recipe:slime"` | `45.ckpt_name == "nova3DCGXL_ilV90.safetensors"` |
| `a recipe leaves only its own loras switched on` | aynısı | `27`'de tek açık yuva: `translucent_penetration_v5` @ **0.9**; USNR açık değil |
| `a recipe's trigger opens the prompt` | aynısı, prompt `"kraliçe"` | `3` → `"translucent penetration, kraliçe"`, iki alana birden |
| `a recipe with no trigger leaves the prompt and the negative alone` | `model="recipe:nova3dcg"`, negatif `"blurry"` | `3` → `"kraliçe"`, `4` → `"blurry"` |
| `a bare file name still leaves the loras alone` | `model="başka.safetensors"` | `45` yazılmış, `27` grafikteki hâlinde |
| `no model leaves both the checkpoint and the loras alone` | `model=""` | `45 == "export.safetensors"`, `27` grafikteki hâlinde |
| `an unknown recipe stops the render` | `model="recipe:yok"` | `RuntimeError`, içinde `yok` |
| `a recipe on a graph with no lora loader says which node is missing` | `27`'siz grafik, `model="recipe:slime"` | `RuntimeError`, içinde `27` |

Yedincisi maddenin kalbi: *"Slime seçtim, normal fotoğraf geldi"* sessizliği burada kırmızıya
çevrilir. Sekizincisi `45`'in bugünkü kontrolünün eşi, ama **yalnız tarif seçilmişken** — `27`'yi her
render için şart koşmak tarif kullanmayan bir grafiği de kırardı, ve 11. olgu tam olarak onu tutuyor.

**3 · `test_notebook_installs_the_producer_groups.py` — kurulum (olgular 14–17).** Defter okunur,
çalıştırılmaz; bugünkü `PHOTO_MODELS` testlerinin yerine tarif karşılıkları geçer.

| Test | Ne bekler |
|---|---|
| `every recipe the app knows has a checkbox of its own` | CONFIG'deki `PHOTO_*` kutuları ile `RECIPES` kimlikleri birebir aynı küme |
| `an unticked recipe costs no bytes` | `PHOTO_RECIPES` satırları kendi anahtarıyla süzülüyor |
| `two recipes sharing a checkpoint fetch it once` | indirme listesi ve `PHOTO_GIB` dosya adına göre tekilleniyor |
| `the app is told which recipes the notebook chose` | `"QE_PHOTO_RECIPES"` `flask_env`'de |

Birincisi iki listeyi birbirine bağlayan yer: ad ve LoRA dizilimi uygulamada, sürüm kimliği ve boyut
defterde — ve bir kimlik bir tarafta olup ötekinde olmazsa ya indirilemeyen bir satır ya da
kapatılamayan bir indirme doğar. Bugün aynı işi checkpoint'ler için
`test_every_photo_model_has_a_checkbox_of_its_own` yapıyor; o test tariflere taşınıyor.

**4 · `test_producers.py` — olgu 18.** `test_the_photo_group_carries_everything_the_graph_reads`
beklenen satır listesine `("loras", "translucent_penetration_v5.safetensors")` eklenir. Bu yeşile
dönünce `test_every_file_the_panel_counts_is_fetched_by_the_notebook` defteri de zorlar *(olgu 19)*.

**5 · `GeneratePanel.test.jsx` — ön yüz (olgular 20–22).** `MODELS` sabiti nesne listesine döner
*(`{value, label}`)*.

| Test | Ne bekler |
|---|---|
| `shows the recipe labels and sends the values` | `<option>` metinleri etiketler, seçilen değer `onGenerate`'e `model` olarak gider |
| `falls back to the first row when nothing was saved` | ilk satırın **değeri** seçili |
| `keeps a saved pick that is no longer offered, and says so` | değer seçili kalıyor, *"Bu model artık kurulu değil."* görünüyor |

**5b · `PhotoDetail.test.jsx` — kare detayı (olgular 23–24).** Sayfa satır listesini kendi okuyacak
*(`useModels`)*, o yüzden api taklidi `listModels`'ı da taşır ve `open()` yardımcısı satırları
alır.

| Test | Ne bekler |
|---|---|
| `says a recipe by the name it was picked by` | `Model` satırı `Slime`, ve ekranda `recipe:` geçmiyor |
| `falls back to what the frame stored when the row list is not there` | satır listesi boşken kaydedilen değer yazıyor |

**6 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: **queen-editor'ün iki takımı kırmızı**, queen-agent'ın ikisi yeşil *(bu madde onlara
dokunmuyor)*. Kırmızıların hepsi yukarıdaki olgular olmalı — başka bir yerin kırmızıya dönmesi, bu
turun kapsamı dışına taştığı anlamına gelir.

**7 · Kırmızı commit'lenir.**

## Değişen dosyalar

`queen-editor/backend/tests/test_photo_usecases.py`,
`queen-editor/backend/tests/test_photo_routes.py`,
`queen-editor/backend/tests/test_comfy_photo_generator.py`,
`queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`,
`queen-editor/backend/tests/test_producers.py`,
`queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx`,
`queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`.
