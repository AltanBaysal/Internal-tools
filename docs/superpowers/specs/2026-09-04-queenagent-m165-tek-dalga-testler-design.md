# Madde 165 — `AT_ONCE` kalkar · **test turu**

**Tarih:** 4 Eylül 2026 · **Branch:** `feat/v7` · **Kaynak:** [v7 yol haritası, Madde
165](../plans/2026-09-03-v7-roadmap.md)

Bu belge yalnız **testlerin** ne çivileyeceğini anlatır. Kodun kendisi ikinci turun işi.

## Neyi çiviliyoruz

`write_frame_prompt` bugün istekleri **beşerli dalgalar** hâlinde atıyor
*(`ThreadPoolExecutor(max_workers=AT_ONCE)`, `AT_ONCE = 5`)*. Beşin gerekçesi m155'in spec'inde
yazılı: *"sağlayıcı dolu havuzda 429 veriyor"*. O cümlenin kaynağı m149'un DeepInfra/OpenRouter
denemesi, ve **o deneme geri alındı** — bugün `config.py`'de yalnız `api.x.ai` ve `api.deepseek.com`
var. Yani sabit, artık hiç kullanılmayan bir sağlayıcının ölçümünü taşıyor.

Kullanıcının kararı *(4 Eylül)*: **"Kaldır — yüzü birden uçsun."**

## İlk istek yine tek başına gidiyor

Kalkan şey dalga, sıra değil. İlk istek hâlâ yalnız çıkıyor ve sebebi 429 değil: **istem ve
haritalar her istekte birebir aynı**, ve hepsi birden çıkarsa hiçbiri sağlayıcının önek önbelleğini
sıcak bulamaz. `test_the_first_request_goes_alone` olduğu gibi kalıyor, ve yeşil kalması bunun
kanıtı.

## Değişen test — `test_tools.py`

1. **`test_no_more_than_five_requests_are_in_the_air`**, yerine
   **`test_every_frame_after_the_first_flies_at_once`** — on iki sahne, biri önden, kalan **on biri
   aynı anda havada**: `writer.at_once == 11`. Bugün 5.

   Kesin sayı isteniyor, *"beşten çok"* değil: tavanın kalkması ile tavanın altıya çıkması aynı
   şey değil, ve testin ölçtüğü şey tavanın **kare sayısına eşitlenmesi**. Ölçülebilir olmasının
   sebebi `ScriptedWriter`'ın 0.01 saniyelik uykusu — on bir iplik doğup işi alana kadar geçen süre
   bunun yanında hiç kalıyor.

2. **`ScriptedWriter`'ın docstring'i** *"the waves"* diyor. Tek dalga kaldı; cümle onu söyleyecek.

## Bu turda dokunulmayanlar

- **`MOST_FRAMES_PER_CALL` / `AT_MOST` = 100** duruyor. Kaç kare yazıldığı ayrı bir soru, ve
  `test_it_stops_at_a_hundred_requests` yeşil kalıyor — 105 sahnenin 100'ü yazılıyor, artık tek
  dalgada.
- **Yeniden deneme yok, ve gelmiyor.** m155'in kararı; bu madde onu değiştirmiyor.
- **Adlandırma düzeltmesi ayrı iş.** `AT_MOST` bu turda adını korur.

## Nasıl kırmızı olacak

Tek `assert`: bugünkü kod on bir isteği beşerli iki dalga artı bir hâlinde atıyor, `at_once` 5'te
kalıyor, ve test 11 bekliyor.

Beklenen: **1 kırmızı**, artı defterin bilinen 2'si.
