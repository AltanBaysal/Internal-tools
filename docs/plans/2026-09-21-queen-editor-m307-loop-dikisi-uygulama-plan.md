# Madde 307 — Loop dikişi, implementasyon turunun planı

**Spec:** [m307 implementasyon turu](../specs/2026-09-21-queen-editor-m307-loop-dikisi-uygulama-design.md)

Üç dosya: `domain/ports.py`, `data/xai_prompt_writer.py`, `domain/run_loop.py`. Testlere
dokunulmaz — turun testleri `6c0defcb`'de yazıldı.

## Adımlar

1. **`LOOP_RULE`** ve üç yazıcının ikinci argümanı.
2. **Port** güncellenir.
3. **Döngü** kipi geçirir.
4. **Dört test satırı koşulur.**

## Beklenen yeşil

Turun altı testi, ve yazıcıların bugünkü bütün testleri — standart kipte talimat kıpırdamıyor.
