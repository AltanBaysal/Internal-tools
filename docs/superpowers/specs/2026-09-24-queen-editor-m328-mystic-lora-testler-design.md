# Madde 328 — H3'e Mystic XXX LoRA'sı, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Grafik yeniden export edilmiyor, Colab'da ölçülecek bir şey de yok:
LoRA grafiğin kendi yığınına, JSON'u düzenlenerek giriyor *(aşağıda)*. Adres kullanıcının verdiği;
collab-toolbox'ın H3 denemesi de aynı sürümü aynı adla indirmişti
*([indirilecekler.md](../../../collab-toolbox/video_experiments/minimax-h3/indirilecekler.md), §7)*.
Deneme kullanıcının, H3 seçili bir Colab kurulumunda.

## Bugün ne oluyor

İki H3 grafiğinde de LoRA'lar tek bir node'da: `2678`, `DaSiWa_LTX2LoraLoader`. Yığın `stack_data`'da
on iki yuvalık bir JSON dizesi; her yuva `on`, `lora` *(`loras/` altındaki ad)* ve `str` taşıyor. Dolu
tek yuva Motion Booster, 0.7 *(madde 213)*. **Yığın modelini Director'ın 5. çıkışından alıyor** —
`model`, Director'ın kipine göre seçtiği model — yani aynı yığın I2VA'ya, FL2VA'ya ve REF2VA'ya
uygulanıyor. REF2VA'nın kendi grafiği yok: I2VA grafiği kipi değiştirilerek koşuyor *(madde 304)*.
Üretici yığına hiç dokunmuyor.

Panelin H3 grubu *(`model_groups.H3_VIDEO`)* Motion Booster'ı sayıyor, çünkü grafik onu yüklüyor;
defter onu `CIVITAI_H3`'te, yalnız H3 seçiliyse indiriyor. `MIRRORLESS` boş *(madde 327)*.

## Kural

- **Yığına ikinci LoRA:** `MysticXXX_MMH3-V4.safetensors`, güç 1, iki grafikte de. Motion Booster
  0.7'de kalıyor. Yığın Director'ın seçtiği modeli aldığı için tek düzenleme üç kipi birden kapsıyor.
- **Panel onu da sayıyor:** ad `H3_VIDEO`'ya giriyor. Grafik yüklediği hâlde grup saymasa, dosya
  eksikken panel "kurulu" der ve render başlamaz — Motion Booster'ın orada durma sebebi bu.
- **Defter onu H3 seçiliyse indiriyor:** `CIVITAI_H3`'e bir satır, sürüm `3266628`, klasör `LORA`.
  `CIVITAI_H3` yalnız `VIDEO_MODEL == "h3"`'te okunuyor, yani *"bu lora h3 seçiliyse insin"*
  bugünkü anahtarla geliyor.
- **Aynası kapalı:** ad `MIRRORLESS`'e giriyor — 327'nin ilk kullanıcısı. Listede, defterde, grupta
  ve grafikte aynı dize; testler dördünü de aynı harflere bağlıyor.
- **Tetik kelimesi yok**, yani video prompt'unun yazıcısı ve üretici değişmiyor.

## Yazılacak testler

Bu turda kaynak kod, grafik ve defter değişmiyor.

### `test_workflow_asset.py` — grafikler

1. **Değişen:** `test_the_h3_graphs_carry_motion_booster_alone_at_seventy` →
   `test_the_h3_graphs_carry_motion_booster_at_seventy_and_mystic_xxx_at_one`. İki grafikte de yığın
   modelini Director'ın 5. çıkışından alıyor, açık yuvalarda Motion Booster 0.7'de ve Mystic XXX 1'de
   yükleniyor, başka bir şey yüklenmiyor; iki ad da H3 grubunda. Karşılaştırma sıralanmış listeyle:
   testler yuvanın yerini değil yığının ne yüklediğini soruyor, ve aynı LoRA'nın iki kez girmesi yine
   yakalanıyor. Director'dan gelen kablo bugün de yerinde; üç kipi birden kapsamanın sebebi o
   olduğu için bu testte soruluyor. Bugün kırmızı: yığında Motion Booster tek başına.

### `test_comfy_h3_video_generator.py` — ComfyUI'ye giden grafik

2. **Her H3 videosu Mystic XXX'le, gücü 1** — üretici gerçek grafiklerle *(`config`'in iki yolu)* ve
   sahte istemciyle kuruluyor; üç kip parametreyle: kaynaklı *(I2VA)*, kaynak ve bitişli *(FL2VA)*,
   havuzdan *(REF2VA)*. Gönderilen grafiğin `2678` yığınında Mystic XXX açık ve gücü 1. Grafik testi
   dosyaları okuyor; bu, Kareden'in ve Referanstan'ın ComfyUI'ye ne yolladığını — REF2VA'nın kendi
   grafiği olmadığı için onu ancak üretici söyleyebiliyor. Bugün üçü de kırmızı: yığında Mystic yok.

### `test_notebook_installs_the_producer_groups.py` — defter

3. **Defter Mystic XXX'i H3'le, kendi sürümüyle `loras/`'a indiriyor** — `CIVITAI_H3` listesinin
   içinde `(3266628, LORA, "MysticXXX_MMH3-V4.safetensors", …)` satırı. Etiket sorulmuyor. Bugün
   kırmızı: satır yok.

### `test_colab_downloads.py` — liste

4. **Mystic XXX aynasız iniyor** — ad `downloads.MIRRORLESS`'te. Listenin ne yaptığını 327'nin beş
   testi soruyor; bu, dosyanın listede olduğunu. Bugün kırmızı: liste boş.

### `test_producers.py` — grup

5. **Değişen:** `H3_FILES`'a `("loras", "MysticXXX_MMH3-V4.safetensors")`, Motion Booster'ın
   ardına. `test_the_h3_group_names_its_files_the_way_the_graph_loads_them` grubu bu listeyle birebir
   karşılaştırıyor; bugün kırmızı: grupta satır yok.

## Değişen

- `test_the_h3_graphs_carry_motion_booster_alone_at_seventy` *(1)*: "tek başına" artık doğru değil.
  Adı ve beklediği yığın değişiyor; Motion Booster'ın 0.7'si ve gruptaki yeri aynen soruluyor.
- `test_producers.py`'nin `H3_FILES`'ı *(5)*: grubun tam listesi bir satır uzuyor. Aynı listeyle
  kurulan `test_a_machine_with_h3_on_it_has_a_video_producer` yeşil kalıyor — disk yine grubun
  istediği her dosyayı tutuyor.

## Bekçiler, bugün de yeşil

- `test_an_unticked_group_costs_no_bytes` — `CIVITAI_H3` kendi anahtarının arkasında: H3 seçilmeyen
  koşu Mystic'i indirmiyor.
- `test_every_file_the_h3_group_counts_is_fetched_by_the_notebook` — grup ve defter aynı adı söylüyor;
  uygulamada biri değişip öteki değişmezse kırmızıya döner.
- `test_the_notebook_fetches_the_h3_checkpoint_and_lora_by_their_versions` — checkpoint ve Motion
  Booster yerinde.
- 327'nin beş `MIRRORLESS` testi — listedeki bir dosya aynaya hiç uğramıyor.
- H3 grafiklerinin öteki testleri *(API biçimi, kip başına bir grafik, 4 sn ve 512 × 768, mp4)* —
  grafiğin geri kalanı değişmiyor.
- `test_the_notebook_stays_well_under_what_the_tools_can_read` — satır deftere ~75 karakter
  ekliyor; tavan 29.000. Uygulama turu bakar.

## Sorulmayan

- **Yuva:** Mystic'in hangi yuvada durduğu. Yuvanın `vs` / `as` alanları da: Motion Booster'ınkiler de
  sorulmuyor, ve ne yaptıkları repoda yazılı değil.
- **Disk tahmini:** 148 MB, H3'ün ~37 GiB'lık tahmininin yuvarlamasında kalıyor.
- **Checkpoint:** H3 Eros Max bu maddede değil *(satır — "2 ayrı task")*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız yedi test: 1, 2'nin üç kipi, 3, 4
ve 5'in grup testi, hepsi Mystic XXX henüz hiçbir yerde olmadığı için. Geri kalan her şey yeşil.
