# Madde 133 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 133
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

`stream_answer` her raundun `sent`'ini bir öncekinin üstüne ekliyor, yani `usage.sent` bir turun
**bütün raundlarının toplamı**. Üç yer o sayıyı okuyor ve yalnız biri doğru okuyor:

| Okuyan | Ne soruyor | Toplam doğru cevap mı |
|---|---|---|
| Mesajın altındaki kart *(83)* | bu cevap kaça mal oldu | **evet** |
| Composer'ın dairesi *(92)* | ne kadar doldum | hayır |
| `is_full` *(92)* | durmalı mıyım | hayır |

Sekizinci denemede iki mesajlık bir sohbet kapandı: turlar 6 ve 5 adımdı, toplamları 48.8k ve
51.4k, ve gerçek bağlam ~10-12k. Tavanın kendi açıklaması bir **istek boyu** hakkında konuşuyor
*("models get worse as the input grows and what sits in the middle of a long request goes
unread")*, ve `last_sent`'in docstring'i varsayımı yazmış: *"no single turn is large enough to
cross it on its own."* Yanlış olan o varsayım.

## Yol

`Usage` dördüncü bir sayı taşır: **turun son raundunun `sent`'i**, yani tur bittiğindeki bağlam
boyu. Tavan ve daire onu okur; kart toplamı okumaya devam eder.

Neden saklanıyor: toplamdan son raundu geri çıkarmanın yolu yok. Yeni bir disk alanı, ama göç yok
— eski kayıtlar 0 okuyor, ve 0 hiçbir sohbeti dolu yapmıyor.

## Kurallar

- **Ad:** `Usage.context`. Uçtaki `context: {sent, ceiling}` nesnesi zaten bu adı taşıyor.
- **Fonksiyon adı düzelir:** `last_sent` → `last_context`. Eski ad artık yalan söylerdi.
- **Uçtaki JSON şekli değişmiyor.** `context.sent` anahtarı duruyor — değişen yalnız hangi sayıyı
  taşıdığı. Ön yüz hiç değişmiyor, `dist` derlenmiyor.
- **Mesajın `usage` nesnesine yeni alan eklenmiyor.** Ekran onu çizmiyor, ve çizilmeyen bir sayıyı
  yollamak FOUNDATION 3'e çarpıyor. Diske yazılıyor, uçtan gitmiyor.
- **Tavan 50k'da kalıyor** *(kullanıcı kararı)*. Sohbetler kabaca beş kat uzuyor, ve bu bilinen
  sonuç.
- **Sıfırın anlamı değişmiyor:** ölçülmemiş demek, ve ölçülmemiş bir sohbet dolu değil.

## Bu turun testleri

`test_chat.py`:

- `_answered` yardımcısı ikinci bir sayı alır *(varsayılan: `sent` ile aynı)* — **değişen**
- `test_the_ceiling_ignores_what_the_rounds_added_up_to` — **kırmızı**, maddenin tek cümlesi
- `test_an_answer_from_before_the_field_never_fills_the_chat` — **kırmızı**
- `test_the_ceiling_is_read_off_the_last_answer` ve `test_a_chat_with_no_answer_yet_has_sent_nothing`
  yeni adı çağırır — **değişen**
- `test_the_ceiling_is_fifty_thousand` ve `test_a_chat_is_full_at_the_ceiling_and_not_before` —
  bekçi

`test_stream_answer.py`:

- `test_the_answer_remembers_what_it_spent` ve `test_what_two_rounds_spent_is_added_up` dördüncü
  sayıyı bekler — **değişen**, ve ikisi birden maddenin ayrımını gösteriyor: toplam ile son raunt
  bir turda aynı, iki turda değil
- `test_the_turn_remembers_what_its_last_round_carried` — **kırmızı**

`test_file_chat_store.py`:

- `test_the_last_rounds_size_survives_a_round_trip` — **kırmızı**
- `test_a_stored_usage_from_before_the_field_reads_zero` — bekçi

`test_chats_api.py`:

- `test_the_record_says_how_much_of_the_ceiling_it_has_used` — bekçi *(tek raundluk turda iki sayı
  aynı, o yüzden yeşil kalıyor ve kalmalı)*

## Ayakta kalması gerekenler

83'ün kartı ve okuduğu sayı, 76'nın ölçüsü, 92'nin tavanı ve dairesi, 124'ün önbellek payı,
`is_owed_an_answer`, ve cevapsız bir soruyu atlayarak geriye yürüme kuralı.

## Bilerek yapılmayanlar

Göç, ön yüz, `dist`. 134 ile 135 ayrı maddeler.
