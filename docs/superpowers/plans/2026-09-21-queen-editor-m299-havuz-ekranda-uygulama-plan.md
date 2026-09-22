# Madde 299 — Havuz ekranda, implementasyon turunun planı

**Spec:** [m299 implementasyon turu](../specs/2026-09-21-queen-editor-m299-havuz-ekranda-uygulama-design.md)

Beş dosya: `presentation/reference_routes.py`, `shared/api.js`, yeni `ReferencePanel.jsx`,
`ProjectScreen.jsx`, ve `dist`. Testlere dokunulmaz — turun testleri `458e45ef`'te yazıldı.

## Adımlar

1. **Kapı sınırları da döndürür** — `references.LIMITS` cevaba eklenir.
2. **`api.js`:** `timeout` seçeneği, üç çağrı, bir adres yardımcısı.
3. **`ReferencePanel.jsx`** yazılır.
4. **`ProjectScreen.jsx`** paneli en sola alır, açma/kapama düğmeleriyle.
5. **Dört test satırı koşulur.**
6. **`npm run build --prefix queen-editor/frontend`**, ve `dist` aynı commit'e girer.

## Beklenen yeşil

Turun on bir testi; `ProjectScreen`'in öteki testleri kıpırdamaz.
