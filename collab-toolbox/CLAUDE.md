# collab-toolbox

Google Colab'da çalışan AI medya üretim/temizleme araçlarının notebook koleksiyonu (`.ipynb`). Her notebook bağımsız çalışır; ortak girdi/çıktı kanalı **Google Drive** (`MyDrive/...`). Çoğu araç ComfyUI'yi arka planda API olarak ayağa kaldırıp Drive'daki dosyaları toplu (batch) işler.

## Notebook'lar

| Notebook | Amaç | Donanım |
|---|---|---|
| [photo_generator/PhotoGenerator_API.ipynb](photo_generator/PhotoGenerator_API.ipynb) | Referans görsel + IPAdapter ile SDXL foto üretimi (ComfyUI API, loop + resume) | GPU |
| [video_generator/imageToVideo.ipynb](video_generator/imageToVideo.ipynb) | Image-to-video — WAN 2.2 Smooth Workflow v5.0; `input/` görsellerini videoya çevirir (batch + resume) | A100 (Colab Pro) |
| [loop_maker/comfy_ui.ipynb](loop_maker/comfy_ui.ipynb) | Wan 2.1 VACE ile batch video işleme (loop/döngü), Cloudflared tüneli | GPU |
| [mmaudio_generate.ipynb](mmaudio_generate.ipynb) | Video ve/veya metinden ses üretimi (NSFW fine-tuned MMAudio large_44k), videoya birleştirir | T4 GPU |
| [mp4_converter.ipynb](mp4_converter.ipynb) | Bağımsız video → H.264 mp4 dönüştürücü (idempotent) | CPU |
| [frame_extractor.ipynb](frame_extractor.ipynb) | Videolardan ilk kareyi çıkarır (JPG/PNG) | CPU |
| [watermark/watermark_detection.ipynb](watermark/watermark_detection.ipynb) | YOLOv11 + corzent konsensüs ile watermark tespiti → `results.json` | GPU |
| [watermark/watermark_remove.ipynb](watermark/watermark_remove.ipynb) | `results.json`'a göre ProPainter ile watermark silme (composite inpaint) | GPU |

## Genel kullanım

1. [Google Colab](https://colab.research.google.com/) → **File → Upload notebook** ile ilgili `.ipynb` yükle
2. **Runtime → Change runtime type** ile tabloda belirtilen donanımı seç
3. İlk **CONFIG** hücresindeki değişkenleri doldur (token, Drive yolu, prompt vb.)
4. **Runtime → Run all** — diğer hücrelere dokunma

## Drive yapısı (notebook başına)

```
MyDrive/
├── photo_generator/        # workflow.json + outputs/        (PhotoGenerator_API)
├── ImageToVideo/           # imageToVideo.json + input/ + output/   (video_generator)
├── wan_batch/              # workflow.json + input_videos/ + output_videos/ + batch_log.txt  (loop_maker)
├── mmaudio-videos/         # girdi videoları                 (mmaudio_generate)
├── mmaudio-outputs/        # ses eklenmiş videolar → photos/ (mmaudio + frame_extractor)
│   └── photos/             # frame_extractor çıktısı
├── mmaudio-models/         # MMAudio model cache (~2 GB)
├── mp4_converter/          # input/ + output/                (mp4_converter)
├── Watermark-Input/        # tespit girdisi                  (watermark_detection)
└── Watermark-Output/       # results.json + temizlenmiş videolar  (watermark detection + remove)
```

## Pipeline zinciri

Araçlar Drive üzerinden birbirini besleyebilir (tipik akış):

```
photo_generator → (görseller) → video_generator/input/ → mmaudio (ses) → frame_extractor (kare)
mp4_converter → watermark_detection → results.json → watermark_remove
```

- **watermark**: detection `Watermark-Output/results.json` yazar; removal aynı JSON'u `source_path` üzerinden okuyup işler. JSON `videos` key'i `INPUT_FOLDER`'a göre **göreli yoldur** (`subfolder/video.mp4`), alt klasör yapısı tüm stage'lerde korunur.
- **mp4_converter** bağımsızdır; çıktısını başka pipeline'a `INPUT_FOLDER` olarak verebilirsin.

## Ortak tasarım kalıpları

Notebook'lar arası tekrar eden, korunması gereken kalıplar:

- **Tek CONFIG hücresi** — tüm ayarlar (token, Drive yolu, prompt, render parametreleri) ilk hücrede; gerisi dokunulmadan "Run all".
- **Fail-loud** — bozuk/eksik model indirmesi veya başlamayan ComfyUI sessizce geçmez, `RuntimeError` fırlatır (örn. `imageToVideo` `is_valid_safetensors` + 90s sunucu bekleme). Eski `UNETLoader → JSONDecodeError` hatası bu yüzden gizleniyordu.
- **Resume / idempotent** — çıktı Drive'da zaten varsa atlanır; oturum koparsa tekrar çalıştırmak sadece eksikleri tamamlar. (Resume sıra-bağımlı olan yerlerde — `photo_generator` `NN.png`, `imageToVideo` dosya-adı eşlemesi — ACTIONS/prompt listesini yeniden sıralamak eski çıktıları yanlış eşleştirir.)
- **Model indirme** — HuggingFace büyük dosyalar `aria2c -x16` ile paralel; Civitai (login-gated NSFW checkpoint/LoRA) `curl` + **SADECE `__Secure-civitai-token` cookie** ile, **`?token=` API key OLMADAN** (bkz. `imageToVideo` model hücresindeki `fetch`/`civitai_url`/`cookie_header`). `?token=` koyarsan civitai.com isteği o key'in hesabı olarak doğrular → gated asset **401 "requires you to be logged in"**; token'sız cookie = login olmuş kullanıcı → iner (probe ile doğrulandı: cookie-only 200, token-only & both 401). Host **`civitai.com`** kalır (`.red` farkı değil); cookie **civitai.red** F12 → Cookies'ten alınır (süresi dolarsa yenile + CONFIG hücresini tekrar çalıştır). İndirme bozuksa `is_valid_safetensors` HTML/JSON hata gövdesini header'dan ayırıp `RuntimeError` atar — eski sessiz `UNETLoader → JSONDecodeError` böyle önlenir.
- **Drive ↔ Colab kopyalama** — ComfyUI lokal diskte (hız), sadece veri Drive'da; her video işlendikten sonra Colab kopyası temizlenir (disk dolmasın).

## MMAudio notları (`mmaudio_generate.ipynb`)

- Model: NSFW fine-tuned FP16 safetensors (`phazei/NSFW_MMaudio`), large_44k. T4 için **float16** (bfloat16 desteklenmez), doğrudan GPU'ya yükleme, adım adım `del`+`empty_cache`+`gc.collect`, 720p resize.
- `CACHE_MODELS_ON_DRIVE=True` → modeller (~2 GB) ilk çalıştırmada `mmaudio-models/`'a kaydedilir; `.cache_complete` marker'ı cache'i işaretler. Sıfırlamak için klasörü sil.
- Çıktı: `.flac` (44kHz) → ffmpeg ile video'ya birleştirilir (`.mp4`).
- Lisans: CC-BY-NC 4.0 (yalnızca ticari olmayan kullanım).

## Yorum & dokümantasyon standardı

Tüm notebook'lar kök [../CLAUDE.md](../CLAUDE.md)'deki **Notebook Comment Conventions** bölümüne tabidir. Özet: dil okuyucuya göre ayrılır — markdown/başlık + runtime mesajları (`print`/`log`/`assert`) **Türkçe**, kod yorumları (`#`) + docstring'ler **İngilizce**; üst başlık `# <Araç> — <amaç>` + `Input/Output`, bölüm başlıkları `## N) Başlık`, `# === ... ===` divider, yorum NE değil NEDEN anlatır, drift yasağı (yorum koda uydurulur, kod yoruma değil).
