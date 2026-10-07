# Madde 137 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-31-queenagent-m137-son-tur-testler-design.md](../specs/2026-08-31-queenagent-m137-son-tur-testler-design.md)
**Dal:** `feat/queenagent-m137-son-tur`
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## 0. `LAST_ROUND` fonksiyon içinden import edilir.

Sabit henüz yok. Modül başında import edilirse `test_prompt.py` ile `test_stream_answer.py`
toplanamaz, ve iki dosyanın **bütün** testleri hata verir — altı kırmızı yerine seksen hata, ve
maddenin kendi kırmızısı onların içinde kaybolur. Fonksiyon içinden çağrıldığında yalnız yeni
testler düşüyor. Ev bu deseni zaten kullanıyor: `test_stream_answer.py`'deki `allowed()` ve
`refused()` `Decision`'ı içeriden alıyor.

Uygulama turunda oldukları yerde kalıyorlar; sabit doğduktan sonra da doğru çalışıyorlar, ve
taşımak bu maddenin işi değil.

## A. `test_prompt.py`: iki kırmızı — kullanıcının isteğinin iki yarısı.

- `test_the_last_round_notice_says_no_tool_will_run` — cümle, o rauntta tool çalışmayacağını
  söylüyor.
- `test_the_last_round_notice_asks_what_is_left` — cümle, ne kaldığını ve sıradaki adımı soruyor.

Dosyanın bugünkü on dört bekçisi `SYSTEM_PROMPT`'u ölçüyor ve ellenmiyor.

## B. `test_stream_answer.py`: dört kırmızı.

Altyapı hazır — `ScriptedEngine` her rauntun teklif edilen araçlarını `self.tools`'a, gördüğü
mesajları `self.seen`'e zaten yazıyor. Yardımcılara dokunulmuyor.

- `test_the_last_round_is_offered_no_tools` — `MAX_ROUNDS` boyu tool çağıran bir senaryoda
  `engine.tools[-1]` boş, ve ondan önceki her raunt dolu. Maddenin mekanizması.
- `test_the_last_round_says_it_is_the_last` — `engine.seen[-1]`'in son mesajı `LAST_ROUND` taşıyor.
- `test_the_notice_is_the_requests_last_word` — skill seçilmiş bir sohbette cümle **yönergeden
  sonra** duruyor. 93'ün sırasını bu madde bozmuyor, uzatıyor. `_said_with` tek raunt koştuğu için
  kullanılamıyor; kurulum `_seeded` + `append_message(..., skill="generate-prompts-plus")` ile
  yerinde yapılıyor.
- `test_a_turn_that_ends_early_never_sees_the_notice` — iki rauntta biten turun hiçbir isteğinde
  `LAST_ROUND` geçmiyor, ve her rauntu araçlarını almış.

**Bekçiler, ikisi de yeşil kalmalı:**
`test_the_loop_stops_at_the_round_limit_and_still_writes` *(raunt sayısı 16'da kalıyor)* ve
`test_a_silent_turn_that_runs_out_of_rounds_is_not_an_answer_either` — ikincisi yeşil kalıyor çünkü
`ScriptedEngine` `tools` argümanını yok sayıp senaryosunu oynuyor: sahte motor gerçek modelin artık
yapamayacağını yapmaya devam ediyor. Test kuralı ölçüyor, mekanizmayı değil.

## C. `test_tools.py`: bekçi, dokunulmuyor.

`test_the_round_limit_carries_the_longest_chain` — `MAX_ROUNDS == 16` değişmiyor, ve yeşil kalmalı.

## D. Koşuldu: **6 kırmızı, 647 yeşil.**

`python -m pytest queen-agent -q` — planlanan altısı, ve yalnız onlar. Fonksiyon-içi import kararı
tuttu: iki dosyanın geri kalan testleri toplanıp yeşil koştu, hiçbiri maskelenmedi.

Beşi `ImportError: cannot import name 'LAST_ROUND'` — sabit henüz yok. Altıncısı,
`test_the_last_round_is_offered_no_tools`, gerçek bir `AssertionError` veriyor ve maddenin cümlesini
sayıyla söylüyor: **son raunt bugün sekiz araç teklif ediliyor**, boş liste bekleniyor. Kırmızıların
tek doğru olanı bu — ötekiler bir adın yokluğunu, bu bir davranışın yanlışlığını gösteriyor.

**Üç bekçi de yeşil:** `test_the_loop_stops_at_the_round_limit_and_still_writes`,
`test_a_silent_turn_that_runs_out_of_rounds_is_not_an_answer_either` *(beklendiği gibi — sahte motor
`tools` argümanını yok sayıyor)* ve `test_the_round_limit_carries_the_longest_chain`.

**`npm test --prefix queen-agent/frontend` koşulamadı:** cihazda Node kurulu değil *(31 Ağustos,
kullanıcı bilgisayarı sıfırladı; Python aynı gün kuruldu)*. Bu madde ön yüze dokunmuyor, ama komut
koşulmadığı için yeşil olduğu **görülmedi** — Node kurulunca koşulacak.

## E. Kırmızı commit.

## Bilerek yapılmayanlar

`skip`/`xfail` yok. Kod ellenmez — `prompt.py`, `stream_answer.py` ve `tools.py` bu turda
değişmiyor. Ön yüz ve `dist` ellenmez.
