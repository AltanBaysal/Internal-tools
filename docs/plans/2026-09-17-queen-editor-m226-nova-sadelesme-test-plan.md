# Madde 226 · Nova Orange ve Nova Anime kaldırılacak — test turunun planı

**Spec:** [test turu](../specs/2026-09-17-queen-editor-m226-nova-sadelesme-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Adımlar

**1 · `test_photo_usecases.py`.** `test_the_recipe_list_is_nova_3dcg_and_slime_alone`.

**2 · `test_notebook_installs_the_producer_groups.py`.**
`test_the_notebook_offers_every_checkpoint_a_recipe_asks_for` yalnız Nova 3DCG'yi (`2744564`)
çiviler. Yanına `test_the_retired_nova_checkpoints_are_gone_from_the_notebook`: iki dosya adı ve iki
version id defterde geçmiyor.

**3 · `test_comfy_photo_generator.py`.** `test_a_retired_nova_recipe_renders_as_nova_3dcg`,
`novaorange` ve `novaanime` ile parametreli: checkpoint `nova3DCGXL_ilV90.safetensors`, lora dizilimi
yalnız USNR.

**4 · Takım koşulur**, dördü de. Beklenen: yalnız **queen-editor'ün arka ucu kırmızı**.

**5 · Kırmızı commit'lenir.**
