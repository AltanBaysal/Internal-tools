# Madde 42 — Karakter dosyaya, sayı kullanıcıya · Test Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m42-karakter-testler-design.md](../specs/2026-08-19-queenagent-m42-karakter-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `test_skills.py`

`test_the_character_instruction_asks_for_candidates_and_leaves_quality_out`'un aday cümlesi yeni
kurala taşınır; `test_the_two_chat_only_skills_say_they_write_no_file` yalnız
`split-into-frames`'i tutar. Üstüne altı test:

1. `test_the_character_count_comes_from_the_user` — "two or three" yok; sayı söylenmediyse sorulur.
2. `test_the_character_candidates_go_into_a_file` — `create_file` var, sohbette kalma cümlesi yok.
3. `test_the_character_file_is_named_after_the_character` — örneğiyle.
4. `test_the_character_file_has_the_shape_of_the_structure` — `characters` ve `outfits` girdileri.
5. `test_a_pasted_prompt_is_read_as_a_format_example` — kareye ait olanlar ayıklanır.
6. `test_only_the_frame_split_still_stays_in_the_chat` — sohbette kalan tek beceri.

## Adım 2 — Kırmızıyı gör, commitle

Altısı da düşer.

---

## Kapanış denetimi

- `git status` yalnız `test_skills.py`'ı gösteriyor.
