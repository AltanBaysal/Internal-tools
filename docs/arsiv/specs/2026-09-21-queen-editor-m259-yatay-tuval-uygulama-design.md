# Madde 259 · Birleşik export yatay tuvale geçiyor — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m259-yatay-tuval-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**Tuval iki sabit oluyor:** `MERGED_WIDTH = 1920`, `MERGED_HEIGHT = 1080`. Kullanıcının kararı
*(260 düştü: "1080 otomatik olsun")*, ve **koda yazılıyor** çünkü artık devralınan bir sayı değil.

**`DISCLAIMER_WIDTH` siliniyor.** Disclaimer tuvalin tam genişliğini kaplıyor, yani oran 1.0 —
ve 1.0 ile çarpan bir sabit, okuyana aramaya değer bir şey varmış gibi görünür.
`scale={MERGED_WIDTH}:-1` zaten söylediği şeyi söylüyor.

**`DISCLAIMER_MARGIN` kalıyor, ölçtüğü şey değişiyor** — tuvalin yüksekliğinin %4'ü, yani 43
piksel. Oran olarak kalıyor çünkü kural o: *dibe yapışan yazı telefonda oynatıcı çubuğunun altında
kalıyor.* Tuval bir gün değişirse pay kendiliğinden doğru kalır.

**`_stamp_for(width, height)` argümanlarını kaybediyor ve `_stamp()` oluyor.** Zincir artık
kaynağın ölçüsünden hiçbir şey hesaplamıyor: sabit bir metin. İki işi var ve ikisi tek
`filter_complex` okumasında olmak zorunda — birleşmiş görüntüyü tuvale **sığdırmak**, sonra
disclaimer'ı üstüne koymak:

```
[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[c];
[1:v]scale=1920:-1[d];
[c][d]overlay=(W-w)/2:H-h-43:enable='lt(t,60)'[v]
```

**`decrease` seçildi, `increase` değil:** ilki oranı koruyarak tuvale **sığan** en büyük ölçüyü
verir, ikincisi tuvali doldurur ve taşan yeri kırpar. Kullanıcının sözü *"sığdır"*, ve bir karenin
üstünü altını kesmek FOUNDATION 1'in *"kullanıcının işi kutsaldır"*ına girer — bant, kaybolan
görüntüden iyidir. Kullanıcı bantları görüp kabul etti.

**`merge()` iki satır kaybediyor:** ölçüyü parçadan söken satır ve onu zincire geçiren argüman.

**Farklı ölçülerin mesajı düzeliyor.** Cümle *"ikisini birden sığdırmak da kırpmak ya da bant
koymak olurdu"* diyordu; bu maddeyle bant koymak tam olarak yaptığımız şey. Yerine duran gerçek
sebep yazılıyor: **`concat` parçaları olduğu gibi okuyor, ölçü değiştirmiyor** — iki farklı ölçüyü
tek akış olarak okuyamaz. Kural aynı yerde, gerekçesi doğru. *(Aynı iş 250'de de yapıldı: yanlışa
düşmüş bir mesaj, kodun kendisinden uzun yaşar.)*

**`ffprobe` kalıyor**, ve sebebi daralıyor: ölçü artık bindirme için değil, yalnız bu red için
soruluyor. Yorum bunu söylüyor.

## Bunun getirdiği

**Disclaimer ilk kez okunuyor.** PNG `1902 × 98`, tuval 1920 geniş: dosya neredeyse hiç
ölçeklenmiyor ve iki satır yazı ~99 piksel yükseklikte duruyor. `480 × 720` bir tuvalde aynı yazı
384 piksele sıkışıyordu, yani satır başına ~10 piksel — kullanıcının *"okunmuyor"* dediği şey.

**Bedeli, açıkça:** çıkan dosya `1920 × 1080`, yani karelerin `480 × 720`'sinden **2,25 kat** daha
büyük bir çerçeve kodlanıyor. Kodlama zaten yapılıyordu *(bindirme yeni bir görüntü)* ve karta
gidiyor *(253, 257)*; bu madde o işin çerçevesini büyütüyor. Süre ölçülmedi, ve buraya sayı
yazılmıyor — kullanıcının sıradaki export'u söyleyecek.

**Videonun iki yanında bant var.** Dikey bir kareyi yatay bir çerçeveye koymanın kırpmadan başka
yolu yok, ve kullanıcı bunu bilerek seçti.

## Dokunulmayan

`piece()` *(261 — ayrı export kopyalıyor)*, `_encoder()` ve karta sorulan soru *(253, 257)*,
`concat` liste dosyası, sesin `-map 0:a?` ile kopyalanması, `assets/disclaimer.png`, ve
`DISCLAIMER_SECONDS` *(250'nin saati)*.

## Bu turda değişen

- `data/ffmpeg_video_exporter.py`: tuval sabitleri geldi, `DISCLAIMER_WIDTH` gitti, `_stamp_for`
  → `_stamp()`, `merge()` ölçüyü zincire geçirmiyor, farklı ölçü mesajının gerekçesi düzeldi,
  modül başlığı tuvali söylüyor.
