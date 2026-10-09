# Madde 229 · Model listesi ComfyUI'ye gitmeyecek — test turunun planı

**Spec:** [test turu](../specs/2026-09-17-queen-editor-m229-model-listesi-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. Testler henüz olmayan şuna göre yazılıyor: `list_models(chosen)`
yalnız tarif kimliklerini alıyor, ve route'un tesisatı `partial(list_models, [])`.

## Adımlar

**1 · `test_photo_usecases.py` — olgu 1–4.**

| Test | Ne bekler |
|---|---|
| `test_with_no_recipes_chosen_the_list_is_empty` | `list_models([]) == []` |
| `test_the_recipes_the_notebook_chose_are_what_the_panel_lists` | iki satır, defterin sırasıyla |
| `test_a_recipe_the_notebook_did_not_choose_is_not_offered` | yalnız Slime |
| `test_an_unknown_recipe_id_is_dropped_and_takes_nothing_with_it` | yalnız Slime |

`FakeGenerator`'dan `models`, `models_called` ve `installed` çıkar.

**2 · `test_photo_routes.py` — olgu 5.** Tesisat `partial(list_models, [])` olur.
`test_with_no_recipes_the_models_endpoint_answers_an_empty_list` → 200, `{"models": []}`.
`test_the_models_endpoint_lists_what_the_renderer_has` ve
`test_an_unreachable_renderer_answers_with_its_own_words` silinir. Sahtenin `models`'i ve
`installed`'ı çıkar.

**3 · Silinecek koda ait testler.** `test_comfy_photo_generator.py`'den
`test_the_installed_models_come_from_the_server` ve `FakeClient.checkpoints`.
`test_comfy_client.py`'den iki `checkpoints` testi ve `_object_info`.

**4 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: yalnız **queen-editor'ün arka ucu kırmızı**, öteki üçü yeşil.

**5 · Kırmızı commit'lenir.**
