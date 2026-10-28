# WAN 2.2 arbuzai I2V — girdi başına N varyant (tasarım)

**Tarih:** 2026-07-24 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

`wan22-arbuzai/api.ipynb` şu an foto başına tek video üretiyor (`PROMPTS[0]` ↔ `input/0.*` ↔ `output/0.mp4`). Foto generator'daki varyant sistemi buraya taşınır: aynı foto + aynı prompt, **farklı seed → farklı hareket**, çıktı `output/N_a.mp4, N_b.mp4, ...`. Kullanıcı beğendiği varyantı seçer.

## Bağlam

- Varyant deseni `photo_generator/nova-3dcg/api.ipynb`'de kanıtlı: `VARIANTS` + `VARIANT_LETTERS`, plan tablosu, `SEED + v` formülü, varyant düzeyi resume.
- Video foto'dan **çok pahalı**: A100'de render dakikalar sürer (foto T4'te saniyeler). 5 foto × 4 varyant = 20 video = saatler. Bu yüzden video'da default varyant düşük tutulur.
- Değişen tek dosya `wan22-arbuzai/api.ipynb`; grafik, modeller, manual, foto sistemi dokunulmaz.

## Kararlar

| Karar | Gerekçe |
|---|---|
| `VARIANTS = 2` default (CONFIG'de değiştirilebilir) | Kullanıcı kararı. Video pahalı — düşük default kazara saatlerce render'ı önler; kullanıcı isterse 4-5 yapar. |
| Çıktı `output/N_<harf>.mp4`, hep harfli (`VARIANTS=1` bile `N_a.mp4`) | Foto deseniyle tutarlı; kod tek yol izler, "1 ise harfsiz" özel durumu yok. |
| Varyant = aynı foto + aynı prompt, farklı seed | Foto'daki mantığın aynısı. Seed hem PromptGenerator hem sampler'a gider (mevcut `set_seed`), değişmez. |
| Seed: `None` → varyant başına rastgele; sabitse varyant `v` için `SEED + v` | Foto formülü. Sabit seed'de dört varyant aynı seed'i alsaydı dört kez aynı video çıkardı. |
| Foto **bir kez** yüklenir, N varyant o server-adıyla render edilir | `upload_image` foto başına bir kez; aynı fotoyu N kez yüklemek boşa I/O. |
| Resume varyant düzeyinde: `output/N_<harf>.mp4` varsa o varyant atlanır | Foto deseni. Yarıda kesilen batch kaldığı varyanttan devam eder. Yeniden üretim = o mp4'ü silmek. |
| Boş prompt / foto yok → o numaranın **tüm varyantları** atlanır, loglanır | Mevcut arbuzai kuralları varyant düzeyine yayılır. |

## Mimari

`collab-toolbox/video_generator/wan22-arbuzai/api.ipynb` — hücre yapısı korunur, üç bölge değişir:

| Bölüm | Değişiklik |
|---|---|
| 1) CONFIG | `VARIANTS = 2` + `VARIANT_LETTERS = "abcdefghijklmnopqrstuvwxyz"` eklenir; `VARIANTS` aralık assert'i. Kalan CONFIG (PROMPTS, SEED, Drive, cookie) aynı. |
| Plan hücresi | `build_plan` satır başına `(n, letter, action, image_path, prompt, reason)` döner — her foto × varyant için bir satır. Karar mantığı (ÜRET / ATLA-foto-yok / ATLA-prompt-boş / ATLA-zaten-var) varyant düzeyinde. Tabloda `N_a` gibi çıktı adı gösterilir. |
| Üret hücresi | `generate_one(client, n, letter, image_name, prompt, seed)` — foto adı dışarıdan gelir (yükleme döngü dışına taşınır). `process_all`: her ÜRET satırı için, o numaranın fotosu bir kez yüklenip varyantlar sırayla render edilir → `output/N_<harf>.mp4`. Hata sınıflandırması (infra-stop / video-atla / 3-ardışık / timeout) korunur. |

### Drive düzeni

```
imageToVideoV2/
├── workflow_api.json
├── input/          ← 0.png, 1.jpg, ... (kullanıcı koyar)
└── output/         ← 0_a.mp4, 0_b.mp4, 1_a.mp4, ... (notebook yazar)
```

### Foto yükleme optimizasyonu

Mevcut `generate_one` her çağrıda `upload_image` yapıyor. Varyantla bu foto başına N kez tekrarlanırdı. Yükleme `process_all` döngüsünde foto başına bir kez yapılır; dönen server-adı o numaranın tüm varyantlarına verilir.

## Eski çıktılar (uyarı)

Önceki arbuzai çalıştırmalarından `output/N.mp4` (harfsiz) varsa yeni sistem onları "zaten var" saymaz — `N_a.mp4`'ü yeniden üretir. Eski dosyalar Drive'da kalır, karışmaz; sadece kullanıcı bilsin.

## Doğrulama (kullanıcı, Colab)

1. `input/`'a numaralı fotolar, CONFIG'e prompt listesi + `VARIANTS = 2` → Run all → plan tablosu her foto için `N_a` / `N_b` satırlarını doğru ÜRET/ATLA ile gösterir.
2. Her ÜRET satırı için `output/N_<harf>.mp4` Drive'da; iki varyant birbirinden farklı (seed loglarda).
3. Notebook yarıda kesilip yeniden çalıştırılır → var olan `N_<harf>.mp4`'ler "zaten var" ile atlanır, kalanlar üretilir.
4. `VARIANTS` 4 yapılıp tekrar çalıştırılır → mevcut a/b atlanır, c/d üretilir.

## Kapsam dışı

`wan22-arbuzai/api.ipynb` dışındaki her şey: grafik, modeller, `manual.ipynb`, foto generator. Per-prompt değişken varyant sayısı (hepsi tek `VARIANTS`), eski harfsiz çıktıların otomatik taşınması.
