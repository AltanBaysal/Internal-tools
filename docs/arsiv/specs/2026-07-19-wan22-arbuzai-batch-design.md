# WAN 2.2 arbuzai I2V — batch üretim (tasarım)

**Tarih:** 2026-07-19 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

`api.ipynb` tek görsel + tek prompt üretiyor. Batch'e dönüşür: Drive'a numaralı fotolar (`0.png, 1.jpg, ...`), CONFIG'e numarayla eşleşen prompt listesi → her eşleşme için bir video, `output/N.mp4`. Kullanıcı kararı: ayrı bir batch notebook'u değil, **`api.ipynb` yerinde dönüştürülür** — tek görsel artık 1 elemanlı batch.

## Bağlam

- **Numara→prompt eşleşmesi** repoda kanıtlı: `imageToVideo.ipynb` `ACTION_PROMPTS[0] → 01.png` deseniyle çalışıyor.
- **Plan-önce-üretim, resume, hata sınıflandırması** `loop_maker/comfy_ui.ipynb`'den: karar tablosu GPU dakikası harcanmadan basılır; var olan çıktı atlanır; loader hatası batch'i durdurur.
- `api.ipynb`'nin ComfyUI istemcisi (`ComfyClient`, `describe_comfy_error` + `is_infra`, `/upload/image`, `/view`) zaten batch'in ihtiyacı olan her parçayı taşıyor.

## Kararlar

| Karar | Gerekçe |
|---|---|
| `api.ipynb` yerinde batch'e dönüşür | Kullanıcı kararı. Girdi mekanizması zaten değişiyor (dosya seçici → Drive klasörü); ikinci notebook bakım yükü. |
| Prompt listesi CONFIG'de (`PROMPTS = ["""...""", ...]`) | Kullanıcı kararı; `ACTION_PROMPTS` deseni. Üç tırnak çok satırlı prompt'u taşır. |
| Girdi: `DRIVE_ROOT/input/<N>.<ext>` | Numara = eşleşme anahtarı, uzantı serbest (png/jpg/jpeg/webp). Dosya seçici kalkar — girdiler oturum kopsa da Drive'da durur. |
| Foto listesi esas; eşleşmeyen taraf loglanıp atlanır | Kullanıcı kararı. Prompt var + foto yok → "atlandı, fotoğraf yok". Foto var + prompt yok (yalnız numara ≥ liste boyu olabilir — düz liste, delik yok) → "atlandı, prompt yok". |
| Boş prompt (`""` / boşluk) = "prompt yok" | Kullanıcı onayı. Listeyi kaydırmadan bir numarayı devre dışı bırakmanın yolu: `PROMPTS[2] = ""` → 2 atlanır, loglanır. |
| Çıktı `output/<N>.mp4` + resume | Kullanıcı kararı. Var olan çıktı atlanır ("zaten var"); Colab kopunca aynı notebook baştan çalıştırılır, kaldığı yerden devam eder. Yeniden üretim = Drive'dan o mp4'ü silmek. |
| Seed: video başına rastgele, loglanır; `SEED` sabitse hepsinde o | Tek görsel akışındaki davranışın batch karşılığı. |

## Mimari

`collab-toolbox/video_generator/wan22-arbuzai/api.ipynb` — hücre yapısı korunur, üç bölge değişir:

| Bölüm | Değişiklik |
|---|---|
| 1) CONFIG | `PROMPT` → `PROMPTS` listesi. Görsel seçme hücresi **kalkar**; yerine **plan hücresi**: `input/` taranır, eşleşme tablosu basılır (ÜRET / ATLA-fotoğraf-yok / ATLA-prompt-yok / ATLA-zaten-var), üretilecek sayı 0 ise fail-loud. |
| 2-5) Yardımcılar, custom node'lar, modeller, ComfyUI başlatma | **Dokunulmaz.** |
| 6) Görseli ComfyUI'ya yükle | Kalkar — yükleme üretim döngüsünün içine taşınır (her foto kendi sırasında). |
| 7) Üret | `generate(prompt, image_name, seed)` korunur; etrafına `process_all()` döngüsü gelir. |

### Drive düzeni

```
imageToVideoV2/
├── workflow_api.json
├── input/          ← 0.png, 1.jpg, ... (kullanıcı koyar)
└── output/         ← 0.mp4, 1.mp4, ... (notebook yazar)
```

### Plan hücresi (CONFIG'in ardı, indirmeden önce)

Her numara için karar: foto yolu + prompt dolu + çıktı yok → **ÜRET**; değilse nedeniyle **ATLA**. Tablo basılır, `ÜRET = 0` ise `RuntimeError` — 36 GiB'lık indirme boşa başlamaz. Aynı numaralı iki dosya (`3.png` ve `3.jpg`) → fail-loud, hangisi kastedildiği tahmin edilmez.

### process_all() (loop_maker deseni)

Döngü içinde her foto için: **disk yeniden kontrol edilir** (`output/N.mp4` bu oturumda üretilmiş olabilir) → `/upload/image` → `generate` → Drive'a yaz → Colab kopyaları silinir. Hata sınıflandırması:

- `is_infra` (loader hatası) → **batch durur** — her video aynı hatayı alır
- Video'ya özgü hata → o video atlanır, ham hata loglanır, devam
- Üst üste 3 hata → batch durur
- Sonda özet: üretilen / atlanan / başarısız sayıları

## Doğrulama (kullanıcı, Colab)

1. `input/`'a numaralı fotolar, CONFIG'e prompt listesi → Run all → plan tablosu doğru kararları gösterir.
2. Eşleşen her foto için `output/N.mp4` Drive'da; atlananlar loglarda nedeniyle görünür.
3. Notebook yarıda kesilip yeniden çalıştırılır → var olan mp4'ler "zaten var" ile atlanır, kalanlar üretilir.
4. `PROMPTS`'a bilerek `""` konur → o numara "prompt yok" ile atlanır.

## Kapsam dışı

Foto başına N render (`NUM_RENDERS`), seed listesi, prompt'ları Drive dosyasından okuma, paralel üretim, tek-görsel dosya seçici akışının korunması.
