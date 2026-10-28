# Madde 325 — Referanstan'ın prompt listesi sunucuya ulaşıyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m325 test turu](2026-09-24-queen-editor-m325-prompt-listesi-yolda-testler-design.md),
`6706b391`.

## Değişen

**`SidePanel.jsx`** — video ve ses panelinin `onQueue`'su, katmanın adını başa koyup **aldığı her
argümanı** `onQueueLayer`'a geçiriyor:

```jsx
onQueue={(...asked) => onQueueLayer(open, ...asked)}
```

Argümanları tek tek adlandırmak yerine hepsini geçirmek bilerek seçildi: hata tam olarak bir
argümanın listede unutulmasıydı, ve panelin çağrı şekli bir gün daha büyürse bağlantı yine
kıpırdamamalı. Çağrının anlamı panelde *(`LayerPanel.handleAdd`)* ve kancada
*(`useGeneration.queueLayer`)* yazılı; yan panel yalnız katmanın adını ekliyor.

**Değişmeyen:** `LayerPanel`, `useGeneration`, `api.js`, sunucu — hepsi dördüncü argümanı zaten
doğru taşıyor.

## Dist

Kaynak değiştiği için `npm run build --prefix queen-editor/frontend` koşulur ve `dist/` aynı
commit'e girer *(FOUNDATION, karar 3)*.

## Bitti sayılır

Dört test satırı yeşil; kod, dist, bu spec ve planı tek commit.
