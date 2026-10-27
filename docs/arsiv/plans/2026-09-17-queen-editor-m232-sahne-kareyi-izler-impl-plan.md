# Madde 232 · Kare değişince sahnede eski karenin dosyası kalmayacak — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-17-queen-editor-m232-sahne-kareyi-izler-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · `Arriving.jsx`.** Render-prop, üç durum: `loading`, `ready`, `failed`.

**2 · `LayerPlayer.jsx`.** `onReady`, `onFail` props. Sekme sıfırlayan `useEffect` silinir.

**3 · `PhotoDetail.jsx`.** Üç medya yeri `` <Arriving key={`${frame.id}/${open}`} url={…}> `` ile sarılır.

**4 · Takım koşulur**, dördü de. Beklenen: dördü yeşil.

**5 · `npm run build --prefix queen-editor/frontend`**, ve `dist` kaynakla aynı commit'e girer.
Madde roadmap'te işaretlenir.
