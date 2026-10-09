# Madde 216 · Varsayılan mod Loop — test turunun planı

**Spec:** [test turu](../specs/2026-09-13-queen-editor-m216-varsayilan-loop-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Adımlar

**1 · İki test yeniden yazılır** (`LayerPanel — the production mode`):

| Bugün | Yerine |
|---|---|
| `opens on the plain one` → Standart accent'li | `opens on loop` → Loop accent'li, öteki ikisi border'lı |
| `sends the plain mode when nobody touched the row` → `"standard"` | `sends loop when nobody touched the row` → `"loop"` |

**2 · Bir test eklenir:** `still sends the plain mode from the sound panel`. `renderPanel({ layer:
"sound", onQueue })` ile kurulur, *Kuyruğa ekle*'ye basılır, `onQueue`'nun üçüncü argümanı
`"standard"` beklenir. Yorumunda sebebi: sunucu ses işine Standart'tan başka bir mod verilirse
reddediyor, ve o red ön yüzde görünmüyor.

**3 · Altı beklenen metin güncellenir.** Video panelini kurup açılıştaki tahmini okuyan testler:

| Satır | Bugün | Yerine |
|---|---|---|
| 37 | `2 video üretilecek — her kare kendi videosunu alır.` | `2 loop video üretilecek — her video kendine döner.` |
| 45 | `1 video üretilecek — …` | `1 loop video üretilecek — her video kendine döner.` |
| 70 | `6 video üretilecek — …` | `6 loop video üretilecek — her video kendine döner.` |
| 87 | `1 video üretilecek — videolu 1 kare için …` | `1 loop video üretilecek — videolu 1 kare için …` |
| 498 | `1 video üretilecek — ${COPY}` | `1 loop video üretilecek — ${COPY}` |
| 506 | `2 video üretilecek — ${COPY}` | `2 loop video üretilecek — ${COPY}` |

Testlerin kurduğu şey değişmiyor — kapsamı sayıyorlar — yalnız açılışta duran cümle değişiyor.

**4 · Takım koşulur.**

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Kırmızı **okunur**: video tarafındaki sekiz beklenti düşmeli, **ses tarafındaki hiçbiri
düşmemeli**. Ses testlerinden biri düşerse okuma yanlıştır — ses paneli bu maddede değişmiyor.

**5 · Kırmızı commit'lenir.**

## Değişen dosya

`queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`.
