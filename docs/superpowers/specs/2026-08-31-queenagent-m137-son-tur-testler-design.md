# Madde 137 · Tur 1 (test) — Tasarım

**Kaynak:** kullanıcının 31 Ağustos'taki isteği, ve aynı gün `stream_answer` üzerinde yapılan hata
incelemesi. Yeni bir yol haritası açılmadı *(kullanıcı kararı, 31 Ağustos)*; numara
[v5 yol haritasının](../plans/2026-08-25-queenagent-v5-roadmap.md) kapanış kuralından geliyor —
*"madde nereye eklenirse eklensin 137'den devam eder."*
**Dal:** `feat/queenagent-m137-son-tur`.

## Sorun

Bir tur en çok 16 raunt sürüyor (`MAX_ROUNDS`). Model o 16 rauntu tool çağırmakla geçirip hiç düz
metin söylemezse — ve bu arada bir dosya da üretmemişse — `append_message` turu `EmptyMessage` ile
reddediyor ve **yapılan işin tamamı kayboluyor**. Kullanıcı bunu 70 tool call'lık bir koşuda gördü.

Kural yanlış değil: söz de söylemeyen, dosya da bırakmayan bir tur cevap değildir, ve
`append_message` bunu bilerek reddediyor *(dosya bırakan sessiz tur kaydediliyor; sınır orada)*.
Yanlış olan, **modele turun bittiğini kimsenin söylememesi**. Her raunt ötekinin aynısı gidiyor, o
yüzden 16. rauntta model hâlâ 17. rauntun geleceğini sanıyor: konuşmak yerine bir tool daha
çağırıyor, ve o çağrının cevabını okuyacak raunt yok.

`tools.py`'nin kendi cümlesi durumu zaten söylüyor — *"Reaching the limit is a stop, not a failure"*
— ama bugün limite çarpmak sessizce bir hata. Olması gereken, limite çarpmanın **cevaplanmış bir
tur** olması.

## Yol

Turun son rauntu kapanış rauntu olur, ve isteğe iki farkla gider:

1. İsteğin **en sonuna** bu rauntun son olduğunu söyleyen bir cümle eklenir. Cümle modelden ne
   yaptığını, ne kaldığını ve sıradaki adımın ne olduğunu söylemesini ister.
2. **Araç tanımları gönderilmez.** Model tool çağıramaz; üretebileceği tek şey metindir.

İkincisi olmadan birincisi bir rica olurdu, ve bugünkü hata zaten modelin turu yanlış okumasından
doğuyor — uyum bekleyen bir çare aynı yerden yeniden kırılır. Araç tanımlarının çekilmesi aynı şeyi
isteğin şekline yazıyor: çağıracak tool yoksa uyulacak rica da yok.

## Kurallar

- **`MAX_ROUNDS` 16'da kalıyor** *(kullanıcı kararı, 31 Ağustos)*. Bütçe 15 çalışma rauntu artı bir
  kapanış olarak bölünüyor. 17'ye çıkarıp çalışma bütçesini korumak seçilmedi — sayı zaten cömert
  seçilmişti.
- **`tools.py`'deki sayının yorumu düzelir.** Bugün *"Sixteen rounds carry it"* diyor; on beşi
  taşıyor ve on altıncısı kapatıyor. Kod ile çarpışan yorum koda uydurulur (CLAUDE.md).
- **Kapanış cümlesi `prompt.py`'de durur**, adı `LAST_ROUND`. Model-facing bir ürün davranışı, ve o
  dosya modele söylenenin evi. Dosyanın *"before every answer"* diyen docstring'i genişler: burada
  her cevaba değil, bir cevabın son rauntuna giden bir metin var.
- **Cümle isteğin son sözü olur** — skill yönergesinin de arkasına. 93 yönergeyi sona indirirken
  gerekçesi *sabit olan başta, değişen sonda* idi; yönerge tur boyunca sabit, bu cümle ise turda bir
  kez görünen en değişken parça. Aynı kural onu bir adım daha sona koyuyor.
- **Rauntun son olup olmadığını döngü bilir, `_asked` söyler.** `stream_answer`'ın döngüsü sayacını
  okur *(`MAX_ROUNDS - 1`)*, `_asked` bayrağı alıp cümleyi ekler, ve `tools` argümanı aynı bayrakla
  `None` gider. `tools=None` istemciye kadar iniyor ve `XaiClient._request` `if tools:` ile zaten
  anahtarı hiç yazmıyor — transport tarafında değişiklik yok.
- **`EmptyMessage` kuralı duruyor.** Bu madde turun konuşmasını sağlıyor, konuşmayan turu kabul
  etmeyi değil. Araçsız bir rauntta boş cevap dönmek bir motor anormalliği, ve *"cevap ya vardır ya
  yoktur"* çizgisi onun için konmuştu.
- **Erken biten tur cümleyi hiç görmez.** Model 5. rauntta konuşup durursa 16. raunt hiç
  başlamıyor, ve kapanış cümlesi o turun hiçbir isteğinde geçmiyor.
- **Kip ve izin kapısı etkilenmiyor.** Son rauntta çağrı olmadığı için sorulacak bir şey de yok;
  `needs_permission` oraya hiç ulaşmıyor.

## Bu turun testleri

Altyapı hazır: `ScriptedEngine` her rauntun teklif edilen araçlarını `self.tools`'a, gördüğü
mesajları `self.seen`'e zaten yazıyor. Yardımcılarda değişiklik yok.

`test_stream_answer.py`:

- `test_the_last_round_is_offered_no_tools` — **kırmızı**. Maddenin mekanizması: `engine.tools[-1]`
  boş, ve ondan önceki her raunt dolu.
- `test_the_last_round_says_it_is_the_last` — **kırmızı**. `engine.seen[-1]`'in son mesajı
  `LAST_ROUND` taşıyor.
- `test_the_notice_is_the_requests_last_word` — **kırmızı**. Skill yönergesi taşıyan bir sohbette
  cümle yönergeden *sonra* duruyor; 93'ün sırasını bu madde bozmuyor, uzatıyor.
- `test_a_turn_that_ends_early_never_sees_the_notice` — **kırmızı**. İki rauntta biten turun
  hiçbir isteğinde `LAST_ROUND` geçmiyor, ve her rauntu araçlarını almış.
- `test_the_loop_stops_at_the_round_limit_and_still_writes` — **bekçi**. Raunt sayısı 16'da
  kalıyor.
- `test_a_silent_turn_that_runs_out_of_rounds_is_not_an_answer_either` — **bekçi**, ve yeşil
  kalıyor: `ScriptedEngine` `tools` argümanını yok sayıp senaryosunu oynuyor, yani sahte motor
  gerçek modelin artık yapamayacağı şeyi yapmaya devam ediyor. Test kuralı ölçüyor, mekanizmayı
  değil — ve o kural duruyor.

`test_prompt.py`:

- `test_the_last_round_notice_says_no_tool_will_run` — **kırmızı**.
- `test_the_last_round_notice_asks_what_is_left` — **kırmızı**. İkisi birlikte kullanıcının
  isteğinin iki yarısı: *ne kaldı* ve *ne yapacaksın*.

`test_tools.py`:

- `test_the_round_limit_carries_the_longest_chain` — **bekçi**. `MAX_ROUNDS == 16` değişmiyor.

## Ayakta kalması gerekenler

92'nin tavanı ve `is_full`'ü, 93'ün yönerge sırası, 91'in kip kapısı, 124'ün `x-grok-conv-id`
başlığı, 129'un bağlam kabı, 133'ün dört sayısı, ve `append_message`'ın boş mesaj kuralı.

## Bilerek yapılmayanlar

**Ön yüz ve `dist`.** Madde ekranda yeni bir şey çizmiyor; değişen, var olan cevabın hata yerine
gelmesi.

**Harcama freni.** Aynı incelemenin ikinci yarısı — bir turun `usage`'ını hiçbir karar okumuyor, ve
`_boxed` her rauntta önbelleğe düşmeyen bir kopya gönderiyor. Gerçek bir turun sayılarına
bakılmadan girilmemeli, ve kullanıcı bu maddeyi istedi. Ayrı iş.

**`MAX_ROUNDS`'un yeniden ölçülmesi.** 15 çalışma rauntunun yetmediği görülürse kendi maddesi olur;
bugün bunu söyleyen bir gözlem yok.
