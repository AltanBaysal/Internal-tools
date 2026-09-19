# Madde 237 · Model ve LoRA ayrı iki kutu — test turunun planı

**Spec:** [test turu](../specs/2026-09-18-queen-editor-m237-model-ve-lora-ayri-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Adımlar

**1 · `test_photo_usecases.py`** — katalog ve listeler.

| Test | Olgu |
|---|---|
| `the_model_list_is_nova_3dcg_and_dasiwa` | 1 |
| `the_lora_list_is_slime_alone` | 2 |
| `with_no_models_chosen_the_list_is_empty` | 1 |
| `the_models_the_notebook_chose_are_what_the_panel_lists` | 1 |
| `an_unknown_model_id_is_dropped_and_takes_nothing_with_it` | 1 |
| `the_lora_box_opens_with_standart` | 2 |
| `the_loras_the_notebook_chose_follow_standart` | 2 |
| `a_planned_frame_carries_the_lora_it_was_submitted_under` | 8 |

**2 · `test_comfy_photo_generator.py`** — render.

| Test | Olgu |
|---|---|
| `a_model_renders_with_its_own_checkpoint_and_its_standard_loras` | 3 |
| `dasiwa_renders_on_its_own_checkpoint_with_no_lora` | 5 |
| `a_chosen_lora_replaces_the_models_standard_arrangement` | 4 |
| `a_chosen_loras_trigger_opens_the_prompt` | 4 |
| `an_old_recipe_value_renders_as_its_model_and_its_lora` | 6 |
| `an_unknown_lora_stops_the_render` | 7 |

Bugünkü `recipe:` testleri bu satırlara dönüşüyor; elenen Nova'ların testi *(madde 226)* eski
değerlerle kalıyor, çünkü o kayıtlar hâlâ diskte.

**3 · `test_photo_routes.py`** — uç nokta iki listeyi birden veriyor, ve kuyruk isteği LoRA'yı
taşıyor *(olgu 1, 2, 8)*.

**4 · `test_notebook_installs_the_producer_groups.py`** — defterin her fotoğraf kutusu bir model ve
uygulamanın model kimlikleriyle eşleşiyor; DaSiWa'nın checkpoint'i kendi kutusunun arkasında;
seçilen modeller `QE_PHOTO_MODELS` ile geçiyor *(olgu 12, 13, 14)*. `test_plan_store.py` LoRA'yı
*(olgu 15)*, `test_photo_usecases.py` yeniden üretmeyi *(olgu 16)* çiviliyor.

**5 · `GeneratePanel.test.jsx`** — Model kutusunun altında LoRA kutusu, `Standart` ile açılıyor,
seçilen LoRA kuyruk isteğiyle gidiyor *(olgu 9, 10)*.

**6 · `PhotoDetail.test.jsx`** — kare detayı modelin ve LoRA'nın adını yazıyor *(olgu 11)*.

**7 · Takım koşulur**, dördü de. Beklenen: queen-editor'ün **iki tarafı da kırmızı**, queen-agent
yeşil.

**8 · Kırmızı commit'lenir.**
