# Madde 215 · İkinci projede üretme hatası — test turunun planı

**Spec:** [test turu](../specs/2026-09-13-queen-editor-m215-ikinci-proje-hatasi-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Adımlar

**1 · `LayerPanel.test.jsx`'e dört çivi.** Panel iki yeni prop alacak — `busyElsewhere` ve `error` —
ve testler onları geçerek kurulur.

| Test | Kurulum | Ne bekler |
|---|---|---|
| `is disabled while another project holds the worker` | `busyElsewhere`, koşan proje `balo` | *Kuyruğa ekle* kapalı, ve **"Üretim sürüyor: balo — bitmesini bekle."** |
| `says the same thing on the sound panel` | aynısı, `layer: "audio"` | aynı cümle |
| `shows a refusal where the press was made` | `error: "Zaten bir üretim sürüyor."` | cümle panelde duruyor |
| `leaves the button alone when nobody else is running` | varsayılan | düğme açık, uyarı yok |

Cümle fotoğraf panelinden birebir alınıyor
*([GeneratePanel.jsx:266-269](../../../queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx))* —
iki panelin aynı durumu iki türlü söylemesi, bu maddenin şikâyet ettiği şeyin kendisi olurdu.

**2 · `SidePanel.test.jsx`'e bir çivi:** `hands the layer panel what the photo panel already gets`.
Sütun `busyElsewhere` ile kurulur, raydan **Video üret** açılır, ve cümle orada beklenir. Panelin
kendi testleri propu doğru kullandığını tutuyor; bu çivi propun **geldiğini** tutuyor, ve eksik olan
tam olarak oydu.

**3 · Takım koşulur**, dördü de:

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Beklenen: dört kırmızı *(dördüncü çivi yeşil)*, biri SidePanel'de. **Fotoğraf panelinin kendi
çivileri ayakta kalmalı** — bu madde ona dokunmuyor.

**4 · Kırmızı commit'lenir.**

## Değişen dosyalar

`queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`,
`queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx`.
