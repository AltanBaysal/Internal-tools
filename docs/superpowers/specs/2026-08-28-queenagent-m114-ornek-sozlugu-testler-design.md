# Madde 114 — Şemanın örneği model sözlüğüyle yazılır · Tur 1 (testler) tasarımı

**Kaynak madde:** [v5 yol haritası, Blok 8, Madde 114](../plans/2026-08-25-queenagent-v5-roadmap.md)

## Neyi tarif ediyoruz

Şema biçimi iki yoldan öğretiyor: 7. kural artikeli yasaklıyor, düzyazı da *"The example is the
measure"* diyor. İkisi çelişiyor — örneğin ikinci karesi `standing by **the** window` yazıyor,
kamera düzyazısı `from **the** side`, ve bir kamera değeri hiç tag değil: `from slightly above`.
Zayıf model kuralı değil örneği kopyalıyor; üçüncü denemenin `sitting on the couch`, `on the bed`,
`walking together in the park` değerleri buradan geliyor.

Ölçü dışarıdan: SDXL rehberlerinin kuralı *"Avoid natural sentences and articles"*, açı tag'leri de
`from side` / `from above` / `from behind`. Kaynaklar yol haritasının Blok 8 girişinde.

## Dört pin

**1 · Süpürme — örnekteki hiçbir değer artikel taşımaz.** Tek tek kelime aramak yerine örnek
bloğundaki bütün değerler taranıyor: JSON bloğu kesiliyor, `: "…"` kalıbındaki her değer `the` /
`a` / `an` için sınanıyor. Bu maddenin asıl sebebi zaten kaçmış tek bir artikel *(109 örneğe ikinci
kareyi eklerken girmiş)*, ve bir sonrakini yakalayacak şey hafıza değil süpürme. Reponun kendi
idiomu: `test_the_schema_never_calls_a_frame_a_shot` de böyle çalışıyor.

**2 · Örnekteki iki kamera değeri birebir.** `"medium shot, from above"` ve `"upper body, from
side"`. Kamera değeri prompta olduğu gibi giriyor, yani örnekteki yazım doğrudan çıktının yazımı.

**3 · Kamera sözlüğü düzyazıda da tag.** `from side, from above, from behind` sırası duruyor ve
`from the side` metinde hiç geçmiyor. Düzyazı bir sözlük sayıyor; sözlük yanlış yazılırsa örnek tek
başına kalır.

**4 · Artikelin düştüğü söyleniyor.** Biçim paragrafı bugün *"short comma-separated fragments --
tags and brief phrases"* diyor; zayıf model *"brief phrases"*'i okuyup `sitting on the couch`
yazıyor. Yeni cümlenin pini `an article is not a tag`. 7. kural "articles" kelimesini zaten
taşıdığı için pin ayırt edici bir öbeğe basıyor — yoksa kırmızı doğmadan yeşil olurdu.

## Bilerek pinlenmeyen

- **`cowboy shot` yok.** Gerçek danbooru tag'i, ama "shot" süpürme pinini gevşetmek gerekirdi ve
  `medium shot` çalışıyor *(kullanıcı onayı, 28 Ağustos)*.
- **Karakter değerlerinin üslubu.** `in her mid 20s` kullanıcının çalışan promptundan geliyor
  *(araştırma belgesi §5c)*; süpürme onu artikel saymıyor, doğru.
- **Kalite zinciri.** Nova'nın sayfası başka bir zincir öneriyor; `DEFAULT_QUALITY` ancak
  kullanıcının sözüyle değişir, bu maddenin dışında.

## Görülür hâli

Dört kırmızı: süpürme `by the window`'da, kamera pini iki değerde, sözlük pini `from the side`'da,
cümle pini hiç yazılmamış öbekte. Ön yüz değişmiyor, `dist` derlenmiyor.
