# Madde 131 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m131-satir-numarasi-testler-design.md](../specs/2026-08-29-queenagent-m131-satir-numarasi-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_tools.py`: okumanın biçimi, şemanın muafiyeti, eşleşmenin değişmezliği — yedi test.

## B. `test_tools.py`: `test_reading_gives_the_contents` numaralı hâli bekler.

## C. `test_stream_answer.py`: kabın aynı biçimi taşıması — iki test.

## D. İki komut koşuldu. **5 kırmızı, 5 bekçi yeşil**, frontend 568 yeşil, defter çifti bilinen kırmızı.

Kırmızı olanlar davranışın değiştiği yerler: `test_a_read_hands_back_numbered_lines`,
`test_the_numbers_are_right_aligned_so_the_text_starts_in_one_column`,
`test_the_edit_tool_tells_the_model_to_drop_the_numbers`, `test_reading_gives_the_contents`,
`test_the_box_numbers_the_lines_it_shows`.

Yeşil doğanlar bekçi, ve bekçi oldukları için yazıldılar — değişmemesi gereken şeyi tutuyorlar:
boş dosya *(numaralı okumada `1` yazan bir satır doğabilirdi)*, satır sayımı *(`outcome` gösterilen
metnin değil dosyanın satırlarını sayar)*, şemanın numaralanmaması, `_edit`'in diske bakması, ve
kap ile okumanın tek biçim olması. Beşi de uygulama turunda yeşil kalmak zorunda.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez; `offset`/`limit` ve `replace_all` yok.
