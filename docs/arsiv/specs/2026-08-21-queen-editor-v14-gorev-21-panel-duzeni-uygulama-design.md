# v14 · Görev 21 — Sağ panelin düzeni · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-21-panel-duzeni-testler-design.md) ·
kırmızı commit `c2e6d0d` (494 testin 12'si kırmızı).

İki dosya: `PhotoDetail.jsx` ve `glyphs.jsx`. Bu maddede sütun ekleyerek değişiyor — dördü de bir
şeyin *olmamasından* doğan farklar.

## 1 · Kopya ikonu

`glyphs.jsx`'e `CopyGlyph` giriyor — evin kendi dili: 14×14 kutu, `currentColor`, 1.4 yuvarlak
çizgi, `data-glyph` kimliği. Vendor kitinde kopya ikonu yok ve oraya yazılmıyor: `vendor/` tasarımın
kendi dosyalarının birebir kopyası.

`PhotoDetail.jsx`'e iki küçük bileşen giriyor:

**`CopyButton`** — `RawOutput`'un pano çağrısının aynısı. Yazma **basıştan doğrudan** çağrılıyor,
bir mikro görev sonrasından değil: pano bir kullanıcı hareketine veriliyor ve bir tık geç gelen
yazmayı tarayıcı reddedebilir. `try` öteki yarısı için — pano nesnesi hiç yoksa çağrı olduğu yerde
patlar, izin reddedilirse söz reddedilir, ve kullanıcının iki durumda da aynı cevaba ihtiyacı var.

Cevap ikonun **erişilebilir adı**: 2,5 saniye "Kopyalandı" ya da "Kopyalanamadı", ve o süre boyunca
vurgu ya da tehlike rengi. Boş kutuda `disabled` ve silik.

**`BoxLabel`** — başlık satırı: solda etiket, sağ uçta ikon. İki prompt kutusu da bunu kullanıyor,
yani başlık satırı tek yerde tarif ediliyor.

> **Not:** buradaki `space-between` satır içi bir hizalama. Tasarımın geri aldığı `space-between`
> denemesi sütunun kendisiyle ilgiliydi — grupları dikeyde birbirinden itmek — ve o hâlâ
> yapılmıyor.

## 2 · Kutular kendi ölçüsünü alıyor

```js
const PROMPT_HEIGHT = { photo: 162, video: 150, audio: 150 };
const NEGATIVE_HEIGHT = 96;
```

`TextBlock` ve `PromptBox` `flex: 1` yerine `height` alıyor. Dış sarmalayıcılarındaki `flex: 1` ve
`minHeight: 0` de gidiyor: paylaşacak bir şey kalmadı.

Kutulara `boxSizing: "border-box"` yazılıyor. Bu depoda genel bir `box-sizing` sıfırlaması **yok** —
yalnız `.wf-input` kendi içinde tanımlıyor, ve bu iki kutu onu kullanmıyor. Onsuz 10 piksellik iç
boşluk tasarımın ölçüsünün üstüne eklenir, 162 ekranda 182 olurdu.

## 3 · Etiketler

```jsx
label={`${LAYER_LABEL[open]} prompt'u`}          // Foto / Video / Ses prompt'u
label={`${LAYER_LABEL.photo} negatif prompt'u`}  // Foto negatif prompt'u
```

19. maddede kurulan tablodan. Kelimeler ikinci kez yazılmıyor.

## 4 · İki grup ve tek ritim

```jsx
<div data-side style={SIDE}>
  <div data-group="info" ...>        {/* Sıra · Dosya adı · Üretim modu */}
  <div data-group="production" ...>  {/* prompt'lar · yeni mod · üret · sil */}
</div>
```

- `SIDE`: `gap` 14 → **16**, ve `overflowY: "auto"`.
- Bilgi grubu: `columnGap: 24`, `rowGap: 16` — yatay ölçü ritme dahil değil, dikey ölçü dahil.
- Üretim grubu: `gap: 16`.
- `Field`: etiketle değeri arası 4 → **6**.

Sütunda `justifyContent` yok: iki grup da yukarıdan diziliyor, artan yer alta düşüyor.

## Değişmeyen

- Kutuların içindekiler: bekleyen kutunun ortalanmış satırı, boş negatifin "—"si, değişmiş
  prompt'un vurgu çerçevesi.
- Negatif salt okunur (fark 117 22. maddede).
- Sahne, sekme şeridi, oynatıcı, onay pencereleri.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 694 / 494. `dist` aynı commit'te derleniyor.
