# Madde 215 · İkinci projede üretme hatası — uygulama turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Test turu:** [tasarım](2026-09-13-queen-editor-m215-ikinci-proje-hatasi-testler-design.md) ·
[plan](../plans/2026-09-13-queen-editor-m215-ikinci-proje-hatasi-test-plan.md) · kırmızı `f170c29`

## Yeni kod değil, geçmeyen üç prop

Düzeltme bir davranış icat etmiyor; var olanı ikinci panele de veriyor. `SidePanel` zaten
`busyElsewhere`, `error` ve `job`u tutuyor ve ikisini fotoğraf ile kuyruk paneline geçiyor —
`LayerPanel` çağrısında o satırlar yok. Eklenen şey o satırlar, ve panelin onları kullanması.

Cümle fotoğraf panelinden **birebir** alınıyor: *"Üretim sürüyor: {proje} — bitmesini bekle."* İki
panelin aynı durumu iki türlü söylemesi, bu maddenin şikâyet ettiği şeyin ta kendisi olurdu.

## Panelin dibi: hangi sıra

Düğmenin altındaki tek yuva bugün üç şey gösteriyor — eklendi kartı, yerel red kartı, tahmin cümlesi.
İkisi araya giriyor:

```
eklendi  →  yerel red  →  sunucunun reddi  →  başka proje sürüyor  →  tahmin
```

**Sunucunun reddi yerel reddin hemen ardında**, çünkü ikisi de aynı soruya cevap: *bu basış neden
gitmedi.* Aynı kırmızı kartı kullanıyorlar; ikisi bir arada olamaz, çünkü biri gönderilmemiş bir
basışın, öteki gönderilmiş olanın cevabı.

**Uyarı en sonda ve gri**, kırmızı değil: başka bir projenin koşuyor olması bir hata değil, bir
durum — kapalı düğmenin sebebini söylüyor. Fotoğraf panelinde de `var(--ink-3)` ile duruyor.

## Düğme

`disabled={submitting || missingProducer || busyElsewhere}`. Üçüncüsü ötekilerle aynı türden: basışın
şu an gidemeyeceği bir hâl, ve sebebi hemen altında yazılı.

## `job` neden geçiyor

Cümle koşan projenin **adını** taşıyor, ve o ad `job.project`te. Panelin başka hiçbir işi `job`la
değil; yalnız bu cümle için alıyor — fotoğraf paneli de tam olarak bunun için alıyor.

## Dokunulmayanlar

- **Sunucunun cümlesi.** *"Zaten bir üretim sürüyor."* olduğu gibi kalıyor. Projenin adını ön yüz
  ekliyor çünkü bilen taraf o; sunucu isteğin hangi ekrandan geldiğini bilmiyor.
- **Fotoğraf ve kuyruk panelleri.** Bu madde onlara dokunmuyor; çivileri de ayakta kalmalı.
- **`useGeneration`'ın hata yakalaması.** 409 zaten `error`a yazılıyordu — eksik olan, onu çizecek
  panelin o sırada ekranda olmaması.

## Değişen

[SidePanel.jsx](../../../queen-editor/frontend/src/features/photo_generation/SidePanel.jsx),
[LayerPanel.jsx](../../../queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx), ve
`dist`.
