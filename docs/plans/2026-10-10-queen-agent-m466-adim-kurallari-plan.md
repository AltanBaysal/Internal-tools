# Madde 466 — Adım kuralları tek sözlükle, plan

> **Koşum:** ana klasörde, `feat/queenagent-v10` dalında, **commit'lenmeden** ve hiçbir şey stage
> edilmeden. Modele giden metni ana agent okur ve commit'ler. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** `SYSTEM_PROMPT`'un döngüsü tek sözlükle anlatılır; biten plan adımı dosyada işaretlenir;
soru turun son şeyidir; adımı bitirmek Remember'da tekrarlanır; Start a scenario ilerlemeyi planın
işaretlerinden okur.

**Yaklaşım:** önce testler, kırmızı görülür, sonra metin. Dosyalar Edit ile değişir.

**Spec:** [m466](../specs/2026-10-10-queen-agent-m466-adim-kurallari-design.md)

## Görev 1: Testler — `queen-agent/backend/tests/test_prompt.py`

- [ ] `_a_line_says`'in yanına `_section(heading)`: başlığın altındaki bölümün satırları, küçük harfle;
  böyle bir bölüm yoksa boş. 465'in testi bölümü bununla bulur.
- [ ] `LOOP` ve `test_the_loop_has_one_vocabulary`: How you work'ün numaralı adımlarının adları ve
  Planning'in `one at a time` satırı üç evreyi de taşır.
- [ ] `test_a_plan_files_done_step_is_marked_before_the_next`: Planning'in bir satırı `plan file`,
  `done`, `edit_file`, `before`, `next`'i birlikte söyler.
- [ ] `test_a_question_ends_the_turn_and_comes_last`: Asking'in bir satırı `question`, `ends`, `turn`,
  `last`'ı birlikte söyler.
- [ ] `test_the_three_core_rules_close_the_text` → `test_the_core_rules_close_the_text`: sayı ve sıra
  yerine kurallar; dördüncüsü `finish`, `step`, `next`.
- [ ] `python -m pytest queen-agent/backend/tests/test_prompt.py -q`: dördü kırmızı, doğru sebeple.

## Görev 2: Metin — `queen-agent/backend/features/workspace/domain/prompt.py`

- [ ] How you work: 1. *Gather context*, 3. *Take action*, 4. *Verify results*.
- [ ] Planning: plan dosyası satırının altına işaretleme satırı.
- [ ] Asking: sonuna soru satırı.
- [ ] Remember: dördüncü satır.
- [ ] Aynı testler: yeşil.

## Görev 3: Akış aynı şeyi söyler (reviewer'dan sonra; kullanıcı, 10 Ekim — "işaretlesin model sıkıntı yok, şu an model daha güçlü")

- [ ] `test_prompt.py`: `test_the_loop_has_one_vocabulary` adı `partition`'la alır; `. ` olmayan
  numaralı satır assertion'la kırılır.
- [ ] `test_skills.py`: `test_where_the_work_stopped_is_read_off_the_files` →
  `test_where_the_work_stopped_is_read_off_the_plans_marks` (1. adımın bir satırı `marked`,
  `how far the work got`, `files of the project`).
- [ ] `test_skills.py`: `test_no_step_is_ticked_off_the_plan_at_all` →
  `test_a_step_is_marked_with_edit_file_by_the_base` (akış ne `mark_step_done` ne `edit_file` anar;
  tabanın bir satırı `plan file`, `mark`, `edit_file`).
- [ ] `test_skills.py`: çekilen kurala yaslanan iki yorum düzelir.
- [ ] `python -m pytest queen-agent/backend/tests/test_skills.py -q`: 1. adım testi kırmızı.
- [ ] `prompt.py`, `START_A_SCENARIO` 1. adım: *"The plan's marked steps show how far the work got,
  and the files of the project confirm it."*
- [ ] Aynı testler: yeşil.
- [ ] `test_skills.py`: `test_the_plan_gives_both_the_empty_and_the_done_shape` (1. adım `- [ ] 1.`
  ve `- [x] 1.`'i verir); kırmızı.
- [ ] `prompt.py`, `START_A_SCENARIO` 1. adım: boş kutunun ardından *"A done step reads - [x] 1. write
  the plan."*; yeşil. Akış 1830 kelimelik sınırın altında kalır.

## Görev 4: Dört suite, sırayla

- [ ] `python -m pytest queen-agent -q`
- [ ] `npm test --prefix queen-agent/frontend`
- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend`
