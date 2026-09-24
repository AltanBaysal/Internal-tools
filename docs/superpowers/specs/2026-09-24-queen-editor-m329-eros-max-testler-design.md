# Madde 329 — H3'ün modeli Eros Max beta5, Mystic XXX yarı güçte, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Dosyanın adresi kullanıcının yapıştırdığı sayfadan okundu ve satırda
yazılı: Hugging Face `TenStrip/10Eros-Max`, `10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`,
20.970.414.464 bayt. Grafik yeniden export edilmiyor: model düğümlerinin adı ve yığındaki güç JSON'da
düzenleniyor. Colab'da ölçülecek bir şey de yok. Deneme kullanıcının, H3 seçili bir Colab kurulumunda.

## Bugün ne oluyor

İki H3 grafiğinin de iki model düğümü var *(`UNETLoader`)*: biri Director'ın `fl2va_model`'ine, öteki
`ref2va_model`'ine gidiyor, ve Director kipine göre birini seçiyor. Dördü de aynı dosyayı yüklüyor:
`MiniMaxH3/dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors`,
`weight_dtype` `default`. Üretici bu düğümlere dokunmuyor: yalnız `2730`'u ve `2739`'u yazıyor, yani
ComfyUI'ye giden model grafiğin kendi modeli. REF2VA'nın kendi grafiği yok, I2VA grafiği kipi
değiştirilerek koşuyor *(madde 304)*.

Defter DaSiWa'yı `CIVITAI_H3`'ün ilk satırında, sürüm `3314686`'dan `H3DIFF`'e *(`diffusion_models/MiniMaxH3/`)*
indiriyor, aynadan geçerek. Panelin H3 grubu *(`model_groups.H3_VIDEO`)* onu sayıyor.

Yığında *(`2678`)* Motion Booster 0.7'de, Mystic XXX 1'de *(madde 328)*. Mystic `CIVITAI_H3`'te ve
`colab/downloads.py`'nin `MIRRORLESS`'inde.

## Kural

- **Dört model düğümü de Eros'u yüklüyor:** `MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors`,
  iki grafikte de, `weight_dtype` `default`'ta kalıyor. Director hangi kipte hangi düğümü seçerse
  seçsin Eros geliyor — Kareden'in iki kipi de, Referanstan da.
- **Defter Eros'u `HF_H3`'ten indiriyor:** bir satır, repo `TenStrip/10Eros-Max`, yol ve ad aynı dosya,
  klasör `H3DIFF` — DaSiWa'nın yattığı yer, grafiğin `MiniMaxH3/` öneki oraya bakıyor. `HF_H3` yalnız
  `VIDEO_MODEL == "h3"`'te okunuyor, yani Eros H3 seçiliyse iniyor.
- **Eros aynaya gitmiyor, ve bunun için hiçbir şey eklenmiyor:** `HF_H3`'teki satır `hf_fetch`'ten
  geçiyor, `hf_fetch` hiçbir şey yüklemiyor; aynaya yalnız `civitai_fetch` yüklüyor. `MIRRORLESS`'e
  satır girmiyor.
- **DaSiWa gidiyor:** `CIVITAI_H3`'teki satırı defterden, adı H3 grubundan çıkıyor. Grafik onu artık
  yüklemediği için grupta kalsa, panel H3'ü ancak kullanılmayan 21 GB diskte dururken "kurulu" sayardı.
- **Mystic 0.5:** yığındaki gücü 1'den 0.5'e. Motion Booster 0.7'de kalıyor. Mystic `CIVITAI_H3`'te ve
  `MIRRORLESS`'te olduğu gibi duruyor.
- Eros'un adı grafikte, grupta ve defterde aynı dize; testler üçünü de aynı harflere bağlıyor.

## Yazılacak testler

Bu turda kaynak kod, grafik ve defter değişmiyor.

### `test_workflow_asset.py` — grafikler

1. **Değişen:** `test_the_h3_graphs_carry_motion_booster_at_seventy_and_mystic_xxx_at_one` →
   `test_the_h3_graphs_carry_motion_booster_at_seventy_and_mystic_xxx_at_half`. Aynı test, Mystic'in
   beklenen gücü 0.5. Director'dan gelen kablo ve grubun iki LoRA'yı sayması aynen soruluyor. Bugün
   kırmızı: Mystic 1'de.
2. **İki H3 grafiği de Eros'u yüklüyor** — iki grafikteki her `UNETLoader`'ın `(unet_name, weight_dtype)`
   çifti `("MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", "default")`. Düğümler id'leriyle
   değil sınıflarıyla bulunuyor: sorulan grafiğin hangi modeli yüklediği, hangi düğümün yüklediği değil;
   id'ye bağlı bir test, üçüncü bir model düğümü eklenince yeşil kalırdı. Grubun onu sayması burada
   sorulmuyor — `test_every_model_the_h3_graphs_load_is_in_the_h3_group` `unet_name`'i zaten görüyor
   *(Bekçiler)*; 328'de soruluyordu çünkü LoRA'lar o taramanın göremediği JSON'un içinde. Bugün kırmızı:
   dördü de DaSiWa.

### `test_comfy_h3_video_generator.py` — ComfyUI'ye giden grafik

3. **Değişen:** `test_every_h3_video_is_rendered_with_mystic_xxx_at_full_strength` →
   `test_every_h3_video_is_rendered_with_mystic_xxx_at_half_strength`. Üç kip aynen *(I2VA, FL2VA,
   REF2VA)*, beklenen güç 0.5. Bugün üçü de kırmızı: 1 gidiyor.
4. **Her H3 videosu Eros'la** — üretici gerçek grafiklerle ve sahte istemciyle, üç kip parametreyle
   *(3'ün kurulumu)*. Gönderilen grafikteki her `UNETLoader` Eros'u yüklüyor. Sebep 328'inki: grafik
   testi dosyaları okuyor, bu ComfyUI'ye gideni; REF2VA'nın kendi grafiği yok, ve Director kipine göre
   iki model düğümünden birini seçtiği için "üç kip de Eros'la" ancak gönderilenin bütün model
   düğümlerine bakarak söylenebiliyor. Bugün üçü de kırmızı: DaSiWa gidiyor.

### `test_notebook_installs_the_producer_groups.py` — defter

5. **Değişen:** `test_the_notebook_fetches_the_h3_checkpoint_and_lora_by_their_versions` →
   `test_the_notebook_fetches_motion_booster_by_its_version`. Checkpoint artık sürümüyle Civitai'den
   inmiyor; test yalnız Motion Booster'ın `3228867`'sini soruyor. Bugün de yeşil.
6. **Defter Eros'u yazarın reposundan H3'ün model klasörüne indiriyor** — `HF_H3` listesinin içinde
   `("TenStrip/10Eros-Max", "10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", H3DIFF,
   "10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", …)` satırı. Etiket ve taban sorulmuyor. Liste
   328'deki gibi `HF_H3 = [`'ten ilk `\n]`'ye kadar kesiliyor: satır başka bir listede olsaydı ya başka
   bir anahtarın arkasında ya da Civitai'nin ve aynanın yolunda inerdi. Bugün kırmızı: satır yok.
7. **Defterde DaSiWa'dan iz kalmıyor** — ne `3314686` ne DaSiWa'nın dosya adı defterin kaynağında.
   Emsali `test_the_retired_nova_checkpoints_are_gone_from_the_notebook`: geride kalan bir satır, H3
   seçen her koşuya hiçbir şeyin yüklemediği 21 GB indirtirdi. Bugün kırmızı: ikisi de orada.

### `test_producers.py` — grup

8. **Değişen:** `H3_FILES`'ın ilk satırı `("diffusion_models", "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors")`
   oluyor, DaSiWa'nın yerinde. Bu listeyi iki test okuyor, ikisi de bugün kırmızı:
   `test_the_h3_group_names_its_files_the_way_the_graph_loads_them` *(grup DaSiWa'yı sayıyor)* ve
   `test_a_machine_with_h3_on_it_has_a_video_producer` *(disk Eros'u tutuyor, grup DaSiWa'yı arıyor —
   "kurulu değil")*.

## Değişen

- *(1)* ve *(3)*: Mystic'in gücü kullanıcının kararıyla 1'den 0.5'e iniyor; "at one" ve "at full
  strength" artık doğru değil. Adları ve bekledikleri güç değişiyor, geri kalan her şey aynen soruluyor.
- *(5)*: "checkpoint and lora by their versions" — checkpoint artık Civitai sürümüyle inmiyor. Test
  LoRA yarısıyla kalıyor; checkpoint yarısını *(6)* ve *(7)* soruyor.
- *(8)*: grubun tam listesinde DaSiWa'nın satırı Eros'unkiyle değişiyor. Aynı listeyle kurulan
  `test_a_machine_with_h3_on_it_has_a_video_producer` bu yüzden bugün kırmızıya dönüyor ve uygulamada
  yeşile dönecek — disk yine grubun istediği her dosyayı tutuyor.

## Bekçiler, bugün de yeşil

- `test_every_model_the_h3_graphs_load_is_in_the_h3_group` — grafik ve grup aynı adı söylüyor; uygulamada
  biri değişip öteki değişmezse kırmızıya döner.
- `test_every_file_the_h3_group_counts_is_fetched_by_the_notebook` — grup ve defter aynı adı söylüyor.
- `test_an_unticked_group_costs_no_bytes` — `HF_H3` kendi anahtarının arkasında: H3 seçilmeyen koşu
  Eros'u indirmiyor.
- `test_no_huggingface_file_is_fetched_by_its_address`, `test_huggingface_files_come_down_through_hf_fetch`
  — Eros adresle değil, repo ve yolla `hf_fetch`'ten iniyor.
- `test_the_notebook_fetches_mystic_xxx_by_its_version_into_the_loras`,
  `test_mystic_xxx_is_kept_out_of_the_mirror` — Mystic `CIVITAI_H3`'te ve `MIRRORLESS`'te kalıyor.
- `test_the_disk_estimate_counts_h3_when_h3_is_picked` — `SIZES` H3'ü sayıyor.
- H3 grafiklerinin öteki testleri *(API biçimi, kip başına bir grafik, 4 sn ve 512 × 768, mp4)* —
  grafiğin geri kalanı değişmiyor.
- `test_the_notebook_stays_well_under_what_the_tools_can_read` — Eros'un satırı DaSiWa'nınkinin
  yerine giriyor, defter aşağı yukarı aynı boyda kalıyor; tavan 29.000. Uygulama turu bakar.

## Sorulmayan

- **Satırın etiketi ve tabanı:** öteki H3 satırlarında da sorulmuyor; taban yok, dosya safetensors
  başlığıyla doğrulanıyor.
- **Eros'un aynaya gitmemesi** ayrı bir testle sorulmuyor: *(6)* onu `HF_H3`'e bağlıyor, ve
  `hf_fetch`'in hiçbir şey yüklemediği kodun kendisinde.
- **Disk tahmini:** değişmiyor. DaSiWa 20.967.669.168 bayt
  *([indirilecekler.md](../../../collab-toolbox/video_experiments/minimax-h3/indirilecekler.md), §6)*,
  Eros 20.970.414.464 bayt — 2,7 MB fark; H3'ün 37 GiB'ı yerinde kalıyor.
- **Örnekleyici ve adım** *(euler/simple, 8)*: değişmiyor, bugün de hiçbir test sormuyor.
- **`test_colab_downloads.py`'deki `3314686`'lar:** indirme kodunun testlerinde örnek bir sürüm
  numarası, deftere dair bir iddia değil; kalıyorlar.
- **Düz `int8`'in yüklenip yüklenmediği:** repo cevaplayamaz, ilk Colab koşusu gösterir *(satırın
  dürüst notu)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız on iki test: 1, 2, 3'ün üç kipi,
4'ün üç kipi, 6, 7 ve 8'in iki testi. Hepsi aynı sebepten: Eros henüz hiçbir yerde yok, DaSiWa her
yerde duruyor, Mystic 1'de. 5 yeşil. Geri kalan her şey yeşil.
