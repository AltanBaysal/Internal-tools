# Madde 315 — Loop kuralı sabit hız da istiyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Deneme kullanıcının, iş bittikten sonra: loop klibi beş kez yan yana.

## Bugün ne oluyor

Loop modunda video prompt'unu yazan modelin talimatının sonuna `LOOP_RULE` ekleniyor *(madde 307)*:
kendine dönen bir hareket, biten bir hareket değil. Kural hızdan hiç söz etmiyor. İki yazıcı da —
WAN'ınki ve H3'ünki — kuralı aynı şekilde ekliyor, ve standart video eskisiyle aynı talimatı alıyor;
ikisini de 307'nin testleri tutuyor.

## Kural

**Loop kuralı hareketin sonuna kadar aynı hızda sürmesini, sona doğru yavaşlamamasını da istiyor.**
Kullanıcının onayladığı cümle: *"hareket sonuna kadar aynı hızda sürsün, sona doğru yavaşlamasın"*.
Kural İngilizce, çünkü modele yazılıyor; H3'ün loop rehberi de aynı şeyi sabit hızla söylüyor
*("repeats at constant speed", "no sudden speed change")*. Kural tek yerde durduğu için iki yazıcıya
birden gidiyor.

## Yazılacak test

### `test_video_prompt_writer.py` — koşularak

1. **Loop kuralı tek hız istiyor, sona kadar** — `LOOP_RULE`'da `same speed` ve `slow down` geçiyor.

**Değişen:** yok.

**Bekçiler, bugün de yeşil:** `test_a_loop_video_is_asked_for_a_motion_that_returns` ve
`test_wan_asks_for_the_same_returning_motion` — kural iki yazıcıya da gidiyor, yeni cümle dahil;
`test_a_plain_video_is_asked_for_nothing_extra` — standart video etkilenmiyor;
`test_the_loop_rule_says_what_it_wants_and_what_it_refuses` — 307'nin sözleri yerinde.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız 1.
