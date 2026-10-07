# Madde 430 · Fotoğrafta hiçbir detailer çalışmaz — uygulama turunun tasarımı

**Tarih:** 7 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
430 · **Dal:** `feat/queen-editor-v9` · **Tur:** 2/2 — kod ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md) ·
**Test turu:** [m430 testler](2026-10-07-queen-editor-m430-detailer-yok-testler-design.md)
*(`0730ac56`, `f2515493`)*

## Grafik — `assets/workflow_api.json`

Kullanıcının Face ADetailer'ı ve Detailer Settings'i kapatıp alacağı export'un aynısı:

- **Çıkan düğümler:** `5` ToDetailerPipe, `6` SAMLoader, `9` ve `42` UltralyticsDetectorProvider,
  `14` Edit DetailerPipe, `19` Max Size, `24` Tiled Detailer, `31` FaceDetailer (pipe), `37` BBOX
  Crop Factor, `44` Differential Diffusion, `57` Image Comparer.
- **Save Image** (`50`): `images` `["31", 0]` yerine `["33", 0]` — VAE Decode.
- Kalan 21 düğümün hiçbir girdisi değişmez. Bir export'ta da ComfyUI bypass'lı düğümü atıp onun
  girdisini çıkışına bağlar; FaceDetailer'ın resim girdisi `33`'tü.

## Üreticiler paneli — `features/producers/domain/model_groups.py`

Fotoğraf grubundan `ultralytics/bbox/face_yolov9c.pt` ve `sams/sam_vit_b_01ec64.pth` satırları ve
dedektör klasörünü açıklayan yorum çıkar. Grubun başındaki yorum bugün beş dosyayı sayıyor ve
FaceDetailer'ın açılışta yüklediklerini anlatıyor; dört dosyayı sayar, detailer'ın olmadığını
söyler.

## Notebook — `queeneditor.ipynb`

- **ComfyUI hücresi:** `CUSTOM_NODES`'tan `ComfyUI-Impact-Subpack` çıkar; başlık ve giriş hücresi
  21'i 20 der.
- **Modeller hücresi:** `BBOX` ve `SAMS` klasörleri, `HF_PHOTO`'daki `Bingsu/adetailer` satırı,
  `OPEN_PHOTO` listesi, `open_jobs`, açık adresli indirme döngüsü, ve özetteki `ultralytics/bbox` ile
  `sams` satırları çıkar.
- **Yardımcılar hücresi:** `fetch` artık kullanılmıyor, `colab.downloads`'tan import'u düşer.
  `colab/downloads.py`'nin kendisi değişmez: `fetch` orada `hf_fetch` ve `civitai_fetch`'in de
  yolu, ve testleri onu doğrudan koşuyor.
- `PHOTO_GIB = 2 +` taban sayısı kaba bir pay; dokunulmaz.

## Yorumlar

- `comfy_photo_generator.py`'nin başı: `"40"` Seed'i "KSampler, FaceDetailer and both wildcard
  processors" okuyor diyor; FaceDetailer düşer.
- `colab/nodes.py`: sam2'yi atlamanın gerekçesi "our photo graph loads SAM's first version through
  segment-anything" diyor; artık hiçbir grafiğimiz SAM yüklemiyor. Atlama kalır: sam2'nin derlenmesi
  Impact-Pack'in kurulumunu uzatıyordu, ve Impact-Pack prompt düğümleri için kurulu.

## Dokunulmayan

Impact-Pack — `ImpactWildcardProcessor` ve `ImpactSwitch` ondan. `test_colab_downloads.py` — yüz
dedektörü ve SAM orada indiricinin örnek dosyası.

## Beklenen sonuç

Beş kırmızı yeşile döner; dört satır yeşil. Çıktıyı değiştirdiği için asıl görüş Colab'da: fotoğraf
detailer'sız üretilir, ComfyUI "model bulunamadı" ya da "node bulunamadı" demez.
