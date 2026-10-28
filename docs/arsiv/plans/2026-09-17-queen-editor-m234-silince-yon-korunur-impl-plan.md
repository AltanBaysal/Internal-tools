# Madde 234 · Detayda silinen kareden sonra gidilen yönde kalınır — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-17-queen-editor-m234-silince-yon-korunur-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · `PhotoDetail.jsx`.** `useRef` ile `backwards`. `step(frame, back)` yönü yazıp kareye gider.
İki `Arrow` ile iki tuş ondan geçer. `handleRemove`'daki `after` yöne göre seçilir, yorumu da buna
göre düzeltilir.

**2 · Takım koşulur**, dördü de. Beklenen: hepsi yeşil.

**3 · `npm run build --prefix queen-editor/frontend`**, `dist/` kaynakla aynı commit'e girer.

**4 · Yol haritasında 234 işaretlenir**, Durum 20/23 olur. Commit'lenir.
