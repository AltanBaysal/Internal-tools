# Madde 147 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-02-queen-editor-m147-kare-modeli-testler-design.md](2026-09-02-queen-editor-m147-kare-modeli-testler-design.md)
**Kırmızı commit:** `853aaf1` — 2 kırmızı, 589 yeşil *(28 dosya, 591 test)*; arka uç 739 yeşil.
**Dal:** `feat/v6`

## Ne yeşile dönecek

İki test: alanın çizilmesi *(adı uzantısız)*, ve foto sekmesinin bilgi grubunun üç satıra
çıkması. Öteki ikisi vakumdaki yeşilliğini bırakıp gerçek bekçiye dönüşüyor.

## Tek dosya: `PhotoDetail.jsx`

**Bir türetilmiş değer**, `madeIn`'in yanına — o da aynı grubun aynı soruna verdiği cevap:

```js
// Which checkpoint rendered this frame. The plan row carries the file name the notebook downloaded,
// and the column already has a file-name row of its own -- so the extension comes off and this row
// says the model. Only .safetensors: that is the one kind the notebook installs.
const madeWith = (frame?.model || "").replace(/\.safetensors$/, "");
```

**Bir alan**, `Dosya adı`'nın hemen altına:

```jsx
{open === "photo" && madeWith && (
  <Field label="Model" value={madeWith} />
)}
```

## Üç şart, üçü de koşulda yazılı

| Koşulun parçası | Neyi engelliyor |
|---|---|
| `open === "photo"` | modelin videonun ya da sesin özelliğiymiş gibi görünmesi |
| `madeWith` | modeli olmayan eski karede boş bir satır, ya da uydurma bir ad |
| sıradaki yeri | kimliği söyleyen iki satırın önüne geçmesi |

Bu, `Üretim modu`'nun bugün izlediği kalıbın aynısı — `open === "video" && madeIn`. Yeni bir kural
değil, var olanın ikinci kullanıcısı.

## Yeni görsel dil yok

Var olan `Field` bileşeni, var olan `info` grubu, var olan 24/16 ritmi. Sütun genişlemiyor: grup
zaten `flexWrap` ve uzun bir değer alta sarıyor.

## Değişmeyen

**Arka uç, kayıt biçimi, galeri, üretim paneli, öteki 26 test dosyası.**

## `dist` aynı commit'te

Defter derlenmiş arayüzü klonluyor ve hiç derlemiyor: kaynağı commit'leyip `dist`'i bırakmak,
Colab'da hiçbir şeyin değişmemesi demek.

## Colab'da görülecek

Bir kare açılır, sağ sütunda `Sıra` ve `Dosya adı`'nın altında `Model`, değeri `novaAnimeXL_ilV190`.
Video ya da ses sekmesine geçilince satır kayboluyor.
