# mmaudio-generate

MMAudio modeli ile video ve/veya metin girdisinden ses dosyası üreten Colab notebook'u.

## File

- `mmaudio_generate.ipynb` — Video/text-to-audio generation (NSFW fine-tuned MMAudio large_44k)

## Usage

1. [Google Colab](https://colab.research.google.com/) açın
2. **File → Upload notebook** ile `mmaudio_generate.ipynb` dosyasını yükleyin
3. **Runtime → Change runtime type → T4 GPU** seçin
4. Hücreleri sırayla çalıştırın (Shift + Enter)
5. Konfigürasyon hücresindeki parametreleri değiştirip tekrar çalıştırabilirsiniz

## Modes

- **Video + Text → Audio** — Video yükleyip metin ile yönlendirme (en iyi kalite)
- **Video → Audio** — Sadece video, model sesi otomatik üretir
- **Text → Audio** — Sadece metin açıklaması ile ses üretimi

## Drive Structure

```
Google Drive/My Drive/
├── mmaudio-videos/     # Girdi videoları (DRIVE_VIDEO_FOLDER)
├── mmaudio-outputs/    # Çıktı videoları (DRIVE_OUTPUT_FOLDER)
└── mmaudio-models/     # Model cache (DRIVE_MODEL_FOLDER)
    ├── vae.pth
    ├── synchformer.pth
    ├── bigvgan_16k.pth
    ├── mmaudio_large_44k_nsfw_...safetensors
    └── .cache_complete
```

## Model Cache

- `CACHE_MODELS_ON_DRIVE = True` açıkken model dosyaları (~2 GB) ilk çalıştırmada Drive'a kaydedilir
- Sonraki çalıştırmalarda Drive'dan local'e kopyalanır, HuggingFace indirmesi atlanır
- `.cache_complete` marker dosyası cache'in tamamlandığını gösterir
- Cache'i sıfırlamak için `mmaudio-models/` klasörünü silmek yeterli

## RAM & VRAM Verimli Kullanım

Notebook, T4 GPU'nun sınırlı VRAM'i (~15 GB) ve Colab'ın sınırlı RAM'i (~12 GB) ile çalışmak üzere optimize edilmiştir:

- **float16 precision** — T4 bfloat16 desteklemez, float16 kullanılır (VRAM yarıya iner)
- **Doğrudan GPU'ya yükleme** — Model ağırlıkları CPU RAM'e uğramadan direkt GPU'ya yüklenir (`load_file(..., device=device)`)
- **Adım adım temizlik** — Her video işlendikten sonra `del` + `torch.cuda.empty_cache()` + `gc.collect()` ile bellek serbest bırakılır
- **720p resize** — Videolar işlenmeden önce 720p'ye küçültülür (MMAudio 224x224 frame çıkarır, 4K gereksiz RAM harcar)
- **pip cache purge** — Kurulumdan sonra pip cache temizlenir
- **`mem_status()` fonksiyonu** — Her kritik adımda RAM ve VRAM kullanımı loglanır, sızıntılar erken tespit edilir
- Yeni kod eklerken büyük tensorleri kullanımdan sonra `del` ile silip `torch.cuda.empty_cache()` çağırmaya dikkat edin
- CPU RAM'de büyük ara veriler tutmaktan kaçının; mümkünse streaming/chunk yaklaşımı kullanın

## Notes

- Model: NSFW fine-tuned FP16 safetensors (`phazei/NSFW_MMaudio`)
- Ses süresi otomatik olarak video süresine göre ayarlanır
- Çıktı formatı: `.flac` (44kHz) → ffmpeg ile video'ya birleştirilir (`.mp4`)
- Model lisansı: CC-BY-NC 4.0 (yalnızca ticari olmayan kullanım)
