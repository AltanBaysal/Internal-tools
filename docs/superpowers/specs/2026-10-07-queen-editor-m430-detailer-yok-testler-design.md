# Madde 430 · Fotoğrafta hiçbir detailer çalışmaz — test turunun tasarımı

**Tarih:** 7 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
430 · **Dal:** `feat/queen-editor-v9` · **Tur:** 1/2 — yalnız testler ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Karar maddede *(7 Ekim — "abi hiç bir detailer açık olmasın direkt"; plana — "yap tabiki")*.
Grafiğin yeni hâli, kullanıcının ComfyUI'da Face ADetailer'ı ve Detailer Settings'i kapatıp alacağı
Export (API) ile aynı; kullanıcı export vermek yerine kapatmayı Claude'a bıraktı *("pek isen
kapatabilir misin?")*.

## Bugün ne var

- **Grafik** (`assets/workflow_api.json`): Save Image (`50`) resmi FaceDetailer'dan (`31`) alıyor.
  FaceDetailer'ı besleyenler: Edit DetailerPipe (`14`), ToDetailerPipe (`5`), iki yüz dedektörü
  (`9`, `42` — `UltralyticsDetectorProvider`), SAMLoader (`6`), Differential Diffusion (`44`), ve
  üç ayar (`19` Max Size, `24` Tiled Detailer, `37` BBOX Crop Factor). Karşılaştırma paneli (`57`,
  Image Comparer) ayrı bir çıkış; hiçbir şeyi beslemiyor.
- **Üreticiler paneli** (`model_groups.py`): fotoğraf grubu `ultralytics/bbox/face_yolov9c.pt` ve
  `sams/sam_vit_b_01ec64.pth`'yi sayıyor.
- **Notebook:** `HF_PHOTO` yüz dedektörünü, `OPEN_PHOTO` SAM'i indiriyor; `CUSTOM_NODES`
  `ComfyUI-Impact-Subpack`'i kuruyor — dedektör düğümünü veren paket, başka işi yok.

## Testler

**`test_workflow_asset.py`** — üç yeni test, grafiği okur:

1. `test_the_photo_graph_runs_no_detailer` — hiçbir düğümün sınıfı `Detailer` ya da `Detector`
   içermiyor, ve `SAMLoader` yok. Maddenin kendi cümlesi.
2. `test_the_photo_graph_saves_the_decoded_picture` — Save Image'ın tek girdisi VAE Decode'un çıkışı.
3. `test_every_node_of_the_photo_graph_feeds_the_saved_picture` — Save Image'dan geriye bağlantılar
   izlenince her düğüme varılıyor. Detailer'ın sınıf adı taşımayan artıkları — Differential
   Diffusion, üç ayar, karşılaştırma paneli — ancak böyle yakalanır: kullanıcının export'unda da
   bulunmazlardı. Bugün `57` yüzünden kırmızı.

`test_the_positive_encoder_understands_break`'in docstring'i ToDetailerPipe'ı anıyor; artık yalnız
KSampler okuyor, cümle düzelir.

**`test_producers.py`** — `test_the_photo_group_carries_everything_the_graph_reads`'in beklediği
listeden iki satır düşer; docstring'deki "other four" "other three" olur.

**`test_notebook_installs_the_producer_groups.py`** — bir yeni test:

4. `test_the_face_detailer_s_files_are_gone_from_the_notebook` — defterde `face_yolov9c.pt`,
   `sam_vit_b_01ec64.pth`, `Bingsu/adetailer`, `ComfyUI-Impact-Subpack`, `ultralytics` ve
   `models/sams` geçmiyor. 226'nın ve 333'ün "emekliler defterden çıktı" testlerinin kalıbı. Klasör
   adları da listede: boş klasör açan ve özette onları basan satırlar da artık.

`test_the_photo_estimate_counts_only_what_the_group_always_takes`'in docstring'i tabanı "the
detector, the SAM" diye sayıyor; o iki kelime düşer. Taban sayısı (`PHOTO_GIB = 2 +`) kaba bir
pay, değişmez.

**`test_colab_nodes.py`** — `test_impact_pack_is_installed_without_sam2`'nin docstring'i grafiğin
SAM'i segment-anything'den yüklediğini söylüyor; artık hiçbir grafiğimiz SAM yüklemiyor. Testin
kendisi aynı: sam2'nin atlanması kurulumun süresi için.

Başlıktaki node sayısı ayrı test istemiyor: `test_the_notebook_says_how_many_custom_nodes_it_installs`
ve `test_the_intro_agrees_with_the_custom_node_list` listeyle başlığı ve girişi zaten karşılaştırıyor.

## Dokunulmayanlar

`test_colab_downloads.py` yüz dedektörünü ve SAM'i indiricinin örnek dosyaları olarak kullanıyor;
defterin ne indirdiğini değil indiricinin nasıl indirdiğini soruyor. Olduğu gibi kalır.

## Beklenen sonuç

**Beş kırmızı:** 1, 2, 3, 4 ve fotoğraf grubunun listesi. Geri kalan her şey yeşil.
