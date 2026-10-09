# Nova 3DCG foto üretimi — API modu (tasarım)

**Tarih:** 2026-07-22 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

`manual.ipynb` çalıştı ve beğenildi; şimdi UI açmadan üretim: CONFIG'e prompt listesi yazılır, her prompt için **4 varyant** (`VARIANTS = 4`, değiştirilebilir) üretilir, çıktılar Drive'a `photoGenV2/output/N_a.png, N_b.png, ...` olarak iner. Kullanıcı beğendiğini `imageToVideoV2/input/N.png` diye elle kopyalar — video batch'inin girdisi olur.

## Bağlam

- İskelet arbuzai `api.ipynb`'den kanıtlı: plan-önce-üretim, resume, `ComfyClient` (`POST /prompt` + `/history` polling + `/view`), `describe_comfy_error`/`is_infra`, üst üste 3 hatada durma.
- Fark: girdi görseli yok (text-to-image) — `input/` klasörü, `/upload/image`, numara-foto eşleşmesi tamamen kapsam dışı. Girdi = sadece `PROMPTS`.
- Workflow kullanıcının kendi **Export (API)** dosyası; Drive'dan okunur (`photoGenV2/workflow_api.json`). Kullanıcı ayarı her değiştirdiğinde yeniden export alır — notebook değişmez.

## Kararlar

| Karar | Gerekçe |
|---|---|
| Prompt enjeksiyonu POSITIVE kutusuna, **aynı metin iki alana birden** (`wildcard_text` + `populated_text`) | API modunda sunucunun hangi alanı okuduğu garanti değil: [Impact Pack issue #483](https://github.com/ltdrdata/ComfyUI-Impact-Pack/issues/483) sunucunun `wildcard_text`'i işlemediğini gösteriyor (hâlâ açık). Çift yazım iki dünyada da doğru prompt'u garantiler. |
| **Sözleşme: düz prompt** — `__x__` / `{a\|b}` wildcard sözdizimi desteklenmez | Sunucu `populated_text`'i ham kullanırsa sözdizimi açılmadan CLIP'e gider. Creator'ın kendi prompt'ları da düz; `(x:1.3)` ağırlık sözdizimi CLIPTextEncode'da işlenir, etkilenmez. |
| Enjeksiyon node id'leri **kullanıcının export'undan okunup sabitlenir** (arbuzai deseni: `PROMPT_NODE`/`SEED_NODE` sabitleri) | Kullanıcı kararı: "ben export'u atayım, onu kullan, kendi bulmasın". Export repoya `nova-3dcg/workflow_api.json` olarak girer, id'ler oradan tespit edilir; dinamik arama yok. Plan, export gelmeden yazılamaz. |
| `NEGATIVES` de CONFIG'de **liste** — `PROMPTS` ile paralel (`NEGATIVES[n]` ↔ `PROMPTS[n]`), node 4'e çift alanla enjekte | Kullanıcı kararı ("positive ile aynı şekilde olsun; her videonun negatifi farklı"). İki liste aynı uzunlukta olmalı, değilse CONFIG'de fail-loud. Boş `""` negatif = o üretim negatifsiz (atlama değil — atlama yalnız PROMPTS'ta). |
| USNR LoRA **export'un içinde** (`lora_1`: USNR @ 0.8, on); notebook Power Lora Loader'a dokunmaz | Kullanıcı kararı ("yeniden export alırım") — uygulandı: repodaki `workflow_api.json` LoRA'lı export. Export tek gerçek kaynak. |
| Seed: varyant başına rastgele, loglanır; `SEED` sabitse ondan türetilir | rgthree Seed node'u `-1`'i frontend'de çözer — arbuzai'de kanıtlanmış tuzak; API'de seed'i biz üretip node'a yazarız. Grafikte KSampler + her iki wildcard kutusunun seed'i aynı Seed node'una bağlı → tek yazım hepsini besler. |
| `VARIANTS = 4` default; çıktı `output/<prompt_idx>_<a,b,c,...>.png` | Kullanıcı kararı. Varyant = aynı prompt, farklı seed. |
| Resume varyant düzeyinde: `N_x.png` varsa o varyant atlanır | arbuzai deseni; yarıda kesilen oturum kaldığı varyanttan devam eder. Yeniden üretim = Drive'dan o png'yi silmek. |
| Boş prompt (`""`/boşluk) = o numara atlanır, loglanır | arbuzai batch kuralının aynısı — listeyi kaydırmadan numara devre dışı bırakma. |
| Üretim başına **tam 1** `type=="output"` görseli beklenir; değilse fail-loud | Önizleme node'ları (Image Comparer) `temp` tipinde çıktı üretebilir, filtrelenir. Birden fazla `output` görseli = grafikte Batch Size > 1 → tahmin edilmez, gerçek liste basılıp durulur. Markdown'a "Batch Size grafikte 1 kalsın" notu düşülür. |
| Donanım: T4 | manual ile aynı; SDXL sınıfı. |

## Mimari

```
collab-toolbox/photo_generator/nova-3dcg/
├── manual.ipynb           (mevcut, değişmez)
├── workflow_manual.json   (mevcut, değişmez)
├── workflow_api.json      (YENİ — kullanıcının Export (API)'ı, id'lerin kaynağı)
└── api.ipynb              (YENİ — arbuzai api.ipynb iskeleti, foto uyarlaması)
```

### Drive düzeni

```
photoGenV2/
├── workflow_api.json   ← kullanıcının Export (API)'ı (kullanıcı koyar)
└── output/             ← 0_a.png, 0_b.png, ... (notebook yazar)
```

### api.ipynb hücre akışı

| Bölüm | İçerik |
|---|---|
| 1) CONFIG | `PROMPTS = ["""...""", ...]` + `NEGATIVES = ["""...""", ...]` (paralel liste; kullanıcının test negatifi ilk maddede hazır) + `VARIANTS = 4` + `SEED = None` + cookie + `DRIVE_ROOT = MyDrive/photoGenV2`. Dolu prompt yoksa ve liste uzunlukları eşit değilse assert. |
| 2) Plan | Drive mount + `workflow_api.json` yüklenir (yoksa/UI formatıysa fail-loud: `nodes` anahtarı görülürse "Export (API) gerekir" uyarısı) + prompt×varyant tablosu: ÜRET / ATLA (prompt boş / çıktı zaten var). ÜRET = 0 → RuntimeError. Sabit enjeksiyon id'lerinin (`PROMPT_NODE` vb.) dosyada var olduğu burada doğrulanır, yoksa fail-loud — indirmeden önce. |
| 3-4) Yardımcılar, custom node'lar | manual ile aynı (8 paket). |
| 5) Modeller | manual ile aynı 5 dosya. |
| 6) ComfyUI başlat | Headless (tunnel yok) — arbuzai api deseni. |
| 7) Üret | `ComfyClient` + `generate_one(prompt_idx, variant, prompt, seed)`: POSITIVE çift alan + Seed node yazılır → kuyruk → polling → history'den `type=="output"` görseli `/view` ile alınır → `output/N_x.png`. `process_all()`: infra-stop / varyant-atla / üst üste 3 hatada dur / özet. |

## Doğrulama (kullanıcı, Colab)

1. Manual'de beğenilen ayarla Export (API) → `photoGenV2/workflow_api.json`.
2. CONFIG'e 2+ prompt (biri boş) → Run all → plan tablosu doğru ÜRET/ATLA kararlarını basar.
3. Her dolu prompt için `output/`'ta `N_a..N_d.png` — 4'ü birbirinden farklı (seed loglarda).
4. Aynı notebook yeniden çalıştırılır → hepsi "zaten var" ile atlanır.
5. Prompt'lardan birinin çıktısı silinip tekrar çalıştırılır → sadece o varyant yeniden üretilir.

## Kapsam dışı

Wildcard sözdizimi desteği, NEGATIVE'in CONFIG'e alınması, upscale/detailer dallarının notebook'tan yönetimi (export ne içeriyorsa o), `imageToVideoV2/input/`'a otomatik kopyalama, CLAUDE.md tablo satırı (iki notebook da kanıtlanınca).
