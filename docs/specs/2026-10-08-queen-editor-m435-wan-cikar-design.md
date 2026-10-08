# Madde 435 · WAN Queen Editor'den çıkar — tasarım

**Tarih:** 8 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
435 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Kod için hiçbir şey. Kullanıcı roadmap'in sonunda Colab'da dener: H3 videosu, fotoğraf ve ses bugünkü
gibi üretiliyor mu, ve ComfyUI hücresi 9 paketle kalkıyor mu *(aşağıda, Risk)*.

## Ne, neden

Kullanıcı *(8 Ekim)*: *"wan modelini kaldıralım queen editorden direkt kullanımıyor zaten"*. Queen
Editor bundan sonra yalnız H3 videosu üretir. WAN'ın grafikleri, üreticisi, seçimi, Queen AI'daki
metni, notebook'taki indirmesi ve yalnız WAN için duran her şey gider.

**Claude'un önerisi, kabul edildi** *(kullanıcı, 8 Ekim — "sırayla koş paralele koşma acelem yok")*:
projelerde daha önce üretilmiş WAN videoları yerinde kalır, açılır ve export'a girer. Giden yalnız
WAN üretimi. Bu yüzden eski videoları okuyan hiçbir şeye dokunulmaz: galeri, karenin sayfası, kayıt,
export ve sessiz videoya sessiz iz ekleyen yol *(`ffmpeg_video_exporter`'ın `sound`'u ve
`_with_sound`'u — eski WAN videosunun ses izi yok)*.

## Oturum bugün nasıl "H3" ya da "WAN" oluyor

Notebook'un CONFIG'inde iki kutu var, `VIDEO_WAN` ve `VIDEO_H3`. Notebook seçileni
`QE_VIDEO_MODEL`'le (`"wan"`, `"h3"` ya da video kurulmadıysa `""`) uygulamaya geçiriyor, ve
uygulamada altı yer ona bakıyor:

| Yer | `"h3"` | `"wan"` ya da `""` |
|---|---|---|
| `main.py` — üretici ve prompt yazarı | `ComfyH3VideoGenerator`, `H3VideoPromptWriter` | `ComfyVideoGenerator`, `VideoPromptWriter` |
| `main.py` — kuyruğun uzunluğu | projenin uzunluğu | `None`, iş uzunluk taşımaz |
| `queue_references`'ın `has_h3`'ü | Referanstan çalışır | `NoReferenceProducer` |
| `model_groups.groups_for` | H3'ün dosyaları | WAN'ın dosyaları |
| Üreticiler satırının `model`'i | `"MiniMax H3"` | `"WAN 2.2 I2V"` |
| Üreticiler satırının `reads_references`'ı | `true` | `false` |

Video panelinde iki şey `reads_references`'a bakıyor: *Video uzunluğu* seçimi
(`useVideoLength`) ve Referanstan'ın düğmenin üstündeki *"Referanstan üretim için H3 gerekiyor…"*
satırı. Karenin sayfasındaki *"Yeniden üret"* ve *"Tekrar dene"* notlarının uzunluğu da aynı kancadan
geliyor.

**Olacak:** `QE_VIDEO_MODEL` ve `config.VIDEO_MODEL` gider. Uygulama her oturumda H3'ü kurar; video
kurulmadıysa üreticiler paneli bunu H3'ün dosyalarına bakarak söyler, bugün bir H3 oturumunda dosyalar
eksikken söylediği gibi. `INSTALL_VIDEO` artık "H3'ü kur" demek.

## Video paneli ne gösterir

Her oturumun video paneli bugünkü H3 oturumunun paneli — her hâlinde, tasarımcının kuralları dahil:

- Üreticiler satırı `{id, name, installed, model: "MiniMax H3"}`. `reads_references` gider: tek işi
  WAN'ı H3'ten ayırmaktı. *Model* kutusu adı bugünkü gibi sunucudan okur, ve sunucu cevap verene kadar
  boş kalır.
- *Video uzunluğu* seçimi, üreticilerin video satırı okununca ve projenin uzunluğu okununca çizilir.
  Bugün de "model okunmamışken çizilmez" *(424, tasarımcının kararı)*, ve bugün de bir H3 oturumunda
  video üreticisi kurulu değilken çizilir.
- *"Kuyruğa ekle"*nin altındaki cümle ve karenin sayfasının iki notu uzunluğu her oturumda söyler.
- Referanstan'ın *"Referanstan üretim için H3 gerekiyor — bu oturumda başka bir video modeli
  kurulu."* satırı ve sunucunun `NoReferenceProducer`'ı gider: yalnız WAN oturumunda çıkabiliyorlardı.
  *"Havuzda referans yok…"* satırı bugünkü gibi.

**Ekranda görünen tek değişiklik:** video kurulmamış bir oturumda panel bugün *"WAN 2.2 I2V"* yazıyor ve
uzunluk çizmiyor. Artık *"MiniMax H3"* yazar ve uzunluğu çizer; üstte kurulum kartı, ve *Kuyruğa
ekle* bugünkü gibi kapalı.

**Elenen — model adını frontend'e koymak**, sesin *"MMAudio v2"*'si gibi, ve satırdan `model`'i
çıkarmak: birkaç satır kısa, ama *Model* kutusunun ve uzunluk bloğunun ne zaman çizildiğini değiştirir.

## Export ve özetin toplamı (madde 423)

`export_summary` ve `main.py`'deki bağlantısı değişmez. Uzunluğunu söyleyen satır kendi uzunluğuyla
sayılır: 423'ten beri yazılan her satır, WAN'ınkiler dahil — WAN'ın satırı 5 der, ve 5 sayılmaya devam
eder. Uzunluk söylemeyen satır — 423'ten *(6 Ekim)* önce yazılmış satır — oturumun grafiğiyle, artık her
zaman H3'ün 4'üyle sayılır.

**Sınır:** 423'ten önce yazılmış bir WAN satırı artık 4 saniye sayılır, 5 değil — bugün bir H3
oturumunun onu saydığı gibi. Satır ve plan hangi modelin yaptığını söylemiyor; bilmenin tek yolu
dosyayı ffprobe'la ölçmek, ve 423 her özette her video için bir Drive okuması ve bir süreç demek
olduğu için ölçmemeyi seçti *(koordinatörün kararı, 8 Ekim)*. Export'un kendisi dosyaları birleştirir;
toplam yalnız özetin cümlesi.

## Notebook

- **CONFIG:** *Video modelleri* bölümü, `VIDEO_WAN` ve `VIDEO_H3` kutuları, iki kontrolleri
  (*"Video seçildi ama model işaretlenmedi"*, *"WAN ve H3 aynı oturumda kurulmaz"*) ve `VIDEO_MODEL`
  gider. Üreticilerin cümlesi *"Video ~37 GiB"* der. Seçim satırı *"video (H3)"*.
- **Klon:** üç grafiği arar — fotoğraf ve iki H3.
- **ComfyUI hücresi:** 20 paketten yalnız WAN'ın grafiklerinin kullandığı 11'i gider *(koordinatör, 8
  Ekim — öğenin "notebook'taki indirmesi"nin içinde)*: `comfy_mtb`, `ComfyUI-VideoHelperSuite`,
  `ComfyUI-WanVideoWrapper`, `ComfyUI-GGUF`, `ComfyMath`, `ComfyUI-Frame-Interpolation`,
  `ComfyUI-VFI`, `ComfyUI_Comfyroll_CustomNodes`, `ComfyUI-mxToolkit`, `ComfyUI-NAG`,
  `comfyui-adaptiveprompts`. Kalan 9: Manager, rgthree, Impact-Pack, Easy-Use, Custom-Scripts,
  UltimateSDUpscale, KJNodes, ppm, DaSiWa. Başlık ve giriş hücresi *"(9)"* der. **Nasıl bulundu:** iki
  H3 grafiği ComfyUI'nin kendisini, DaSiWa'yı ve KJNodes'u kullanıyor *(`ModelAttentionBackend` ve
  `MiniMaxH3*` çekirdekten — `minimax-h3/workflow.json`'un `cnr_id`'leri)*; fotoğraf grafiği
  çekirdeği, Impact-Pack'i, ppm'i, rgthree'yi ve Easy-Use'u. Manager, Custom-Scripts ve
  UltimateSDUpscale fotoğrafın notebook'undan (`nova-3dcg`) geldi. Giden 11 yalnız WAN'ın notebook'unda
  (`wan22-arbuzai`) vardı, ve düğümlerini yalnız WAN'ın grafikleri kullanıyordu.
- `!pip install -q opencv-python imageio imageio-ffmpeg` satırı **kalır**: WAN'ın notebook'undan
  geldi, ama DaSiWa'nın video kaydedicisinin `imageio-ffmpeg`'i okuyup okumadığı burada anlaşılamıyor.
- **Modeller:** WAN'ın listeleri (`HF_VIDEO`, `CIVITAI_VIDEO`) ve yalnız WAN'ın CLIP vision'ının
  indiği `clip_vision` klasörü gider. `HF_H3` ve `CIVITAI_H3` `INSTALL_VIDEO`'nun arkasında; disk hesabı
  `(INSTALL_VIDEO, 37, "video (H3)")`.
- **Flask hücresi:** `QE_VIDEO_MODEL` gider.

## Risk

**H3 grafiği Queen Editor'de o 11 paket olmadan hiç koşmadı.** H3 243'te geldiğinde paketler WAN için
zaten kuruluydu. 213'ün deneme notebook'u H3'ün grafiğini yalnız Manager, rgthree, KJNodes, GGUF,
DaSiWa ve MMH3-UltimateUpscale'le koşturdu — GGUF orada tam grafiğin sahipsiz yükleyicileri içindi, ve
bizim export'umuzda öyle bir düğüm yok. Kullanıcının Colab denemesi gösterir; bir paket gerekirse geri
gelir.

## Kod — giden ve değişen

**Giden dosyalar:** `assets/workflow_video_api.json`, `assets/workflow_video_first_last_api.json`,
`backend/features/photo_generation/data/comfy_video_generator.py`,
`backend/tests/test_comfy_video_generator.py`.

**Değişen:**

- `config.py` — `VIDEO_WORKFLOW_PATH`, `VIDEO_FIRST_LAST_WORKFLOW_PATH` ve `VIDEO_MODEL` gider.
  `H3_VIDEO_*` adları kalır.
- `main.py` — dal gider: video üreticisi `ComfyH3VideoGenerator`, yazarı `H3VideoPromptWriter`;
  `_video_length` her zaman projenin uzunluğu; `queue_references` `has_h3`'süz; üreticiler paneli
  `list_producers(GROUPS, _model_files)`.
- `prompt_writer.py` — `VIDEO_INSTRUCTION` ve `VideoPromptWriter` gider. Döngünün ve bağlı videonun
  kurallarının yorumları yalnız H3'ü söyler.
- `queue_references.py` — `has_h3` parametresi ve `NoReferenceProducer` gider; sıra: proje, prompt
  listesi, varyant, havuz. `reference_routes.py` onu yakalamaz.
- `model_groups.py` — `GROUPS["video"]` H3'ün altı dosyası; `H3_VIDEO`, `groups_for` ve
  `video_model_name` gider.
- `producers.py` — `VIDEO_MODEL = "MiniMax H3"`, *Model* kutusunun adı.
  `list_producers(groups, files)` video satırına onu yazar; `reads_references` yok.
- Yalnız yorum ve belge: `comfy_h3_video_generator.py`, `ports.py`, `run_loop.py`'nin `_made_with`'i,
  `video_length.py`, `queue_layer.py`, `regenerate.py`, `retry_frame.py`,
  `ffmpeg_video_exporter.py`'nin `sound`'u *(eski WAN videosunun sesi yok)*. Uzunluğun `None`'ı
  kalır: uzunluk verilmeyen çağıran — çoğu test — işe uzunluk yazmaz, ve 422'den önce kuyruğa girmiş
  iş grafiğin 4'ünde çıkar.
- Frontend — `useVideoLength.js` satır okununca çizer; `LayerPanel.jsx`'ten `H3_ONLY` ve
  `poolRefusal`'ın ilk satırı gider; yorumlar. `dist` yeniden derlenir.
- Belgeler — `CODE-STANDARD.md`'nin miras tablosu (video grafikleri H3'ün, düğüm id'leri `"2730"` ve
  `"2739"`, kaynak `video_experiments/minimax-h3/`), `README.md`'nin CONFIG'i ve DeepSeek satırı,
  `BACKLOG.md`'deki loop maddesi (WAN yolunun artık olmadığı notu). `FOUNDATION.md`'de WAN geçmiyor;
  değişmez.

## Testler

**Yalnız WAN için olanlar gider:** `test_comfy_video_generator.py` bütünüyle;
`test_workflow_asset.py`'nin WAN grafiklerini soran yedi testi ve `config.VIDEO_MODEL`'i soran biri;
`test_producer_contract.py`'nin iki WAN uzunluğu testi; `test_composition_root.py`'nin WAN oturumu
testleri; `test_producers.py`'nin WAN satırını ve `groups_for`'u soranları;
`test_video_prompt_writer.py`'nin WAN metni ve yazarı testleri; `test_reference_usecases.py`'nin
*"H3'süz Referanstan reddedilir"*i; `test_video_length.py`'nin *"WAN oturumu uzunluk taşımaz"*ı;
notebook testlerinden iki kutuyu, iki kontrolü, video modelleri bölümünü ve `QE_VIDEO_MODEL`'i
soranlar; frontend'de WAN satırıyla kurulan panel ve sayfa testleri.

**Bütün grafiklerde bir kuralı soran testler kalanlar için sorar:**

- `test_every_graph_makes_a_portrait_frame` — fotoğraf grafiği ve iki H3 Director'ı.
- `test_every_writer_s_system_prompt_ends_with_queen_agent_s_suffix` — H3'ün ve sesin yazarı; döngüden
  yalnız `VideoPromptWriter` çıkar *(koordinatör)*.
- `test_a_failed_answer_is_never_a_prompt` — H3 ve ses.
- `test_every_graph_config_names_is_a_file` — üç grafik.
- `test_every_file_the_panel_counts_is_fetched_by_the_notebook` — dosyayı adının son parçasıyla arar,
  çünkü H3'ün satırları `MiniMaxH3/`'ü taşıyor; aynı şeyi H3 için soran test onunla birleşir.
- Üreticilerin sözleşme testi gerçek üreticileri koşturur: video üreticisi artık H3'ün.

**QueenAgent'ın `prompt.py`'sini okuyan iki dosya:** ikisi de yalnız WAN yazarını test etmiyor.
`test_video_prompt_writer.py`'de `test_the_suffix_is_queen_agent_s_word_for_word` değişmez;
`test_every_writer_s_system_prompt_ends_with_queen_agent_s_suffix`'in döngüsünden yalnız
`VideoPromptWriter` çıkar — ad artık yok. `test_agent_answer.py`'ye dokunulmaz.

**Dokunulmayan, ve neden:** `test_export.py`'nin sessiz WAN videosu testleri — eski WAN videoları
export'a girmeye devam eder. `test_colab_downloads.py`'nin WAN VAE'li örneği — `hf_fetch`'in dosyayı
verilen adla koyduğunu test ediyor, WAN'ı değil.

**Kırmızı önce** *(kod değişmeden kırmızı)*:

1. Assets'te yalnız üç grafik var: `workflow_api.json`, iki H3 grafiği.
2. Uygulama `QE_VIDEO_MODEL`'süz H3'ü kurar: video üreticisi `ComfyH3VideoGenerator`, yazarı
   `H3VideoPromptWriter`, ve kuyruk projenin uzunluğunu okur.
3. Üreticilerin video satırı `{id, name, installed, model}`, `model` `"MiniMax H3"`; video grubu H3'ün
   dosyaları.
4. Referanstan `has_h3`'süz çalışır.
5. Notebook'ta WAN'dan iz yok: kutular, `VIDEO_MODEL`, `QE_VIDEO_MODEL`, WAN'ın dosyaları ve
   depoları, `clip_vision`, iki WAN grafiği ve 11 paket.
6. `prompt_writer`'da WAN'ın yazarı ve metni yok.
7. Frontend: `reads_references` taşımayan bir video satırıyla uzunluk çizilir ve cümleler onu söyler;
   Referanstan H3_ONLY demez ve düğme açılır; karenin sayfasının notları uzunluğu söyler.

**Koşuda görülen:** son testlerle, kod değişmeden backend'de 29, frontend'de 24 test kırmızı — hepsi
yeni biçimden (backend'in 29'unu QA ölçtü; coder'ın ilk kırmızı adımı, kalan test düzenlemelerinden
önce, 23 gösterdi); değişince ikisi de yeşil. Notebook'un kalan dokuz paketini ve sayısını soran bir test de
eklendi (`test_the_notebook_keeps_the_packages_the_photo_and_h3_graphs_read`). `ProjectScreen.test.jsx`'in
`api.js` sahtesi artık `getVideoLength`'e de cevap veriyor: video paneli uzunluğu satır okununca
soruyor, ve o testlerin satırı `reads_references` taşımadığı için bugüne kadar hiç sormuyordu. WAN'ın
şekil testindeki kural — iki şekil ayrılınca resim sessizce esner — H3'ün şekil testinin docstring'ine
taşındı.

## Sınırlar

- Eski WAN videoları, satırları ve plan satırları olduğu gibi kalır; hiçbir şey taşınmaz ya da
  silinmez. Kuyrukta WAN zamanından kalmış bir iş varsa H3 yapar, uzunluk taşımıyorsa grafiğin 4'ünde
  — bugün bir H3 oturumunun yaptığı gibi.
- `hf_fetch`, `civitai_fetch` ve `colab/`'un geri kalanı değişmez.
- `export_summary` değişmez *(yukarıda, Sınır)*.
- Roadmap'e dokunulmaz.

## Bitti sayılır

- Queen Editor'de WAN seçilemiyor ve üretilemiyor: kutusu, grafikleri, üreticisi, yazarı ve
  `QE_VIDEO_MODEL` yok; notebook WAN'ın modellerini ve paketlerini indirmiyor.
- Video paneli her oturumda bugünkü H3 paneli; Referanstan'ın H3_ONLY satırı yok.
- Eski projelerdeki WAN videoları açılıyor ve export'a giriyor; özetin toplamı uzunluğunu söyleyen
  satırı kendi uzunluğuyla sayıyor.
- Kırmızı testler kod değişmeden kırmızı, değişince yeşil; dört satır yeşil; `dist` yeniden
  derlenmiş.
- Colab'da: H3, fotoğraf ve ses 9 paketle üretiliyor — kullanıcının denemesinde görülecek.
