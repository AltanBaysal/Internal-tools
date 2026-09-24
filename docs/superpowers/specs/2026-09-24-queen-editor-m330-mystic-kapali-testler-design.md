# Madde 330 — H3 videoları Mystic XXX'siz, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Grafik yeniden export edilmiyor: Mystic'in yuvası JSON'da boş yuvanın
biçimine dönüyor. Defter değişmiyor, Colab'da ölçülecek bir şey yok. Deneme kullanıcının, H3 seçili
bir Colab kurulumunda.

## Bugün ne oluyor

İki H3 grafiğinin yığınında *(`2678`, `DaSiWa_LTX2LoraLoader`, on iki yuva)* iki dolu yuva var: Motion
Booster 0.7'de, Mystic XXX 0.5'te *(madde 329)*. Kalan on yuva boş, hepsi aynı biçimde:
`"on":true,"lora":"None"`. Yığın Director'ın kipine göre seçtiği modeli alıyor, yani üç kip de onu
yüklüyor; REF2VA I2VA grafiğinde koşuyor *(madde 304)*. Üretici yığına dokunmuyor.

Panelin H3 grubu *(`model_groups.H3_VIDEO`)* iki LoRA'yı da sayıyor. Defter Mystic'i `CIVITAI_H3`'te,
H3 seçiliyse indiriyor; adı `colab/downloads.py`'nin `MIRRORLESS`'inde, yani aynasız, Civitai'den
çerezle iniyor.

## Kural

- **Mystic'in yuvası boş yuvanın biçimine dönüyor:** `{"on":true,"lora":"None","str":1,"vs":1,"as":1}`,
  öteki boş yuvalar gibi. **`"on":false` değil:** yükleyicinin onu dinleyip dinlemediği bilinmiyor;
  `"None"` 213'ten beri her boş yuvanın hiçbir şey yüklemediği biçim. Bu yüzden testler bir yuvanın
  yüklediğini `on`'a bakarak değil adına bakarak okuyor: adı `"None"` olmayan her yuva sayılıyor, açık
  ya da kapalı. Kapatılıp adı bırakılmış bir Mystic kırmızı kalıyor.
- **Motion Booster 0.7'de, açık, yığının adı olan tek yuvası.** Eros ve örnekleyici değişmiyor.
- **Grup Mystic'i artık saymıyor.** Panel "kurulu"yu bu gruba bakarak söylüyor; grafiğin yüklemediği
  bir dosya H3'ün kurulu olup olmadığını belirlememeli. Diskinde Mystic olmayan bir makine H3'ü kurulu
  saymalı.
- **Defter değişmiyor — Mystic inmeye devam ediyor.** `CIVITAI_H3`'teki satırı ve `MIRRORLESS`'teki adı
  kalıyor: geri istenirse yalnız grafiğe ve gruba dokunuluyor, defter değişmiyor *(satır — "geri
  istenirse defter değişmeden açılıyor")*. Bedeli açık: H3 seçen her koşu yüklenmeyen 148 MB indiriyor,
  ve dosya aynasız olduğu için Civitai çerezini hâlâ istiyor.
- **Hiçbir test bununla çatışmıyor** *(tarandı)*: defterin H3 için indirdiği her şeyin grupta ya da
  grafikte olmasını isteyen bir test yok. Var olan iki yön — grafiğin yüklediği grupta, grubun saydığı
  defterde — Mystic'in gruptan çıkmasıyla bozulmuyor.

## Yazılacak testler

Bu turda kaynak kod, grafik ve defter değişmiyor.

### `test_workflow_asset.py` — grafikler

1. **Değişen:** `test_the_h3_graphs_carry_motion_booster_at_seventy_and_mystic_xxx_at_half` →
   `test_the_h3_graphs_carry_motion_booster_alone_at_seventy` — 328'den önceki adı. İki grafikte de
   yığın modelini Director'ın 5. çıkışından alıyor, ve adı `"None"` olmayan yuvalar
   `[("H3_Motion_BoosterV2.safetensors", 0.7, True)]` — ad, güç ve `on`. `on` burada okunuyor ama
   yuvaları süzmüyor: Motion Booster'ın açık olduğu soruluyor, Mystic'in kapalı olması yetmiyor
   *(Kural)*. Motion Booster grupta. Bugün kırmızı: Mystic 0.5'te yığında.

### `test_comfy_h3_video_generator.py` — ComfyUI'ye giden grafik

2. **Değişen:** `test_every_h3_video_is_rendered_with_mystic_xxx_at_half_strength` →
   `test_no_h3_video_is_rendered_with_mystic_xxx`. Üç kip aynen *(I2VA, FL2VA, REF2VA)*; gönderilen
   yığının hiçbir yuvası Mystic'i adlandırmıyor, açık ya da kapalı. REF2VA'nın kendi grafiği olmadığı
   için bunu ancak üretici söyleyebiliyor — 328'in gerekçesi. Bugün üçü de kırmızı: Mystic 0.5'te gidiyor.

### `test_producers.py` — grup

3. **Değişen:** `H3_FILES`'tan Mystic'in satırı çıkıyor. Bu listeyi iki test okuyor, ikisi de bugün
   kırmızı: `test_the_h3_group_names_its_files_the_way_the_graph_loads_them` *(grup Mystic'i sayıyor)* ve
   `test_a_machine_with_h3_on_it_has_a_video_producer` *(disk Mystic'siz, grup onu arıyor — "kurulu
   değil")*. İkincisi maddenin panel tarafı: Mystic'i olmayan makine H3'ü kurulu saymalı.

### `test_notebook_installs_the_producer_groups.py` — yalnız docstring

4. `test_the_notebook_fetches_mystic_xxx_by_its_version_into_the_loras`'ın docstring'i *"the name is
   the one the lora stack loads"* diyor; uygulamadan sonra yanlış olur. Neden durduğunu söyleyecek:
   yığın onu artık yüklemiyor, satır geri dönüşün ucuz yolu olarak kalıyor. Assert aynen; bugün de
   yeşil.

## Değişen

- *(1)*: "and Mystic XXX at half" artık doğru değil. Test 328'den önceki adına ve beklentisine dönüyor,
  bir farkla: yuvaları `on`'la süzmüyor, adlarıyla okuyor *(Kural)*. Director kablosu ve grup sorusu
  aynen.
- *(2)*: "rendered with Mystic XXX at half strength" artık doğru değil; test tersini soruyor.
- *(3)*: grubun tam listesi bir satır kısalıyor; `test_a_machine_with_h3_on_it_has_a_video_producer`
  bu yüzden bugün kırmızıya dönüyor ve uygulamada yeşile dönecek.
- *(4)*: yalnız docstring, doğru kalsın diye.

## Bekçiler, bugün de yeşil

- `test_the_notebook_fetches_mystic_xxx_by_its_version_into_the_loras` — Mystic'in dosyası inmeye
  devam ediyor.
- `test_mystic_xxx_is_kept_out_of_the_mirror` — ve aynasız iniyor.
- `test_an_unticked_group_costs_no_bytes` — `CIVITAI_H3` kendi anahtarının arkasında: 148 MB'ı yalnız
  H3 koşusu ödüyor.
- `test_every_file_the_h3_group_counts_is_fetched_by_the_notebook` — grubun saydığı her dosya defterde;
  Mystic gruptan çıkınca da doğru.
- `test_every_model_the_h3_graphs_load_is_in_the_h3_group` — grafiğin düz girdilerle yüklediği her
  dosya grupta.
- 329'un Eros testleri *(grafikler ve üç kip)* — model değişmiyor.
- 327'nin beş `MIRRORLESS` testi — listenin davranışı değişmiyor.
- `test_the_notebook_stays_well_under_what_the_tools_can_read` — defter değişmiyor.

## Sorulmayan

- **Boşalan yuvanın `str`, `vs`, `as`'ı:** öteki boş yuvalarınki de sorulmuyor; `"None"` bir şey
  yüklemiyor.
- **Disk tahmini:** dosya inmeye devam ettiği için değişmiyor.
- **Video panelinde LoRA seçimi:** bu maddede değil *(satır — yol olarak konuşuldu, seçilmedi)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız altı test: 1, 2'nin üç kipi ve 3'ün
iki testi, hepsi Mystic hâlâ yığında ve grupta olduğu için. Geri kalan her şey yeşil.
