# Madde 107 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 107
**Dal:** `feat/queenagent-m123-skill-rewrite` — kullanıcı onayı 29 Ağustos.

## Sorun

Colab denemesi: "Nerde kaldık" gibi tek satırlık bir mesaj sekiz araç çağrısı ve 19.2k token
tüketti. Kaynağı ritüel cümleler: taban yönerge her dosyanın her adımda yeniden okunmasını,
akış her turun list_files + write_plan ile açılmasını, iki skill de şemanın her yazımdan önce
yeniden çekilmesini söylüyor. Model bu cümleleri "her turda tekrar yap" diye okuyor — kendi
yazdığını bile geri okuyor.

## Düzeltmenin sınırı

Dört cümle düzeltilir, kod değişmez:

1. **Taban (prompt.py):** taze okuma yalnız *başkasının değiştirmiş olabileceği* dosya için;
   kendi yazdığını doğrulamak için asla; cevabın gerek duymadığı hiçbir şey okunmaz.
2. **Akış, adım 1:** list_files + write_plan bir sohbetin *ilk* turuna aittir; sonraki turlar
   sohbetin zaten bildiğinden devam eder.
3. **Akış, adım 2:** şema *bir kez*, dosyanın doğumundan önce çekilir; sonraki edit'ler
   yeniden çekmez.
4. **Prompt+:** şema *bir kez*, ilk yazımdan önce.

## Bu turun testleri (beşi de kırmızı doğar)

`test_prompt.py` — iki test:

- `test_a_fresh_read_is_for_what_someone_else_may_have_changed`: pin
  `somebody else may have changed` ve `never to check your own writing`; eski cümlenin
  yokluğu da pinlenir (`not the same as reading it now` metinde olmayacak).
- `test_the_base_reads_nothing_the_answer_does_not_need`: pin
  `nothing the answer does not need`.

`test_skills.py` — üç test:

- `test_the_opening_moves_belong_to_the_first_turn`: pin `A chat's first turn` ve
  `carry on from what the chat already knows`.
- `test_the_flow_fetches_the_schema_once`: pin `once, before the birth` ve
  `do not fetch it again`.
- `test_the_builder_fetches_the_schema_once`: pin `once, before the first write`.

## Ayakta kalması gerekenler

- `test_the_base_looks_before_it_writes` (`read it first`) — taze okuma daraltılır,
  okuma silinmez.
- `test_the_base_names_no_task` — yeni cümleler görev kelimesi taşımaz.
- `test_the_flow_writes_the_plan_before_it_asks_anything` — write_plan hâlâ şemadan önce.
- `test_the_structure_file_is_born_once` — şema hâlâ `born once`tan önce.
- `test_the_texts_stay_short_enough_to_be_read` — tavanlar (450 / 300) aşılmaz; giren
  kelime kadar kelime silinir. Bu ikinci turun işi.

## Bilerek yapılmayanlar

Bu tur skills.py ve prompt.py'a dokunmaz; x-grok-conv-id başlığı Madde 124'ündür.
