# Madde 302 — Üretimin reddi, implementasyon turunun planı

**Spec:** [m302 implementasyon turu](../specs/2026-09-21-queen-editor-m302-uretimin-reddi-uygulama-design.md)

Testlere dokunulmaz — turun testleri `6c9c919a`'da yazıldı.

## Adımlar

1. **`domain/usecases/queue_references.py`** — beş kontrol, sonra sıfır.
2. **Kapı** `POST …/references/produce`, ve `main.py` bayrakla bağlar.
3. **`api.js` + `useGeneration`** — referans kipi kendi ucuna.
4. **Dört test satırı koşulur**, sonra `dist`.

## Beklenen yeşil

Turun dokuz testi; havuzun öteki testleri kıpırdamaz.
