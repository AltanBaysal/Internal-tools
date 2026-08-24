# v14 Görev 37 — Export fotoğrafları da taşır: UYGULAMA döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Kullanıcı, 25 Ağustos
**Öncesi:** [Görev 37 test spec'i](2026-08-25-queen-editor-v14-gorev-37-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 37

## Ne yeşile döndürülüyor

Dört kırmızı test. Üçü alan katmanında: fotoğraf videosunun numarasıyla depoya veriliyor, uzantı
kaynağınki kalıyor, videosuz kare bir şey vermiyor. Biri depoda: aynı hedefe ikinci kopyalama dosyayı
yeniden yazmıyor.

## İki dosya, iki iş

**Alan katmanı** (`run_export.py`) bir şeyi biliyor: hangi kare kaçıncı sırada ve fotoğrafının adı
ne. `photos/` diye bir klasörün varlığından haberi yok — yol kurmak onun işi değil, ve depo bunu
kendi belgesinde zaten söylüyor.

**Depo** (`photo_store.py`) klasörü biliyor ve yazmayı yapıyor.

## Numara ve uzantı

Numara döngünün elinde zaten var: videoyu `01.mp4` yapan sayı fotoğrafı `01.png` yapıyor. İkinci bir
sayaç yok.

Uzantı fotoğrafın kendi dosya adından okunuyor. `.png` koda yazılmıyor — ilk `.jpg` geldiğinde adı
yanlış olan bir dosya çıkardı ve ekranda bunu söyleyen hiçbir şey olmazdı. Adın son noktasından
sonrası alınıyor; nokta yoksa uzantı da yok.

Bu okuma alan katmanında kalıyor: dosya **adı** alanın verisi, dosya **yolu** deponun.

## Yazmanın güvenli olması

Kullanıcının sorduğu durum şu: birleşik ve ayrı export aynı anda koşuyor, klasör ortak, ve ikisi de
`01.png`'den başlıyor. Yani iki iş parçacığının aynı hedefe aynı anda yazması **kenar durum değil,
beklenen durum.**

"Varsa atla" tek başına yetmez: iki taraf da "yok" görüp ikisi de yazmaya başlayabilir, ve tek bir
dosyaya birlikte yazan iki kopyalama yarım dosya demektir.

Bu yüzden iki katman birden:

1. **Varsa atla.** İlk mod bitirmişse ikincisi hiç yazmaz — istenen tasarruf bu.
2. **Yazma atomik.** Kopyalama geçici bir ada yapılır, sonra hedefe taşınır. Taşıma bir anda olur,
   yani hedefte hiçbir zaman yarım dosya bulunmaz. İki taraf da yazsa bile sonuç tam bir dosya.

İkisi olmadan "aynı klasöre iki mod" verilen cevap eksik kalır.

## Fotoğrafı olmayan kare

Videosu olup fotoğrafı olmayan kare sessizce atlanır. Beklenen bir durum değil — video fotoğraftan
üretiliyor — ama `layers` sözlüğünde alan eksik olabilir ve export bunun için durmaz.

**Patlamış fotoğraf için ayrı bir kontrol yok.** Sesin `_audio_of`'taki eşi buraya eklenmiyor:
fotoğrafı patlamış bir kareden video üretilemez, dolayısıyla `exportable()` onu zaten dışarıda
bırakıyor. Eklemek, ulaşılamayan ve test edilemeyen bir dal yazmak olurdu.

## İptal, hata ve sayaç

Üçü de değişmiyor.

Fotoğrafın kopyalanması videonun yazılmasından hemen sonra, aynı adımda duruyor. Kopyalama patlarsa
export patlar ve `remove_dir(folder)` klasörü `photos/` ile birlikte alır — videonun patlamasıyla
aynı davranış. `written`/`total` videoyu saymaya devam ediyor: fotoğraf videosunun yanında gidiyor,
ayrı bir adım değil.

## Kapsam dışı

- **Test dosyaları değişmiyor.** Bir önceki commit'te ne yazıldıysa o kalır.
- **Ön yüz.** Export ekranının özeti video sayıyor ve o cümle değişmiyor.
- **Videosu olmayan karelerin fotoğrafları.** Kullanıcı kararı.

## Derlenmiş çıktı

Bu iş arka yüzde. Ön yüz kaynağı hiç açılmıyor, `dist` tazelenmiyor.
