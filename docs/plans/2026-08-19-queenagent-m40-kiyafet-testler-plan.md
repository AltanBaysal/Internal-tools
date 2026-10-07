# Madde 40 — Yapıya kıyafet giriyor · Test Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m40-kiyafet-testler-design.md](../specs/2026-08-19-queenagent-m40-kiyafet-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

Bu plan **yalnız testleri** yazar.

---

## Adım 1 — `test_build_prompts.py`

`_frame`'in varsayılan karakter alanı harita olur (`{"aylin": []}`), sabitlere `GECELIK`, `GUNLUK`,
`ATKI` girer, `_structure`'a `outfits` haritası eklenir. Var olan testler yeni şekle taşınır;
üstüne on test:

1. `test_a_frames_outfit_follows_its_character` — kimlik, hemen ardından kıyafet.
2. `test_two_outfits_keep_the_order_they_were_written_in`
3. `test_each_characters_block_stays_together` — iki karakter, iki blok, araya karışma yok.
4. `test_a_character_with_no_outfit_is_just_the_identity`
5. `test_a_frame_with_nobody_in_it_still_builds` — `{}`.
6. `test_the_old_list_of_names_is_read_as_names_without_outfits` — `["aylin"]` *(bugün de geçer)*.
7. `test_a_single_outfit_written_without_a_list_is_read_as_one`
8. `test_an_unknown_outfit_names_the_frame_and_what_is_known`
9. `test_an_unknown_character_in_the_map_form_is_reported_too`
10. `test_a_structure_with_no_outfits_map_still_builds` *(bugün de geçer)*.

## Adım 2 — `test_skills.py`

- Şema alan listesine `outfits` girer.
- **Yeni:** `test_the_structured_instruction_shows_the_frames_characters_as_a_map` — yönergede
  karede karakter alanının harita olduğu, örneğiyle görünür.
- **Yeni:** `test_the_structured_instruction_says_what_belongs_where` — kalıcı `characters`'ta,
  değişebilen `outfits`'te.
- **Yeni:** `test_the_rulebook_calls_clothing_in_the_wrong_place_a_violation` — `RULEBOOK` kıyafetin
  kimliğe ya da action'a yazılmasını sayar.
- **Yeni:** `test_the_character_instruction_leaves_clothing_out_of_the_identity` — karakter
  yönergesi kıyafeti kimliğin dışında tutar.

## Adım 3 — `test_tools.py` ve `test_stream_answer.py`

İki dosyadaki `STRUCTURE` sabiti yeni şekle taşınır (harita hâli + `outfits`), böylece uçtan uca
akan yapı da yeni şema olur.

## Adım 4 — Kırmızıyı gör, commitle

Geçmesi beklenen iki test: eski liste hâli ve `outfits`'siz yapı. Gerisi düşer.

---

## Kapanış denetimi

- `git status` yalnız test dosyalarını gösteriyor.
