# Madde 300 — Sıra ve boşluk, test turunun planı

**Spec:** [m300 test turu](../specs/2026-09-21-queen-editor-m300-sira-ve-bosluk-testler-design.md)

Dört test dosyası, hepsi var: `test_references.py`, `test_reference_usecases.py`,
`test_reference_routes.py`, `ReferencePanel.test.jsx`. Kaynak koda dokunulmuyor.

## Adımlar

1. **Kural testleri** — `references.placed(order, rows)` ve `references.gaps(rows)`, saf
   fonksiyonlar.

2. **Kullanım senaryoları** — sahte havuza bir `FakeOrderStore` ekleniyor *(sözlük tutar)*, ve
   `list_references` artık onu da alıyor.

3. **Kapı** — `PUT …/references/order`, gerçek diskle ve ikinci bir sunucuyla.

4. **Panel** — boş yuva ve sürükleme.

5. **Dört test satırı koşulur.**

## Beklenen kırmızı

`placed`, `gaps`, `save_reference_order` ve sıra deposu yok; `list_references` fazladan argüman
alamıyor — referans testlerinin çoğu bu yüzden düşer. Panelin iki yeni testi de kırmızı.
