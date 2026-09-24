# Madde 300 — Sıra ve boşluk, implementasyon turunun planı

**Spec:** [m300 implementasyon turu](../specs/2026-09-21-queen-editor-m300-sira-ve-bosluk-uygulama-design.md)

Testlere dokunulmaz — turun testleri `d81f6b1e`'de yazıldı.

## Adımlar

1. **`references.placed` ve `references.gaps`** — saf kural; takım koşulur, `test_references.py`
   yeşile döner.
2. **`data/reference_order_store.py`.**
3. **Dört kullanım senaryosu** sıra deposunu alır; `save_reference_order` doğar.
4. **Kapı:** `PUT …/references/order`, ve `main.py` bağlar.
5. **`api.js` ve `ReferencePanel.jsx`** — sürükleme ve boş yuva.
6. **Dört test satırı koşulur**, sonra `dist`.

## Beklenen yeşil

Turun on beş testi, ve 297–299'un testleri yeni şekilleriyle.
