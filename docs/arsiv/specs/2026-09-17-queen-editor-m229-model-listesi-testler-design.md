# Madde 229 · Model listesi ComfyUI'ye gitmeyecek — test turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Bir sonraki **yalnız video için** açılışta `/content/flask.log`'daki `/api/models` satırı. `502` ile
düştüyse Cloudflare'in HTML sayfası route'un kendi 502'sinin üstüne geçmişti. Hiç düşmediyse Flask o
an cevap vermemişti. **Maddeyi beklemiyor:** karar ikisinde de aynı, ve bu satır yalnız kaydı
tamamlıyor.

## Bugün ne oluyor

[`list_models`](../../../queen-editor/backend/features/photo_generation/domain/usecases/list_models.py)
iki yol taşıyor. Defter tarif seçtiyse satırlar o tarifler. Hiç seçmediyse ComfyUI'ye kurulu
checkpoint'ler soruluyor *(`generator.models()` → `ComfyClient.checkpoints()`)*.

İkinci yol **yerel bir çalıştırma** için yazılmıştı. Ama uygulama yalnız Colab'da koşuyor
*(FOUNDATION, karar 1)*, ve orada tarif listesi boşsa bunun tek anlamı var: **fotoğraf kurulmadı**.
O açılışta soru hiçbir zaman işe yarar bir cevap getirmiyor. Ya boş bir liste getiriyor ya da düşüyor.
Düşünce de `/api/models` 502 dönüyor, ve kullanıcı proje ekranında bir hata kartı görüyor.

## Ne olacak

**İkinci yol tamamen gidiyor.** `list_models` yalnız tarifleri okuyor. Hiç tarif yoksa cevap boş bir
liste, ve bu bir hata değil.

Bu yüzden şunlar da kullanılmaz kalıyor ve siliniyor: `PhotoGenerator.models`,
`ComfyPhotoGenerator.models`, `ComfyClient.checkpoints`. Başka okuyanları yok. Onları tutan testler
de siliniyor.

`/api/models` artık hiçbir dış servise gitmiyor, yani **kendi 502'si de gidiyor**. Tünel ya da Flask
düşerse hata ön yüzün genel `request` yolundan geçer, bugün her istekte olduğu gibi.

## Ekranda değişmeyen, çünkü zaten doğru

- **Kurulu olmadığı söyleniyor.** Yalnız video için açılan defterde fotoğraf üreticisi kurulu
  değil, ve `GeneratePanel` bunu `InstallCard` ile zaten söylüyor. Boş liste de model kutusunda
  *"model bulunamadı"* diye görünüyor. İkinci bir cümle aynı şeyi iki kez söylerdi.
- **Uzun ham çıktı katlanıyor, ve hiçbir şey saklanmıyor.**
  [`RawOutput`](../../../queen-editor/frontend/src/shared/RawOutput.jsx) çıktıyı ~5 satırlık,
  kaydırılabilir bir kutuda gösteriyor, ve *Kopyala* metnin tamamını veriyor. Kullanıcının istediği
  *("hatayı tamamen saklama")* tam bu. Kendi testleri de bunu tutuyor *(`RawOutput.test.jsx`)*.

Bu yüzden ön yüzde **hiçbir dosya değişmiyor**, ve derleme gerekmiyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Hiç tarif seçilmemişse `list_models` boş liste döner | **kırmızı** *(imza değişiyor)* |
| 2 | Seçilen tarifler, defterin sırasıyla satır olur | **kırmızı** *(imza)* |
| 3 | Seçilmeyen tarif sunulmaz | **kırmızı** *(imza)* |
| 4 | Bilinmeyen bir kimlik düşer, kalanları götürmez | **kırmızı** *(imza)* |
| 5 | Tarif yokken `GET /api/models` **200** ve boş liste döner | **kırmızı** *(bugün ComfyUI'ye sorar)* |

2–4 bugün de doğru olan davranışlar. Kırmızıları yalnız yeni imzadan: `list_models(chosen)`,
çünkü artık bir `generator` almıyor.

## Bu turda değişen

Yalnız testler:
- `test_photo_usecases.py`: olgu 1–4, sahte `models()` gider.
- `test_photo_routes.py`: olgu 5, sahte `models()` ve ulaşılamayan-renderer testi gider.
- `test_comfy_photo_generator.py`: `models()` testi ve sahte `checkpoints()` gider.
- `test_comfy_client.py`: iki `checkpoints()` testi gider.
