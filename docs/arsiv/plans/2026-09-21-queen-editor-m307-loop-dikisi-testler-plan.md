# Madde 307 — Loop dikişi, test turunun planı

**Spec:** [m307 test turu](../specs/2026-09-21-queen-editor-m307-loop-dikisi-testler-design.md)

İki test dosyası: `test_video_prompt_writer.py`, `test_photo_usecases.py`. Kaynak koda
dokunulmuyor.

## Adımlar

1. **Beş yazıcı testi** — dosyanın kendi `FakeClient`'ıyla; loop kuralı `LOOP_RULE` adıyla
   dışarıdan okunuyor, çünkü iki yazıcı da aynı cümleyi kullanıyor ve test onu iki yerde
   tekrarlamamalı.
2. **Bir döngü testi** — sahte yazıcı artık kipi de kaydediyor.
3. **Dört test satırı koşulur.**

## Beklenen kırmızı

Altı test: ne `LOOP_RULE` var, ne yazıcılar ikinci argümanı alıyor, ne de döngü kipi geçiriyor.
