# Madde 396 — Tur sınırı 16'dan 32'ye — testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 396. Kullanıcı, 30 Eylül:
*"all tur sınırına 16 dan 32 ye çıakrlaım ona bir task aç bundan sonra koş"*; hizalama aynı gün —
*"abi 16 32 için align olacak mısın direkt başlayabilir misin paralel"*. v9-8'deki 28 Eylül kararını
(*"tur sınırı değişmez … bir tur en çok 16 istek yapıyor"*) kullanıcı 30 Eylül'de değiştirdi.

**Kullanıcıdan gereken:** yok. Sayı kullanıcının; karar, dosya ya da ölçüm beklenmiyor.

## Bugün ne var

- `MAX_ROUNDS = 16`, [tools.py](../../../queen-agent/backend/features/workspace/domain/tools.py)'de. Bir
  tur modele en çok bu kadar gider; `stream_answer` son turu `MAX_ROUNDS`'tan bilir, ona araç vermez ve
  `LAST_ROUND`'u söyler (Madde 137). Ekrana giden `progress` olayının `of`'u da `MAX_ROUNDS`.
- Sayıyı iki test elle tutar:
  - `test_tools.py` — `test_the_round_limit_carries_the_longest_chain`: `MAX_ROUNDS == 16`. Yorumu
    zinciri v9'dan önceki akışla sayıyor (*"list, read, a skeleton, several batches of frames, a
    self-check and the build"*); bugün doğru değil.
  - `test_chats_api.py` — `test_a_running_turn_reaches_the_browser_as_progress`: tarayıcıya giden ilk
    `progress` `{"round": 1, "of": 16, "tokens": 0}`. Sunucunun tarayıcıya söylediği sayı bu; ekran
    `of`'u buradan okur.
- `test_stream_answer.py`'deki son tur testleri sayıyı `MAX_ROUNDS`'tan okur, iki sayıda da doğru
  kalır. Aynı dosyada iki yorum *"sixteen"* der, ve bugünkü sınırı anlatır:
  `test_the_instruction_moves_to_the_end_of_every_round` (*"An answer runs up to sixteen rounds"*) ve
  `test_the_notice_is_the_requests_last_word` (*"one round out of sixteen"*). Madde 137'nin bölüm
  yorumu (*"Sixteen rounds went on tools … the sixteenth round"*) o maddenin çıktığı koşuyu anlatır —
  o koşuda sınır 16'ydı; geçmiş, ve doğru kalır.
- Ön ucun testleri 16'yı yalnız kendi olaylarında örnek veri olarak kullanır (`"of":16`,
  `round 2/16`); sunucunun sayısını okuyan yok.

## Kararlar

1. **İki test 32'yi tutar.** `MAX_ROUNDS == 32`, ve `"of": 32`. Sayı bir karar olduğu için elle
   yazılır — `MAX_ROUNDS`'tan okunsa değişikliği fark etmeden geçerdi (`test_config.py`'nin aynı
   gerekçesi: *"Pinned like MAX_ROUNDS"*).
2. **`test_tools.py`'nin yorumu bugünkü zinciri söyler:** Start a scenario 5. adımdan sonra aynı turda
   yürür — kareler ve build, sonra her biri build edilmiş dosyayı okuyup yeniden build eden dört
   kontrol, sonra negatif liste. Sayı kullanıcının (Madde 396). Sabitlenme gerekçesi değişmez.
   Kullanıcı neden 32 dediğini söylemedi; yorum bir neden uydurmaz.
3. **`test_chats_api.py`'nin yorumu değişmez:** 16'dan söz etmiyor, doğru kalır.
4. **`test_stream_answer.py`'nin iki yorumu *"thirty-two"* der.** İddiaları değişmez; yorum yalnız
   bugün doğru olanı söyler. Madde 137'nin bölüm yorumu olduğu gibi kalır.
5. **Ön uç testlerine dokunulmaz.** Örnek veri kendi olayları; sayaç `of`'u sunucudan okuduğu için
   ekran `round 2/32` der, ön ucun kodu değişmez.
6. **Yeni test yok.** Son turun araçsız ve `LAST_ROUND`'lu oluşu, turun `MAX_ROUNDS`'ta durması
   bugünkü testlerde `MAX_ROUNDS` üzerinden tutuluyor; 32'de de aynı testler onu tutar.

## Testler ne tutar

| # | Test | Ne | Bugün |
|---|---|---|---|
| T1 | `test_tools.py` — `test_the_round_limit_carries_the_longest_chain` | `MAX_ROUNDS == 32`, yorum bugünkü zinciri ve kararı söyler | kırmızı |
| T2 | `test_chats_api.py` — `test_a_running_turn_reaches_the_browser_as_progress` | ilk `progress` `{"round": 1, "of": 32, "tokens": 0}` | kırmızı |
| T3 | `test_stream_answer.py` — `test_the_instruction_moves_to_the_end_of_every_round` ve `test_the_notice_is_the_requests_last_word`'ün yorumları | *"thirty-two"*; iddialar aynı | yeşil |

## Tutmadıkları

- Modelin 32 turda ne yaptığı — gerçek bir çağrıyla denenmez; kullanıcı sonunda dener.
- `dist` — ön uç değişmiyor.

## Nasıl görülür

CLAUDE.md'deki dört satır, olduğu gibi, paralel. `python -m pytest queen-agent -q`'da tam iki test
kırmızı (T1, T2), geri kalanı yeşil; öteki üç süit yeşil. Kırmızı commit'lenir.
