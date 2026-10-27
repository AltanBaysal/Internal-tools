# Madde 333 — H3'ün modeli Eros'a dönüyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Adres 329'unki: Hugging Face `TenStrip/10Eros-Max`,
`10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`; repo herkese açık.

## Bugün ne oluyor

332'nin hâli: dört model düğümü DaSiWa'yı yüklüyor, defter onu `CIVITAI_H3`'ün ilk satırında
`3314686`'dan aynadan indiriyor, grup onu sayıyor; bir test defterde Eros'tan iz kalmadığını
çiviliyor.

## Kural

329'un modeli, 330 ve 331 yerinde:

- **Dört model düğümü de Eros'u yüklüyor:**
  `MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`, `weight_dtype` `default`.
- **Defter Eros'u `HF_H3`'ten, yazarın reposundan `H3DIFF`'e indiriyor**; `hf_fetch` hiçbir şey
  yüklemediği için aynaya gitmiyor *(kullanıcı — aynaya yüklemek istenmiyor)*.
- **Defterde DaSiWa'dan iz kalmıyor:** ne `3314686` ne dosya adı. Dosya **aynada duruyor** — defter
  ona dokunmuyor, yalnız indirmiyor *(kullanıcı — "dasiwa silinmesin, dursun", "dasiwa'yı indirme")*.
- **Grup Eros'u sayıyor.**

## Yazılacak testler

Bu turda kaynak kod, grafik ve defter değişmiyor. Hepsi 332'nin sorularının ters cevabı; 329'un
testlerinin aynısı, docstring'leri 333'ü anlatarak.

1. `test_workflow_asset.py` — `test_both_h3_graphs_load_dasiwa_hybrid_turbo_v2` →
   `test_both_h3_graphs_load_eros_max_beta5`. Bugün kırmızı.
2. `test_comfy_h3_video_generator.py` — `test_every_h3_video_is_rendered_with_dasiwa_hybrid_turbo_v2`
   → `test_every_h3_video_is_rendered_with_eros_max_beta5`, üç kip. Bugün üçü kırmızı.
3. `test_notebook_installs_the_producer_groups.py` —
   `test_the_notebook_fetches_dasiwa_by_its_version_into_the_h3_diffusion_models` →
   `test_the_notebook_fetches_eros_max_from_its_author_s_repo_into_the_h3_diffusion_models`
   *(`HF_H3`'ün içinde `("TenStrip/10Eros-Max", "<ad>", H3DIFF, "<ad>",` satırı)*. Bugün kırmızı.
4. Aynı dosya — `test_the_retired_eros_max_is_gone_from_the_notebook` →
   `test_the_retired_dasiwa_h3_checkpoint_is_gone_from_the_notebook` *(ne `3314686` ne DaSiWa'nın
   adı)*. Docstring dosyanın aynada kaldığını söylüyor. Bugün kırmızı.
5. `test_producers.py` — `H3_FILES`'ın ilk satırı Eros; okuyan iki test bugün kırmızı.

## Değişen

Hepsi: kullanıcı iki modeli denedi ve Eros'u seçti *("eros yapalım")*. 332'nin testleri DaSiWa'yı
soruyordu.

## Bekçiler, bugün de yeşil

Grafik/grup/defter tutarlılık testleri, `test_an_unticked_group_costs_no_bytes`, HF'nin adresle
değil repo ve yolla indirildiğini soran iki test, Motion Booster'ın ve Mystic'in defter testleri,
`MIRRORLESS`, 330'un yığın testleri, 331'in talimat testi, defterin boy testi.

## Sorulmayan

- **Aynadaki DaSiWa:** repo aynanın içini görmüyor; defter ona dokunmuyor, yeter.
- **Disk tahmini:** 2,7 MB fark; 37 GiB yerinde.

## Bitti sayılır

`queen-editor` pytest'te yalnız sekiz kırmızı: 1, 2'nin üç kipi, 3, 4 ve 5'in iki testi.
