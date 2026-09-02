# Madde 147 · Tur 1 (test) — Plan

**Tasarım:** [2026-09-02-queen-editor-m147-kare-modeli-testler-design.md](../specs/2026-09-02-queen-editor-m147-kare-modeli-testler-design.md)
**Dal:** `feat/v6`
**Bu tur yalnız `PhotoDetail.test.jsx`'e dokunur.** `PhotoDetail.jsx` ellenmez.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. `LAYERED` fixture'ı bir model kazanır.

```js
const LAYERED = {
  id: "P0_0", file: "P0_0.png", status: "done", prompt: "kırmızı elbise", negative: "bulanık",
  // The plan row's own shape: list_frames spreads it into the frame, so the name arrives with the
  // extension it is stored under and trimming it is the panel's job.
  model: "novaAnimeXL_ilV190.safetensors",
  layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" },
  failed: [], owed: [],
  prompts: { photo: "kırmızı elbise", video: "kadın dönüyor", audio: "kumaş hışırtısı" },
};
```

Paylaşılan bir fixture, ama eklenen alan yalnız yeni testlerin okuduğu bir alan — bugünkü hiçbir
iddia onu görmüyor.

## B. Dört test, `keeps nothing else in the top group`'un altına.

Kodları tasarımda; oraya yazıldığı gibi, gerekçe yorumlarıyla birlikte girer. Yerleri bu: üçü de
aynı grubu ölçüyor ve grubun bugünkü tek testi orada duruyor.

## C. Koşuldu: **2 kırmızı, 589 yeşil** *(28 dosya, 591 test)*.

`npm test --prefix queen-editor/frontend`

| Test | Koşunun söylediği |
|---|---|
| `says which model the frame was made with` | `Unable to find an element with the text: Model` |
| `keeps the photo tab's top group to its three rows` | `["Sıra", "Dosya adı"]` — üçüncü satır yok |

**İkisi bedavaya yeşil geldi ve bu beklenen** *(tasarımda yazılı)*: `draws no model row…` ile
`keeps the model on the photo tab alone` *"olmasın"* diyor, ve bugün zaten yok. Vakumda yeşiller;
değerleri bundan sonraki turlarda.

`python -m pytest queen-editor -q` — **739 yeşil**, arka uç bu maddede hiç değişmiyor.

## D. Kırmızı commit.

Test dosyası, bu turun iki belgesi, ve yol haritasının 147 kaydı.

`dist` derlenmez: bu turda ön yüz kaynağı değişmiyor.

## Bilerek yapılmayanlar

**`PhotoDetail.jsx` ellenmez** — bu turun tamamı testtir.

**Video sekmesinin bugünkü grup testi ellenmez** — model foto sekmesinde kaldığı sürece yeşil
kalıyor, ve yanlış çizilirse kendiliğinden kırmızı veriyor.

**`skip` / `xfail` yok.**
