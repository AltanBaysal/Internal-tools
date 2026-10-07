# Madde 111 — Kamera tek tipten çıkar · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m111-kamera-testler-design.md) — iki kırmızı
`19f082e`'de.

## Şema — kameranın iki yarısı

`camera` alanının ne olduğu düzyazıda yazılır: **ne kadarı görünüyor** *(close-up, upper body,
medium shot, full body)* ve **nereden bakılıyor** *(from the side, from above, from behind,
looking at viewer)*. Etiketler örnek olarak veriliyor; kapalı bir liste değil, ve kod hiçbirini
tanımıyor — ne yazıldıysa onu basıyor.

Yer: biçim paragrafının hemen ardı, `camera`'nın ilk kez tarif edildiği yerin yanında.

## prompt+ — çeşitlilik kuralı

Craft paragrafına: kamera her sahne için ayrıca seçilir; **aynı kadraj ve açıyı** taşıyan komşu
kareler aynı resmi iki kez okutur, o yüzden komşu kareler **en az birinde** ayrışır. Kural bir
rotasyon dayatmıyor — sahne neyi istiyorsa o, ama tekrar tesadüf olmaktan çıkıyor.

## Değişmeyen

Kod *(`build_prompts` kamerayı olduğu gibi basar)*, şemanın örneği *(109'un getirdiği iki kamera
zaten iki farklı kadraj)*, ve *"shot"* süpürme testleri — yeni metinlerde kelime yalnız
`medium shot` olarak geçiyor.

## Görülür hâli

İki kırmızı yeşerir, başka test kırılmaz *(defter çifti hariç)*. Ön yüz değişmiyor.
