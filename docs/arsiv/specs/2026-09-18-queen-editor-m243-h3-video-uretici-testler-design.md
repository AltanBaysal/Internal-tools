# Madde 243 · queen-editor MiniMax H3 ile video üretiyor — test turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Kararların hepsi 18 Eylül'de kullanıcıdan geldi *(maddenin satırında)*:

1. H3 **WAN'ın yanına** giriyor, ama **ikisi aynı oturumda kurulamıyor**. Defterde video tek bir açılır
   liste: **Yok / WAN / H3**. Panelde yalnız kurulu olan görünüyor.
2. Video **H3'ün kendi sesiyle** geliyor. Ses katmanı eklenebiliyor ve eklenirse videonun sesinin
   **yerine** geçiyor.
3. **Donanım tabanı yok.** H3'ün satırı emir değil bilgi veriyor: boyutu ve T4'te koşmadığı.
4. `dynv2`'yi **prompt yazarı** yazıyor. H3'ün kendi video prompt yazarı var.
5. Ayarlar 242'nin dosyalarında sabit: I2VA ve FL2VA, 4 sn, 512×768, Motion Booster 0.7.

Roadmap'in sonunda Colab'da bir deneme gerekiyor *(aşağıda, "Koşmadan bilinemeyenler")*.

## Dayandığı kurallar

- [FOUNDATION 6](../../../queen-editor/FOUNDATION.md): H3 bir ComfyUI grafiği. WAN gibi kendi
  istemcimizle sürülüyor.
- [FOUNDATION 8](../../../queen-editor/FOUNDATION.md): grafikler queen-editor'ün kendi dosyaları
  (242). Kurulum hücreleri, adresler ve damga kesme `collab-toolbox/video_experiments/minimax-h3/manual.ipynb`'den
  **bilgi olarak** kopyalanıyor; o deftere hiçbir şey bağlanmıyor.
- [FOUNDATION 9](../../../queen-editor/FOUNDATION.md): H3'ü defter kuruyor, uygulama yalnız diskte ne
  olduğunu okuyor. Adresler defterde, dosya adları `features/producers/`'da.
- [CODE-STANDARD § Features](../../../queen-editor/CODE-STANDARD.md): grafiğin şeklini bilen tek yer
  `data/` katmanında kendi dosyası. Hangi üreticinin kullanıldığına composition root karar veriyor
  (`main.py`).

## Bugün ne oluyor

Video tek üretici: WAN 2.2 *(`data/comfy_video_generator.py`)*. İki grafiği var, ve bitiş karesi
verilmişse ilk + son kare grafiği koşuyor. Prompt'u `VideoPromptWriter` yazıyor, WAN'ın I2V
kurallarıyla. Defterde `INSTALL_VIDEO` bir onay kutusu ve WAN'ı kuruyor. Ses katmanı MMAudio'dan
geliyor. Dışa aktarma sesi `-i video -i wav` ile bindiriyor, ama hangi ses akışının alınacağını
ffmpeg'in kendisine bırakıyor. WAN videosunun sesi olmadığı için bugüne kadar bu bir soru değildi.
Oynatıcı da ses katmanını videonun yanında çalıyor, videoyu susturmuyor.

## Ne olacak

**Defter.** CONFIG'de `INSTALL_VIDEO` kutusunun yerini bir açılır liste alıyor:
`VIDEO_MODEL = "Yok"  #@param ["Yok", "WAN", "H3"]`. `INSTALL_VIDEO` ondan türüyor
(`VIDEO_MODEL != "Yok"`), böylece xAI yoklaması ve cookie kapısı bugünkü gibi çalışıyor. Formdaki
satır H3'ün boyutunu ve T4'te koşmadığını söylüyor, emir vermiyor.
- **WAN'ın listeleri** `VIDEO_MODEL == "WAN"` iken iniyor, **H3'ünkiler** `VIDEO_MODEL == "H3"` iken.
  Seçilmeyen modelin tek baytı inmiyor.
- **H3'ün dosyaları**, `manual.ipynb`'nin adresleri ve adlarıyla:
  - Civitai: DaSiWa Hybrid Turbo v2 *(3314686, `diffusion_models/MiniMaxH3/` altına, grafiğin istediği
    adla)* ve Motion Booster *(3228867, `loras/`)*;
  - HF, tek bağlantıyla *(Xet paralel aralık isteklerine 403 veriyor)*: Qwen3-VL metin kodlayıcı,
    video VAE, ses VAE, `taeh3`.
- **Damga kesiliyor.** `strip_unreferenced_tail` deftere giriyor ve `fetch` onu her kontrolden önce
  çağırıyor. Sebebi `manual.ipynb`'de yazılı: niceleme aracının dosya sonuna bıraktığı imza.
- **Custom node:** `ComfyUI-DaSiWa-Nodes`. SeedControl, EnhancedVideoCombine ve LoRA yığını ondan
  geliyor. Sayı 20 → 21.
- **Disk:** H3 ~37 GiB. `manual.ipynb`'nin 40,1 GB'ından kullanılmayan iki LoRA çıkınca kalan bu.
- Klon hücresi H3'ün iki grafiğinin de repoda olduğunu kontrol ediyor.
- Flask'a hangi video modelinin kurulduğu `QE_VIDEO_MODEL` ile geçiyor: `wan`, `h3` ya da boş.

**Üretici paneli.** Video satırı kurulu olan modelin grubuna bakıyor. `model_groups` WAN grubunu
bugünkü yerinde tutuyor ve yanına H3'ünkini koyuyor. `groups_for(model)` paneline verilecek üç grubu
döndürüyor: `h3` için H3'ünkini, başka her şey için WAN'ınkini. H3 grubunun satırları grafiğin
yüklediği adlarla yazılıyor. `MiniMaxH3/` alt klasörü adın parçası
(`{"folder": "diffusion_models", "name": "MiniMaxH3/dasiwa_…"}`), çünkü ComfyUI dosyayı bu adla
arıyor ve diskteki yolu da o.

**H3 üreticisi** (`data/comfy_h3_video_generator.py`), WAN'ınkiyle aynı çağrı şekliyle:
- Bitiş karesi yoksa I2VA grafiği, varsa FL2VA grafiği koşuyor. "Mod" sözcüğü bu katmana inmiyor,
  WAN'da da inmiyor.
- Fotoğraf (ve bitiş karesi) sunucuya yükleniyor. Adları Director'ün (`2730`) timeline'ındaki
  resimlere **sırayla** yazılıyor. Resim sayısı grafiğinkiyle tutmazsa üretici duruyor ve iki sayıyı
  da söylüyor.
- Prompt Director'ün **dört yerine** birden yazılıyor: `prompt`, timeline'ın `simple_prompt`'u ve
  `resolved_prompt`'u, `builder_state`'in `simple_prompt`'u. Hangisini okuduğunu koşmadan
  bilemiyoruz, ve dördü aynıyken soru ortadan kalkıyor.
- Prompt'un başına **referans cümlesi** ekleniyor. Yazarı yazar değil kod, çünkü içeriği sahneye
  değil grafiğe bağlı: kaç resim olduğu ve videonun kaç saniye sürdüğü. Cümle grafiğin kendi
  örneklerinden alındı *(`minimax-h3/workflow.json`, "Example: FL2VA First Frame" ve "First+Last
  Frame" notları)*:
  - I2VA: `For the target video, at 0.00 seconds into the target video, Picture 1 (from Shot 1) is fully referenced.`
  - FL2VA: `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 4.00-second mark of the target video.`
    Saniye grafiğin kendi süresinden okunuyor.
  
  Cümle ile yazarın metni arasında, örneklerdeki gibi, boş bir satır var.
- Seed, SeedControl'ün (`2739`) `seed_value`'suna yazılıyor. Seed'siz iş grafiğin kendi değerine
  dokunmuyor.
- Çıktı yalnız `.mp4`. Önizleme node'u render sayılmıyor.
- `seconds()` Director'ün `duration`'ını okuyor, yani 4. Dışa aktarma özeti de bu sayıyı alıyor.
- Grafik yoksa, UI formatındaysa ya da Director veya SeedControl eksikse WAN üreticisinin
  cümleleriyle duruyor.

**H3 prompt yazarı** (`H3VideoPromptWriter`, `xai_prompt_writer.py`'de). Fotoğrafın prompt'unu
okuyor, `H3_VIDEO_INSTRUCTION` ile. Talimat H3'ün bölümlü biçimini istiyor:
- `integrated_multimodal_description:` hareket, ve **`dynv2.` ile başlıyor**;
- `overall_soundscape:` sahnenin ve hareketin sesleri;
- `non_diegetic_music: N/A`. Müzik yok: ses katmanının talimatı da müzik istemiyor.

**Ses katmanı videonun sesinin yerine geçiyor, iki yerde:**
- **Dışa aktarma:** sesli bir parçada akışlar açıkça seçiliyor: `-map 0:v:0 -map 1:a:0`. Görüntü
  videodan, ses katmandan geliyor. Sessiz parça bugünkü gibi kopyalanıyor ve H3'ün kendi sesi
  içinde kalıyor.
- **Oynatıcı:** ses katmanı varken video susturuluyor. Yoksa video kendi sesiyle çalıyor.

**Composition root.** `config.VIDEO_MODEL` `h3` ise H3 üreticisi ve H3 yazarı bağlanıyor, değilse
bugünkü WAN. Bu tek bir `if`. `main.py`'yi hiçbir test import etmiyor, bu yüzden takım onu değil
parçalarını tutuyor.

## Koşmadan bilinemeyenler

Roadmap sonundaki Colab denemesinde görülecek:
- Director'ün timeline'ı tek resimle I2VA'da koşuyor mu? Biçim FL2VA export'undan alındı.
- `DaSiWa_SeedControl` API modunda `seed_value`'yu olduğu gibi kullanıyor mu? Export'taki
  `seed_control_state` `random` diyor.
- EnhancedVideoCombine'ın `container: Auto`'su `.mp4` yazıyor mu?

Üçünden biri tutmazsa üretici ya çıktıyı bulamadığını ya da ComfyUI'nin kendi hatasını söylüyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Bitiş karesi olmayan video I2VA grafiğiyle, olan FL2VA grafiğiyle üretiliyor; resimler yükleniyor ve timeline'a sırayla yazılıyor | **kırmızı** |
| 2 | Prompt dört yere birden, referans cümlesiyle yazılıyor; FL2VA cümlesi grafiğin süresini söylüyor | **kırmızı** |
| 3 | Seed `seed_value`'ya yazılıyor; seed'siz iş grafiğinkine dokunmuyor | **kırmızı** |
| 4 | Yalnız `.mp4` render sayılıyor; `seconds()` Director'ün süresi | **kırmızı** |
| 5 | Fotoğrafsız video, eksik grafik, UI formatı, eksik node ve tutmayan resim sayısı kendi cümlesiyle duruyor | **kırmızı** |
| 6 | H3 yazarı fotoğrafın prompt'unu H3 talimatıyla gönderiyor; talimat `dynv2`'yi ve üç bölümü istiyor | **kırmızı** |
| 7 | H3'ün iki grafiği API formatında, Director ve SeedControl'ü taşıyor; modları I2VA / FL2VA, timeline'ları 1 / 2 resim | **kırmızı** |
| 8 | H3'ün iki grafiği aynı süreyi (4) ve aynı boyutu (512×768) üretiyor | **kırmızı** |
| 9 | H3 grafiklerinin yüklediği her model H3 grubunda; LoRA yığınında yalnız Motion Booster 0.7 açık ve grupta | **kırmızı** |
| 10 | H3 grubu grafiğin adlarıyla yazılı; `groups_for` `h3`'e H3'ü, gerisine WAN'ı veriyor | **kırmızı** |
| 11 | `config.VIDEO_MODEL` varsayılanı boş; H3 grafiklerinin yolları repodaki dosyalar | **kırmızı** |
| 12 | Defterde video bir açılır liste: Yok / WAN / H3, `INSTALL_VIDEO` ondan türüyor; foto ve ses kutu olarak kalıyor | **kırmızı** |
| 13 | WAN'ın ve H3'ün listeleri kendi seçimlerinin arkasında; H3'ün HF dosyaları tek bağlantıyla iniyor | **kırmızı** |
| 14 | Defter H3 grubunun her dosyasını ve iki Civitai sürümünü indiriyor; damgayı kesiyor; DaSiWa node'larını kuruyor; H3'ün diskini sayıyor | **kırmızı** |
| 15 | Defter `QE_VIDEO_MODEL`'i geçiyor ve H3'ün iki grafiğini klonda arıyor; formda H3 satırı T4'ü anıyor | **kırmızı** |
| 16 | Sesli parça görüntüyü videodan, sesi katmandan alıyor | **kırmızı** |
| 17 | Sessiz parça kopyalanıyor (H3'ün sesi içinde kalıyor) | yeşil *(bekçi)* |
| 18 | Oynatıcı ses katmanı varken videoyu susturuyor, yokken susturmuyor | **kırmızı** |

## Bu turda değişen

Yalnız testler:
- **Yeni:** `test_comfy_h3_video_generator.py`.
- **Kırmızıyı taşıyan eklemeler:** `test_video_prompt_writer.py`, `test_workflow_asset.py`,
  `test_producers.py`, `test_notebook_installs_the_producer_groups.py`, `test_export.py`,
  `LayerPlayer.test.jsx`.
- **Değişen iki test:**
  - `test_every_producer_has_a_checkbox_of_its_own` artık fotoğraf ve sesi soruyor; video açılır
    listeye geçiyor.
  - `test_an_unticked_group_costs_no_bytes` WAN'ın listelerini `VIDEO_MODEL == "WAN"`'ın arkasında
    arıyor.
  - Beklenen `ffmpeg` satırı `-map`'lerle yazılıyor.
- **Sterillik test edilmiyor** *(kullanıcı kararı, 242)*.
