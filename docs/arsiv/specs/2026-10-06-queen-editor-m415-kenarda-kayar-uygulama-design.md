# Madde 415 — Kart sürüklenirken galeri kenarda kayar, uygulama turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 415 · v9-7 · **Tur:** 2/2 — kod.
**Testler:** [m415 test turu](2026-10-06-queen-editor-m415-kenarda-kayar-testler-design.md) — kurallar
orada; bu belge yalnız nasıl yapıldığını söyler. `dist`'i birleştirmede koşu kurar.

## Yaklaşımlar

1. **Seçilen — kutu her `dragover`'da kenarı tartar.** Galerinin kaydığı kutu
   [ProjectScreen.jsx](../../../queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx)'in
   `data-scroll` kutusu; sürükleme olayları kutucuklardan ona kabarcıklanıyor. Kutu `onDragOver`'da
   imlecin yüksekliğini kendi kenarlarıyla karşılaştırır, kenara yakınsa bir adım kayar. Durum yok,
   zamanlayıcı yok: kaymayı tarayıcının tekrarladığı `dragover` yürütür, ve sürükleme bitince
   durduracak bir şey kalmaz. Havuz açıkken dinleyici takılmaz.
2. *Elendi —* galerinin içinde, kutunun ref'i prop'la galeriye taşınarak: aynı iş, bir prop ve bir
   ref daha; kutu zaten ekranın, kenarlarını da o bilir.
3. *Elendi —* zamanlayıcıyla sabit hız: imlecin son yeri bir ref'te, `dragstart`'ta kurulan bir
   aralık onu okuyup kaydırır, `drop` / `dragend`'de durur. Hız tarayıcıdan bağımsız olur, ama bir
   başlat-durdur ömrü doğar — ve sürüklenen kutucuk sürükleme sırasında ekrandan kalkarsa (kare başka
   yerden silinir, yoklama listeyi yeniler) `dragend` kutuya ulaşmaz, kutu kaymaya devam eder.

## Nasıl çalışıyor

- **Kenar 80 px, adım 20 px** — kutunun `getBoundingClientRect()`'inin `top`'una ve `bottom`'una göre.
  İmleç `top + 80`'in üstündeyse `scrollTop` 20 azalır, `bottom − 80`'in altındaysa 20 artar, arada
  hiçbir şey olmaz. Tarayıcı `scrollTop`'u kendisi sınırlar: en üstte ve en altta adım boşa gider.
- **Hız tarayıcının `dragover` sıklığından:** HTML'in modeli, imleç dururken de en geç 350 ms ± 200 ms'de
  bir tekrar ister; imleç kıpırdadıkça olay daha sık gelir, kutu daha hızlı kayar. Kullanıcı koşunun
  sonundaki denemesinde yavaş ya da hızlı bulursa değişen tek sayı adım.
- **Kart dışında bir şey:** kutu, galerinin üstündeki her sürüklemede kenarı tartar — galeride
  sürüklenebilen tek şey kart. Masaüstünden galerinin üstüne getirilen bir dosya da kenarda kaydırır;
  galeri dosya almaz, kayma bir şey bozmaz.
- **`preventDefault` yok:** kutu bırakma yeri olmaz; bırakma yerini bugünkü gibi kutucuklar açar.
- **Havuz açıkken** `onDragOver` `undefined` — havuzun satırları bugünkü gibi.

## Dosyalar

### `frontend/src/features/photo_generation/ProjectScreen.jsx`

- Modülün üstünde iki sabit (`EDGE = 80`, `STEP = 20`) ve bir işlev, `scrollAtEdge(event)`:
  `event.currentTarget` kutunun kendisi.
- `data-scroll` kutusuna `onDragOver={poolShown ? undefined : scrollAtEdge}`.

Başka dosya değişmez — `Gallery.jsx`, `ReferencePanel.jsx`, `useKeptScroll.js` olduğu gibi.

## Doğrulama

Dört satır: `queen-editor` vitest'inde test turunun beş testi yeşil, öteki her şey yeşil. Ekranda:
kutu kenara yakın sürüklenen kartla kayıyor, en üstteki kart en alta bırakılabiliyor — Playwright'la
ve kullanıcının son denemesinde.
