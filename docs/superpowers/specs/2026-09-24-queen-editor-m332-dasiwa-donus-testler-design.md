# Madde 332 — H3'ün modeli DaSiWa'ya dönüyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Adres 329'dan önce defterde duran: Civitai `3314686`, aynada da
duruyor *(madde 311)*.

## Bugün ne oluyor

İki H3 grafiğinin dört model düğümü *(`UNETLoader`)* Eros Max beta5'i yüklüyor; defter onu
`HF_H3`'ün ilk satırında yazarın Hugging Face reposundan indiriyor; panelin grubu onu sayıyor
*(madde 329)*. DaSiWa'nın satırı defterden çıkmış, ve bir test onun izinin kalmadığını çiviliyor.
Yığında yalnız Motion Booster 0.7 *(330)*.

## Kural

- **Dört model düğümü de DaSiWa'yı yüklüyor:**
  `MiniMaxH3/dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors`,
  `weight_dtype` `default` — 329'dan önceki hâli.
- **Defter DaSiWa'yı sürümüyle indiriyor:** `CIVITAI_H3`'te `(3314686, H3DIFF, "<ad>", …)` satırı —
  aynadan, 311'in yolundan. Eros'un `HF_H3` satırı gidiyor; defterde Eros'tan iz kalmıyor.
- **Grup DaSiWa'yı sayıyor**, Eros'u değil.
- Yığın, Mystic'in satırı ve `MIRRORLESS`, 331'in talimatı değişmiyor.

## Yazılacak testler

Bu turda kaynak kod, grafik ve defter değişmiyor.

### `test_workflow_asset.py`

1. **Değişen:** `test_both_h3_graphs_load_eros_max_beta5` → `test_both_h3_graphs_load_dasiwa_hybrid_turbo_v2`.
   Aynı soru *(her `UNETLoader`, sınıfıyla bulunur)*, beklenen DaSiWa. Bugün kırmızı: dördü Eros.
2. `test_the_h3_graphs_carry_motion_booster_alone_at_seventy` — yalnız docstring: *"Eros is tried
   alone, its author having folded Mystic XXX into the checkpoint itself"* artık doğru değil. Assert
   aynen; yeşil.

### `test_comfy_h3_video_generator.py`

3. **Değişen:** `test_every_h3_video_is_rendered_with_eros_max_beta5` →
   `test_every_h3_video_is_rendered_with_dasiwa_hybrid_turbo_v2`, üç kip. Bugün üçü kırmızı.
4. `test_no_h3_video_is_rendered_with_mystic_xxx` — yalnız docstring *("Eros is tried alone")*.
   Yeşil.

### `test_notebook_installs_the_producer_groups.py`

5. **Değişen:** `test_the_notebook_fetches_eros_max_from_its_author_s_repo_into_the_h3_diffusion_models`
   → `test_the_notebook_fetches_dasiwa_by_its_version_into_the_h3_diffusion_models`: `CIVITAI_H3`
   listesinin içinde `(3314686, H3DIFF, "<DaSiWa'nın adı>",` satırı. Bugün kırmızı: satır yok.
6. **Değişen:** `test_the_retired_dasiwa_h3_checkpoint_is_gone_from_the_notebook` →
   `test_the_retired_eros_max_is_gone_from_the_notebook`: ne `TenStrip/10Eros-Max` ne Eros'un dosya
   adı defterde. Bugün kırmızı: ikisi de orada.

### `test_producers.py`

7. **Değişen:** `H3_FILES`'ın ilk satırı yeniden DaSiWa. Okuyan iki test —
   `test_the_h3_group_names_its_files_the_way_the_graph_loads_them` ve
   `test_a_machine_with_h3_on_it_has_a_video_producer` — bugün kırmızı.

## Değişen

1, 3, 5, 6 ve 7 329'un sorularını ters cevapla soruyor: kullanıcı *"dasiwa'yı da denemek istiyorum,
ona döner misin bir"* dedi, ve seçim notebook'a taşınmadı *(satır — "1")*; bir oturumda tek bir H3
modeli var.

## Bekçiler, bugün de yeşil

- `test_every_model_the_h3_graphs_load_is_in_the_h3_group`,
  `test_every_file_the_h3_group_counts_is_fetched_by_the_notebook` — grafik, grup ve defter aynı adı
  söylüyor.
- `test_an_unticked_group_costs_no_bytes` — `CIVITAI_H3` yalnız H3 seçilince okunuyor.
- `test_the_notebook_fetches_motion_booster_by_its_version`, Mystic'in defter ve `MIRRORLESS`
  testleri, 330'un yığın testleri, 331'in talimat testi.
- `test_the_notebook_stays_well_under_what_the_tools_can_read`.

## Sorulmayan

- **Disk tahmini:** iki dosya arasında 2,7 MB; 37 GiB yerinde.
- **Aynanın DaSiWa'yı hâlâ tuttuğu:** repo cevaplayamaz; tutmuyorsa 311'in yolu dosyayı Civitai'den
  çerezle indirip yeniden yüklüyor.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız sekiz test: 1, 3'ün üç kipi, 5, 6
ve 7'nin iki testi. Geri kalan her şey yeşil.
