# v14 · Görev 1 — Motorun bitiş karesi alabilmesi · **test turu**

**Kaynak:** [Yol haritası v14, 1. madde](../plans/2026-08-20-queen-editor-v14-roadmap.md) ·
[20 Ağustos arayüz brifi, 3. bölüm](../research/2026-08-20-queen-editor-arayuz-brifi.md)

Bu tur yalnız testleri yazar. Takım kırmızı biter ve kırmızı commit edilir; kodu ikinci tur yazar.

## Bu turun sınırı

**İçeride:** video üreticisinin bitiş karesi alabilmesi, hangi grafiği yükleyeceğine karar vermesi,
her iki karenin ComfyUI'ye yüklenmesi, yeni grafiğin depodaki hâlinin doğrulanması, ve yeni grafiğin
okuduğu modelin üreticiler listesinde adının geçmesi.

**Dışarıda:** bitiş karesinin hangi kare olduğuna karar vermek. Üretim modu, kuyruk, `run_loop` —
hepsi 2. maddenin işi. Bu turdan sonra motor bitiş karesi **alabiliyor** olacak, ama ona bir bitiş
karesi veren kimse olmayacak. Madde başlığının söylediği tam olarak bu.

## Kararlar

**1. İki grafik yan yana durur.** `workflow_video_api.json` standart üretimin, yeni
`workflow_video_first_last_api.json` bitiş kareli üretimin. Sebebi kullanıcı kararı ve ölçüldü:
FIRST2LASTFRAME, I2V hattının bir node'u değişmiş hâli değil — kendi checkpoint'i, kendi CLIP
vision'ı, kendi sampling'i olan ayrı bir hat. Standart üretimi ona taşımak bugün çalışan videoların
karakterini değiştirirdi.

**2. Üretici modu bilmez, yalnız bitiş karesi verilip verilmediğini bilir.** `generate` bir `end`
argümanı alır; **verildiyse** yeni grafik, verilmediyse bugünkü grafik yüklenir. Loop ile bağlı
arasındaki fark yalnız hangi fotoğrafın gönderildiği — ikisi de aynı grafiği kullanır. Böylece
"üretim modu" kavramı `data/` katmanına hiç inmez; orada kalması gereken yer domain.

**3. Bitiş karesi de kaynak fotoğraf gibi yüklenir.** İkisi de `(ad, bayt)`, ikisi de
`upload_image` ile ComfyUI'ye gider, dönen ad grafiğe yazılır — biri `338`'e, öteki `342`'ye.

**4. Süre tek grafikten okunur, ama ikisinin aynı olduğu teste bağlanır.** `seconds()` bugünkü
grafiği okumaya devam eder; export tahmini oradan besleniyor. İki grafik farklı süre taşırsa tahmin
yalan söyler, o yüzden eşitlikleri kendi testini alır. Bugün ikisi de 5.

**5. Yeni grafik de varlık olarak doğrulanır.** Bugünkü grafiğin `test_workflow_asset.py`'daki
nöbeti neyse yenisininki de o: API formatında mı, yamaladığımız node'lar yerinde mi, ve **yüklediği
her model üreticiler listesinde adı geçiyor mu**. Sonuncusu `clip_vision_h.safetensors`'ı listeye
sokar; listeye girince de defterin o dosyayı indirmesi
`test_notebook_installs_the_producer_groups.py` tarafından zaten isteniyor. Yeni test yazmaya gerek
yok — var olan nöbet bu işi görüyor.

**6. Bitiş karesi kaynak fotoğrafın yerini tutmaz.** `end` verilip `source` verilmezse bugünkü
"kaynak foto verilmedi" hatası aynen çıkar: video bir resmin üstüne kurulur, bitiş karesi onun
yerine geçmez.

## Yazılacak testler

### `backend/tests/test_workflow_asset.py`

| # | Test | Ne diyor |
|---|---|---|
| 1 | `test_the_first_last_video_workflow_is_api_format_with_the_nodes_we_patch` | `338`/`342` LoadImage, `343` WanFirstLastFrameToVideo'da iki kare girişi, `333:291` prompt+seed, `327` seed |
| 2 | `test_both_video_graphs_agree_on_how_long_a_render_runs` | `178` ile `335` aynı sayıyı taşıyor |
| 3 | `test_every_model_the_first_last_graph_loads_is_in_the_video_group` | Grafiğin yüklediği her dosyanın adı listede |

### `backend/tests/test_comfy_video_generator.py`

| # | Test | Ne diyor |
|---|---|---|
| 4 | `test_a_video_with_no_end_frame_is_rendered_by_the_standard_graph` | Bugünkü node'lar yamalanıyor, yeni grafik hiç okunmuyor |
| 5 | `test_a_video_with_an_end_frame_is_rendered_by_the_first_last_graph` | `338`, `342`, `333:291`, `327` yamalanıyor |
| 6 | `test_both_frames_reach_the_server_as_uploads` | İki yükleme, önce başlangıç sonra bitiş |
| 7 | `test_an_end_frame_does_not_stand_in_for_the_photo` | `end` var `source` yok → "foto" hatası |
| 8 | `test_a_missing_first_last_graph_names_the_file_it_wants` | Dosya adı hatada geçiyor |
| 9 | `test_a_first_last_graph_exported_in_ui_format_says_which_export_to_use` | "Export (API)" hatada geçiyor |
| 10 | `test_a_first_last_graph_whose_nodes_moved_names_the_missing_one` | Eksik node numarası hatada geçiyor |
| 11 | `test_the_length_is_still_read_from_the_standard_graph` | `seconds()` davranışı değişmedi |

### `backend/tests/test_producer_contract.py`

| # | Test | Ne diyor |
|---|---|---|
| 12 | `test_a_producer_with_no_end_frame_takes_the_argument_anyway` | Foto ve ses üreticileri `end` alıp yok sayıyor — kuyruğun tek çağrı biçimi var |

## Bitti sayılır

`python -m pytest queen-editor -q` on iki yeni testte kırmızı. Kırmızılık üreticinin `end`
bilmemesinden, `config`'de yeni grafiğin yolunun olmamasından ve `clip_vision_h`'ın üreticiler
listesinde bulunmamasından geliyor. Susturulmuş tek test yok.
