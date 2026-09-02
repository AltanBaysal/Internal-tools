# Madde 147 · Tur 1 (test) — Tasarım

**Kaynak:** [v6 yol haritası — Madde 147](../plans/2026-09-01-v6-roadmap.md#madde-147--kare-hangi-modelle-üretildiğini-söyler-queen-editor)
**Dal:** `feat/v6` · **Önceki commit:** `45503ac`

## Problem

140 üç checkpoint getirdi. Detay sayfası karenin sırasını, dosya adını, video sekmesinde üretim
modunu söylüyor — **hangi modelle üretildiğini söylemiyor.** Üç modelle üretilmiş bir projede
karşılaştırma yapmanın tek yolu hangi batch'in ne zaman atıldığını hatırlamak.

## Bu tur yalnız ön yüz testlerine dokunuyor

`PhotoDetail.test.jsx`. `PhotoDetail.jsx` ellenmiyor, arka uç zaten değişmiyor.

## Değişen tek fixture: `LAYERED` bir model kazanıyor

```js
const LAYERED = {
  id: "P0_0", file: "P0_0.png", status: "done", prompt: "kırmızı elbise", negative: "bulanık",
  model: "novaAnimeXL_ilV190.safetensors",
  ...
};
```

Gerçek biçimiyle: `list_frames` plan satırını olduğu gibi yayıyor, ve planda duran şey **dosya adı**,
uzantısıyla birlikte. Kısaltma ön yüzün işi, ve testin ölçtüğü şey tam olarak o.

`PHOTOS` fixture'ları modelsiz kalıyor — modeller seçilebilir olmadan önce üretilmiş kareler tam
olarak böyle görünüyor, yani ikinci testin fixture'ı bedavaya geliyor.

## Dört test

**1. Alan çiziliyor, ve adı uzantısız.**

```js
it("says which model the frame was made with", async () => {
  await open("P0_0", { frames: [LAYERED] });

  expect(screen.getByText("Model").parentElement.textContent).toContain("novaAnimeXL_ilV190");
  expect(screen.queryByText(/\.safetensors/)).toBeNull();
});
```

İkinci satır olmasa ilk satır uzantılı adla da yeşil gelirdi — `toContain` bir önek eşleşmesi.

**2. Modeli olmayan kare alanı çizmiyor.**

```js
it("draws no model row for a frame that never carried one", async () => {
  await open("0_a", { frames: PHOTOS });

  expect(screen.queryByText("Model")).toBeNull();
});
```

Boş modelin bir ada çevrilmemesi bu maddenin kararı: o ad `workflow_api.json`'ın kopyası olurdu, ve
eski karelerin hangi export'la çıktığını hiçbir kayıt söylemiyor.

**3. Model fotoğrafın, video ile sesin değil.**

```js
it("keeps the model on the photo tab alone", async () => {
  await open("P0_0", { frames: [LAYERED] });

  fireEvent.click(tab("Video"));
  expect(screen.queryByText("Model")).toBeNull();

  fireEvent.click(tab("Ses"));
  expect(screen.queryByText("Model")).toBeNull();
});
```

Video ve ses işleri modelsiz planlanıyor. Sekmelerinde bir model adı, fotoğrafın modelini o
katmanınki gibi gösterirdi.

**4. Foto sekmesinin bilgi grubu bütün olarak çivileniyor.**

```js
it("keeps the photo tab's top group to its three rows", async () => {
  await open("P0_0", { frames: [LAYERED] });

  expect([...document.querySelectorAll("[data-field]")].map((one) => one.textContent))
    .toEqual(["Sıra", "Dosya adı", "Model"]);
});
```

Video sekmesinin aynısı zaten var *("keeps nothing else in the top group")*; foto sekmesininki
yoktu. Sırayı da çiviliyor: model en sona giriyor, çünkü kimliği söyleyen iki satır önce okunuyor.

## Neden dördü de gerekli

| Test | Onsuz ne kaçardı |
|---|---|
| 1 | alanın hiç olmaması, ya da uzantıyla yazılması |
| 2 | eski karelerde boş ya da uydurma bir ad |
| 3 | modelin videonun özelliğiymiş gibi görünmesi |
| 4 | gruba dördüncü bir satırın sessizce eklenmesi, ya da sıranın kayması |

## Değişmeyen

- **`PhotoDetail.jsx`, arka uç, `dist`.**
- **Video sekmesinin bugünkü grup testi** — model foto sekmesinde kaldığı sürece yeşil kalıyor, ve
  yanlış çizilirse kendiliğinden kırmızı veriyor. Yani 3'ün video yarısının ikinci bir bekçisi var.
- **`skip` / `xfail` yok.**

## Beklenen kırmızı

Dördün üçü: 1, 3'ün hiçbir yarısı değil — 3 bugün de yeşil, çünkü ortada hiç `Model` alanı yok — ve
4. Yani **1 ile 4 kırmızı, 2 ile 3 yeşil.**

İkisinin bedavaya yeşil gelmesi kabul ediliyor ve sebebi kayda geçiyor: ikisi de *"olmasın"* diyen
testler, ve bugün zaten yok. Bir vakumda yeşiller; kırmızıya döndürecek şey 1 ile 4'ün uygulaması.
Değerleri bu turda değil, ondan sonraki her turda.
