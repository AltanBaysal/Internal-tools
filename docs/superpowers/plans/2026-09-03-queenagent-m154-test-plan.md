# Madde 154 — Test turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m154-haritalar-testler-design.md) ·
**Tur:** test *(kırmızı commit'lenir)*

Yalnız testler. `tools.py`, `modes.py`, `build_prompts.py`'ye dokunulmuyor.

---

## 1. `test_tools.py` — `create_structure`

- **`test_create_structure_writes_an_empty_skeleton`** — dört anahtar, dördü de boş.
- **`test_create_structure_forces_the_json_extension`** — `bar-scene` → `bar-scene.json`.
  `safe_name` tek başına `.md` ekliyor, ve yapı dosyası olmayan bir yapı dosyası doğardı.
- **`test_create_structure_refuses_a_name_that_is_taken`** — ret, ve var olan dosya aynı kalıyor.
- **`test_create_structure_draws_a_card`** — `created` dolu; dosya doğuran araçların kuralı.

## 2. `test_tools.py` — `set_character`

- **`test_set_character_adds_a_new_one`** — girdi `{"kind": …, "tags": …}` şeklinde.
- **`test_set_character_changes_the_one_that_is_there`** — ikinci girdi doğmuyor, harita hâlâ tek.
- **`test_set_character_says_whether_it_added_or_changed`** — iki çağrı, iki farklı cevap.
- **`test_changing_a_character_says_how_many_frames_name_it`** — düzeltmenin yarıçapı.
- **`test_a_kind_that_is_neither_girl_nor_boy_is_refused`** — ret, harita değişmiyor.
- **`test_set_character_refuses_a_file_that_is_not_there`** — ret, ve **dosya doğmuyor**; bir yazım
  hatası sessizce ikinci bir senaryo kurmasın.

## 3. `test_tools.py` — `set_outfit` ve `set_location`

- **`test_set_outfit_adds_and_changes`**
- **`test_set_location_adds_and_changes`**
- **`test_only_a_character_carries_a_kind`** — diğer iki aracın tanımında `kind` yok.

## 4. `test_tools.py` — kurallar açıklamalara taşındı

- **`test_the_character_tool_says_clothing_belongs_elsewhere`**
- **`test_the_outfit_tool_says_one_entry_dresses_one_person`**

## 5. `test_build_prompts.py` — iki şekil

- **`test_a_character_written_with_a_kind_still_builds`** — yeni şekil.
- **`test_a_character_written_as_plain_text_still_builds`** — eski şekil; bugün de yeşil.
- **`test_a_preview_reads_both_shapes_too`** — `build_character_prompts` için ikisi birden.

## 6. `test_modes.py` — dördünün yeri

- **`test_the_new_structure_tools_run_without_asking_in_edit`**
- **`test_the_new_structure_tools_ask_in_plan_and_ask`**

## 7. Koş, kırmızıyı gör, commit'le

```
python -m pytest queen-agent -q
```

Diğer üç satır ardışık koşulur.

`test(m154): …`
