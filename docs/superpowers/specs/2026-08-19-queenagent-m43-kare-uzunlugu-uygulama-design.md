# Madde 43 — Kare açıklaması 1-2 cümle · Uygulama Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 43](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Test turu:** [2026-08-19-queenagent-m43-kare-uzunlugu-testler-design.md](2026-08-19-queenagent-m43-kare-uzunlugu-testler-design.md) — kırmızı commit `fd7073a`
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · Tek cümle değişiyor

`SPLIT_INTO_FRAMES`'in ikinci paragrafı. "one line in prompt language" gidiyor, yerine sayı
geliyor:

> A frame is one or two sentences: who is in it, what is happening, from what camera. Not a
> paragraph of prose. Number them.

"prompt language" ifadesi de bu cümleyle birlikte düşüyor — ama sebebi Madde 43 değil: o ifade
listenin İngilizce gelmesinin asıl kaynağı ve **Madde 44'ün konusu**. Burada düşmesinin sebebi
cümlenin baştan yazılması; Madde 44 dilin hangi dil olacağını ayrıca söyleyecek.

Bu, iki maddenin aynı cümleyi paylaşmasının kaçınılmaz sonucu. Alternatif — ifadeyi bu turda
korumak — cümleyi anlamsız bırakırdı ("bir ya da iki cümle, prompt dilinde"), ki zaten çelişkinin
kendisi.

## 2 · Kabul ölçütü

1. Test turunun üç testi de yeşil, başka hiçbir test düşmüyor.
2. İki komut da yeşil.
3. Elle: kare listesinde uzun paragraf yok.
