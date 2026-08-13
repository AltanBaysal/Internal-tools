# Görev 11 — Durum yazısı okunur olsun

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 4

## Sorun

"foto kuyrukta" okunmuyor. Etiket 9 piksel, rengi paletin en soluk üçüncü tonu (`--ink-3`,
`#6a6a70`) ve zemini fotoğrafın üstündeki yarı saydam koyu bir çip. O boyutta, o zeminde, o ton
sessiz bir etiket değil, okunmayan bir etiket.

Diğer iki durum bu sorunu yaşamıyor: üretiliyor vurgu rengiyle, hata tehlike rengiyle yazılıyor —
ikisi de parlak. Sorun yalnız bekleyen durumda, ve orada da renk sebebiyle.

## Kararlar

1. **Bekleyen durum paletin en açık mürekkebiyle yazılır** (`--ink`). Kullanıcının istediği bu, ve
   9 pikselde doğru olan da bu: küçük yazı, sesini renkten değil boyuttan zaten kaybediyor.
2. **Çip biraz daha örter.** Zemin, altındaki fotoğraf ne olursa olsun yazıyı taşımak zorunda;
   parlak bir karenin üstünde yarı saydam koyu bir çip yeterince koyu değil.
3. **Diğer iki durumun rengi değişmez.** Onlar okunuyor ve renkleri anlam taşıyor.
4. **Karonun altındaki dosya adı değişmez.** O, düz zemin üzerinde ve daha büyük; sessiz olması
   kasıtlı.

## Testler

- Bekleyen durumun etiketi en açık mürekkeple yazılıyor.
- Üretiliyor ve hata durumlarının renkleri olduğu gibi kalıyor.

## Öz eleştiri

- *En açık ton, etiketi fotoğraftan daha baskın yapmaz mı?* — Yapmaz: etiket 9 piksel ve küçük bir
  çipin içinde. Baskınlığı boyut belirliyor, ton yalnız okunurluğu.
- *Kontrastı ölçtük mü?* — Ölçüldü: `#6a6a70` neredeyse siyah bir zeminde 9 pikselde okunmuyor,
  `#ececee` aynı zeminde rahat okunuyor. Bunu teste çevirmek renk hesabını ön yüze taşımak olurdu;
  test, verilen kararın uygulandığını sabitliyor.
