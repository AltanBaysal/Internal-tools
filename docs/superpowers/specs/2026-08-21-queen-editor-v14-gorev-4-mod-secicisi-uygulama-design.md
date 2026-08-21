# v14 · Görev 4 — Video panelinde Üretim modu seçicisi · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-4-mod-secicisi-testler-design.md) —
kararlar orada verildi ve commit edilmiş on iki test onları tarif ediyor. Bu belge kodun nereye
yazılacağını söyler.

## Değişen dosyalar

**`features/photo_generation/production_modes.js`** (yeni) — sıralı liste, her satırda kimlik ve
Türkçe etiket, artı `STANDARD` sabiti. Sıra tesadüfi değil: Standart önce, çünkü varsayılan o.

**`features/photo_generation/LayerPanel.jsx`** — `mode` durumu (açılışta `STANDARD`), `ModeRow`
bileşeni, ve satırın yalnız video panelinde çizilmesi. `onQueue` üçüncü argümanla çağrılıyor.

`ModeRow`, `ScopeRow`'un sağdaki sayı hücresi olmadan hâli. İkisini tek bileşende toplamak,
sayının yokluğunu bir `undefined` kontrolüyle anlatmak olurdu.

**`features/photo_generation/SidePanel.jsx`**, **`useGeneration.js`**, **`shared/api.js`** —
argüman zinciri. Üçü de yalnız taşıyor; hiçbiri modu okumuyor.

**`backend/features/photo_generation/presentation/routes.py`** — `body.get("mode", STANDARD)` ve
`InvalidMode` → 400 + `field: "mode"`.

## Bu turda olmayan

Ardışıklık kuralı 5., moda göre değişen cümleler 6. maddede. Panel bugün üç modu da her seçimde
kabul ediyor; ardışık olmayan seçimde bağlama seçilirse motor hedefsiz kalan kareyi 2. maddedeki
kuralla dışarıda bırakıyor.

## Bitti sayılır

Dört komutun dördü de yeşil. **`dist` bu commit'te derleniyor** — not defteri bu depoyu klonluyor,
derlemiyor, ve derlenmemiş bir ön yüz Colab'da eski hâliyle açılır.
