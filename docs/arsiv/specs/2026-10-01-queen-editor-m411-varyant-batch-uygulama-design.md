# Madde 411 — Varyantlar tek işte, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Parça:** 411 · v8-8 · **Tur:** 2/2 — kod.
**Testler:** [m411 test turu](2026-10-01-queen-editor-m411-varyant-batch-testler-design.md) — kurallar
ve araştırma orada; bu belge yalnız nasıl yapıldığını söyler. **Commit yok:** her şey çalışma ağacında
kalır, kullanıcı Changes'te okur; `dist`'i birleştirmede koşu kurar.

## Yaklaşımlar

1. **Seçilen — batch, fotoğraf üreticisinin isteğe bağlı yeteneği.** Üretici `fits_batch` ve
   `generate_batch` taşır; döngü işin üreticisinde bu ikisi varsa ve kart tutuyorsa varyantları tek
   işte ister, yoksa bugünkü yoldan gider. Hangi işlerin birlikte üretileceği küçük, saf bir domain
   kuralı. Video ve ses üreticileri, ve testlerin bugünkü sahteleri, batch yapamaz — bugünkü yol
   kendiliğinden korunur.
2. *Elendi —* `make_job`'a ayrı bir `batcher` bağımlılığı: kuyruğun sekiz kapısından ve `main.py`'den
   geçirilecek bir parametre, aynı nesneyi iki kez taşımak için.
3. *Elendi —* üretici kendi içinde karar versin (sığmazsa tek tek döngü kursun): "tek tek, bugünkü
   gibi" her varyantın kendi seed'ini, kendi üç denemesini, kendi inişini ve satırını ister — o
   döngünün işi.
4. *Elendi —* batch'i planda tek satır yapmak: her karenin kimliği planda yazılı ve değişmez
   *(plan_frames)*; plan şemasını değiştirmek eski projeleri de ilgilendirir.

## Bellek eşiği — sayılar ve kaynakları

Bir batch'in kartta istediği, **ComfyUI'nin kendi bellek kurallarıyla** —
`ComfyPhotoGenerator`'da üç sabit, her biri kaynağıyla:

- **Ağırlıklar:** SDXL'in UNet'i, 2,6 milyar parametre *(SDXL makalesi,
  [arXiv 2307.01952](https://arxiv.org/abs/2307.01952))*, fp16'da ikişer bayt → **5,2 GB**.
- **ComfyUI'nin her işte ayırdığı:** `minimum_inference_memory()` = 0,8 GiB + Linux'ta
  `EXTRA_RESERVED_VRAM` 400 MiB *([model_management.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy/model_management.py))*
  → **1,28 GB**.
- **Resim başına örnekleme payı:** `memory_required()` = latent alanı × 2 bayt × 0,01 ×
  `memory_usage_factor` MiB *([model_base.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy/model_base.py))*,
  SDXL'de faktör 0,8 *([supported_models.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy/supported_models.py))*;
  grafiğin 1024 × 1536'sı 128 × 192'lik latent; cfg batch'i ikiye katlıyor
  *([sampler_helpers.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy/sampler_helpers.py))*;
  ve `_calc_cond_batch` cond ile uncond'u birlikte koşmadan önce bunun **1,5 katını** boş istiyor
  *([samplers.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy/samplers.py))*
  → **1,24 GB**.

**Kart tutar ⇔ `vram_total ≥ 5,2 GB + 1,28 GB + n × 1,24 GB`.** `vram_total` ComfyUI'nin
`/system_stats`'ından. Colab'ın kartları, PyTorch'un bellek hatasındaki "total capacity"leriyle: T4
14,74 GiB → en çok **7** varyant; A100 40 GB 39,56 GiB → **29**, yani panelin 26'sının hepsi. **4
varyantlı bir prompt T4'te de batch'le üretilir** — kullanıcının "T4 olabilir"i ComfyUI'nin kuralında
tutmuyor. Eşik daha az varyantta durmalıysa değişen tek satır bu formül. ComfyUI kendi tahminini
"TODO: this needs to be tweaked" diye işaretliyor; tahmin düşük kalırsa ComfyUI ağırlıkları kısmen
indirip yavaşlar, VAE'yi parçalar — çökmez. Gerçekten bellek biterse batch karenin hatası olarak düşer,
üç kez denenir, sonra varyantlar kırmızı; Tekrar dene onları tek tek üretir.

**Bekleme sınırı resim başına** — `RENDER_TIMEOUT` "tek fotoğraf için" bir takılma bekçisi (15
dakika). T4'te 7'lik bir batch 1:30–2:00'lık resimlerle 10–14 dakika sürer; tek fotoğrafın sınırı onu
takılmış sayıp üç kez baştan başlatırdı. `generate_batch` sınırı resim sayısıyla çarpar. *Test turunun
22. testi bunu söylemiyordu (`60` bekliyordu); bu turda `240`'a döndü — sebep bu paragraf.*

## Dosyalar

### `backend/services/comfy/client.py`

- **`fetch_outputs(history_entry, count, extensions=None)`** — bugünkü süzgeç aynen; çıktı yoksa
  bugünkü hata; sayı `count` değilse
  `"{count} çıktı bekleniyordu, {n} geldi — grafikte Batch Size {count} mi?\n{gelenler}"`; yoksa her
  çıktı `/view`'dan, sırasıyla, liste olarak.
- **`fetch_output(history_entry, extensions=None)`** = `fetch_outputs(entry, 1, extensions)[0]` —
  metni ve sözleşmesi aynı.
- **`vram_total()`** — `GET /system_stats`, `raise_for_status`, `devices[0]["vram_total"]`. İlk cihaz
  ComfyUI'nin render ettiği: `system_stats` kendi cihazını başa koyuyor. `_send` üzerinden, yani
  ulaşılamayan sunucu bugünkü sözlerle.

### `backend/features/photo_generation/data/comfy_photo_generator.py`

- `BATCH_NODE = "23"`; modül belgesine eklenir. Üç bellek sabiti, yukarıdaki kaynaklarıyla.
- Grafiği kuran kısım `generate`'ten `_graph(prompt, negative, seed, model, lora)`'ya taşınır;
  `generate` onu kullanır, davranışı aynı.
- **`generate_batch(prompt, negative, seed, count, model="", lora="")`** — `_graph`; `"23"` yoksa
  `_set_loras`'ın üslubuyla hangi node'un eksik olduğunu söyler; değere `count` yazılır; `submit`,
  `wait(prompt_id, timeout × count)`, `fetch_outputs(history, count)`.
- **`fits_batch(count)`** — `client.vram_total() ≥ ağırlıklar + ayrılan + count × resim payı`.
  Her batch'te bir kez sorulur; saklanmaz.

### `backend/features/photo_generation/domain/variant_batch.py` — yeni, saf

- `MADE_FROM = ("prompt", "negative", "model", "lora")` — seed'in yanında bir resmin yapıldığı her şey.
- **`together(owed, slots)`** — kuyruğun başı; başı hiç sırası gelmemiş bir fotoğraf işiyse, hemen
  arkasından aynı numaradan, `MADE_FROM`'u aynı, hiç sırası gelmemiş fotoğraf işleri — ilk uymayanda
  durur. "Hiç sırası gelmemiş": fotoğraf yuvasında hiçbir satır yok (Tekrar dene'nin `queued`'ı satır).
- **`asked(jobs, head)`** — plandaki aynı prompt'un varyantları, kimlikle sayılır.

### `backend/features/photo_generation/domain/run_loop.py`

- **`_made_together(owed, jobs, slots, producer)`** — `together`; birden çoksa ve üreticide
  `fits_batch` varsa ve `fits_batch(asked(...))` evetse grup, yoksa yalnız baş.
- **`_files(name, together)`** — başın kendi adı, sonra batch'in öteki resimleri `photo_file`.
- Turun ilk raporu `"batch": None` taşır (`startedAt` gibi). `try`'dan önce `together = [current]`.
- Üretim dalında: `together = _made_together(...)`; başlama raporu `startedAt`, `batch` (baş
  dışındaki kimlikler) ve `pending` (`owed[len(together):]`); birden çoksa
  `producer.generate_batch(...)`, değilse `[producer.generate(...)]` → `made`.
- Karenin hatası: `together`'ın her işi `_files` adıyla kırmızı, aynı sebeple.
- İniş: `renderSeconds = round((rendered - started) / len(together), 1)`; kapının altında her iş için
  önce dosya, sonra satır; seed `chosen`. Videonun ilk karesi `made[0]`'dan — video hep tek başına.
  Zaman satırı dosyaları virgülle birleştirir.

### `backend/features/photo_generation/domain/ports.py`

`BatchPhotoGenerator(PhotoGenerator, Protocol)` — `fits_batch` ve `generate_batch`'in sözleşmesi;
döngünün onları yalnız varsa sorduğu yazılır.

### Ekran — `frontend/src/features/photo_generation/`

- **`useGeneration.js`** — `batch = current ? job.batch || [] : []`; döndürülür. Bekleyen sayılırken
  `current` gibi batch'tekiler de atlanır.
- **`Gallery.jsx`** — `batch = []` prop'u; `making(fid)` = `current` ya da batch'te. Kutucuğun
  üretiliyor hâli, seçilebilirlik ve shift'le seçilen dizi `making`'e bakar.
- **`PhotoDetail.jsx`** — `batch`'i hook'tan alır; `running` batch'teki karede de dolu.
- **`ProjectScreen.jsx`** — `batch`'i galeriye verir.

### `queen-editor/CODE-STANDARD.md`

İki satır doğru kalsın diye: fotoğrafın enjeksiyon node'larına `"23"`; `comfy/` servisi üretilen
dosyaları alır ve kartın belleğini okur.

## Bilinçli olarak yapılmayan

- Satıra batch'in büyüklüğü ya da sırası yazılmaz; plana yeni alan girmez.
- Kartın cevabı saklanmaz; ComfyUI'nin başlatılması, defter, `workflow_api.json` değişmez.
- `dist` bu turda kurulmaz; yol haritasına dokunulmaz.
