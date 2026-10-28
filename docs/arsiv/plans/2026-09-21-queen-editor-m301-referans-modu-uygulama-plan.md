# Madde 301 — Referans modu, implementasyon turunun planı

**Spec:** [m301 implementasyon turu](../specs/2026-09-21-queen-editor-m301-referans-modu-uygulama-design.md)

İki dosya: `production_modes.js`, `LayerPanel.jsx`, ve `dist`. Testlere dokunulmaz — turun testleri
`166940b0`'da yazıldı.

## Adımlar

1. **`production_modes.js`:** `FROM_FRAME`, `FROM_POOL`, `SOURCES`.
2. **`LayerPanel.jsx`:** `source` durumu, iki satırın kapanması, prompt kutusu, sayan cümle, ve
   `refusalOf`'a prompt sebebi.
3. **Dört test satırı koşulur**, sonra `dist`.

## Beklenen yeşil

Turun yedi testi; panelin öteki 72 testi kıpırdamaz.
