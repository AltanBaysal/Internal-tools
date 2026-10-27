# Madde 255 · Export ekranı disclaimer adımını söyleyecek — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m255-disclaimer-adimi-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `ExportScreen.jsx`:** `merging` durumunun cümlesi `Disclaimer ekleniyor…` oluyor, yanındaki
yorum adımın adını anlatıyor.

**2 · Build:** `npm run build --prefix queen-editor/frontend`.

**3 · Takım:** dört satır paralel, verbatim. Beklenen: bir kırmızı yeşile döner.

**4 · Commit** (yeşil) — kaynak ve `dist/` aynı commit'te.

**5 · Yol haritası:** 255 işaretlenir, `Durum: 9/9`, ve koşunun kapanış notu kullanıcının testine
döner. Ödenecek borç *(defterin ve testin `BRANCH` sabiti `main`'e döner)* orada duruyor.
