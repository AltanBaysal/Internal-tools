# Madde 298 — Sınırlar, implementasyon turunun planı

**Spec:** [m298 implementasyon turu](../specs/2026-09-21-queen-editor-m298-sinirlar-uygulama-design.md)

Altı dosya: `data/ffmpeg_clips.py`, `data/reference_store.py`, `domain/references.py`,
`domain/ports.py`, iki kullanım senaryosu, `presentation/reference_routes.py` ve `main.py`.
Testlere dokunulmaz — turun testleri `2503dd6e`'de yazıldı.

## Adımlar

1. **`FfmpegClips`** yazılır, takım koşulur: araç testleri yeşile, ötekiler kendi kırmızılarına.
2. **`references.check`** ve sınırlar.
3. **Depo `items`'a geçer**, port güncellenir.
4. **İki kullanım senaryosu** — liste `seconds` taşır, ekleme `clips` alır ve kuralı çağırır.
5. **Kapı ve `main.py`.**
6. **Dört test satırı koşulur.**

## Beklenen yeşil

Turun on beş testi, ve 297'nin testleri yeni şekilleriyle.
