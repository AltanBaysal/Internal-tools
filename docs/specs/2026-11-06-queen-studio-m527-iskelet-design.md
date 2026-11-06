# Madde 527 · İskelet ve ilk ekran, sürüm V1 — tasarım

**Tarih:** 6 Kasım 2026 · **Madde:** [v1 yol haritası](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-3),
527 · v1-3 · **Dal:** `feat/queen-studio-v1`

## Ne ve neden

queen-studio'nun ilk kodu. Core bu makinede tek komutla açılır, UI'ı aynı adresten sunar; `/api`
core'un, gerisi UI'ındır ([6. adım, Adresler](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md#adresler)).
Tek endpoint `GET /api/health`'tir; ekran yalnız "Queen Studio V1" yazan bir yer tutucu sayfadır,
tasarlanan ekranlar sonda ([v1-28](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-28)) onun yerine
geçer. Sonraki maddelerin hepsi bu iskeletin üstüne kurulur: klasörler, kontrol araçları, suite'ler,
türlerin OpenAPI'den UI'a geçtiği yol ve log burada yerine oturur. Depo portu, ortak sözleşme (dört
alanlı hata, `GET /api`) ve öbür endpoint'ler sonraki maddelerindir.

## Klasörler

```
queen-studio/
  main.py              başlangıç dosyası: gerçek kapılar burada bağlanır, core buradan açılır
  write_openapi.py     core'un OpenAPI'sini ui/src/api/openapi.json'a yazar
  pyproject.toml       ruff, pyright ve pytest'in ayarı
  requirements.txt     core'un çalışırken istedikleri (notebook bunu kurar, v1-25)
  requirements-dev.txt üstüne testler ve kontrol araçları
  core/
    about.py           uygulamanın adı ve sürümü: kodda yazıldıkları tek yer
    server.py          /api'yi kuran ve UI'ı yanına koyan iki fonksiyon
    log.py             log'u diske ve konsola yönlendirmek
    api/endpoints.py   `api` grubu (discovery ve health): bugün yalnız health
    disk/identity.py   Colab diski kapısı: core'un kimliği, core.json
  tests/               pytest
  ui/
    src/               React, TypeScript
    src/api/           openapi.json (üretilir, commit'lenir) ve schema.d.ts (üretilir, commit'lenmez)
    dist/              derlenmiş UI, commit'lenir (FOUNDATION 7)
```

Gruplar ve kapılar CODE-STANDARD'ın Düzen'indeki gibi: `api` bir gruptur, `disk` bir kapıdır. `api`
grubunun kuralı ve kaydı yok; yalnız endpoint'i var. Kapılar `core/<kapı>/` altında durur; sonrakiler
(`storage`, `comfy`, `ffmpeg`, `downloads`, saat, ekran kartı) da öyle.

## Komutlar

Depo kökünden. Her şey depoda kalır: Python paketleri `queen-studio/.venv`'de, npm paketleri
`queen-studio/ui/node_modules`'ta; global kurulum yok (kullanıcı, 6 Kasım).

| Ne | Komut |
|---|---|
| Python paketlerini kurmak | `queen-studio/.venv/Scripts/python -m pip install --no-cache-dir -r queen-studio/requirements-dev.txt` |
| UI paketlerini kurmak | `npm ci --prefix queen-studio/ui --cache tmp/npm-cache` |
| Core'u açmak | `queen-studio/.venv/Scripts/python queen-studio/main.py` → `http://127.0.0.1:8200` |
| Python suite'i (ruff ve pyright dahil) | `queen-studio/.venv/Scripts/python -m pytest queen-studio -q` |
| UI suite'i (`tsc`, `eslint`, Vitest) | `npm test --prefix queen-studio/ui` |
| UI'ı derlemek | `npm run build --prefix queen-studio/ui` |
| OpenAPI'yi UI'a yazmak | `queen-studio/.venv/Scripts/python queen-studio/write_openapi.py` |

`.venv` kurulumda (v1-1) açıldı, Colab CLI'ı da içinde (kararlar, Sapma 2); bu madde ona yalnız ekler.
pip'in önbelleği kapalı, npm'inki deponun `tmp/`'sinde: ikisi de kullanıcı klasörüne yazmasın diye.

## Kararlar

- **Ad ve sürüm tek yerde:** `core/about.py`'de `NAME = "queen-studio"`, `VERSION = "1.0.0"`. Core
  onları health'e ve OpenAPI'nin `info`'suna (`title`, `version`) koyar. UI adı ve sürümü
  `openapi.json`'ın `info`'sundan okur, ekrandaki "Queen Studio V1"i ondan kurar: ad tirelerden
  bölünüp her parça büyük harfle başlar, sürümün ilk sayısı "V"nin yanına gelir. Adı değiştirmek
  `about.py`'yi değiştirip `write_openapi.py`'yi ve `npm run build`'i koşmaktır (commit'lenen `dist`
  adı taşır); ikisi üretimdir, yazmak değil. Testler
  adı yazmaz, sabitten okur: test de ikinci bir yer olmasın diye. Python paketinin, npm paketinin
  (`ui`) ve log klasörünün adı da sabitten gelir ya da adı hiç taşımaz.
- **`/api` ayrı bir FastAPI uygulaması, `/`'e bağlı UI'ın yanında:** core'un `/api`'si kendi FastAPI
  uygulamasıdır ve `/api`'ye bağlanır; geri kalan her adres UI'ın klasörüne gider. Böylece:
  `/api`'nin altındaki, API'de olmayan bir adres hiçbir zaman UI'a düşmez (bugün FastAPI'nin 404'ü,
  v1-5'ten sonra `unknown_endpoint`); OpenAPI'deki adresler 6. adımdaki gibi `/api` öneksiz
  (`/health`) yazılır; FastAPI'nin `/docs` sayfaları kapalıdır, o adresler UI'ındır. Çıplak `/api`
  (sorgusuyla, `GET /api?path=…`) API'nin köküdür, v1-5 dizini orada (`/`) tanımlar. Starlette'in
  `Mount`'u yalnız `/api/…`'yi tuttuğu için `serve` gelen `/api`'yi `/api/`'ye çevirir: yönlendirme
  yok, tek gidiş dönüş, sorgu dokunulmadan; testle. Seçenek: tek uygulama, her endpoint
  `/api` önekiyle; o zaman `/api/olmayan` UI'ın 404'üne düşerdi ve v1-5'in hata biçimi iki yerde
  kurulurdu.
- **UI `StaticFiles`'la sunulur,** `html=True`: `/` `index.html`'i verir, dosyalar adlarıyla. Adresten
  yola Starlette'in kendi kontrolü bakar, klasörün dışına çıkan istek dosya vermez (testle).
  Ekranlar adrese göre değişmediği için bilinmeyen adres `index.html`'e dönmez; ekranlar adres
  kullanırsa v1-28 bunu ekler.
- **Türler:** `write_openapi.py` core'un OpenAPI'sini sunucu açmadan `ui/src/api/openapi.json`'a
  yazar. `info`, `paths` ve `components` `/api/openapi.json`'ın sunduğuyla aynıdır; sunulan belge
  yalnız bağlandığı yerden gelen `"servers": [{"url": "/api"}]`'yi ekler, türler ona dayanmaz. Dosya
  commit'lenir. `openapi-typescript` her `npm test`'ten ve `npm run build`'den önce ondan `src/api/schema.d.ts`'i üretir (`pretest`,
  `prebuild`); üretilen dosya commit'lenmez, hep taze kalır. `tsc` hem testte hem derlemede koşar:
  core'un değiştirdiği bir alana UI uymazsa derleme düşer (FOUNDATION 2). Python suite'inde bir test
  commit'lenen `openapi.json`'ı core'unkiyle karşılaştırır; core değişip dosya yazılmadıysa düşer ve
  komutu söyler. Ekrandaki başlığı kuran fonksiyon (`ui/src/about.ts`) girdisini `Health`'in `app` ve
  `version` alanlarıyla tanımlar: health'in alanı değişirse `tsc` düşer. UI `openapi.json`'dan yalnız
  `info`'yu alır; derlenen paket belgenin geri kalanını taşımaz.
- **Core'un kimliği:** 4. adımdaki gibi Colab diskindeki `core.json`'dan (`{"core": "<kimlik>"}`).
  Yoksa üretilir (10 karakter, küçük harf ve rakam, proje kimliği gibi) ve geçici dosyaya yazılıp
  yerine konur; varsa okunur, makine yaşadıkça core yeniden başlasa da aynı kalır. Okunamayan ya da
  bozuk `core.json` core'u açtırmaz ve üstüne yazılmaz. Log satırı bir kez söyler: dosyanın yolunu,
  hatanın kendi sözünü, neden açılmadığını (yeni kimlik `runner`'ı eski kimlik olan kuyrukları sahipsiz
  bırakırdı) ve ne yapılabileceğini (dosyayı düzeltmek ya da silip yeni kimliği kabul etmek; o kuyruklar
  sonra `resume` ister).
  Bir makinede tek core açılır (4. adım); aynı anda iki core'un ilk açılışı bu maddenin durumu değil.
- **Disk klasörü:** bu makinede `<depo>/tmp/<NAME>/` (git'in görmediği `tmp/`); `core.json` ve
  `core.log` orada. Colab'daki yeri ve ortamdan verilmesi v1-25'in.
- **Log:** kök logger'a iki çıkış: dosya (`core.log`, ekleyerek, UTF-8) ve konsol. Uvicorn kendi log
  ayarını yapmaz (`log_config=None`), onun satırları da aynı yere düşer. Satır:
  `2026-11-06T12:00:00Z INFO core: queen-studio 1.0.0, core k3v9q2mz7a` — zaman UTC, 6. adımın
  biçiminde; adresi hemen ardından Uvicorn'un kendi satırı söyler. Notebook'un çıktısı ve Drive'a 5 dakikada bir gitmesi v1-25'in.
  Log'a hiçbir sır yazılmaz: bugün core hiçbir sır okumaz.
- **Kapı:** `127.0.0.1:8200`. queen-editor 8000'de, queen-agent 8100'de, ComfyUI 8188'de; üçüyle de aynı
  anda açılabilir. Sabit, `main.py`'de; ortamdan verilmesi gerekirse v1-25 ekler.
- **Kontrol araçları testle koşar:** Python suite'i ruff'ı (`check` ve `format --check`) ve pyright'ı
  (sıkı mod) birer test olarak koşar; UI'ın `npm test`'i `tsc`, `eslint` ve Vitest'i art arda koşar.
  CODE-STANDARD'ın "testlerle birlikte koşarlar" kuralı böylece bir komut: biri hata verirse suite
  kırmızıdır. Kodun hedefi Python 3.12 (`ruff` ve `pyright` ona göre bakar): Colab'ın Python'u bu
  makinedekinden (3.14) eski olabilir.
- **pyright** PyPI paketiyle, kendi içindeki sürümüyle ve bu makinedeki Node'la çalışır; hiçbir şey
  indirmez, kullanıcı klasörüne yazmaz.
- **Sürümler:** `requirements.txt` core'un çalışırken yüklediği her paketi tam sürümle (`==`) sabitler,
  yalnız adını verdiği ikisini değil: Colab'ın önceden kurulu sürümleri (pydantic gibi) bu makinede
  sınananın yerine geçmesin diye. Testin istemcisi `httpx2`: Starlette 1.10 `TestClient`'ta düz
  `httpx`'i eskimiş sayıyor. UI'da TypeScript 5.9: `typescript-eslint` 6.1'den eskisini,
  `openapi-typescript` yalnız 5.x'i alıyor.

## `GET /api/health`

```json
{"app": "queen-studio", "core": "k3v9q2mz7a", "version": "1.0.0"}
```

6. adımdaki gibi. Alanlar ve endpoint agent'a yazar gibi açıklanır. `def`, `async` değil (FOUNDATION 2).

## Maliyet

| İşlem | Drive | Disk | Ağ |
|---|---|---|---|
| `GET /api/health` | 0 | 0 | 0 |
| UI'ın bir dosyası | 0 | 1 okuma | 0 |
| Core'un açılışı | 0 | `core.json` 1 okuma; yoksa 1 yazma + 1 yer değiştirme | 0 |
| Bir log satırı | 0 | 1 ekleme | 0 |

Health kimliği açılışta okunmuş değerden verir; istek başına disk ya da Drive yok. Health'in Drive'a
gitmediği bugün yapıyla sınanır: API'nin elinde depo yok. Depo portu gelince (v1-7) health'in sıfır
depo çağrısı yaptığı sayan taklitle sınanır.

## Ne bozulabilir

- **`core.json` yarım yazılırsa:** geçici dosyaya yazılıp yerine konduğu için yarım dosya yerinde
  kalmaz. Okunamayan dosya boş sayılıp üstüne yazılmaz; yeni kimlik üretmek `runner`'ı eski kimlik olan
  kuyruğu sahipsiz bırakırdı (4. adım).
- **`ui/dist` yoksa** core açılmaz, Starlette'in sözüyle; `dist` commit'li olduğu için klonda vardır.
- **Commit'lenen `openapi.json` eskiyse** Python testi düşer; derlenen `dist` de eski türlerle
  kurulmuş olurdu.
- **Adresten yol:** Starlette `StaticFiles` UI klasörünün dışına çıkmaz; testle. Testteki `..`'lar
  kodlanmış yazılır (`%2e%2e`, `..%2f`): düz `/../`'yu test istemcisi kendisi çözer, sunucuya hiç
  ulaşmaz.

## Testler

Kırmızıdan başlar (CODE-STANDARD, Testler). Hiçbiri gerçek saniye beklemez, ağ açmaz.

- `GET /api/health` uygulamayı, kimliği, sürümü verir; ad ve sürüm sabitten.
- `/` UI'ın `index.html`'ini, `/assets/…` dosyasını verir; `/api/olmayan`, `/api` ve
  `/api?path=…` UI'a düşmez, API'nin JSON 404'ünü alır; `/docs` UI'ındır; UI klasörünün dışındaki
  bir dosya 404'tür; `/api/openapi.json` core'un belgesidir.
- `core.json` yoksa yazılır, varsa aynı kimlik döner, bozuksa açılış durur ve dosya değişmez.
- Log dosyası açılır, satır UTC zamanla yazılır, klasörü yoksa açılır.
- `main.build`: kimlik `core.json`'dakidir, açılış satırı log'da; bozuk `core.json`'da çıkış kodu 1,
  neden ve ne yapılacağı log'da, konsolda bir kez.
- Commit'lenen `openapi.json` core'unkiyle aynı.
- ruff ve pyright temiz.
- UI: başlık fonksiyonu ad ve sürümden "Queen Studio V1"i kurar; yer tutucu sayfa `openapi.json`'ın
  ad ve sürümünü gösterir.

## Bitti sayılır

Kabul koşulunun yedi satırı: core tek komutla açılıyor ve UI'ı aynı adresten sunuyor; health üç alanı
veriyor, Drive'ı bilmiyor; ekran "Queen Studio V1"; ad `about.py`'de tek yerde; UI'ın türleri
`openapi.json`'dan, `tsc` onlarla; log diskte; iki suite yeşil, kontrol araçları onlarla koşuyor,
komutlar CLAUDE.md'de, `dist` commit'e hazır. Ayrıca CODE-STANDARD'ın başındaki ve FOUNDATION'ın
4. kararındaki yer tutucu cümleler komutlarla değişti.

## Sonraki maddeler için

Reviewer'ın bu maddede gördüğü, sonraki coder'ların bilmesi gerekenler:

- **v1-7:** kapılar `create_api`'ye tek bir nesne olarak verilsin, OpenAPI belgesi taklitlerle
  kurulabilsin; `write_openapi.py`'nin `core_id=""`'si bunun ilk işareti.
- **v1-11:** 10 karakterlik kimlik üreticisi proje kimliğiyle paylaşılsın, ama disk kapısından
  (`core/disk/identity.py`) alınarak değil: ortak bir yere taşınsın.
- **v1-16:** ComfyUI kapısı için `httpx` mi `httpx2` mi bir kez seçilsin ve kararlar belgesine
  yazılsın (5. adım `httpx` diyor; testin istemcisi `httpx2`).
- **v1-8 ve v1-16:** Google API istemcisinin ve `httpx`'in logger'ları `WARNING`'e çekilsin: kök
  logger `INFO`'da, her çağrıları yoksa log'a düşer.
- **v1-5:** FastAPI'nin `redirect_slashes`'ı mutlak adresli bir 307 döner; tünelin `https`'i
  arkasında yanlış adresi gösterir. Yerine konsun.
- **v1-5:** dizin `?path=`'i okuyunca, çıplak `/api`'nin `/api/`'ye çevrilmesinin sorguyu olduğu gibi
  bıraktığı testle sınansın (`GET /api?path=/health` o adresin ayrıntısını verir).
- **v1-27:** `tests/test_checks.py` ruff'ı, pyright'ı ve Node'u ister; suite Colab'da koşacaksa
  orada da bulunsunlar.
