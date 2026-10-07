# Madde 315 — Loop kuralı sabit hız da istiyor, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m315 test turu](2026-09-24-queen-editor-m315-loop-sabit-hiz-testler-design.md),
`73f11ff0` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## `xai_prompt_writer.py`

- **`LOOP_RULE`'un sonuna bir cümle:**
  *"Keep the same speed from the first frame to the last: the motion must not slow down toward the
  end."* — kullanıcının onayladığı *"hareket sonuna kadar aynı hızda sürsün, sona doğru
  yavaşlamasın"*. 307'nin cümleleri olduğu gibi kalıyor.
- **Kuralın üstündeki yoruma bir paragraf:** neden — üreticilerin çoğu son karelerde özneyi
  durgunluğa doğru yavaşlatıyor, ve döngü istemek bunu yasaklamıyor; H3'ün kendi loop tavsiyesi de
  sabit hız istiyor. Sözcükler yavaşlamayı azaltabilir, kaldıramaz; kaldıran çözüm birleşmeye iki
  taraftan birkaç karelik hareket vermek, ve backlog'da bekliyor.

`asked` ve iki yazıcı değişmiyor: kural tek yerde, ikisine de oradan gidiyor.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil.
