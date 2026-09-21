# Madde 290 · Ekran açılışta koşan export'u görecek — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m290-yenilemeye-dayanan-ekran-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · Açılıştaki okuma.** `ExportScreen.jsx`'e `[project]`'e bağlı bir efekt: `getExportState`
çağrılır, cevaptan `busy(...)` olan modlar süzülür, ve **yalnız boş değilse** `runs`'a yazılır.

**2 · `npm run build --prefix queen-editor/frontend`.** `dist/` aynı commit'e girecek.

**3 · Takım:** dört satır paralel. Sekiz kırmızının yeşile dönmesi beklenir.

**4 · Commit** (yeşil), kaynak ve `dist` birlikte.
