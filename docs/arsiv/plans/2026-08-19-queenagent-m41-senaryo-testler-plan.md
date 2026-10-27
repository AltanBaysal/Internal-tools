# Madde 41 — Senaryo kısa ve madde madde · Test Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m41-senaryo-testler-design.md](../specs/2026-08-19-queenagent-m41-senaryo-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `test_skills.py`

`test_the_scenario_instruction_says_how_long_and_where_it_goes` düşer; yerine altı test:

1. `test_the_scenario_instruction_no_longer_counts_sentences` — "10 to 15" ve "plain prose" yok.
2. `test_the_scenario_instruction_asks_for_a_list` — maddeler istenir.
3. `test_the_scenario_instruction_says_why_it_stays_short` — amacı: ne anlaşıldığını görmek.
4. `test_the_scenario_file_is_named_after_its_subject` — sabit `scenario.md` yok, örnek ad var.
5. `test_a_correction_reaches_the_scenario_file_too` — `create_file` ve `edit_file` birlikte geçer.
6. `test_the_scenario_still_goes_into_the_chat_as_well` — dosya cevabın yerine geçmez.

## Adım 2 — Kırmızıyı gör, commitle

1-5 düşer; 6 geçer (kural bugün de var, tur boyunca bozulmasın diye tutuluyor). Başka hiçbir test
düşmemeli.

---

## Kapanış denetimi

- `git status` yalnız `test_skills.py`'ı gösteriyor.
