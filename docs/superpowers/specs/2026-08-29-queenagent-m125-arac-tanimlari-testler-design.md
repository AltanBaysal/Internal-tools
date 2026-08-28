# Madde 125 · Tur 1 (test) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 125
**Dal:** `feat/queenagent-m123-skill-rewrite`.

## Sorun

Madde 107 tabana *"never to check your own writing"* cümlesini yazdı. Ama her istekte, taban
yönergeden çok daha yakında — araç tanımlarının içinde — iki koşulsuz emir duruyor:

- `edit_file`: *"so read the file first and include enough of what surrounds it"*
- `write_plan`: *"so read it first and hand back the whole plan"*

Altıncı denemedeki `create_file` → `read_file` → `edit_file` zinciri ile üç plan yazımı bunun
doğrudan ürünü. Zayıf model, düzyazı ricayı değil, tam çağıracağı aracın tanımını dinliyor.

## Düzeltmenin sınırı

İki tanım cümlesi koşullanır; kod, parametreler ve araç adları değişmez. Koşul ikisinde de aynı
sözle yazılır ki model iki ayrı kural okuduğunu sanmasın: **bu turda görülmemişse okunur**, bu
turda okunan ya da yazılan zaten elin altındadır.

## Bu turun testleri (ikisi de kırmızı doğar)

`test_tools.py` — iki test:

- `test_the_edit_tool_asks_for_a_read_only_when_the_turn_has_not_seen_the_file`:
  `edit_file` tanımında `if this turn has not seen it` ve `already in front of you` geçer;
  koşulsuz `so read the file first` **geçmez**.
- `test_the_plan_tool_does_not_demand_a_read_of_what_the_turn_just_wrote`:
  `write_plan` tanımında `if this turn has not seen it` geçer; `so read it first` **geçmez**.

## Ayakta kalması gerekenler

- `test_write_plan_ends_only_the_turn_that_was_asked_to_plan` (`asked only to plan`, `carry on`).
- `edit_file`'ın *"appear exactly once and match what is on disk now"* şartı — okuma koşullanıyor,
  eşleşme şartı değil; kaldırılırsa `_edit`'in çoklu-eşleşme reddi anlaşılmaz olur.
- `write_plan`'ın *"the whole plan rather than the part you changed"* şartı: araç dosyayı baştan
  yazıyor, yarım içerik veren çağrı planı siler.
- `test_every_tool_is_declared_to_the_model` — bu madde araç eklemez, çıkarmaz *(çıkarma 127'nin)*.

## Bilerek yapılmayanlar

Taban yönerge, skill metinleri ve `run_tool` ellenmez; `list_files` bu maddede durur.
