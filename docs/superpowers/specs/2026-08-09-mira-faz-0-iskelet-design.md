# Mira — Faz 0: İskelet (Madde 1)

**Tarih:** 2026-08-09 · **Branch:** `feat/queen-editor-v2`
**Üst belgeler:** [tasarım dokümanı v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md)

Faz 0 tek maddelidir ama en çok karar taşıyan yerdir: burada verilen her karar sonraki 31 maddeyi
bağlar. Ürettiği görünür şey azdır — tasarımın zemin renginde boş bir sayfa — asıl çıktısı **zemin**dir.

**Kapsam:** klasör düzeni · Flask iskeleti · React iskeleti · açılış ve derleme · test koşum düzeni ·
CSS temeli · `mira/FOUNDATION.md` · `mira/CODE-STANDARD.md` · `CLAUDE.md` bölümü.
**Kapsam dışı:** hiçbir ekran, hiçbir veri, hiçbir uç nokta (sağlık yoklaması hariç).

---

## 1 · Klasör düzeni

queen-editor'ün düzeni taklit edilir; farklar tek tek gerekçelidir.

```
mira/
  FOUNDATION.md
  CODE-STANDARD.md
  README.md
  main.py                     kompozisyon kökü — tek çalıştırma noktası
  backend/
    __init__.py
    config.py                 yollar, port, kök dizin, model adı
    web/
      __init__.py
      app.py                  create_app: blueprint kaydı + dist servisi
      health.py               /api/health
    services/__init__.py      (Faz 1'de store/, Faz 6'da xai/ dolar)
    features/__init__.py      (Faz 1'de workspace/ dolar)
    tests/
      test_health.py
      test_static.py
  frontend/
    package.json
    vite.config.js
    index.html
    src/
      main.jsx
      App.jsx
      test-setup.js
      shared/
        app.css               CSS temeli — renkler, tipografi, odak, kaydırma
      features/               (Faz 2'den itibaren dolar)
```

**`backend/features/` ve `backend/services/` boş `__init__.py` ile başlar.** queen-editor'ün kuralı
"gerçek bir şey olmadan klasör açılmaz" der; buradaki iki paket dosyası klasör değil, ithal edilebilir
paketin kendisidir ve Faz 1 onlara ilk gerçek içeriği koyar.

## 2 · Çalıştırma ve derleme

**İki mod vardır.**

| Mod | Komut | Ne olur |
|---|---|---|
| Kullanım | `python mira/main.py` | Flask `frontend/dist/`'i servis eder, tek port |
| Geliştirme | `npm run dev` + `python mira/main.py` | Vite kendi sunucusunda çalışır, `/api/*` isteklerini Flask'a proxy'ler |

Geliştirme modundaki proxy queen-editor'de **yok**, burada **var**. Gerekçesi: queen-editor'ün ön yüzü
Colab'a önceden derlenmiş gider ve geliştirici arada bir derler; Mira yerelde çalışıyor ve arayüzü 20
maddede sürekli değişecek. Her değişiklikte tam derleme beklemek koşuyu yavaşlatır. Proxy dört satırdır
ve üretim yolunu hiç etkilemez.

**`frontend/dist/` git'e girmez.** queen-editor onu commit ediyor çünkü Colab npm çalıştırmıyor; Mira'da
derleyen ile çalıştıran aynı makine, o yüzden `dist/` `.gitignore`'a girer. Aynı gerekçeyle
`node_modules/` de.

**Port `8100`.** queen-editor `8000` kullanıyor. İkisi de artık yerelde çalışabildiği için farklı port
gerekiyor; aynı anda ikisi açıkken çakışma olmasın.

## 3 · Flask iskeleti

`create_app(dist_dir, blueprints=())` — app factory. Kurallar:

- **Statik servis bizim rotalarımızdadır** (`static_folder=None`): `/` → `index.html`; başka her yol →
  dosya varsa dosya, yoksa `index.html` (SPA geri düşüşü).
- `/api/health` daha özel bir kural olduğu için SPA geri düşüşünden **önce** eşleşir.
- **`web/` hiçbir feature ithal etmez.** Blueprint'ler dışarıdan verilir; somut sınıflar yalnız
  `main.py`'de bağlanır. Bu, `presentation → domain ← data → services` yönünü ilk günden korur.

`config.py` tek karar noktasıdır:

| Ayar | Değer / kaynak |
|---|---|
| `DIST_DIR` | `mira/frontend/dist` |
| `HOST` / `PORT` | `127.0.0.1` / `8100` |
| `MIRA_ROOT` | ortam değişkeni; yoksa kullanıcının ev dizini altında `Mira` |
| `XAI_API_KEY` | ortam değişkeni (Faz 6'da kullanılır, burada yalnız okunur) |
| `XAI_MODEL` | ayar satırı (Faz 6'da doğrulanacak) |

Kök dizin **repo dışındadır**: kullanıcının verisi kaynak ağacında durmaz, `git status` onu hiç
görmez.

## 4 · React iskeleti

`index.html` → `<div id="root">` + `src/main.jsx`. `App.jsx` Faz 0'da tek iş yapar: tasarımın zeminini
kaplayan boş bir çerçeve çizer. Ekran yok, veri yok, istek yok.

`lang="en"` — arayüz dili İngilizce.

Yazı tipleri Google Fonts'tan gelir: **Newsreader** (başlık), **DM Sans** (gövde/arayüz), **DM Mono**
(etiket, sayı, zaman). Uygulama zaten Grok'a gitmek için internete muhtaç, o yüzden uzak yazı tipi ek
bir kısıt getirmiyor.

## 5 · CSS temeli

`shared/app.css` tasarımın 6. bölümünü koda çevirir. Faz 0'da yalnız **temel** girer; bileşen stilleri
kendi maddelerinde yazılır.

**Renkler** (CSS değişkeni olarak, tek tanım yeri):

| Değişken | Değer | Nerede |
|---|---|---|
| `--canvas` | `#F7F5F1` | ana zemin |
| `--sidebar` | `#EFEBE4` | sol sütun |
| `--surface` | `#FFFDFA` | kart, panel, composer |
| `--accent` | `#B5623C` | tek vurgu — yalnız birincil eylem |
| `--accent-strong` | `#8F4A2C` | vurgunun üzerine gelme hâli |
| `--ink` | `#22201D` | ana metin |
| `--muted` | `#8B8378` | ikincil metin |
| `--line` | `#E2DCD2` | çerçeve ve ayraç |

**Tek vurgu kuralı:** `--accent` birincil eylemi işaretler ve başka hiçbir şeyi. Bir maddede ikinci bir
yerde kullanılmak istenirse o maddenin spec'i gerekçesini yazar.

**Yarıçaplar:** kontrol 8px · kart 12–14px · hap 20px.

**Odak:** `:focus-visible` → `2px solid var(--accent)`, `outline-offset: 2px`, `border-radius: 8px`.
Uygulama genelinde tek kural; hiçbir madde kendi odak stilini yazmaz.

**Hareket:** yalnız opaklık geçişleri (180–220ms) ve rayın genişlik geçişi (220ms). Yerleşmiş bir
elemanı yana kaydıran hiçbir animasyon yoktur. Faz 0'da `riseIn`, `blink`, `spin` ve `slideIn`
kare-dizileri tanımlanır — sonraki maddeler bunları kullanır, yenisini icat etmez.

**Kaydırma çubuğu:** 10px, `#DED7CD` başlık, 8px yarıçap.

## 6 · Testler

**Arka uç** — `pytest`, `mira/` dizininden koşar:

- `test_health.py`: `/api/health` 200 ve gövdesinde uygulamanın ayakta olduğu bilgisi.
- `test_static.py`: `/` `index.html` döndürür · var olan bir varlık dosyası olduğu gibi döner · bilinmeyen
  bir yol (`/projects/x`) `index.html`'e düşer · `/api/health` SPA geri düşüşüne **takılmaz**.

Bu üçüncü test bir kaza için var: statik rota `/api/*`'i yutarsa bütün uç noktalar sessizce
`index.html` döndürür ve hata Faz 6'ya kadar fark edilmez.

**Ön yüz** — `npm test` (vitest + jsdom), `mira/frontend/` dizininden:

- `App.test.jsx`: kabuk hata vermeden render oluyor.

Test dosyaları kaynağının yanında (`<ad>.test.jsx`), hiçbir yerden ithal edilmiyor, bu yüzden
derlemeye girmiyorlar. Ağ ve saat testlerde sahtedir; hiçbir test gerçek saniye beklemez.

## 7 · `mira/FOUNDATION.md`

queen-editor'ünkinden türetilir. **İlkeler aynen geçer** (kullanıcının emeği kutsaldır · gerçek diskte
durur · correctness > simplicity > generality > performance · kod yeniden üretilebilirlik için
yazılır). **Kararlar değişir:**

| # | Karar | Gerekçe |
|---|---|---|
| 1 | Uygulama **yerel makinede** çalışır | Motor uzak bir API; GPU gerekmiyor, Colab'ın verdiği tek şey Mira'ya lazım değil |
| 2 | Arka uç sync **Flask**, ön yüz **React 18** (Vite) | Arka uç ince: dosya işlemleri + bir API çağrısı + akış |
| 3 | Ön yüz **yerelde derlenir**, `dist/` git'e girmez | Derleyen ile çalıştıran aynı makine |
| 4 | Ön yüz görüntüdür, kural arka uçtadır | Kurallar tarayıcısız test edilebilsin; kopyalanan kural ilk değişiklikte ayrışır |
| 5 | **Disk** tek kalıcı depodur | Kök `MIRA_ROOT` ile adlanır, repo dışındadır |
| 6 | Motor **xAI Grok**, kendi ince katmanımızın arkasında | Servis değişebilir olsun; döngü ve araçlar bizim kodumuz |
| 7 | **`collab-toolbox/` ve `queen-editor/`'e sıfır bağımlılık** | Araçlar birbirinden bağımsız evrilebilsin |

## 8 · `mira/CODE-STANDARD.md`

İçereceği bölümler:

- **Yığın** — Flask + React, neden.
- **Bağımsızlık** — queen-editor'den miras alınan şey belgedir, kod değil.
- **Katmanlar** — `presentation → domain ← data → services`; yasaklar. **Tek feature `workspace`**
  kararının gerekçesi burada yazılır: bir cevabın dosya yazması proje/sohbet/dosyaya aynı anda
  dokunduğu için ayırmak `feature ↛ feature` yasağını kırar.
- **Diskteki gerçek** — düzen ve "hiçbir dosya başkasının cevabını tekrarlamaz" kuralı.
- **Ön yüz** — `features/` + `shared/`; **`vendor/` yoktur** ve tasarım görsel şartnamedir, kaynak kod
  değildir. Gerekçe: prototip tek parça bir DC bileşenidir, satır içi stillidir, `style-hover` gibi
  DC'ye özel öznitelikler kullanır — kopyalanacak bir bileşen dosyası yoktur.
- **Dil** — arayüz metni, kod, yorum, docstring, test adı ve commit mesajı **İngilizce**; superpowers
  belgeleri Türkçe. queen-editor'ün "arayüz Türkçe" kuralının buraya taşınmadığı açıkça yazılır.
- **Testler** — nasıl koşulur, neyin sahtelendiği.

## 9 · `CLAUDE.md`

Kök `CLAUDE.md`'ye `## mira — Mira (web UI)` bölümü eklenir: bir cümlelik tanım, `FOUNDATION.md` /
`CODE-STANDARD.md` / yol haritası bağlantıları, ve **queen-editor'den ayrışan iki kural** — arayüz dili
İngilizce, `dist/` commit edilmez. Bu iki satır olmazsa komşu aracın kuralları buraya sızar.

## 10 · Kabul kriteri

- `python mira/main.py` → tarayıcıda tasarımın zemin renginde boş sayfa açılıyor.
- `pytest` `mira/` dizininden yeşil (4 test).
- `npm test` `mira/frontend/` dizininden yeşil (1 test).
- `mira/FOUNDATION.md`, `mira/CODE-STANDARD.md` ve `CLAUDE.md` bölümü yazılmış.

## 11 · Bu fazda karara bağlanmayanlar

`MIRA_ROOT`'un içindeki dizin düzeni Faz 1'in işidir — Faz 0 yalnız kökü adlar, altına hiçbir şey
yazmaz.
