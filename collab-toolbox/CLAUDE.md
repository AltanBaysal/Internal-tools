# collab-toolbox

Google Colab'da çalışan AI medya üretim/temizleme araçlarının notebook koleksiyonu (`.ipynb`). Her notebook bağımsız çalışır; ortak girdi/çıktı kanalı **Google Drive** (`MyDrive/...`). Çoğu araç ComfyUI'yi arka planda API olarak ayağa kaldırıp Drive'daki dosyaları toplu (batch) işler.

## Notebook'lar

| Notebook | Amaç | Donanım |
|---|---|---|
| [photo_generator/PhotoGenerator_API.ipynb](photo_generator/PhotoGenerator_API.ipynb) | Referans görsel + IPAdapter ile SDXL foto üretimi (ComfyUI API, loop + resume) | GPU |
| [video_generator/imageToVideo.ipynb](video_generator/imageToVideo.ipynb) | Image-to-video — WAN 2.2 Smooth Workflow v5.0; `input/` görsellerini videoya çevirir (batch + resume) | A100 (Colab Pro) |
| [loop_maker/comfy_ui.ipynb](loop_maker/comfy_ui.ipynb) | Wan 2.1 VACE ile batch video işleme (loop/döngü); localhost API, UI tüneli opsiyonel (`USE_TUNNEL`) | GPU |
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
├── wan_batch/              # workflow.json + input_videos/ + output_videos/   (loop_maker)
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

- **Tek CONFIG hücresi** — tüm ayarlar (token, Drive yolu, prompt, render parametreleri) ilk hücrede; gerisi dokunulmadan "Run all". **Drive mount CONFIG hücresinin en başında** (`loop_maker` kalıbı): auth istemi ilk saniyede çıksın, 40 dakikalık model indirmesinin ortasında kullanıcıyı beklemesin.
- **Fail-loud** — bozuk/eksik model indirmesi veya başlamayan ComfyUI sessizce geçmez, `RuntimeError` fırlatır (`check_safetensors` + 90s sunucu bekleme). Eski `UNETLoader`/`VAELoader → JSONDecodeError` hataları bu yüzden gizleniyordu.
- **Resume / idempotent** — çıktı Drive'da zaten varsa atlanır; oturum koparsa tekrar çalıştırmak sadece eksikleri tamamlar. (Resume sıra-bağımlı olan yerlerde — `photo_generator` `NN.png`, `imageToVideo` dosya-adı eşlemesi — ACTIONS/prompt listesini yeniden sıralamak eski çıktıları yanlış eşleştirir.)
- **Model indirme doğrulama standardı** (`video_generator/imageToVideo` + `loop_maker/comfy_ui` — yeni notebook'lar da bunu kullanır) — indirme fonksiyonu `fetch(url, dir, filename, label, *, parallel, headers)`, akış hep aynı: `.part` durumunu kontrol et → gerekiyorsa indir → **`check_safetensors(path)`** → `"ok"` değilse `RuntimeError`. Üç sorumluluk üç fonksiyonda (SRP): `run()` komut hatası, `check_safetensors()` dosya durumu, `describe_download()` sebep.
  - **Doğrulama ağa soru sormaz.** Safetensors = `[8 byte header uzunluğu][header JSON][tensör verisi]`; header'daki `data_offsets` verinin nerede bittiğini söyler → **olması gereken boyutu dosyanın kendisi verir**. `check_safetensors` üç durum döndürür: **ok** (tam) / **partial** (geçerli yarım → resume güvenli) / **invalid** (boş, HTML/JSON hata sayfası, LFS pointer, ya da beklenenden uzun). Böylece hem bozuk içerik hem kesik indirme tek yerel kontrolle yakalanır. **HEAD/`Content-Length` KULLANMA:** HF'in Xet CDN'i imzalı URL'de HEAD'i **403** ile reddeder (GET çalışır) ve o 403'ün 48 byte'lık gövdesi "dosya boyutu" sanılıp sağlam inen 34.7 GB model "kesik" ilan edilmişti.
  - **İndirme hatasının tek kapısı `run()`** — curl/aria2c HTTP hatasında (`--fail`), bildirilen uzunluktan önce biten transferde ve dolu diskte sıfırdan farklı exit verir → `RuntimeError` + komutun **gerçek stderr kuyruğu**. Ayrı disk/boyut ön-kontrolü yok (KISS).
  - **Hiçbir şey silinmez.** Geçersiz dosya silinmez, üstüne yazılmaz, resume edilmez — çalışma durur, dosya inceleme için diskte kalır. (Bozuk dosyanın üstüne resume etmek çöpün ardına iyi byte'lar ekler.) İndirmeler `.part`'a yapılır, sadece `"ok"` alınca gerçek isme rename edilir → ComfyUI hiçbir zaman yarım dosyayı model olarak görmez; tam `.part`'a curl hiç çağrılmadığı için "range past EOF" (416) da imkânsızdır.
  - **Hata HAM basılır, yorumlanmaz.** Okuyucu yazılımcı: hata mesajını insan cümlesine çevirme, sunucunun/komutun kendi çıktısını bas. `curl --fail-with-body` (`--fail` DEĞİL): HTTP hatasında yine non-zero exit verir ama response gövdesini `.part`'a yazar → hata mesajı = curl stderr + `head_text(part)` (gövdenin ilk 4 KB'ı, ham). `--fail` gövdeyi yutuyordu, elde sadece "403" kalıyordu. ComfyUI tarafında da aynı: `/prompt` reddi → `node_errors` JSON'u, execution error → `node_id`/`node_type`/`exception_*` + traceback, ham.
- **Batch hata politikası** (`loop_maker`) — ComfyUI'nin `messages` blob'undan `describe_comfy_error` ile `node_id`/`node_type`/`exception_type`/`exception_message` + traceback çıkarılır ve **ham** basılır (Drive'a log dosyası yazılmaz; her şey konsolda). Hata **video-özel** ise (bozuk mp4, timeout) o video atlanır; **altyapı** kaynaklıysa (`*Loader` node'u → model bozuk/eksik) ya da üst üste `MAX_CONSECUTIVE_FAILURES` kez hata olursa batch `RuntimeError` ile **durur** — aynı hatayla onlarca video "FAILED" olarak harcanmaz.
- **Model indirme yöntemi** — HuggingFace büyük dosyalar `aria2c -x16` ile paralel (**ama Xet-backed dosyalarda imzalı CDN URL'i paralel byte-range'e 403 verir** → tek-bağlantılı `curl` GET, `parallel=False`; bkz. `loop_maker`); Civitai (login-gated NSFW checkpoint/LoRA) cookie ile, **`?token=` API key OLMADAN** (`?token=` → istek o key'in hesabı olarak doğrulanır → gated asset **401 "requires you to be logged in"**). **Civitai auth `auth.civitai.com`'a taşındı (2026-06, run'da kanıtlı):** cookie adı artık **`__Secure-civ-token`** (eski `__Secure-civitai-token` DEĞİL → eski adı gönderince login+turnstile sayfası döner), değeri kısa **ES256 JWT** (~420 char, `iss: auth.civitai.com`; eski uzun JWE değil), host **`civitai.red`** (cookie ile **same-origin**; `.com`'a atınca cross-domain → login+turnstile). Cookie **civitai.red** F12 → Cookies → `__Secure-civ-token` değerine **çift tıkla → Ctrl+A → Ctrl+C** (tabloya tek tıkla kopyalama token'ı yarıda keser, `assert len>200` yine geçer ama geçersiz olur); CONFIG'e yapıştır, exp ~30 gün, dolunca yeniden login + yenile. Doğrulanmış desen: **`video_experiments/ltx23-eros`** c3 (`civitai_url`/`cookie_header`/`civitai_probe`/`fetch`). İndirme bozuksa (login HTML) `check_safetensors` `"invalid"` döner ve `fetch` `RuntimeError` atar — eski sessiz `UNETLoader → JSONDecodeError` böyle önlenir. **aria2c↔curl:** bazı dosyalar Backblaze B2'ye (`b2.civitai.com`) yönlenir → aria2c cookie'yi depoya forward edip **403** alır, curl cross-host redirect'te cookie'yi düşürdüğü için geçer (B2 dosyaları `curl_first=True`); R2 (`r2.cloudflarestorage.com`) ikisinde de iner.
- **Drive ↔ Colab kopyalama** — ComfyUI lokal diskte (hız), sadece veri Drive'da; her video işlendikten sonra Colab kopyası temizlenir (disk dolmasın).

## video_experiments/ — görsel workflow denemeleri (Drive yok)

Farklı video workflow'larını Colab Pro'da **görsel** denemek için bağımsız ComfyUI notebook'ları. Yukarıdaki batch araçların aksine **Drive kullanmaz**: her notebook ComfyUI + Manager + custom node + modelleri kaynaktan indirir, `cloudflared` ile bir UI linki verir; kullanıcı `workflow.json`'u UI'a elle yükleyip çalıştırır. (Base: `video_experiments/comfyui_colab_with_manager.ipynb`.)

| Deneme | Workflow | Model |
|---|---|---|
| [video_experiments/ltx23-eros/](video_experiments/ltx23-eros/) | MrXin LTX 2.3 I2V "Eros" V6 | LTX-Video 2.3 |
| [video_experiments/wan22-painter/](video_experiments/wan22-painter/) | PainterI2V (kenpechi) v2.4 | WAN 2.2 I2V |
| [video_experiments/wan22-allinone/](video_experiments/wan22-allinone/) | All-in-One I2V/FLF/Loop | WAN 2.2 I2V |
| [video_experiments/wan22-dasiwa/](video_experiments/wan22-dasiwa/) | DaSiWa FastFidelity C-AiO | WAN 2.2 I2V-A14B |

Her klasörde `<deneme>.ipynb` + `workflow.json` + `instructions.md`. Kullanım: A100 runtime → CONFIG'e Civitai cookie → Run all → `trycloudflare` linkinden `workflow.json`'u yükle. Civitai gated indirme, fail-loud ve tek-CONFIG kalıpları yukarıdaki **Ortak tasarım kalıpları** ile aynı (gated modeller önce probe edilip indirilir). NSFW concept LoRA'lar (Painter, DaSiWa) URL'siz; kullanıcı kendi koleksiyonundan ekler.

**Başlatma hücresi (ComfyUI + cloudflared) kalıpları:**
- **`--enable-manager` HER ZAMAN açık** — `python main.py ... --enable-manager`. Yeni ComfyUI'da Manager bu flag olmadan KAPALI; bu olmadan UI'daki **Manager → Install Missing Custom Nodes** çalışmaz. Workflow'lar elle yüklendiği için eksik node çok olası → Manager hep erişilebilir olmalı.
- **Hücre ön planda bloklu kalır** — ComfyUI arka planda başlar (fail-loud `/system_stats` kontrolü), link basılır, sonra hücre `tail -f /content/comfyui.log` ile **bilerek açık tutulur**. Hücre biterse Colab runtime'ı 'idle' sayıp bağlantıyı keser → ComfyUI + tünel ölür. (Orijinal `comfyui_colab_with_manager.ipynb` da son satırda `!python main.py` ile ön planda bloklar.)
- **cloudflared çıktısı dosyaya** yazılır (pipe dolup süreci bloklamasın), link dosyadan regex'le okunur (alınamazsa fail-loud).

## MMAudio notları (`mmaudio_generate.ipynb`)

- Model: NSFW fine-tuned FP16 safetensors (`phazei/NSFW_MMaudio`), large_44k. T4 için **float16** (bfloat16 desteklenmez), doğrudan GPU'ya yükleme, adım adım `del`+`empty_cache`+`gc.collect`, 720p resize.
- `CACHE_MODELS_ON_DRIVE=True` → modeller (~2 GB) ilk çalıştırmada `mmaudio-models/`'a kaydedilir; `.cache_complete` marker'ı cache'i işaretler. Sıfırlamak için klasörü sil.
- Çıktı: `.flac` (44kHz) → ffmpeg ile video'ya birleştirilir (`.mp4`).
- Lisans: CC-BY-NC 4.0 (yalnızca ticari olmayan kullanım).

## Yorum & dokümantasyon standardı

Tüm notebook'lar kök [../CLAUDE.md](../CLAUDE.md)'deki **Notebook Comment Conventions** bölümüne tabidir. Özet: dil okuyucuya göre ayrılır — markdown/başlık + runtime mesajları (`print`/`log`/`assert`) **Türkçe**, kod yorumları (`#`) + docstring'ler **İngilizce**; üst başlık `# <Araç> — <amaç>` + `Input/Output`, bölüm başlıkları `## N) Başlık`, `# === ... ===` divider, yorum NE değil NEDEN anlatır, drift yasağı (yorum koda uydurulur, kod yoruma değil).
