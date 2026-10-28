# Madde 238 · LoRA kutusu: USNR, Slime, Boş — test turunun planı

**Spec:** [test turu](../specs/2026-09-18-queen-editor-m238-lora-usnr-slime-bos-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Adımlar

**1 · `test_photo_usecases.py`** — katalog, liste, kuyruk isteğinin denetimi.

| Test | Olgu |
|---|---|
| `the_lora_list_is_usnr_then_slime` *(bugünkü `slime_alone`)* | 1 |
| `the_lora_box_offers_usnr_slime_and_none_in_that_order` *(bugünkü `opens_with_standart`)* | 2 |
| `a_lora_the_app_does_not_know_is_refused_before_anything_is_planned` | 10 |
| `every_lora_the_box_offers_is_accepted` | 11 |
| `a_frame_planned_before_loras_reaches_the_renderer_naming_none` *(ad değişir)* | — |

**2 · `test_comfy_photo_generator.py`** — render. Standart'ı anan testler yeni kurala döner.

| Test | Olgu |
|---|---|
| `a_nova_frame_that_names_no_lora_renders_with_usnr` | 4 |
| `a_dasiwa_frame_that_names_no_lora_renders_with_usnr` *(bugünkü DaSiWa testi)* | 5 |
| `usnr_chosen_loads_usnr_alone_and_leaves_the_prompt` *(iki model)* | 6 |
| `none_chosen_loads_no_lora_and_leaves_the_prompt` *(iki model)* | 7 |
| Slime'ın, eski değerlerin, modelsiz ve çıplak dosya adlı karelerin testleri, yorumları düzelerek | 8, 9 |

**3 · `test_photo_routes.py`** — uç noktanın LoRA listesi *(3)*, tanınmayan LoRA'nın 400'ü ve alanı
*(10)*. Yanlış tipteki LoRA'nın testi *söylenmemiş* adını alır.

**4 · Ayarlar** — `test_settings_store.py`, `test_projects_routes.py`, `test_project_usecases.py`
LoRA'yı yazıp okuyor *(12, 13)*.

**5 · `test_plan_store.py`** — iki testin adı ve yorumu. **`test_notebook_installs_the_producer_groups.py`**
— standart LoRA döngüsü gider, iki docstring düzelir.

**6 · `useModels.test.jsx`** — okunamayan liste boş LoRA listesi veriyor *(21)*.

**7 · `GeneratePanel.test.jsx`** — sabit yeni üç satır; kayıtlı LoRA, ilk satırla dolma, Boş, liste
gelmeden, liste okunamayınca, listeden düşmüş kayıt *(14–16, 18–20)*.

**8 · `ProjectScreen.test.jsx`** — ayarlar LoRA ile kaydediliyor *(17)*; sabit yeni üç satır.

**9 · `PhotoDetail.test.jsx`** — üç ad, ve LoRA söylemeyen karede satır yok *(22, 23)*.

**10 · Takım koşulur**, dördü de. Beklenen: queen-editor'ün **iki tarafı da kırmızı**, queen-agent
yeşil.

**11 · Kırmızı commit'lenir.**
