# Madde 297 — Referans havuzu, implementasyon turunun planı

**Spec:** [m297 implementasyon turu](../specs/2026-09-21-queen-editor-m297-referans-havuzu-uygulama-design.md)

Yedi dosya: `domain/references.py`, `domain/ports.py`, üç kullanım senaryosu,
`data/reference_store.py`, `presentation/reference_routes.py`, ve `main.py`. Testlere dokunulmaz —
turun testleri `68285f01`'de yazıldı.

## Adımlar

1. **`domain/references.py`** yazılır, ve takım koşulur: `test_references.py` yeşile döner, öteki
   iki dosya hâlâ toplamada düşer. Kuralın kendi kırmızısı böyle görülür.

2. **`ports.ReferenceStore`** eklenir.

3. **Üç kullanım senaryosu** yazılır, ve takım koşulur: `test_reference_usecases.py` yeşile döner.

4. **`data/reference_store.py`** ve **`presentation/reference_routes.py`** yazılır.

5. **`main.py`** havuzu kurar ve blueprint'i kaydeder.

6. **Dört test satırı koşulur.**

## Beklenen yeşil

Turun on altı testi döner; var olan 981 testin hiçbiri kıpırdamaz — havuz bir alt klasör, ve
`next_number` yalnız dosyalara bakıyor.
