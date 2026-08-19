# Madde 54 · Tur 1 (test) — Tasarım

**Madde:** [v4 yol haritası Madde 54](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Bu belgenin konusu:** `dist`'in commit'lendiğini **ne tutacak**. Kuralın kendisi değil — o bir
sonraki turun konusu.

---

## Tutulacak kural

Defter bu depoyu klonluyor ve **hiç derlemiyor**. Yani derlenmiş arayüz depoda yoksa, karşı tarafa
boş bir sayfa olarak varıyor — ve boş sayfa sebebini söylemez.

## Testin sorması gereken soru

**"Diskte var mı" diye sorulmaz.** Dosyalar `npm run build` çalıştığı an diskte oluyor, yani
`os.path.exists` kimsenin sormadığı bir soruya "evet" der ve kuralı hiç tutmaz. Sorulacak olan
**commit'lenmiş mi** — ve bunu yalnızca git bilir.

Bu, testi bir alt sisteme değil depoya bakan bir test yapıyor. Kabul ediliyor: kural da depo
hakkında. queen-editor'ün defter testi de aynı cinsten — çalıştırmadan, dosyayı okuyarak sorar.

## İki soru, çünkü iki ayrı hata var

**1. Hiç commit'lenmemiş.** En kaba hâli: `dist` yok sayılıyor, git hiçbirini taşımıyor.

**2. Sayfa commit'lenmiş, istediği dosya unutulmuş.** Asıl sinsi olan bu. `index.html` bundle'ını
kendi içeriğinin hash'iyle adlandırıyor (`index-D3JKzVAq.js`), yani **her derleme onu yeniden
adlandırıyor**. Sayfayı ekleyip yeni asset'i unutmak, açılan ama sonra var olmayan bir dosya isteyen
bir sayfa bırakır. Birinci test bunu yakalamaz — `index.html` orada çünkü.

İkincisi hash'e bağlı olmadan sorulmalı: sayfanın **kendi istediği** yollar okunur, sonra her biri
git'e sorulur. Böylece test her yeni derlemede geçerli kalır.

## Sınır

Testin cevaplamadığı şey: bundle'ın **güncel** olup olmadığı. Kaynağıyla aynı commit'te derlendiği
ucuz ve kesin biçimde sorulamaz — hash yalnız bundle'ın kendi içeriğini özetliyor, kaynağı değil.
Bu bilerek dışarıda: yanlış bir "güncel" cevabı, hiç cevap vermemekten kötü.

## Bilerek yapılmayan

- queen-editor'ün `dist`'i için test yok. Bu madde queen-agent hakkında, ve orada kural zaten
  yürüyor.
- Frontend takımına bir şey eklenmiyor: soru git'e sorulacak, ve git'i vitest'ten sormak için bir
  sebep yok.
