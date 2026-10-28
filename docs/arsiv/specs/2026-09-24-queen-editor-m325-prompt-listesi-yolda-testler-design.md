# Madde 325 — Referanstan'ın prompt listesi sunucuya ulaşıyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.**

## Bugün ne oluyor

Video paneli Referanstan'dan basınca `onQueue(null, variants, "reference", prompts)` çağırıyor —
dört argüman. Yan panel bu çağrıyı `onQueueLayer`'a bağlarken yalnız ilk üçünü geçiriyor
*([SidePanel.jsx:183](../../../queen-editor/frontend/src/features/photo_generation/SidePanel.jsx#L183))*,
yani `useGeneration.queueLayer`'ın `prompts`'u `undefined` geliyor ve istek sunucuya prompt'suz
gidiyor.

LayerPanel'in kendi testi `onQueue`'nun dört argümanla çağrıldığını tutuyor
*(`sends the prompts and the variants under the reference kind`)*; yan panelin bağlantısını hiçbir
test koşmuyor. Kırılan yarı o.

## Kural

**Video panelinin `onQueue`'ya verdiği her argüman `onQueueLayer`'a, katmanın adının ardından,
olduğu gibi ulaşıyor.**

## Yazılacak test

### `SidePanel.test.jsx` — koşularak, `SidePanel — the icon rail` bloğunda

1. **Referanstan'ın prompt listesi yan panelden geçiyor** — video paneli açılır, `Referanstan`
   seçilir, prompt kutusuna `["gotik kız", "dans"]` yazılır, `Kuyruğa ekle`'ye basılır;
   `onQueueLayer` `("video", null, 1, "reference", '["gotik kız", "dans"]')` ile çağrılmış.

**Değişen:** yok.

**Bekçiler, bugün de yeşil:** `hands the layer panel what the photo panel already gets` — öteki
bağlantılar; LayerPanel'in `sends the prompts and the variants under the reference kind` — panelin
kendi yarısı; ses panelinin `still sends the plain mode, so the server reads one call shape` —
kareden çağrının şekli.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor/frontend` vitest kırmızı — yalnız 1.
