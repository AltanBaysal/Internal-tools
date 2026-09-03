# Madde 155 — Test turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m155-sahne-testler-design.md) ·
**Tur:** test *(kırmızı commit'lenir)*

Yalnız testler. `tools.py`, `ports.py`, `xai_engine.py`, `modes.py`, `skills.py`,
`stream_answer.py`'ye dokunulmuyor.

---

## 1. Sahte motor

`test_tools.py`'ye küçük bir `ScriptedWriter`:

- `write_once(system, user, model)` çağrılarını kaydediyor.
- Sırayla cevap veriyor; bir cevap `None` ise o istek düşmüş sayılıyor.
- **Aynı anda kaç istek gördüğünü** sayıyor — beşerli dalganın tek gözlenebilir izi.
- İlk isteğin tek başına bittiğini görebilmek için her çağrının başlangıç ve bitiş sırasını
  tutuyor.

## 2. `add_scene` — sekiz test

- **`test_add_scene_opens_a_frame_for_each_sentence`**
- **`test_a_scene_frame_carries_no_prompt_fields`**
- **`test_add_scene_appends_and_renumbers`**
- **`test_add_scene_says_which_numbers_the_scenes_got`**
- **`test_add_scene_refuses_an_empty_list`** · **`…_a_list_that_is_not_one`** ·
  **`…_something_that_is_not_a_sentence`** — üçünde de dosya değişmiyor.
- **`test_add_scene_refuses_a_file_that_is_not_there`**

## 3. `write_frame_prompt` — on iki test

- **`test_an_empty_frame_is_filled_from_its_scene`**
- **`test_a_frame_that_is_already_written_is_left_alone`**
- **`test_a_frame_without_a_scene_is_left_alone`**
- **`test_the_request_carries_the_scene_and_the_maps`**
- **`test_the_request_is_sent_without_tools`** — `write_once`'ın imzasında araç yok; çağrının
  metninde de araç adı geçmiyor.
- **`test_a_name_the_writer_invented_leaves_that_frame_empty`** — diğerleri doluyor.
- **`test_an_answer_that_is_not_json_leaves_that_frame_empty`**
- **`test_the_report_counts_what_was_written_and_what_was_left`**
- **`test_running_again_fills_only_the_empty_ones`**
- **`test_no_more_than_five_requests_are_in_the_air`**
- **`test_the_first_request_goes_alone`**
- **`test_it_stops_at_a_hundred_requests`**
- **`test_what_the_sub_requests_spent_is_reported`**
- **`test_without_an_engine_the_tool_refuses`**

## 4. `test_skills.py` — akış metinleri

- **`test_the_flow_writes_scenes_with_the_tool`** — `add_scene` geçiyor, `-scenes` geçmiyor.
- **`test_the_handoff_names_one_file`**
- **`test_prompt_plus_calls_the_writer`** — `write_frame_prompt` geçiyor, eşleştirme paragrafı yok.
- Bugünkü `add_frames` anan testler yeni ada çevriliyor.

## 5. Araç listesi ve modlar

- `test_every_tool_is_declared_to_the_model` — `add_frames` çıkıyor, iki yeni ad giriyor.
- `test_modes.py`'nin `WRITES` demeti aynı şekilde güncelleniyor.

## 6. `test_tools.py` — `add_frames`'in testleri

`add_frames` artık yok; onun on beş testi **siliniyor**. Ölçtükleri şeyin bir kısmı yeni araçlara
taşınmış durumda *(ret kuralları, adların kontrolü, numaralama)*, geri kalanı o araçla birlikte
gidiyor.

## 7. Koş, kırmızıyı gör, commit'le

```
python -m pytest queen-agent -q
```

Diğer üç satır ardışık koşulur.

`test(m155): …`
