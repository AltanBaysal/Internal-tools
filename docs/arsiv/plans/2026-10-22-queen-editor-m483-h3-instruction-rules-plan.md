# Madde 483 · H3'ün video talimatına üç kural — plan

**Spec:** [2026-10-22-queen-editor-m483-h3-instruction-rules-design.md](../specs/2026-10-22-queen-editor-m483-h3-instruction-rules-design.md)
· **Dal:** `feat/queen-editor-v10` · Test önce (TDD).

1. `queen-editor/backend/tests/test_video_prompt_writer.py` — üç kuralın talimatta kelimesi
   kelimesine durduğunu, ve Mutlu son'un *"her moans"* deyip *"groans"* demediğini soran dört test.
   Kırmızı.
2. `queen-editor/backend/features/photo_generation/data/prompt_writer.py`:
   - `H3_VIDEO_INSTRUCTION`'ın `Rules`'unda `overall_soundscape` satırının arkasına üç kural;
   - `HAPPY_ENDING_RULE`'da *"the moans or groans"* → *"her moans"*;
   - iki sabitin yorumuna madde 483 ve sebep.

   Yeşil.
3. `python -m pytest queen-editor -q`.
