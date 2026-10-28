# Madde 469 · Yüz detailer'ı geri açılır — 430'un geri alınması

**Tarih:** 12 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
469 · **Dal:** `feat/queen-editor-v9` (ana klasör, worktree yok) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md) ·
**Geri alınan:** [m430 uygulama](2026-10-07-queen-editor-m430-detailer-yok-uygulama-design.md)
*(`0730ac56`, `f2515493` testler; `07f099ed` kod)*

## Kullanıcının istediği

12 Ekim 2026: "Yüz detailer'ını geri aç ... 430'u geri alırım: grafik, notebook'taki indirmeler (yüz
dedektörü, SAM, Impact-Subpack) ve Üreticiler paneli 430'dan önceki haline döner. Elimizde hazır
duruyor, yeni bir export gerekmez." — "bunu aç queen agentta branchında aç".

Görülecek sonuç: Colab'da fotoğraf yeniden FaceDetailer'dan geçerek kaydedilir; notebook yüz
dedektörünü ve SAM'i indirir, Impact-Subpack'i kurar; Üreticiler paneli fotoğrafı ancak bu iki dosya
da diskteyse kurulu sayar.

## 430'dan bu yana değişen zemin

`git revert 07f099ed` tek başına uygulanamaz; 430'un dokunduğu yerlerden üçü sonra taşındı:

- **438** notebook'un kodunu `colab/` modüllerine taşıdı. Modeller hücresi artık klasör açmıyor
  (`hf_fetch` ve `fetch` hedef klasörü kendileri açıyor), indirme döngüleri
  `colab/downloads.py`'deki `download_models(hf_jobs, civitai_jobs, mirror, cookie)`'de, klasör
  listesi hücredeki `FOLDERS` satırlarından `show_folders` ile basılıyor. 430'dan önceki "açık adresli
  indirme döngüsü"nün bugün bir yeri yok — aşağıda `download_models`'a döner.
- **435** custom node'ları 20'den 9'a indirdi; Subpack dönünce 10 olur.
- **432** `hf_fetch`'e yeniden deneme ekledi; yüz dedektörü `hf_fetch` ile indiği için bunu kendiliğinden
  alır, ayrıca bir şey gerekmez. `fetch` (açık adres) değişmedi.

`assets/workflow_api.json` 430'dan beri hiç değişmedi (`git diff 07f099ed HEAD` boş). Grafik bu yüzden
birebir 430'un öncesine döner.

## Grafik — `assets/workflow_api.json`

Dosya `07f099ed^`'deki haline döner (`git show 07f099ed^:queen-editor/assets/workflow_api.json`),
bayt bayt; elle yazılmaz. Geri gelenler:

- `5` ToDetailerPipe (`model` ← `44`, `clip` ← `27`/1, `vae` ← `34`, `positive` ← `36`,
  `negative` ← `38`, `bbox_detector` ← `42`, `sam_model_opt` ← `6`)
- `6` SAMLoader `sam_vit_b_01ec64.pth`, `AUTO`
- `9` ve `42` UltralyticsDetectorProvider `bbox/face_yolov9c.pt`
- `14` Edit DetailerPipe (`[CONCAT] {face|face,detailed face}`, `detailer_pipe` ← `5`,
  `bbox_detector` ← `9`)
- `19` Max Size 1536, `24` Tiled Detailer `false`, `37` BBOX Crop Factor 2.5
- `31` FaceDetailer (pipe) — `image` ← `33`, `detailer_pipe` ← `14`, `seed` ← `40`, `cfg` ← `18`,
  `max_size` ← `19`, `bbox_crop_factor` ← `37`, `tiled_encode`/`tiled_decode` ← `24`; 14 adım,
  denoise 0.26
- `44` Differential Diffusion (`model` ← `27`)
- `57` Image Comparer (rgthree) — A `31`, B `33`
- **Save Image** (`50`): `images` `["33", 0]` yerine yeniden `["31", 0]`.

Kalan 21 düğümün girdisi değişmez. Image Comparer'ın önizlemeleri `temp` tipinde ve `images` dışında
bir anahtarda gelir; `ComfyClient.fetch_outputs` (madde 411) yalnız `type == "output"` görüntüleri
saydığı için bir işin resim sayısını değiştirmez.

## Üreticiler paneli — `backend/features/producers/domain/model_groups.py`

Fotoğraf grubunun sonuna, Remacri'den sonra, 430'un çıkardığı iki satır ve yorumu döner:

```python
        # UltralyticsDetectorProvider lists this one as "bbox/<name>", so the folder is nested.
        {"folder": "ultralytics/bbox", "name": "face_yolov9c.pt"},
        {"folder": "sams", "name": "sam_vit_b_01ec64.pth"},
```

Grubun başındaki yorum 430'dan öncekinin bugünkü loralarla söylenişi olur: checkpoint ve loralar
render'ın kendisi; kalan üçü aynı grafiğin dalları — varsayılan açık FaceDetailer dedektörü ve SAM'i
açılışta yükler, bypass'lı Ultimate SD Upscale Remacri'yi açıldığı anda okur; yalnız render'ın
dosyalarını saymak "fotoğraf üreticisi kurulu" sözünü yalan yapar. "madde 430" cümlesi çıkar.

Panel grupları backend'den okuyor; frontend'de değişen bir şey yok, `dist` yeniden derlenmez.

## İndirme kodu — `colab/downloads.py`

SAM tek açık adresli dosyadır ve bugün açık adres için bir döngü yok. `download_models` üçüncü bir
liste alır, 430'dan önceki sırayla — HF, açık adres, Civitai:

```python
def download_models(hf_jobs, open_jobs, civitai_jobs, mirror, cookie):
    """The Hugging Face files, then those fetched by their address, then the Civitai ones. Every
    file's row, in that order, for download_summary."""
    rows = []
    for repo, path, folder, filename, label, floor in hf_jobs:
        rows.append(hf_fetch(repo, path, folder, filename, label, floor=floor))
    for url, folder, filename, label, floor in open_jobs:
        rows.append(fetch(url, folder, filename, label, parallel=True, floor=floor))
    for version_id, folder, filename, label in civitai_jobs:
        rows.append(civitai_fetch(mirror, version_id, folder, filename, label, cookie))
    return rows
```

`open_jobs` konumsal ve varsayılansız: unutulmuş bir argüman notebook'ta sessiz bir boş liste değil,
`TypeError` olur. Var olan bir fonksiyonun imzası değiştiği için ana ajana soruldu; cevap aşağıda,
Kararlar 1.

`fetch` dokunulmaz; `parallel=True` aria2c'nin 16 bağlantısı, `floor` .pth'yi boyutundan yargılar,
klasörü kendisi açar.

**Maliyet:** dosya diskteyse `fetch` tek bir `exists` + başlık okumasıyla döner (her Run all'da O(1),
ağ yok). İlk kurulumda SAM ~375 MB tek indirme, dedektör ~40 MB tek `hf_hub_download`. Yarıda kalan
SAM `.part`'tan sürer; bozuk dosya silinmez, hücre dosyanın başını basarak durur (bugünkü `fetch`
davranışı).

## Notebook — `queeneditor.ipynb`

Hücreler Edit ile düzenlenir (NotebookEdit ya da JSON'un `source` dizgesi); betikle değil.

- **Giriş hücresi:** "(9 custom node)" → "(10 custom node)".
- **Başlık hücresi:** "## ComfyUI + Custom Node'lar (9)" → "(10)".
- **ComfyUI hücresi:** `CUSTOM_NODES`'ta Impact-Pack'in hemen altına, 430'dan önceki yerine:
  `("ComfyUI-Impact-Subpack",    "https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git"),`
- **Modeller hücresi** (`# === Target folders ===`):
  - `UPSC`'nin altına `BBOX = f"{COMFY}/models/ultralytics/bbox"` ve
    `SAMS = f"{COMFY}/models/sams"`. `os.makedirs` döngüsü geri gelmez — 438'den beri klasörü
    indirici açıyor.
  - `HF_PHOTO`'ya Remacri'den sonra:
    `("Bingsu/adetailer", "face_yolov9c.pt", BBOX, "face_yolov9c.pt", "Yuz dedektoru (yolov9c)", 40_000_000),`
    (iki satıra bölünmüş, 430'dan önceki biçimde).
  - `HF_PHOTO`'nun altına:
    ```python
    OPEN_PHOTO = [
        ("https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
         SAMS, "sam_vit_b_01ec64.pth", "SAM ViT-B", 300_000_000),
    ]
    ```
  - `# === What this run installs ===` altına `hf_jobs`'tan sonra:
    `open_jobs = OPEN_PHOTO if INSTALL_PHOTO else []`
  - `FOLDERS`'ta `upscale_models` satırının altına:
    `(INSTALL_PHOTO, "ultralytics/bbox", BBOX, "*.pt"),` ve `(INSTALL_PHOTO, "sams", SAMS, "*.pth"),`
  - Çağrı: `landed = download_models(hf_jobs, open_jobs, civitai_jobs, HF_MIRROR, COOKIE_VALUE)`.
- **Yardımcılar hücresi:** değişmez. `fetch`'i artık `download_models` çağırıyor; notebook import
  etmez.
- `PHOTO_GIB = 2 +` aynen kalır: 430'dan önce de taban 2'ydi ve dedektörle SAM'i içeriyordu.

## Yorumlar

- `comfy_photo_generator.py`'nin başı: `"40" Seed (rgthree) -> KSampler, FaceDetailer and both
  wildcard processors read it`.
- `colab/nodes.py`, `SKIPPED`'ın yorumunun son cümlesi 430'dan önceki haline: "Our photo graph loads
  SAM's first version through segment-anything, and Impact-Pack imports sam2 only when it is
  installed." sam2 atlanmaya devam eder.
- `colab/downloads.py`'nin modül docstring'i değişmez (zaten "every file" diyor).

## Testler — önce kırmızı

Testler kodlardan önce tek turda değişir; aşağıdaki **kırmızı** olanlar kod gelene kadar kırmızı
kalır, gerisi yeşil.

`backend/tests/test_workflow_asset.py`
- `test_the_photo_graph_runs_no_detailer` → `test_the_photo_graph_runs_the_face_detailer`
  (**kırmızı**): sınıfa göre arar — tam bir `FaceDetailerPipe`, `SAMLoader`'ın `model_name`'i
  `sam_vit_b_01ec64.pth`, her `UltralyticsDetectorProvider` `bbox/face_yolov9c.pt` okur. Docstring
  kullanıcının 12 Ekim cümlesini taşır.
- `test_the_photo_graph_saves_the_decoded_picture` → `test_the_photo_graph_saves_the_detailed_picture`
  (**kırmızı**): tek Save Image'ın `images` kaynağının sınıfı `FaceDetailerPipe`.
- `test_every_node_of_the_photo_graph_feeds_the_saved_picture` →
  `test_every_node_of_the_photo_graph_feeds_an_output` (yeşil): geri dönen grafikte `57` Image
  Comparer Save Image'a ulaşmaz, bu yüzden test her çıkış düğümünden — `SaveImage` ve
  `Image Comparer (rgthree)` — geriye yürür ve her düğüme ulaşmayı ister (Kararlar 2).
- `test_the_positive_encoder_understands_break` docstring'i: "Only this node changes. Both KSampler
  and ToDetailerPipe read the positive from its output, so one swap covers the detailer too." (yeşil)

`backend/tests/test_producers.py`
- `test_the_photo_group_carries_everything_the_graph_reads` (**kırmızı**): listeye
  `("ultralytics/bbox", "face_yolov9c.pt")` ve `("sams", "sam_vit_b_01ec64.pth")` döner; docstring
  "The other five are named by the file itself. The face detector and SAM came back with the
  detailer (madde 469): FaceDetailer loads them at startup, so a photo render needs them on the
  disk." olur, 430 cümlesi çıkar.

`backend/tests/test_notebook_installs_the_producer_groups.py`
- `test_the_face_detailer_s_files_are_gone_from_the_notebook` →
  `test_the_notebook_fetches_the_face_detailer_s_files` (**kırmızı**): `HF_PHOTO` listesinde
  `"Bingsu/adetailer", "face_yolov9c.pt", BBOX` satırı, `OPEN_PHOTO` listesinde SAM adresi ve `SAMS`
  — Eros/Mystic testlerindeki gibi liste dilimlenip regex ile.
- `test_an_unticked_group_costs_no_bytes`: foto üçlüsü yeniden `("CIVITAI_PHOTO", "OPEN_PHOTO",
  "HF_PHOTO")` (**kırmızı**).
- `test_the_chosen_files_come_down_through_download_models_with_the_mirror_and_the_cookie`: beklenen
  satır `download_models(hf_jobs, open_jobs, civitai_jobs, HF_MIRROR, COOKIE_VALUE)` (**kırmızı**).
- `test_the_notebook_keeps_the_packages_the_photo_and_h3_graphs_read`: listeye
  `"ltdrdata/ComfyUI-Impact-Subpack"`, sayı `== 10`, mesaj "on paketten"; docstring "the ten that
  stay ... Impact-Subpack gives the detector node" (**kırmızı**).
- Yeni `test_the_models_cell_lists_the_detailer_s_folders`: `FOLDERS`'ta
  `(INSTALL_PHOTO, "ultralytics/bbox", BBOX, "*.pt")` ve `(INSTALL_PHOTO, "sams", SAMS, "*.pth")`
  (**kırmızı**).
- `test_the_photo_estimate_counts_only_what_the_group_always_takes` docstring'i yeniden "both loras,
  the upscaler, the detector, the SAM" (yeşil).
- Sayım testleri (başlık, giriş) zaten listeden okuyor; liste 10 olunca kodla birlikte yeşile döner,
  test değişmez.
- `test_every_name_the_notebook_imports_from_its_code_exists`, grubun her dosya adının defterde
  geçtiğini soran test: değişmez, kodla yeşil.

`backend/tests/test_colab_downloads.py`
- `test_the_chosen_files_come_down_huggingface_first_then_civitai` →
  `test_the_chosen_files_come_down_huggingface_then_by_address_then_civitai` (**kırmızı**): `fetch`
  de sahte, çağrısı `("open", url, folder, filename, parallel, floor)` kaydeder; üç listeyle çağrılır,
  sıra HF, açık adres, Civitai ve açık adresin `parallel=True` ile gittiği, satırların bu sırayla
  döndüğü sorulur.

`backend/tests/test_colab_nodes.py`
- `test_impact_pack_is_installed_without_sam2` docstring'i 430'dan önceki haline: "Our graph loads
  SAM's first version, sam_vit_b, through segment-anything, and Impact-Pack imports sam2 only when it
  is installed (madde 314)." (yeşil)

Beklenen kırmızı sayısı: workflow 2, producers 1, notebook 5, downloads 1 — 9. Kod turundan sonra
dört suite yeşil.

## Dokunulmayan

Impact-Pack ve sam2'nin atlanması; `fetch`, `hf_fetch`, `civitai_fetch`; H3 grafikleri ve video
grubu; frontend ve `dist`; `CODE-STANDARD.md` (custom node sayısını ya da detailer'ı anmıyor);
`test_colab_downloads.py`'deki SAM/dedektör örnek dosyaları.

## Bitti sayılır

Dokuz kırmızı yeşile döner, dört suite yeşil. Asıl görüş Colab'da, push'tan sonra: Subpack kurulur,
dedektör ve SAM iner, ComfyUI "node/model bulunamadı" demez, fotoğraf FaceDetailer'dan geçmiş olarak
kaydedilir; Üreticiler paneli fotoğrafı dedektör ve SAM diskte olmadan kurulu saymaz.

## Kararlar

Spec'in açık soruları ana ajana gitti; cevapları (12 Ekim):

1. **`download_models`'ın imzası:** `download_models(hf_jobs, open_jobs, civitai_jobs, mirror,
   cookie)` — `open_jobs` konumsal ve varsayılansız; 430'dan önceki sıra ve döngü, yalnız yeri
   değişmiş. SAM'i HF'den indirmek ya da hücrede ayrı bir döngü reddedildi.
2. **"Her düğüm kaydedilen resme ulaşır" testi:** silinmez, değişir — her çıkış düğümünden
   (`SaveImage`, `Image Comparer (rgthree)`) geriye yürür ve her düğüme ulaşmayı ister; geri dönen
   grafikte yeşil.
3. **Yol haritası:** 469 [v9 yol haritasına](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md)
   yazılır; v9 469 için 12 Ekim'de yeniden açılır, ve 469 `feat/queen-editor-v9` dalında commit'lenir.
