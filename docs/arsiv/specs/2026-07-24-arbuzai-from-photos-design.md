# WAN 2.2 arbuzai I2V — foto-tanıyan batch (tasarım)

**Tarih:** 2026-07-24 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

Foto generator `1_a.png, 1_b.png, ...` üretiyor. Kullanıcı bir numaranın birden çok iyi fotosunu (ör. `1_a` ve `1_b`) videoya çevirmek istediğinde bugün onları `0.png, 1.png` diye yeniden adlandırıp aynı prompt'u iki kez yazmak zorunda. Ayrı bir notebook bu adlandırmayı **tanır**: `input/1_a.png` + `input/1_b.png` → ikisi de `PROMPTS[1]` ile → `output/1_a.mp4`, `1_b.mp4`. Yeniden adlandırma ve tekrar prompt yok.

## Bağlam

- `wan22-arbuzai/api.ipynb` ile **aynı grafik, aynı modeller, aynı render motoru**. Tek fark: girdi tarayıcı (numaralı tek foto → numara+harf çoklu foto) ve çıktı adı.
- Foto generator çıktı deseni kanıtlı: `photo_generator/nova-3dcg/api.ipynb` → `N_<harf>.png`.
- Seed-varyant altyapısı arbuzai api.ipynb'de kanıtlı: `VARIANTS`, `SEED + v`, varyant düzeyi resume, `uploaded` foto-bir-kez-yükleme.

## Kararlar

| Karar | Gerekçe |
|---|---|
| Ayrı notebook: `wan22-arbuzai/api_from_photos.ipynb` | Kullanıcı kararı. Aynı klasör/grafik; arbuzai api.ipynb'nin kardeşi, girdi tarayıcı + çıktı adı dışında birebir. |
| Girdi: `input/<numara>_<harf>.<ext>`, numaraya göre gruplanır; `PROMPTS[numara]` o numaranın **tüm** fotolarına uygulanır | Kullanıcı kararı ("aynı promptu 2 kere yapıştırmaktansa sistem tanısın"). Foto generator adlandırmasını olduğu gibi kabul eder. |
| Foto başına `VARIANTS` seed varyantı | Kullanıcı kararı. İki varyasyon kaynağı: seçtiğin fotolar + seed. |
| `VARIANTS = 1` default | Asıl ihtiyaç "2 iyi foto → 2 video" — default 1'de foto başına tek video, ucuz. Seed varyantı isteyen 2+ yapar. |
| Çıktı: `VARIANTS=1` → `N_<harf>.mp4`; `VARIANTS>1` → `N_<harf>_<v>.mp4` (v 1'den) | Kullanıcı kararı. Harf = foto, sayı = seed varyantı — gözle ayrışır, çift harf yok. |
| Drive: arbuzai ile **aynı `imageToVideoV2`** paylaşılır | Kullanıcı kararı. Adlandırma farkı çakışmayı önler: eski api.ipynb `stem.isdigit()` ile yalnız `N.png`'yi görür, `N_a.png`'yi görmez; bu notebook yalnız `N_<harf>` desenini alır. `workflow_api.json` zaten orada. |
| Boş prompt / numara liste dışı → o numaranın tüm fotoları atlanır, loglanır | arbuzai kuralları foto grubuna yayılır. |
| Aynı numara+harf iki uzantıda (`1_a.png` + `1_a.jpg`) → fail-loud | arbuzai `find_image` deseni; hangisi kastedildiği tahmin edilmez. |

## Mimari

`collab-toolbox/video_generator/wan22-arbuzai/api_from_photos.ipynb` — `api.ipynb` kopyası, 6 hücre değişir (0, 1, 2, 3, 12, 13); geri kalanı (yardımcılar, custom node, model, başlatma) aynen.

### Drive düzeni (paylaşımlı)

```
imageToVideoV2/
├── workflow_api.json
├── input/          ← 1_a.png, 1_b.png, 3_c.png … (foto generator'dan kopyalanır)
└── output/         ← 1_a.mp4 / 1_a_1.mp4, 1_a_2.mp4 … (bu notebook yazar)
```

### Girdi tarayıcı

`<numara>_<harf>.<ext>` deseni (`re`), numaraya göre gruplanır → `{numara: {harf: path}}`. Uzantı serbest (png/jpg/jpeg/webp), büyük/küçük harf yok sayılır (Colab dosya sistemi case-sensitive, telefon `.JPG` yazar). `find_image`'in tekil-dosya/çift-dosya mantığı korunur.

### build_plan

Satır: `(numara, foto_harfi, varyant, aksiyon, image_path, prompt, reason)`. Her `PROMPTS[numara]` için o numaranın her fotosunun her seed-varyantı bir satır. ÜRET / ATLA (prompt boş / prompt yok / çıktı zaten var). ÜRET=0 → RuntimeError (indirme boşa başlamaz). Tablo çıktı adını (`1_a`, `1_a_1`) gösterir.

### process_all / generate_one

Foto başına bir kez `/upload/image` (`uploaded` cache), dönen server-adı o fotonun tüm varyantlarına verilir. `generate_one(client, save_path, image_name, prompt, seed)` — çıktı yolu dışarıdan gelir (adlandırma `out_path` yardımcısında, VARIANTS'e göre koşullu). Seed: `None` → varyant başına rastgele, sabitse `SEED + v`. Hata sınıflandırması (infra-stop / video-atla / 3-ardışık / timeout) arbuzai'den korunur.

## Doğrulama (kullanıcı, Colab)

1. `input/`'a `1_a.png, 1_b.png`, CONFIG'e `PROMPTS[1]` dolu (0 boş) + `VARIANTS=1` → Run all → plan `1_a`, `1_b` için ÜRET; `0_*` yok, `1` dışı numaralar için satır yok.
2. `output/1_a.mp4`, `1_b.mp4` Drive'da.
3. `VARIANTS=2` yapılıp tekrar → `1_a.mp4` "zaten var" değil (ad değişti `1_a_1.mp4`) → `1_a_1, 1_a_2, 1_b_1, 1_b_2` üretilir; iki varyant farklı (seed loglarda).
4. Notebook yarıda kesilip yeniden → var olanlar "zaten var" ile atlanır.
5. `PROMPTS[1]` boşaltılır → `1_*` fotoları "prompt boş" ile atlanır.

## Kapsam dışı

`api_from_photos.ipynb` dışındaki her şey: grafik, modeller, `manual.ipynb`, `api.ipynb`, foto generator. Foto-harfi ile seed-varyantının tek isimde birleştirilmesi zaten yapıldı; başka birleşme yok. Foto generator çıktısını otomatik kopyalama (kullanıcı elle seçip kopyalar).
