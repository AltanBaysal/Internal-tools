# Madde 147 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-02-queen-editor-m147-kare-modeli-uygulama-design.md](../specs/2026-09-02-queen-editor-m147-kare-modeli-uygulama-design.md)
**Dal:** `feat/v6` · **Kırmızı commit:** `853aaf1`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. Türetilmiş değer, `madeIn`'in altına.

```js
// Which checkpoint rendered this frame. The plan row carries the file name the notebook downloaded,
// and the column already has a file-name row of its own -- so the extension comes off and this row
// says the model. Only .safetensors: that is the one kind the notebook installs.
const madeWith = (frame?.model || "").replace(/\.safetensors$/, "");
```

`frame?.` gerekli: sayfa kare gelmeden de render oluyor *(`frames === null` dalı)*, ve bu satır
onun üstünde duruyor.

## B. Alan, `Dosya adı`'nın hemen altına.

```jsx
{open === "photo" && madeWith && (
  /* Which checkpoint made this frame. Since Madde 140 that is the user's pick and three of them
     can land in one gallery, so the frame has to carry the answer itself. Drawn only where it is
     true: video and sound jobs are planned with no model, and a frame planned before the choice
     existed carries none -- no record says which checkpoint the graph shipped that day, so naming
     one would be inventing it. */
  <Field label="Model" value={madeWith} />
)}
```

**Yeri önemli:** `Üretim modu`'nun **üstünde**. İkisi aynı grupta ve ikisi de koşullu, ama testi
foto sekmesinde `["Sıra", "Dosya adı", "Model"]` sırasını çiviliyor.

## C. Koşuldu: **591 yeşil, 0 kırmızı** *(28 dosya)*.

`npm test --prefix queen-editor/frontend` — iki kırmızının ikisi de döndü. Video sekmesinin bugünkü
grup testi *(`keeps nothing else in the top group`)* yeşil kaldı, yani satır foto sekmesinden
dışarı taşmadı.

`python -m pytest queen-editor -q` — **739 yeşil**, arka uç hiç değişmedi.

## D. `dist` derlenir.

`npm run build --prefix queen-editor/frontend` — kaynakla aynı commit'te, yoksa Colab eski arayüzü
servis eder.

## E. Yeşil commit.

`PhotoDetail.jsx`, `frontend/dist`, ve bu turun iki belgesi.

## Bilerek yapılmayanlar

**`.ckpt` ve öteki uzantılar** — defter yalnız `.safetensors` indiriyor; olmayan bir vaka için
regex genişletilmiyor.

**Galeri kılavuzu** — modeli tile'a yazmak ayrı bir soru ve bu maddenin isteği değil.

**Arka uç** — model zaten tarayıcıya ulaşıyor.
