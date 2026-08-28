# Madde 126 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 126
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

Altıncı denemede tek bir adımın kapanışı plana üç yazım tuttu: `write_plan`, sonra `edit_file`,
sonra yine `write_plan`. Akış metninin cümlesi — *"An approved step's line in the plan is marked
done."* — işaretlemenin **ne** olduğunu söylemiyor; model iki mekanizmayı da deniyor, ve
`write_plan` dosyanın tamamını yeniden yazdığı için her deneme bir tam plan üretiyor.

Madde 125 `write_plan`'ın tanımındaki koşulsuz okumayı kaldırdı; bu madde diğer yarısını yapıyor:
işaretleme **tek bir satır düzenlemesidir**, yeniden yazım değil.

## Bu turun testi (kırmızı doğar)

`test_skills.py` · `test_a_finished_step_is_marked_with_one_edit`:
akış metninde `marked done with one edit_file` ve `never a rewrite` geçer.

## Ayakta kalması gerekenler

- `test_a_finished_step_reaches_the_plan` (`marked done`) — yeni cümle onu içeriyor.
- `test_the_flow_carries_on_from_a_plan_that_is_already_there`, adım 1'in `write_plan`'ı: planın
  **doğduğu** yazım `write_plan`'dır ve öyle kalır; değişen yalnız adım kapatma.
- `test_the_texts_stay_short_enough_to_be_read` — tavan 450; giren kelimeler kadar kelime silinir
  *(ikinci turun işi)*.

## Bilerek yapılmayanlar

`tools.py` ellenmez *(125'te düzeldi)*; prompt+ metni bu maddede durur — plan akışın işidir.
