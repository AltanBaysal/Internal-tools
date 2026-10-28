# Madde 43 — Kare açıklaması 1-2 cümle · Test Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m43-kare-uzunlugu-testler-design.md](../specs/2026-08-19-queenagent-m43-kare-uzunlugu-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `test_skills.py`

Üç test eklenir:

1. `test_a_frame_is_one_or_two_sentences` — sayı açıkça yazar.
2. `test_the_frame_instruction_no_longer_says_one_line` — kaldırılan biçim tarifi geri gelmesin.
3. `test_a_frame_is_still_not_a_paragraph` — uzun anlatım yasağı durur *(bugün de geçer)*.

## Adım 2 — Kırmızıyı gör, commitle

1 ve 2 düşer, 3 geçer.

---

## Kapanış denetimi

- `git status` yalnız `test_skills.py`'ı gösteriyor.
