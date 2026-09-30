# Madde 396 — Tur sınırı 16'dan 32'ye — uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 396.
**Testler:** [2026-09-30-queenagent-m396-tur-siniri-testler-design.md](2026-09-30-queenagent-m396-tur-siniri-testler-design.md),
kırmızı commit `9095d2b1` — iki test kırmızı: `MAX_ROUNDS == 32` ve ilk `progress`'in `"of": 32`'si.

**Kullanıcıdan gereken:** yok.

## Ne yazılır

1. **[tools.py](../../../queen-agent/backend/features/workspace/domain/tools.py): `MAX_ROUNDS = 32`.**
   Başka hiçbir kod değişmez: `stream_answer` döngüyü, son turu (araçsız, `LAST_ROUND`'lu) ve
   `Progress`'in `of`'unu zaten `MAX_ROUNDS`'tan okur; route `of`'u olduğu gibi tarayıcıya yazar, ekran da
   `round N/of`'u oradan okur.
2. **`MAX_ROUNDS`'un yorumu bugün doğru olanı söyler.** Bugünkü yorum zinciri v9'dan önceki akışla sayıyor
   (*"read the pair, open the scenario, fill the three maps, add the scenes, build"*) ve on beşinci /
   on altıncı turdan söz ediyor. Yeni yorum:
   - en uzun zincir: Start a scenario 5. adımdan sonra aynı turda yürür — kareler ve build, sonra her
     biri build edilmiş dosyayı okuyup yeniden build eden dört kontrol, sonra negatif liste;
   - 32 kullanıcının sayısı (Madde 396), ve sonuncusu turu kapatır (Madde 137); sınırsız bir döngü para
     ve zaman yakar;
   - sınıra varmak bir duruş, hata değil — sayı bu yüzden cömert olmalı: yarıda kesilen bir zincir, pes
     etmiş bir model gibi görünür.

   Eski sayıdan söz edilmez (CLAUDE.md, *Style*: yorum yalnız bugün doğru olanı söyler). Kullanıcı neden
   32 dediğini söylemedi; yorum bir neden uydurmaz.
3. **[stream_answer.py](../../../queen-agent/backend/features/workspace/domain/usecases/stream_answer.py)'nin
   `_asked` docstring'i**: *"shows up in one round out of sixteen"* → *"out of thirty-two"*. Kod değişmez.

## Ne yazılmaz

- Ön uç: sayaç `of`'u sunucudan okur, `round 2/32` der. Kaynak ve `dist` değişmez.
  `ChatScreen.jsx`'teki bir JSX yorumu *"round 0/16"*'yı örnek olarak anar, testlerinin örnek verisiyle
  aynı sayı; sunucunun sayısı hakkında bir iddia değil, olduğu gibi kalır.
- Modele giden metinler: hiçbiri tur sayısını anmıyor (`LAST_ROUND` yalnız bunun son tur olduğunu söyler).
- Madde 137'nin test dosyasındaki bölüm yorumu, o maddenin çıktığı 16 turluk koşuyu anlatır; geçmiş.

## Doğrulama

Dört satır, olduğu gibi, paralel. `python -m pytest queen-agent -q` tamamen yeşil (972); öteki üç süit
yeşil kalır (836, 1160, 749).
