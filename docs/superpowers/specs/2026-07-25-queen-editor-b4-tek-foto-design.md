# Queen Editor — Bölüm 4: Tek foto (tasarım)

**Tarih:** 2026-07-25 · **Durum:** onaylandı, implementasyon planı bekliyor
**Şemsiye tasarım:** [2026-07-24-queen-editor-v1-design.md](2026-07-24-queen-editor-v1-design.md) · **Yol haritası:** [2026-07-24-queen-editor-roadmap.md](../plans/2026-07-24-queen-editor-roadmap.md)
**Bağımsızlık sınırı:** [2026-07-25-queen-editor-bagimsizlik-design.md](2026-07-25-queen-editor-bagimsizlik-design.md)

## Amaç

ComfyUI ilk kez devreye girer: projeyi aç → tek prompt kutusu → **Üret** → bir foto
`queenEditor/<proje>/0_a.png` olarak Drive'a düşer ve ekranda görünür. Kanıtladığı riskler:
modeller iner, ComfyUI headless kalkar, grafiğe prompt/seed enjekte edilir, foto
ComfyUI → Drive → tarayıcı yolunu döner.

İkinci iş: üretim mimarisinin iskeletini **video geleceğini bilerek** kurmak. Ölçüt kullanıcının
koyduğu **değişiklik yerelliği**: foto'ya dokununca yalnız foto dosyaları değişir; video ile ortak
hiçbir çalıştırıcıya/koda kilitlenilmez. Tekrar kod yazmak kabul, bağımlılık kabul değil.

## Bağlam

- Bölüm 3 kanıtladı: Flask + tünel + Drive yaz/oku + Projeler ekranı. Kart henüz tıklanamaz.
- Üretim davranışı `nova-3dcg/api.ipynb`'de kanıtlı (kod devralınmaz, bilgi devralınır —
  bağımsızlık spec'i): `POST /prompt` → `/history` yoklama → `/view` · çift-alan prompt enjeksiyonu
  (Impact Pack #483: sunucunun `wildcard_text` mi `populated_text` mi okuduğu sürüme göre değişir —
  ikisine birden yazılır) · seed'i bizim üretmemiz (rgthree Seed `-1`'i frontend'de çözer, API'de
  frontend yok) · `type=="output"` filtresi + **tam 1 çıktı** sözleşmesi · altyapı hatası ↔ kare
  hatası ayrımı.
- Kurulum bilgisi (bilgi olarak devralınır): 8 custom node paketi · 5 model (~7.5 GiB; 2'si Civitai
  login-gated, 3'ü açık) · ComfyUI headless, port 8188 · donanım **T4**.
- Grafik: nova-3dcg'nin Export (API)'ı. Bağımsızlık spec'i kopyayı bu bölüme erteledi.

## Kararlar

| Karar | Gerekçe |
|---|---|
| Feature adı **`photo_generation`** (backend + frontend), `generation` değil | Kullanıcı kararı. Video kendi feature'ı olacak (`video_generation`); jenerik adı foto işgal etmesin, o gün yeniden adlandırma çıkmasın. Umbrella'ya revizyon notu düşülür. |
| **`services/comfy` yalnız taşıma:** `client.py` (gönder · bekle · çıktıyı al) + `errors.py` (hata metni ayrıştır → `infra` bayrağı). Node id'si, alan adı, medya bilgisi **yok** | KISS + SoC: taşıma ComfyUI protokolü değişmedikçe değişmez — `services/drive` ile aynı sınıfta kararlı altyapı. Foto'ya özgü hiçbir değişiklik bu dosyalara dokunmaz; video aynı client'ı kullanır. |
| **Grafik bilgisi feature'ın `data/`'sında:** `comfy_photo_generator.py` node id'lerini (`3`/`4`/`40`) ve çift-alan yazımını bilen TEK yer | CODE-STANDARD: "şemayı bilen tek yer `data/`" — node id'si de şemadır. Yeni export'ta id değişirse 1 dosya değişir. |
| **`runner.py` feature'ın içinde** (thread + iş durumu), merkezi iş servisi **yok** | Kullanıcı kararı ("bakım = bağımlılık: foto'da değişiklik beni kitlemesin, 15 dosya güncelletmesin"). Ortak çalıştırıcı tam o kilidi üretirdi. Video kendi runner kopyasını yazar — `feature ↛ feature` yasağı bu tercihi zaten zorluyor. Umbrella'nın orijinal yapısına dönüş; merkezi `services/jobs` alternatifi bilinçli elendi. |
| Genel, kararlı yetenekler **`services/` altında gruplanır** — Drive erişimi için `drive/storage.py` **büyür** (`write_bytes` · `read_bytes` · `list_files`), yeni bir kova (`core/` vb.) **açılmaz** | Kullanıcı sorusu üzerine karar. `services/`'in tanımı zaten "genel, feature bilmez, servis→servis yok" — aranan kova bu. `core/` + `services/` yan yana "hangisi nereye" testi olmayan iki kova olur; testi olmayan kova çöplüğe döner. Ham oku/yaz tek yerde, şema (`N_a.png`) feature'ın `data/`'sında kalır. |
| Üretim **arka plan thread'inde**, `POST .../generate` → `202` + UI **`GET /api/status`'u yoklar** | Foto 30-90 sn: senkron istek tünelde/tarayıcıda düşer, UI donmuş görünür, Bölüm 5'te çöpe giderdi. Umbrella zaten "üretim backend thread'inde yaşar, UI durumu sorar" diyor. Sekme kapansa da iş sürer. |
| Üretim sürerken ikinci Üret → **`409`** + Türkçe mesaj | Tek GPU, tek işçi, tek iş. Buton üretim sırasında zaten pasif; 409 yarış durumunun sigortası. |
| `GET /api/status` üretilen **dosya adını taşır** | Sayfa yenilenince foto kaybolmasın: ekran fotoyu status'tan geri yükler. Galeri/listeleme yok (Bölüm 5). Runtime ölürse durum `idle`'a döner — kabul; kalıcılık Bölüm 6-7. |
| Hata: hata kartı **yok**; sunucunun **ham hata metni** kırmızı gösterilir | Yol haritası hata kartını Bölüm 7'ye koydu. Repo kuralı: sebep uydurulmaz — `errors.py`'nin ayrıştırdığı gerçek metin, Projeler ekranındaki hata deseniyle aynı biçimde. |
| **Durdur yok** | Tek foto ~1 dk; artboard 04'ün Durdur'u Bölüm 5'in ekranıyla gelir. |
| Numaralandırma **bu bölümde başlar:** klasördeki en büyük numara + 1, tek foto `N_a.png` | Umbrella kuralı; ikinci Üret `1_a.png` üretir, üstüne yazma imkânsız. `photo_store.py` bilir. |
| Seed **her üretimde rastgele**, sunucu log'una yazılır | nova-3dcg ile aynı. Export'taki `-1` asla sunucuya gitmez. |
| **Negatif kutusu yok** — export'un içindeki negatif geçerli | Yol haritası Bölüm 4 kapsamı ("tek prompt kutusu"). Negatif alanına dokunulmaz; Bölüm 5 ekler. |
| Grafik kopyası **`queen-editor/workflow_api.json`** — nova-3dcg'nin export'unun repoya alınmış kendi kopyamız; Drive'dan okunmaz | Bağımsızlık spec'inin bu bölüme ertelediği iş. Ayar değişikliği = yeni export → commit (tek kaynak). Yükleyici API formatını doğrular (`nodes` anahtarı görülürse "Export (API) gerekir" fail-loud). |
| Kurulum hücreleri (custom node döngüsü · model listesi · `fetch` · `civitai_probe` · `check_binary` · 401 dahil hata metinleri · ComfyUI başlatma) `nova-3dcg`'den **birebir kopyalanır** | Kullanıcı kararı: "collab-toolbox'un desenleri gayet iyi çalışıyor, hata ayıklamasına kadar birebir kopyala — Amerika'yı yeniden keşfetmeye gerek yok." Bağımsızlık kuralıyla çelişmez: yasak olan onların hücresini **çalıştırmak/import etmek** ya da ortak dosya okumak; kendi kopyamız üzerinde çalışmak kuralın tam içinde. Kopya = bakım bedeli iki notebook'a bölünür (bağımsızlığın bilinen fiyatı). |
| Modeller **her oturumda yeniden iner** (Drive cache yok) — nova-3dcg'nin deseni | Aynı kullanıcı kararı: foto pipeline'ının kanıtlı davranışı bu. Bedeli her Run all'da ~10-15 dk; mmaudio'nun Drive-cache deseni bu boru hattına taşınmıyor. |
| **Tek sapma: Civitai cookie'sinin değeri Colab Secrets'tan** (`CIVITAI_COOKIE`) — makinenin geri kalanı birebir | `app.ipynb` git'e giren bir dosya; CONFIG'e yapıştırılan Civitai oturum JWT'si repoya yazılmış olurdu. Bölüm 1'de `GITHUB_TOKEN` için verilen kararın aynısı, tek satırlık fark (`COOKIE_VALUE = userdata.get("CIVITAI_COOKIE")`); `assert len(...) > 200` ve 401 davranışı kopyadaki gibi kalır. |
| ComfyUI adresi `config.COMFY_URL`, **`QE_COMFY_URL`** ile ezilebilir | Drive kökü deseni: değer tek yerde, test sahte URL verir. |
| Frontend yönlendirme: **`/projects/<ad>` yolu + pushState**, react-router yok | KISS: ~15 satır; SPA fallback B2'de hazır ve testli. Yenile → aynı projede kalır. |
| Bölüm 4 proje ekranı **bilinçli iskelet:** başlık (geri + proje adı) · tek prompt kutusu · Üret · durum satırı · üretilen foto. Artboard 03 düzeni değil | Yol haritası kapsamı. Bölüm 5 bu ekranın içini artboard 03'le (liste/negatif/varyant/galeri) değiştirir; iskelet header/yönlendirme aynı kalır. |
| Donanım **T4 GPU** — notebook başlığına ve README'ye yazılır | SDXL sınıfı, nova-3dcg ile aynı. Şimdiye kadar CPU yetiyordu; Run all artık GPU runtime ister. |

## Mimari

### Backend

```
queen-editor/
├── workflow_api.json                      grafiğin repo kopyası (klonla gelir; umbrella'daki yer)
└── backend/
    ├── config.py                          + COMFY_URL (env QE_COMFY_URL) + WORKFLOW_PATH
    ├── services/
    │   ├── drive/                         storage.py BÜYÜR: + write_bytes · read_bytes · list_files
    │   │                                  (şema bilmez; N_a.png adını photo_store kurar)
    │   └── comfy/
    │       ├── client.py                  ComfyClient(base_url): submit(workflow) -> prompt_id ·
    │       │                              wait(prompt_id, timeout) -> history · fetch_output(history) -> bytes
    │       │                              (tam-1-çıktı sözleşmesi burada: type=="output" filtresi)
    │       └── errors.py                  ComfyExecutionError(text, traceback_text, infra) +
    │                                      describe(status) — hata metnini ayrıştırır, sebep uydurmaz
    └── features/photo_generation/
        ├── domain/
        │   ├── ports.py                   PhotoGenerator (generate(prompt, seed) -> bytes) ·
        │   │                              PhotoStore (next_number() · save(number, letter, data) -> filename)
        │   └── usecases/
        │       ├── start_generation.py    meşgulse reddet → numara + seed üret → runner'a bir adım ver
        │       └── get_status.py          runner durumunu okur (saf çeviri)
        ├── data/
        │   ├── comfy_photo_generator.py   grafiği yükle+doğrula · node 3/4 çift-alan · node 40 seed ·
        │   │                              client'ı çağır → bytes  (grafiği bilen TEK yer)
        │   └── photo_store.py             N_a.png şeması + "en büyük numara+1"  (adları bilen TEK yer)
        ├── runner.py                      tek işçi thread + iş kaydı (durum · dosya adı · hata) — fotonun malı
        └── presentation/routes.py         POST /api/projects/<ad>/generate → 202 | 400 | 404 | 409
                                           GET /api/status · GET /photos/<ad>/<dosya>
```

Video günü: `features/video_generation/` kendi runner/policy kopyasıyla açılır, aynı
`services/comfy/client.py`'yi kullanır. Foto değişiklikleri videoya, video değişiklikleri fotoya
dokunmaz. (Bölüm 4'te `policy.py` yok — tek adımlı işte politika kararı doğmaz; Bölüm 5'te
"atla / üst üste 3'te dur" ile birlikte gelir.)

### Uç sözleşmesi

| Uç | Yanıt |
|---|---|
| `POST /api/projects/<ad>/generate` `{"prompt": "…"}` | `202 {"job": "running"}` · `400 {"error": "Prompt boş olamaz."}` · `404 {"error": "Proje yok: <ad>"}` · `409 {"error": "Zaten bir üretim sürüyor."}` |
| `GET /api/status` | `200 {"status": "idle"}` · `{"status": "running", "project": "<ad>"}` · `{"status": "done", "project": "<ad>", "file": "0_a.png"}` · `{"status": "error", "project": "<ad>", "error": "<ham metin>"}` |
| `GET /photos/<ad>/<dosya>` | Drive'daki png; yoksa 404. `send_from_directory` — yol kaçışı Flask'ta hazır. |

### Akış

Üret → `start_generation`: proje var mı, prompt dolu mu, işçi boş mu → `photo_store.next_number()`
(diskteki en büyük + 1) → rastgele seed (log'a) → runner'a tek adım: `generator.generate(prompt,
seed)` → bytes → `store.save(n, "a", bytes)` → `202`. UI 2 sn'de bir `GET /api/status`;
`done` gelince `GET /photos/<ad>/<dosya>` ile fotoyu gösterir.

### Frontend

```
frontend/src/
├── App.jsx                        yol tabanlı iki ekran: "/" → Projeler, "/projects/<ad>" → Proje
├── shared/router.js               path oku · git(path) (pushState) · popstate dinle (~15 satır)
├── features/projects/             (mevcut; ProjectCard tıklanır olur → git("/projects/<ad>"))
└── features/photo_generation/
    ├── ProjectScreen.jsx          header (← Projeler · proje adı) + panel + foto alanı
    ├── GeneratePanel.jsx          prompt textarea · Üret (boşken/üretimde pasif) · durum satırı ·
    │                              hata metni (kırmızı, mono — Projeler'deki desen)
    └── useGeneration.js           status yoklama (2 sn; idle/done'da durur) · generate(prompt)
```

Kart tıklaması Bölüm 3'ün bilinçli borcuydu: `ProjectCard`'a `onClick` + `cursor: pointer` gelir.

### Notebook (`app.ipynb`)

Mevcut akışa ComfyUI bölümü eklenir; sıra: CONFIG → mount → klon → **custom node'lar → modeller →
ComfyUI başlat** → Flask + tünel. Kurulum hücreleri `nova-3dcg/api.ipynb`'den **birebir kopya**
(kopya bağımlılık değil; yasak olan onların hücresini çalıştırmak):

- **CONFIG:** `CIVITAI_COOKIE = userdata.get(...)` (Secrets; fail-loud assert, Bölüm 1 deseni).
  T4 kontrolü: GPU yoksa hücre patlar ("Runtime → Change runtime type → T4 GPU").
- **Custom node'lar:** 8 paket, `--recurse-submodules` klon döngüsü.
- **Modeller:** 5 dosya (~7.5 GiB): 2 Civitai (cookie header + probe → indir), 3 açık;
  `check_binary` doğrulaması (HTML hata sayfası ~KB'lık dosya bırakır — fail-loud).
- **ComfyUI:** headless başlat (port 8188), 90 sn `/system_stats` bekleme, log kuyruğu basılır.
- **Serve hücresi:** Flask'a `QE_COMFY_URL` de geçirilir; klon doğrulaması `workflow_api.json`'ın
  varlığını da kontrol eder.

### Test

pytest (ComfyUI'sız, Drive'sız): `client.py` sahte HTTP ile (submit hata gövdesi · tam-1-çıktı
ihlali) · `errors.py` (infra ayrımı örnek history'lerle) · `comfy_photo_generator` sahte client'la
(node 3/4'e çift alan, 40'a seed yazıldı mı; UI-format grafikte fail) · `photo_store` `tmp_path`
(boş klasör → 0; `7_c.png` varken → 8) · `runner` sahte adımla (running → done · hata → error ·
meşgulken reddet) · route'lar (202/400/404/409 · status geçişleri · foto servisi + 404). Bölüm 3'ün
42 testi bozulmaz.

## Doğrulama (kullanıcı, Colab — T4)

1. Run all: Secrets'ta `GITHUB_TOKEN` + `CIVITAI_COOKIE` → node'lar kurulur, modeller iner,
   ComfyUI kalkar, Flask + tünel linki.
2. Projeler → karta tıkla → proje ekranı açılır (URL `/projects/<ad>`; yenile → aynı ekran).
3. Prompt yaz → **Üret** → durum "üretiliyor…" → ~1-2 dk → foto ekranda; Drive'da
   `queenEditor/<ad>/0_a.png`.
4. Üretim sırasında sekmeyi kapat/aç → durum doğru sürer; bitince foto görünür.
5. İkinci Üret → `1_a.png` — üstüne yazma yok.
6. Boş prompt'la Üret pasif; üretim sürerken ikinci istek 409 mesajı gösterir.
7. (Negatif) ComfyUI'ı öldür → Üret → kırmızı ham hata metni.
8. (Geliştirici) `pytest` → tümü geçer.

## Riskler

- **İlk kurulum ~10-15 dk** (model indirme) — her oturumda tekrarlanır; bilinçli (model cache
  kapsam dışı).
- **Civitai cookie'si ~30 günde ölür** → model indirme 401 verir; hücre ham cevabı basar, kullanıcı
  Secrets'taki değeri yeniler. Sebep uydurulmaz (401'in başka sebepleri de olur).
- **Export eskimesi:** ComfyUI'da ayar değişirse `queen-editor/workflow_api.json` yeniden export
  edilip commit'lenmeli — bağımsızlık spec'indeki bilinen risk.
- **T4 + iki ComfyUI:** nova-3dcg notebook'u ile aynı oturumda çalıştırılamaz (bellek); ayrı
  oturumlar — bağımsızlık spec'inde yazılı sınır.

## Kapsam dışı (Bölüm 4)

Çoklu prompt / varyant / galeri ızgarası (B5) · negatif kutusu (B5) · Durdur (B5) · prompt kaydı,
`prompts.json`/`runs.json` (B6) · hata kartı, Tekrar dene, kaldığı yerden devam (B7) · `policy.py`
(B5) · video (ayrı feature, ileride) · model cache.
