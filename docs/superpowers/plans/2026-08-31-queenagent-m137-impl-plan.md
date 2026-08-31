# Madde 137 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-31-queenagent-m137-son-tur-uygulama-design.md](../specs/2026-08-31-queenagent-m137-son-tur-uygulama-design.md)
**Kırmızı commit:** `24b92b1`
**Bu tur test dosyalarına dokunmaz.** Kırmızılar yazıldığı gibi yeşile dönmeli; dönmüyorsa
değişecek olan kod, test değil.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `prompt.py`: `LAST_ROUND` doğar, docstring genişler.

Metin dört şeyi söylemek zorunda — testler çiviledi: *last round*, *no tool*, *what is left*,
*next step*. `SYSTEM_PROMPT`'a eklenmiyor; ayrı sabit, ayrı biniyor.

Docstring bugün *"before every answer"* diyor ve artık dosyada her cevaba gitmeyen bir metin var.

## B. `stream_answer.py`: `_asked` beşinci parametreyi alır, erken `return` düşer.

`last=False` eklenir, doğruyken `LAST_ROUND` **en sona** gider. `if not instruction: return asked`
kaldırılır — skill seçilmemiş bir sohbette kapanış cümlesi o kapıdan geçemezdi, ve
`test_the_last_round_says_it_is_the_last` tam o durumu koşuyor. Her parça kendi `if`'i, tek `return`.

## C. `stream_answer.py`: döngü rauntu tanır.

`for _ in range(MAX_ROUNDS)` → `for index in range(MAX_ROUNDS)`, ve `last = index == MAX_ROUNDS - 1`.
`last` iki yere gider: `_asked`'a, ve `tools=None if last else TOOL_SPECS`.

## D. `tools.py`: `MAX_ROUNDS`'un yorumu düzelir.

*"Sixteen rounds carry it"* artık yanlış — on beşi taşıyor, on altıncısı kapatıyor. Sayı duruyor.

## E. Koşuldu: **653 yeşil, 0 kırmızı.**

`python -m pytest queen-agent -q` — 647 + 6, tam beklenen sayı. Altı kırmızının altısı da yazıldığı
gibi yeşile döndü ve hiçbir bekçi düşmedi; testlere dokunulmadı.

**`npm test --prefix queen-agent/frontend` yine koşulamadı:** Node hâlâ kurulu değil. Madde ön yüze
dokunmuyor ve `dist` derlenmedi, ama komut koşulmadığı için yeşil olduğu **görülmedi** — Node
kurulunca koşulacak. Bu turun tek doğrulanmamış satırı.

## F. Yeşil commit.

## Bilerek yapılmayanlar

Test dosyaları ellenmez. `MAX_ROUNDS` sayısı değişmez. Harcama freni bu maddenin işi değil. Ön yüz
ve `dist` derlenmez.
