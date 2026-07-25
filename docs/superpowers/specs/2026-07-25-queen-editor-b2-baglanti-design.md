# Queen Editor — Bölüm 2: Bağlantı (tasarım)

**Tarih:** 2026-07-25 · **Durum:** onaylandı, implementasyon planı bekliyor
**Şemsiye tasarım:** [2026-07-24-queen-editor-v1-design.md](2026-07-24-queen-editor-v1-design.md)
**Yol haritası:** [2026-07-24-queen-editor-roadmap.md](../plans/2026-07-24-queen-editor-roadmap.md) — Bölüm 2
**Notebook standardı:** [collab-toolbox/NOTEBOOK-STANDARD.md](../../../collab-toolbox/NOTEBOOK-STANDARD.md)

## Amaç

Yol haritasının ikinci görünmez altyapı sınavı: **sunucu ayağa kalkıyor mu, tünel açılıyor mu, ve açılan sayfa sunucuyla gerçekten konuşuyor mu.** Bölüm 1 klonu kanıtladı; bu bölüm klonun üstüne servis + tünel + frontend↔backend turunu ekler. Arayüz repoya derlenmiş gelir (ComfyUI deseni), Colab derlemez. Gerçek özellik (proje, foto) yok — kanıt tek bir sağlık isteğiyle verilir.

## Kapsam

Bölüm 2 bittiğinde çalışan şey:

1. Colab Run all → repo klonlanır (derlenmiş `frontend/dist` ile birlikte), Flask arka planda başlar, cloudflared linki basılır. Colab'da npm/build yok.
2. Linke girilir → koyu temalı sayfa açılır (tasarımın `styles.css`'i).
3. Sayfa yüklenirken `GET /api/health` çağırır; cevap gelirse **"sunucuya bağlı ✓"**, gelmezse **"sunucuya bağlanılamadı ✗"** gösterir.
4. Sayfa akıcı — donma/kasma yok (tarayıcıda derleme yok, hazır dist servis edilir).
5. `pytest backend/` lokalde geçer (ilk otomatik test).

## Kapsam dışı (sonraki bölümlere)

Drive mount, proje oluşturma/listeleme, prompt paneli, galeri, ComfyUI, model indirme, `features/` klasörü, `kit.jsx` bileşenleri. Health ucu yalnız bağlantı kanıtı — iş mantığı taşımaz.

## Kararlar

| Karar | Gerekçe |
|---|---|
| Sayfa **tasarımın koyu temasıyla** (`vendor/styles.css`) + "sunucuya bağlı ✓" | Kullanıcı kararı. Hem frontend↔backend turunu hem tasarımın (derlenmiş CSS) doğru servis edildiğini tek adımda kanıtlar. `kit.jsx` bileşenleri Bölüm 3'e — henüz gerçek bileşen yok. |
| Arayüz repoya **derlenmiş gelir** (`frontend/dist` commit'lenir); Colab'da npm/build **çalışmaz** — ComfyUI deseni | Kullanıcı kararı ("ComfyUI'yi takip edelim"). ComfyUI frontend'i ayrı repoda derlenip ship ediliyor, Colab'da npm çalışmıyor; biz de aynısını yapıyoruz. Derleme geliştiricide (`npm run build`), `dist/` + `package-lock.json` commit'lenir, `node_modules/` commit'lenmez. Bedel: UI değişince yeniden derleyip commit etmek gerekir (bayat-dist riski, kabul edildi). |
| **Tek origin**: Flask hem `dist/`'i (`/`) hem `/api`'yi servis eder | Kullanıcı kararı. Tek tünel, tek adres, **CORS yok**; `api.js` göreli `/api` çağırır. Ayrı Vite dev sunucusu iki tünel + CORS gerektirirdi — Bölüm 2 için fazla parça. |
| `GET /api/health` **`web/` altyapı katında** (`web/health.py`), feature değil | Kullanıcı kararı. Sağlık ucu bir alan (domain) özelliği değil, altyapı. `features/` klasörü Bölüm 3'te projects gelince ilk kez açılır — boş/yarım feature klasörü olmaz. |
| Health gövdesi **`{"status": "ok"}`** — minimal | Bağlantı kanıtı için yeterli. Çalışan commit'i doğrulamak istenirse ileride `commit` alanı eklenir (Bölüm 2'de gerekmiyor). |
| **`CODE-STANDARD.md` bu bölümde yazılır** | İlk kod burada doğuyor; standart ilk kodla birlikte konur ki sonraki bölümler ona göre yazılsın. Hedef feature-first yapıyı (servis/feature, katman yönü, vendor dokunulmazlığı, dil ayrımı) tarif eder; `features/` fiilen Bölüm 3'te dolar. |
| İlk **pytest** burada başlar (`test_health.py`) | Backend'in ilk `.py`'si burada; sağlık ucu Flask test client'la doğrulanır. Otomatik test yüzeyi bu bölümde açılır (Bölüm 1'de yoktu). |
| Notebook: klon (dist doğrulanır) → **Flask** → cloudflared, hücre `tail -f` ile açık | `manual.ipynb`'nin kanıtlı tünel deseni. Colab yalnız klonlayıp servis eder; node/npm/build yok. Klon hücresi `frontend/dist/index.html`'in geldiğini fail-loud doğrular (unutulan rebuild+commit boş sayfa değil, burada patlar). Hücre biterse Colab runtime'ı idle sayıp tüneli öldürür → canlı log ile açık tutulur. |

## Mimari

### Yapı (bu bölümde ilk kez)

```
queen-editor/
├── app.ipynb                 BÜYÜR: klon (Bölüm 1) + Flask + cloudflared (dist repoda hazır)
├── CODE-STANDARD.md          katman kuralı · servis/feature sınırları · vendor · dil
├── backend/
│   ├── main.py               composition root: create_app() çağırır, sunucuyu başlatır
│   ├── config.py             HOST, PORT, DIST_DIR
│   ├── requirements.txt      flask, pytest
│   ├── pytest.ini
│   ├── web/
│   │   ├── app.py            create_app(): dist statik servis + /api blueprint kaydı
│   │   └── health.py         GET /api/health → {"status": "ok"}
│   └── tests/
│       └── test_health.py    Flask test client ile /api/health
└── frontend/
    ├── package.json
    ├── package-lock.json     geliştirici derlemesi için commit'lenir
    ├── dist/                 DERLENMİŞ arayüz — commit'lenir (Colab bunu servis eder)
    ├── vite.config.js        build.outDir = "dist", base = "./"
    ├── index.html
    └── src/
        ├── main.jsx          React app'i #root'a mount eder
        ├── App.jsx           mount'ta health çeker; durum: kontrol ediliyor / bağlı ✓ / bağlanılamadı ✗
        ├── vendor/
        │   └── styles.css    tasarımdan birebir (koyu tema), elle düzenlenmez
        └── shared/
            └── api.js         tek fetch sarmalayıcı → getHealth()
```

Bağımlılık yönü şemsiye kuraldaki gibi: `web/app.py` (presentation/altyapı) → `web/health.py`; `main.py` composition root. Frontend: `App.jsx` (presentation) → `shared/api.js` (data erişimi). Health'in domain/data'sı yok — saf altyapı.

### Tek origin servis

Flask `create_app()`:
- `GET /api/health` → `{"status": "ok"}` (blueprint, `web/health.py`).
- `/` ve statik varlıklar → `frontend/dist/` (Vite çıktısı). `index.html` kökte, JS/CSS `dist/assets/` altında.
- Bilinmeyen yol → `index.html` (tek sayfa; Bölüm 2'de tek ekran ama desen kurulur).

`api.js` göreli `/api/health` çağırır → aynı origin, CORS yok.

### Notebook akışı (Bölüm 1'in üstüne)

| Adım | İçerik |
|---|---|
| CONFIG | Bölüm 1 (token Secrets, BRANCH, REPO, CLONE_DIR) + `APP_PORT = 8000` eklenir. |
| Klon | Bölüm 1 (sil-yeniden, `--depth 1`). |
| Sunucu | `python -m backend.main` arka planda (dist repodan hazır gelir); 90 sn içinde `/api/health` cevap vermezse log'un son 30 satırı + fail-loud. |
| Tünel | cloudflared `http://127.0.0.1:APP_PORT` → link basılır; hücre `tail -f` ile açık kalır. |

## Test

`pytest backend/`:
- `test_health.py`: `create_app().test_client().get("/api/health")` → 200, gövde `{"status": "ok"}`.

ComfyUI/Drive/tünel gerektirmez; saf Flask test client.

## Doğrulama (kullanıcı, Colab)

1. `app.ipynb`'yi Colab'a yükle (Secrets'ta `GITHUB_TOKEN` zaten var) → **Run all**.
2. Repo klonlanır (dist ile), Flask kalkar, cloudflared linki basılır (~1 dk; npm/build/model indirmesi yok).
3. Linke gir → koyu temalı sayfa, **"sunucuya bağlı ✓"**.
4. Sayfa akıcı; yenile → yine bağlı.
5. (Negatif) Flask'ı durdurup sayfayı yenile → **"sunucuya bağlanılamadı ✗"** (frontend hata durumunu gösteriyor).
6. (Geliştirici, lokal) `pytest backend/ -v` → `test_health` geçer.

## Riskler

- **Bayat dist** — arayüz değişip yeniden derlenip commit'lenmezse Colab eski UI'yi servis eder. Geliştirici disiplini; klon hücresi dist'in *varlığını* doğrular ama güncelliğini değil. (ComfyUI-deseninin kabul edilen bedeli; Bölüm 1'deki "build Colab'da" kararından bilinçli sapma.)
- **Colab'da Flask/servis** — bu bölümün asıl sınadığı şey artık build değil, tek origin servis + tünel + frontend↔backend turu. `/api/health` 90 sn'de cevap vermezse fail-loud.
- **Tünel URL'i herkese açık** — v1 kararı, değişmedi.
