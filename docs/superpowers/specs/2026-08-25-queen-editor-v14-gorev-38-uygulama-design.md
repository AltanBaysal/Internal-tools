# v14 Görev 38 — Açık sekme kareler arasında yerinde kalır: UYGULAMA döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Kullanıcı, 25 Ağustos
**Öncesi:** [Görev 38 test spec'i](2026-08-25-queen-editor-v14-gorev-38-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 38

## Ne yeşile döndürülüyor

Bir kırmızı test: sonraki karede de video varsa sekme yerinde kalıyor. Yanındaki tutucu yeşil
kalmalı: sonraki karede video yoksa fotoğrafa düşüyor.

## Değişikliğin şekli

Kare değişiminde koşan effect bugün sekmeyi koşulsuz sıfırlıyor:

```jsx
setOpen("photo");
```

Yarın aynı satır soruyor: gelen karede bu katman var mı?

```jsx
setOpen((shown) => (has[shown] ? shown : "photo"));
```

Tek satır. Effect'in sıfırladığı diğer beş şey — hata kartı, açık pencere, meşguliyet, yazılmış
prompt, basılmış düğmeler, üretim modu kutusu — olduğu gibi kalıyor. Onlar gerçekten kareye ait.

## Kural katman adı sormuyor

Yazılan şey "video kalsın" değil, "sekmenin gösterdiği şey bu karede var mı". Ses sekmesi için de
aynı satır çalışıyor, ve ileride dördüncü bir katman gelirse onun için de.

## `has` neden bu effect'in içinde doğru

`has`, `frame`'den türüyor ve `frame` her render'da `fid`'den hesaplanıyor. `fid` değiştiğinde
React önce yeni kareyle bir render yapıyor, effect ondan sonra koşuyor — yani effect'in gördüğü
`has` **gelen karenin**, gidenin değil.

Effect'in bağımlılığı `[fid]` olarak kalıyor. Sekme yalnız kare değiştiğinde sorulacak bir soru;
`has` bağımlılığa eklenirse her poll'de yeniden koşar ve kullanıcının açtığı sekmeyi kendi altından
çekebilir.

## Fonksiyonel güncelleme neden

`setOpen(has[open] ? open : "photo")` de yazılabilirdi. Fonksiyonel biçim seçiliyor çünkü effect'in
okuduğu `open`, o render'ın kapanışından geliyor ve aynı effect içinde başka setState'ler de var;
güncel değeri React'ten istemek, sıraya bağlı olmayan tek okuma.

## Bekleyen katman

Gelen karenin videosu kuyruktaysa `has.video` yine doğru — sekme var ve ne olduğunu söylüyor. Sekme
açık kalıyor ve sayfa "video üretiliyor" diyor. Doğrusu bu: kullanıcı videoya bakıyordu, sekme
duruyor, ve neden henüz oynatılamadığını sayfa söylüyor.

## Yorum düzeltiliyor

Effect'in üstündeki yorum bugün sekmenin de kareyle gittiğini söylüyor. Sekme artık gitmiyor; koda
uydurulur (CLAUDE.md).

## Kapsam dışı

- **Test dosyası değişmiyor.** Bir önceki commit'te ne yazıldıysa o kalır.
- **Videonun kendiliğinden oynaması.** Sekme yerinde kalacak ama oynatıcı duraklamış başlıyor.
  Ayrı bir soru ve kullanıcı kararına bırakıldı.
- **Katman silindiğinde fotoğrafa dönüş.** `handleDeleteLayer`'ın kendi `setOpen("photo")`'su ayrı
  bir yol ve değişmiyor: orada katman gerçekten gitti.

## Derlenmiş çıktı

Ön yüz kaynağı değiştiği için `dist` aynı commit'e girer (CLAUDE.md). Defter derlemiyor; itilmemiş
bir `dist` Colab'da görünmez.
