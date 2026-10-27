# Madde 44 — Kare listesi konuşulan dilde ve dosyada · Test Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m44-kare-dili-testler-design.md](../specs/2026-08-19-queenagent-m44-kare-dili-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `test_skills.py`

`test_only_the_frame_split_still_stays_in_the_chat` düşer — kare bölme de dosya yazıyor artık.
Yerine altı test:

1. `test_the_frame_list_comes_in_the_users_own_language`
2. `test_the_frame_list_leaves_the_translating_to_the_prompt_skills`
3. `test_the_frame_list_reaches_a_file_too` — `create_file` ve `edit_file`.
4. `test_the_frame_file_is_named_after_the_subject` — `-frames` eki, örneğiyle.
5. `test_the_frame_split_no_longer_stays_in_the_chat`
6. `test_verify_is_the_one_skill_that_writes_nothing` *(bugün de geçer)*.

## Adım 2 — `skills.test.js`

`the two that produce nothing on disk say so in the menu` düşer. Yerine:

7. `no row promises to stay in the chat any more`
8. `the rows that write a file say so`

## Adım 3 — Kırmızıyı gör, commitle

---

## Kapanış denetimi

- `git status` yalnız iki test dosyasını gösteriyor.
