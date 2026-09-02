# Madde 140 · Üçüncü model — Tasarım *(iki tur birden)*

**Kaynak:** [v6 yol haritası](../plans/2026-09-01-v6-roadmap.md), Madde 140
**Önceki turlar:** `92e0eea` · `8a2f88b` · `4d8af7f` · `95a9ff4`
**Dal:** `feat/v6`

## Ne ekleniyor

Üçüncü foto modeli: **[Nova Anime XL IL v19.0](https://civitai.com/models/376130/nova-anime-xl)**,
Civitai version id `2940478`, dosya `novaAnimeXL_ilV190.safetensors`, 6.46 GiB fp16.

Şartı tutuyor ve bu ölçüldü: Civitai API'si **onüç sürümünün onüçünde de** `baseModel: Illustrious`
diyor. Yani bugünkü grafik, bugünkü yükleyici, bugünkü CLIP; `BREAK` ve USNR LoRA dokunulmadan
çalışıyor.

Kutusu `PHOTO_NOVAANIME`, boş geliyor, ve kontrole adı giriyor.

## Neden bu tasarımın sınavı zaten yazılı

Bir önceki tur mekanizmayı **sayıdan bağımsız** kurdu, ve üç test onu üç ayrı yerden zorluyor:

| Test | Üçüncü model eklenince ne yapar |
|---|---|
| `..._has_a_checkbox_of_its_own` | kutu var satır yok *(ya da tersi)* → kırmızı |
| `..._comes_switched_off` | kutu açık gelirse → kırmızı |
| `..._without_a_model_stops_the_notebook` | kontrole adı yazılmazsa → kırmızı |

Yani üçü de **bekçi**, ve bu turda kırmızıya dönmemeleri gerekiyor — dönerlerse ekleme eksik
yapılmış demektir.

Bugün olmayan tek şey **modelin adını söyleyen iddia.** `test_the_notebook_offers_both_photo_models`
iki adı sayıyor; üçüncüsünü bilmiyor. Kırmızı orada doğuyor.

## Bu yüzden test turu tek bir kırmızı

Testin adı da düzeliyor — *"both"* iki modelde doğruydu, üçte değil:
`test_the_notebook_offers_every_photo_model`.

Bir liste hâline getirilip döngüyle sayılması da düşünüldü ve **seçilmedi**: o zaman test
`PHOTO_MODELS`'ın kendisini okur ve *"listede ne varsa o vardır"* der — kendini doğrulayan, hiçbir
şey söylemeyen bir iddia. Adlar burada elle yazılıyor, çünkü bu testin işi defterin **hangi**
modelleri indirdiğini dışarıdan çivilemek.

## Kapsam dışı

- **`model_groups.py`, üretici, grafik, ön yüz, `dist`** — bir önceki turda olduğu gibi.
- **Panelin yalanı** — `nova3DCG` kutusu boşken **Üreticiler** panelinin *"kurulu değil"* demesi.
  Bilerek taşınıyor, yol haritasında ve defterin kendi metninde yazılı, ayrı bir maddenin işi.
- **Grafiğin CFG'si** — 28 adım / CFG 6 sabit; üç modelin de kendi önerisi farklı olabilir.

## Colab'da görülecek

Foto kutusu ve üç model kutusu işaretli bir Run all: indirme özetinde `checkpoints/` altında **üç**
dosya, arayüzün **Model** listesinde **üç** satır. Disk `2 + 7×3 = 23` GiB sayar, yani 28 GiB boş
alan ister — T4'te dar, ve defter yetmezse gerçek sayılarla durur.
