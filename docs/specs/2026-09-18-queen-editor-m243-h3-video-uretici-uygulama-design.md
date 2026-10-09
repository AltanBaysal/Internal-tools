# Madde 243 · queen-editor MiniMax H3 ile video üretiyor — uygulama turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-18-queen-editor-m243-h3-video-uretici-testler-design.md), commit `64e6e541`

## Kullanıcıdan gereken

Kod için hiçbir şey. Roadmap'in sonunda Colab'da deneme: defterde **H3** seçilip bir kare video
üretilir. Test turunun spec'indeki üç "koşmadan bilinemeyen" orada görülür.

## Tasarım

Ne olacağı test turunun spec'inde yazılı. Burada yalnız kodun nereye gittiği var.

**Backend**
- `config.py`: `VIDEO_MODEL` (`QE_VIDEO_MODEL`, varsayılanı boş), `H3_VIDEO_WORKFLOW_PATH`,
  `H3_VIDEO_FIRST_LAST_WORKFLOW_PATH`.
- `features/photo_generation/data/comfy_h3_video_generator.py` (yeni): `ComfyH3VideoGenerator`.
  Node id'leri (`2730` Director, `2739` SeedControl) ve iki referans cümlesi yalnız burada. Grafik
  yükleme ve hata cümleleri WAN üreticisininkilerle aynı.
- `data/xai_prompt_writer.py`: `H3_VIDEO_INSTRUCTION` ve `H3VideoPromptWriter`.
- `features/producers/domain/model_groups.py`: `H3_VIDEO` ve `groups_for(video_model)`. `GROUPS`
  olduğu gibi kalıyor, video satırı WAN.
- `data/ffmpeg_video_exporter.py`: sesli parçada `-map 0:v:0 -map 1:a:0`.
- `main.py`: `config.VIDEO_MODEL == "h3"` ise H3 üreticisi ve yazarı, değilse WAN. Panel
  `groups_for(config.VIDEO_MODEL)` ile sayıyor.

**Frontend**
- `LayerPlayer.jsx`: `<video muted={Boolean(audioUrl)}>`. `dist/` aynı commit'te yeniden derleniyor.

**Defter** (`queeneditor.ipynb`)
- **CONFIG:**
  - `INSTALL_VIDEO` kutusunun yerini `VIDEO_MODEL` açılır listesi alıyor;
    `INSTALL_VIDEO = VIDEO_MODEL != "Yok"`.
  - Formun bilgi satırı WAN ~39 GiB, H3 ~37 GiB ve H3'ün T4'te koşmadığını söylüyor.
  - Seçilenler satırı hangi video modelinin seçildiğini de yazıyor.
- **Custom node listesi:** `ComfyUI-DaSiWa-Nodes`. Sayı 21 olur, başlıkta ve girişte de.
- **Modeller hücresi:**
  - `H3DIFF`, `H3VAE`, `TAE` klasörleri açılıyor.
  - `strip_unreferenced_tail` ekleniyor ve `fetch` her kontrolden önce çağırıyor
    (`manual.ipynb`'den).
  - `CIVITAI_H3` (3314686, 3228867) ve `OPEN_H3` (dört HF dosyası, `manual.ipynb`'nin adresleri)
    ekleniyor.
  - WAN listeleri `VIDEO_MODEL == "WAN"`'ın, H3'ünküler `VIDEO_MODEL == "H3"`'ün arkasında.
  - `OPEN_H3` ayrı bir döngüde `parallel=False` ile iniyor.
  - SIZES'ta WAN 39, H3 37.
  - Özet H3'ün klasörlerini de listeliyor.
- **Klon hücresi:** H3'ün iki grafiğini de arıyor.
- **Flask ortamı:** `QE_VIDEO_MODEL`.
- **Giriş markdown'ı:** video satırı H3'ü anıyor.

**curl'ün süresi 1800 → 7200 saniye.** Denemede Qwen'in 15 GB'ı ~8 MB/s ile ~29 dakikada indi. 21
GB'lık DaSiWa checkpoint'i 1800 saniyelik tavana takılırdı. `manual.ipynb` de 7200 kullanıyor.

**Defter tavanı** *(madde 239, 29.000 karakter)*. H3'ün kurulumu defteri tavanın ~2.300 karakter
üstüne çıkardı. Kullanıcının kararıyla *("defterdeki yorumlardan kurtul")* markdown hücrelerindeki
açıklamalar kısaldı. Giriş hücresinde yalnız ne yaptığı ve dört kurulum adımı kaldı. Öteki
bölümlerde başlıklar kaldı, Modeller'de de tek cümle. Tavan değişmedi.

**Neden `fetch`'in damga kesmesi her dosyaya uygulanıyor:** Kesilen baytlar hiçbir tensöre ait
değil. Damgası olmayan bir dosyada kesici hiçbir şey yapmıyor. Kesme yalnız H3'e uygulansaydı iki
ayrı indirme yolu olurdu.

## Bu turda değişen

Yukarıdaki dosyalar, `frontend/dist/`, `README.md`'nin Run bölümü *(`INSTALL_VIDEO` kutusu
yerine `VIDEO_MODEL`)* ve yol haritasında 243'ün işareti. Testlere dokunulmuyor.
