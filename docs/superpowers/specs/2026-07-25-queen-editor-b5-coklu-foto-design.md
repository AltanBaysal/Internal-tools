# Queen Editor — Bölüm 5: Çoklu foto (tasarım)

**Tarih:** 2026-07-25 · **Bölüm:** 5/7 · **Önkoşul:** Bölüm 4 Colab'da doğrulandı (tek foto üretildi)
**Şemsiye:** [2026-07-24-queen-editor-v1-design.md](2026-07-24-queen-editor-v1-design.md) ·
**Yol haritası:** [2026-07-24-queen-editor-roadmap.md](../plans/2026-07-24-queen-editor-roadmap.md) ·
**Bölüm 4:** [2026-07-25-queen-editor-b4-tek-foto-design.md](2026-07-25-queen-editor-b4-tek-foto-design.md)

## Amaç

Tasarımın asıl proje ekranı. Prompt **listesi** yapıştırılır, negatif yazılır, varyant seçilir,
**Üret** → her prompt × varyant için bir foto sırayla üretilir, galeri üretim sürerken dolar.
Artboard **03** (form) + **04** (üretiliyor: sayaç, ilerleme çubuğu, şu anki prompt, **Durdur**).
Mutlu yol: kırmızı kare kartları (05) ve kaldığı yerden devam (06) **Bölüm 7'de**; prompt kaydı
(`prompts.json`) **Bölüm 6'da**.

Düzen şemsiye spec'ten: **solda galeri, sağda panel.** (Yol haritasındaki B5 satırı tersini
yazıyordu; bu commit'le düzeltildi — şemsiye spec kararların tek kaynağı.)

## Kararlar

| Karar | Gerekçe |
|---|---|
| **Prompt girişi: tek kutu, Python listesi yapıştırılır** | Yol haritasının sözü ("listeyi yapıştır … (Python list)") ve gerçek iş akışı: prompt listeleri notebook'larda zaten `PROMPTS = [...]` olarak var. 12 ayrı kutuya 12 paste yaptırmayız. Backend `ast.literal_eval` ile güvenli parse eder (kod çalıştırmaz). Baştaki `AD =` kırpılır — notebook'tan değişken satırıyla kopyalamak da geçerli. |
| **Boş öğe = "bu satır kapalı", filtrelenir** | nova-3dcg'nin kanıtlı sözleşmesi: `""` öğesi o satırı üretimden düşürür. Filtre sonrası liste boşsa Türkçe hata. |
| **Negatif: tek ortak kutu** (kullanıcı kararı) | Batch'teki bütün prompt'lara aynı negatif gider. nova'da NEGATIVES paraleldi ama pratikte tek standart metnin tekrarıydı. Boş bırakılabilir — o batch negatifsiz üretilir (nova kuralı). Prompt başına negatif gerekirse B6+. |
| **Hata politikası: atla ve devam** (kullanıcı kararı) | api.ipynb'nin kanıtlı davranışı: patlayan kare atlanır (numarası boş kalır), **üst üste 3** kare hatası veya **infra** hatası (loader) batch'i durdurur. B5'te görüneni durum satırındaki özet + ham hata metni; kırmızı kare kartları B7. |
| **Politikanın evi `domain/policy.py`** (saf) | Kural değişikliği (3→5, yeni durdurma sebebi) tek dosyaya dokunur. Domain servis import edemez; infra bayrağı `getattr(exc, "infra", False)` ile okunur — `ComfyExecutionError` tipine bağımlılık yok. |
| **Batch döngüsü use case'te, runner aptal kalır** | `runner.py` yalnız thread + durum + durdurma bayrağı taşır (B4 + `report()` + `request_stop()`). 48 karelik döngü `start_batch`'in kurduğu closure'da: sync `spawn` ile threadsiz test edilir. Video, runner'ı ve policy'yi **kopyalar** — bağımlılık yok (B4 kararı geçerli). |
| **`start_generation` ölür, tek yol `start_batch`** | Tek foto = 1 elemanlı liste × 1 varyant. İki yol tutmak DRY ihlali ve ölü kod. Endpoint aynı kalır, gövdesi `{prompts, negative, variants}` olur; B4'ün testleri yeni yola taşınır. |
| **Numaralama: batch başında `start = max+1`; prompt `j` → numara `start+j`, varyant → harf** | nova'nın "numara = prompt, harf = varyant" anlamı korunur; üstüne yazma yok, tekrar Üret sona ekler (yol haritası sözü). Patlayan karenin numarası boşluk olarak kalır — dürüst iz, B7'nin devam mekanizması doldurabilir. |
| **Üretim sırası prompt-major** | nova sırası: `0_a 0_b … 0_d 1_a …`. Değiştirmesi 1 satır (plan kurucusunda); "önce her prompt'tan bir tane" istenirse varyant-major yapılır. |
| **Seed: kare başına rastgele** | B4 davranışının devamı. UI'da seed kontrolü yok (YAGNI; nova'nın `SEED` sabiti istenirse sonra). |
| **Durdur: nazik** — süren render biter, sıradaki başlamaz | Bayrak kareler **arasında** okunur. ComfyUI'nin `/interrupt`'u kanıtlanmamış; ~1 dk'lık kare beklenebilir. Durum `stopped` olur, panel forma döner. |
| **Varyant sınırı: domain 1..26, UI 1-4 sunar** (default 4) | Fiziksel sınır harf alfabesi (domain'de); sunulan aralık UI kararı — aralığı değiştirmek 1 frontend dosyası. |
| **Galeri açılışta Drive'dan** — yeni uç `GET /api/projects/<ad>/photos` | Sayfa yenilenince fotolar kaybolmaz (Drive gerçek kaynak). Üretim sürerken liste her yoklamada tazelenir — galeri canlı dolar. |

## Ekran (artboard eşlemesi)

| Durum | Görünen | Artboard |
|---|---|---|
| boşta | Solda galeri (5 sütun, en yeni numara üstte; boşsa "henüz foto yok" notu). Sağda form: prompt listesi kutusu · negatif kutusu · varyant `Segment` (1/2/3/4) · **Üret** (liste boşken pasif) | 03 |
| üretiliyor | Sağ panel durum bloğuna döner: `7/48` + ilerleme çubuğu + şu anki `numara_harf` + prompt'un ilk satırı (kısaltılmış) + başarısız sayısı (varsa) + **Durdur**. Galeri her yoklamada tazelenir | 04 |
| bitti / durduruldu | Özet satırı (`bitti — 48/48` · `durduruldu — 17/48`) + form geri gelir | 03 |
| hata (batch durdu) | Özet + ham hata metni mono kutuda (B4'ün deseni) + form geri gelir | (06'nın hata satırı; kart B7'de) |
| başka projede üretim | "Üretim sürüyor: <proje>" notu, Üret pasif | — |

Foto tıkla → yeni sekme (B4 davranışı). Sayfa yenile: galeri dolu gelir, süren üretim yakalanır,
**form boşalır** (bilinçli bedel — B6 `prompts.json` ile çözer).

## Backend yüzeyi

| Uç | İş | Cevaplar |
|---|---|---|
| `POST /api/projects/<ad>/generate` | Gövde `{prompts: str, negative: str, variants: int}` → parse + doğrula + batch'i başlat. `negative` eksik/str değilse boş sayılır; `variants` eksik/int değilse varyant hatası (400) | 202 · 400 (parse/varyant, Türkçe mesaj) · 404 (proje yok) · 409 (meşgul) |
| `GET /api/status` | Runner durumu, olduğu gibi | `idle` · `running{project, done, failed, total, current{number, letter, prompt}}` · `done` / `stopped` / `error{error}` (üçü de `done/failed/total` taşır) |
| `POST /api/stop` | Durdurma bayrağını kaldır | 200 + güncel durum (boştayken no-op) |
| `GET /api/projects/<ad>/photos` | Galeri listesi: şemaya uyan dosyalar, numara azalan → harf artan | 200 `{photos:[{file}]}` · 404 (proje yok) |
| `GET /photos/<ad>/<dosya>` | Değişmez (B4) | 200 · 404 |

## Domain davranışı

- **`domain/prompt_list.py` — `parse_prompts(text) -> list[str]`:** baştaki `AD =` kırpılır,
  `ast.literal_eval`, yalnız `list` + tüm öğeler `str` kabul; öğeler strip edilir, boşlar düşer.
  Hatalar (Türkçe, 400 olarak döner): okunamadı → örnekli mesaj; liste/str değil → tip mesajı;
  filtre sonrası boş → "Listede dolu prompt yok."
- **`domain/policy.py`:** `MAX_CONSECUTIVE = 3` · `stop_reason(consecutive, infra) -> str | None`
  — infra → "Altyapı hatası (model yükleyici) — üretim durduruldu"; üst üste 3 → "Üst üste 3
  render başarısız — üretim durduruldu"; yoksa `None`.
- **`usecases/start_batch.py`:** doğrula (parse · proje var mı · 1 ≤ varyant ≤ 26) →
  `start = store.next_number(project)` → kare listesi (prompt-major) → closure'ı `runner.start`'a
  ver (`Busy` → 409). Closure her karede: `report({current, done, failed, total})` → durdurma
  bayrağı → üret → kaydet; hatada `policy.stop_reason` bakar, `None` ise atlar. Dönüş: özet dict
  (`done`/`stopped`/`error`).
- **`usecases/get_status.py`:** değişmez.

## Runner sözleşmesi (`runner.py`)

- `start(project, job) -> bool` — `job()` **özet dict döner** (`{"status": "done"|"stopped"|"error", …}`);
  son durumu **runner damgalar** (`project` ekler). Döngüden kaçan beklenmedik exception'ı runner
  yakalar → `error` + ham metin (B4 davranışı korunur).
- `report(patch)` — koşan iş ilerlemeyi yazar; runner `{"status": "running", "project", **patch}` tutar.
- `request_stop()` / `stop_requested()` — bayrak; her `start` bayrağı sıfırlar.
- `status()` değişmez. Tek iş kuralı: aynı anda bir iş (409'un kaynağı).

## Data katmanı

- **`data/comfy_photo_generator.py`:** `NEGATIVE_NODE = "4"` eklenir; `generate(prompt, negative,
  seed)` — node 3 ve 4'e çift alan (`wildcard_text` + `populated_text`), node 40'a seed. `_load`
  artık 3/4/40'ı doğrular. Boş negatif = boş string yazılır (negatifsiz üretim).
- **`data/photo_store.py`:** `list_photos(project) -> list[str]` — şemaya uyan dosyalar,
  `(-numara, harf)` sırasıyla. Şema bilgisi bu dosyada kalır.

## Değişiklik yerelliği (bu bölümün kanıtı)

`services/comfy` · `services/drive` · `features/projects` · `web/` · `config.py`: **sıfır değişiklik.**
İşin tamamı `features/photo_generation/` + `main.py` bağlaması + frontend'in kendi feature klasörü.

| Gelecekteki değişiklik | Dosya |
|---|---|
| Politika (3→5, yeni sebep) | 1 — `domain/policy.py` |
| Graf yeniden export | 1 — `data/comfy_photo_generator.py` |
| Dosya adı şeması | 1 — `data/photo_store.py` |
| Varyant aralığı UI'da | 1 — frontend paneli |
| Üretim sırası (prompt-major ↔ varyant-major) | 1 — `usecases/start_batch.py` |
| Video generation | 0 ortak dosya — runner + policy kopyalanır |

## Frontend

`features/photo_generation/`: `ProjectScreen.jsx` (yerleşim: solda galeri `flex:1`, sağda ~380px
panel) · `Gallery.jsx` (5 sütun grid, yeni sekme, boş durum) · `GeneratePanel.jsx` (form; hata
notları B4 deseni) · `ProgressPanel.jsx` (sayaç, çubuk, şu anki prompt, Durdur) ·
`useGeneration.js` (2 sn yoklama; koşarken foto listesini de tazeler) · `shared/api.js`'e
`generateBatch` / `stopGeneration` / `listPhotos`.

Varyant seçici **kendi bileşenimiz** (`VariantPicker.jsx`), kit'in `Segment`'i değil: o bir
wireframe — butonlarında `onClick` yok, tıklanamaz. Tasarımın görünümünü CSS sınıfını
(`wf-segment` + `is-on`) kullanarak alırız, davranışı kendimiz yazarız. Vendor değişmez (B3'ün
`wf-input`'u doğrudan kullanması gibi). Kit'ten `Status` devreye girer; ilerleme çubuğu ve galeri
ızgarası için kit'te sınıf yok — yerleşim stilleri B3/B4 gibi inline.

## Testler

Mevcut 90'dan tek-foto yoluna bağlı olanlar (`test_photo_usecases`, `test_photo_routes`'un bir
kısmı, `test_photo_runner`) yeni sözleşmeye **taşınır**, kalanlar bozulmaz. Yeni: parse (~6) ·
policy (~4) · batch döngüsü — sıra/numaralama, atla-devam, üst üste 3, infra, durdurma, boş liste
(~8) · runner report/stop (~3) · `list_photos` (~3) · generator node 4 (~3) · route'lar (~7).
`test_workflow_asset` büyür: gönderilen grafikte node **4** de doğrulanır (ImpactWildcardProcessor +
çift alan) — artık ona da yazıyoruz. Hepsi fake port + sync spawn; ComfyUI/Drive/GPU/ağ yok.
Hedef ~115.

## Bilinçli yoklar

- Kırmızı kare kartları + Tekrar dene (artboard 05) → **B7**
- "Kaldığı yerden devam et" kartı (artboard 06) → **B7**
- `prompts.json` / `runs.json` — form yenilenince boşalır → **B6**
- ComfyUI `/interrupt` (anında durdurma) — nazik durdurma yeterli
- Seed kontrolü UI'da — hep rastgele
- Prompt başına negatif — tek ortak kutu

## Doğrulama (Colab, T4)

1. Proje aç → 3 prompt'luk `PROMPTS = [...]` yapıştır, varyant 2 → **Üret** → sayaç `n/6` ilerler,
   galeri canlı dolar, sıra `start_a start_b (start+1)_a …`.
2. Bitince: `bitti — 6/6`, Drive'da 6 dosya, numaralar eskilerin devamı.
3. Tekrar Üret (1 prompt × 1 varyant) → yeni numara sona ekli; üstüne yazma yok.
4. Üretim sürerken **Durdur** → süren kare biter, `durduruldu — n/6`, form geri gelir.
5. Sayfa yenile (üretim sürerken) → galeri dolu, ilerleme bloğu geri gelir; form boş (bilinçli).
6. (Negatif) ComfyUI'yi öldür → sıradaki karede hata; üst üste 3'te `error` + ham metin.
