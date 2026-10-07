# Madde 301 — Referans modu, test turunun planı

**Spec:** [m301 test turu](../specs/2026-09-21-queen-editor-m301-referans-modu-testler-design.md)

Tek test dosyası: `frontend/src/features/photo_generation/LayerPanel.test.jsx`. Kaynak koda
dokunulmuyor.

## Adımlar

1. Dosyanın kendi `renderPanel` yardımcısıyla yedi test, yeni bir `describe` altında.
2. Referansı seçmek için düğmenin adı kullanılıyor *(`Referans`)*, prompt kutusu için etiketi.
3. **Dört test satırı koşulur.**

## Beklenen kırmızı

Yedi test de düşer: pencerede ne böyle bir satır, ne prompt kutusu, ne de sayan cümle var.
Panelin öteki testleri yeşil kalır — standart taraf kıpırdamıyor.
