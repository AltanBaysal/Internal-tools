# v14 Görev 38 — Açık sekme kareler arasında yerinde kalır: TEST döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Kullanıcı, 25 Ağustos
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 38

## Sorun

Detay sayfasında video izlenirken oklarla sonraki kareye geçilince sekme fotoğrafa düşüyor. Sonraki
karede video olsa bile. Bir dizi videoyu sırayla izlemek, her karede sekmeyi yeniden seçmek demek.

Sebebi `PhotoDetail`'in kare değişiminde altı şeyi birden sıfırlayan effect'i. İçinde sekme de var
ve gerekçesi kendi yorumunda yazılı: sonraki karede o katman yoksa, olmayan bir sekme açık kalırdı.

Kaygı gerçek, çare fazla geniş: katman **varken** de düşürüyor.

## Ne test ediliyor

Sekme kareyle birlikte gitmiyor. Sonraki karede o katman varsa yerinde kalıyor; yoksa fotoğrafa
düşüyor.

Bu döngüde **kod değişmiyor.** Testler yazılır, kırmızı görülür, kırmızı commit'lenir.

## Kuralın katman adı sormaması

Kural "video sekmesi kalsın" değil, "bu karede bu katman var mı" — yani ses sekmesi için de aynı
şekilde çalışıyor. İkinci bir test yazılmıyor: aynı satırı ikinci kez sınamak olurdu, ve testin
söylediği şey zaten katman adı geçmeyen bir cümle.

## Neden bugün hiçbir test bunu tutmuyor

Sekmenin sıfırlandığını iddia eden bir test yok. Kareler arası geçişi sınayan tek test prompt
kutusunu anlatıyor, ve geçtiği kare (`SECOND`) videosuz — yani o test bu değişiklikten sonra da
yeşil kalıyor, çünkü videosuz bir kareye geçmek zaten fotoğrafa düşmek demek.

Bu yüzden yeni bir sabit gerekiyor: **videosu olan bir ikinci kare.** Bugünkü fixture'ların hiçbiri
bu değil.

## Yazılacak testler

İkisi de `PhotoDetail.test.jsx`'in *the layer tabs* bloğunda.

| | Test | Bugün |
|---|---|---|
| 1 | Sonraki karede de video varsa sekme yerinde kalıyor | **kırmızı** |
| 2 | Sonraki karede video yoksa fotoğrafa düşüyor | yeşil — tutucu |

Tutucu 2 boşuna değil: sıfırlamanın var oluş sebebi o, ve sekmeyi yerinde tutarken onu düşürmek,
karede olmayan bir katmanın sekmesini açık bırakmak olurdu.

## Bilerek test edilmeyen

Effect'in geri kalanı — prompt kutusu, basılmış düğmeler, hata kartı, üretim modu kutusu. Dördü de
kareye ait, dördü de sıfırlanmaya devam ediyor, ve prompt kutusunun kendi testi zaten var.

## Kapsam dışı

- **Videonun kendiliğinden oynaması.** Sekme yerinde kalacak ama oynatıcı duraklamış başlıyor.
  Ayrı bir soru ve kullanıcı kararına bırakıldı.
- **Kod.** Bu döngü yalnız test.

## Derlenmiş çıktı

Bu döngüde ön yüz **kaynağı** değişmiyor, yalnız test dosyası. `dist` tazelenmiyor.
