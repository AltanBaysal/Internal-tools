# Madde 208 — tek kare yazan araç kalkar · uygulama turu

**Kaynak:** [test turu](2026-09-10-queenagent-m208-tek-kare-araci-testler-design.md) ve
[yol haritasının Madde 208'i](../plans/2026-09-06-queenagent-v8-roadmap.md).

Altı test kırmızı commit edildi *(`4973df2`)*, ve üç bekçi yeşil duruyor. Bu tur kodu yazıyor.

## Nereden ne kalkıyor

### `prompt.py`

- `WRITE_FRAME_PROMPT` ve `WRITE_FRAME_PROMPT_NOTE` gider.
- `ADD_SCENE`'in son cümlesi ilk yazımı **toplu** araca gönderir.
- `WRITE_MISSING_ACTIONS` kalkan aracın adına iki kere yaslanıyor; ikisi de kendi ayakları üstüne
  iner — hangi modele sorduğu kendi cümlesiyle, düzeltme `update_frame`'e.
- `EDIT_PROMPTS`'un *"A line wanted afresh from the scene is write_frame_prompt again, with a
  note"* cümlesi gider; iki yol tek cümlede birleşir.

### `tools.py`

- Şema, `run_tool` dalı, `_write_frame_prompt`.
- `_frame_seen`'in `note` parametresi ve onu yazan iki satır. Tek çağıranı olan toplu yol oraya
  zaten hep `None` geçiyordu.
- `_frame_seen`'in docstring'i **adların neden gösterildiğini** yeniden söyler: bugün *"a note
  saying aylin looks bored has to reach the person the tags describe"* diyor, ve not kalkıyor.
  Kalan sebep daha güçlü: **sahne cümlesi insanları adıyla anıyor**, ve yazarın hangi etiketin
  kimin olduğunu bilmesi gerekiyor.
- `_update_frame`'in docstring'inin son cümlesi *("write_frame_prompt is still the second")* artık
  yanlış: sahneden yeniden yazmak da bu aracın işi.
- `_write_missing_actions`'ın docstring'i kalkan aracı **tarih olarak** anıyor; zamanı geçmişe
  çekilir.

### `modes.py`

EDIT listesindeki `"write_frame_prompt"` girdisi ve onu anlatan yorum. Toplu aracın girdisi ve
yorumu duruyor, ama yorumu *"the tool above stays for the correction"* diyor — o cümle de düşer.

## Ölen testler

`test_tools.py`'nin Madde 176 bölümü. On dört test, ve **iddialarının hepsinin bir ikizi var**:

| Ölen | İddiayı kim taşıyor |
|---|---|
| `test_the_writer_is_asked_with_the_second_part_on_the_end` | `test_the_bulk_tool_asks_with_the_second_part_too` |
| `test_the_writer_is_handed_the_scene_the_cast_and_the_place` | bu turun bekçisi *(toplu yol)* |
| `test_the_writer_is_handed_this_frame_and_no_other` | `test_each_request_carries_its_own_frame_and_no_other` |
| `test_the_writer_is_handed_the_note_when_there_is_one` | **yok** — not yolu kalkıyor |
| `test_what_comes_back_is_written_to_the_frames_action` | `test_every_frame_without_an_action_gets_one` |
| `test_an_action_that_is_already_there_is_written_over` | **yok** — üzerine yazan yol kalkıyor |
| `test_the_answer_is_a_receipt_rather_than_the_prompt` | bu turun bekçisi |
| `test_the_tools_own_spending_comes_back_with_its_answer` | `test_the_whole_bill_comes_back_as_one_figure` |
| `test_a_frame_with_no_scene_has_nothing_to_write_from` | `test_a_frame_with_no_scene_is_skipped_without_being_paid_for` |
| `test_writing_refuses_a_frame_that_is_not_there` | **yok** — toplu araç kare numarası almıyor |
| `test_writing_without_a_model_says_so_rather_than_crashing` | `test_filling_without_a_model_says_so_rather_than_crashing` |
| `test_a_request_that_falls_over_leaves_the_frame_as_it_was` | `test_one_request_falling_over_leaves_the_others_written` |
| `test_an_empty_answer_is_not_written_down` | `test_an_empty_answer_is_not_written_down_either` |
| `test_the_single_frame_tool_is_still_there_for_a_correction` | yerine bu turun *"is gone"* testi |

`_wrote` yardımcısı da onlarla gider. **`FakeWriter` kalır** — toplu aracın testleri onu
kullanıyor.

`test_a_complaint_is_written_again_rather_than_edited` *(`test_skills.py`)* ölür: *"not"* yolunu
tutuyordu. Yerini bu turun bekçisi aldı.

## Kalkan aracı harcayan araç olarak kullanan dört test

`test_stream_answer.py`'de para akışını ölçen dört test kurgusunu bu araçla kuruyor. Hepsi
`write_missing_actions`'a geçer: `_with_a_frame` tek bekleyen kare yazıyor, yani yazara **tek**
istek gidiyor ve bütün sayılar aynı kalıyor.

## Bayat yorumlar

Kod ve testlerde kalkan aracı **şimdiki zamanda** anan yorumlar bugüne çekilir. Tarih anlatan
yorumlar *(Madde 185'in neden geldiği gibi)* geçmiş zamanda duruyor ve doğru kalıyor.

## Doğrulama

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Altı kırmızı yeşile döner, on beş test silinir, başka hiçbir şey kırmızıya dönmez. Ön uç
ellenmiyor.
