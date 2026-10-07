# Madde 286 · Parçaların ses akışı — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m286-parca-sesi-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**`sound(video)` geliyor** — `size()`'ın kardeşi, ve onun gibi tek soru soruyor:
`ffprobe -select_streams a:0 -show_entries stream=sample_rate,channel_layout`. **Boş cevap bir
cevap:** sesi olmayan dosya boş satır döndürüyor, ve dönen şey `None`. Sesi olan dosya
`(hız, kanal_düzeni)` döndürüyor.

**İki ayrı probe, tek soru başına** — `size()` ölçüyü, `sound()` sesi. Tek bir çağrıda ikisini
birden istemek mümkün *(bütün akışları listeleyip ayıklamak)* ama o çağrının cevabı ayıklanmak
zorunda, ve **iki basit soru bir karmaşık sorudan iyi** *(FOUNDATION 3: doğruluk > sadelik >
performans)*. Bedeli parça başına bir ffprobe daha, yani 22 karelik projede 22 küçük çağrı —
dakikaların yanında ölçülemez, ve bu maddenin işi hız değil doğruluk.

**Kural `merge()`'te, tek cümle:** parçalardan birinin sesi varsa hepsinin olmalı. Kod da öyle
okunuyor — sesi olan ilk parçanın ölçüsü alınıyor, sesi olmayanların yanına o ölçüde sessizlik
yazılıyor, ve `concat` listesine yeni dosya giriyor.

**Sessizliği yazan komut:**

```
ffmpeg -y -i <parça> -f lavfi -i anullsrc=r=<hız>:cl=<düzen>
       -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest <parça>-sound.mp4
```

`-c:v copy` — **videonun tek karesi bile yeniden kodlanmıyor**, eklenen şey yalnız bir ses akışı.
`-shortest` olmazsa `anullsrc` sonsuza akar ve dosya hiç bitmez.

**Yeni dosyanın adı `<parça>-sound.mp4`**, yani parçanın yanında: `/tmp`'deki parçalar klasöründe
*(235)*, ve `run_export` o klasörü zaten silip gidiyor. Drive'a bu maddeden hiçbir şey girmiyor.

**`piece()` dokunulmuyor** *(261 yerinde)*, ve ayrı export'un tek karesi bile değişmiyor:
`merge()` yalnız birleşik modda çağrılıyor.

## Tek düzenli setlerde hiçbir şey olmuyor

Kodun şekli bunu kendiliğinden veriyor: sesi olmayan parça listesi boşsa yazacak bir şey yok, ve
**hiçbirinin sesi yoksa** *(yaygın WAN projesi)* örnek de yok — o sette `-map 0:a?` zaten iş
görüyor. İki bekçi test bunu tutuyor.

## Kapsam dışı, ve bilerek

**Kodek uyuşmazlığı** — iki sesli parça farklı kodekte olabilir *(bizim yolumuz aac, H3'ün kendi
sesi kaynağın kodeki)*. Belirti yok, ve düzeltmesi her parçanın sesini yeniden kodlamak olurdu:
bedeli gerçek, sebebi varsayım *(FOUNDATION 3)*. Bu madde varlık/yokluk farkını kapatıyor — koddan
okunabilen tek kesin fark.

## Bu turda değişen

- `data/ffmpeg_video_exporter.py`: `sound()` geldi, `merge()` sesi de soruyor ve karışık sette
  sessizlik yazıyor.
