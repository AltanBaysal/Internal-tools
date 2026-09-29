# Madde 338 — Üst çubuk · test turu

**Kaynak:** [yol haritasının 338'i (v9-2a)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
kararları roadmap'in *v9-2 — Tasarım* başlığında, ve orada *Tasarım turunda değişen iki karar*: sürüm
kalın değil, adla aynı kalınlıkta. Tasarım: queen-design'ın `queen-agent-v3` dalında 150, 159, 161,
166; ölçüler ve sınıf adları `projects/queen-agent/DESIGN-STANDARD.md`'nin *Shell* ve *Bar*
başlıklarında, çizimi `shell.js`'in `bar()`'ında ve `kit.css`'in `.bar` kurallarında.

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı, kararları yazılı; geri kalan teknik.

## Ne kanıtlanacak

Bugün marka kenar çubuğunun başında: `QueenAgent`, altında küçük ve soluk sürüm (Madde 209), ve aynı
satırın sonunda katlama düğmesi. Olacak:

- **Pencerenin üstünde bir çubuk**, her ekranda — ilk yükleme, projesiz açılış ekranı, proje ekranı,
  sohbet — aynı yerde: `app-shell`'in ilk çocuğu, kenar çubuğunun ve `main`'in üstünde. İkisi
  çubuğun altında `app-shell__body`'de yan yana. Boyu 56, ve hiçbir ekranda değişmez.
- **Solda `QueenAgent` ve sürüm, tek satırda**, arada bir boşluk: `QueenAgent V8`. Sürüm adla aynı
  boyda ve aynı kalınlıkta — kendi boyu, rengi ya da kalınlığı yok, `font-weight: 400`.
- **Bir proje açıkken ortada yalnız projenin adı** (`bar__project`), kesilirse tamamı `title`'da.
  Proje açık değilken ortada bir şey yok.
- **Sağda `Exit project`** (`ghost bar__exit`), proje açıkken. Basınca uygulamanın açılışına — `/` —
  dönülür; açılış bugün ne gösteriyorsa o: ilk proje, ya da proje yoksa boş ekran. Proje açık
  değilken sağ boş, ve çubuk yerinden oynamaz (`bar__exit` hep üçüncü sütunda).
- **Kenar çubuğunda marka yok:** ne `QueenAgent`, ne sürüm, ne `sidebar__brand`. **Katlama düğmesi
  kenar çubuğunun başında kalır** — v9-2w onu sağ alta taşıyana kadar.

**"Proje açık"** App'in zaten tuttuğu `project`'tir: adresin projesi, listede bulunduysa. Liste
gelmeden ya da olmayan bir projenin adresinde ortada ad yok, sağda düğme yok. Tasarımın kuralı —
*"`Exit project` with a project open"* — proje ekranını da kapsar; o ekran v9-2n'de kalkıyor, ve o
güne kadar çubuk proje ekranından sohbete geçerken değişmez.

## Testler ne tutar, ne tutmaz

**Yeni `features/workspace/Bar.test.jsx`** — çubuğun kendisi:

| # | Ne |
|---|---|
| 1 | `bar__name`'in yazısı `QueenAgent ` + `VERSION`: ad ve sürüm tek blokta, arada boşluk. Sabite sorulur, `"V8"`'e değil — Madde 209'un testi gibi |
| 2 | Proje yokken ortada ad yok, `Exit project` yok |
| 3 | Proje verilince ortada yalnız adı, `title`'ında da adı; sağda `Exit project`, `ghost bar__exit` |
| 4 | `Exit project`'e basınca `onExit` çağrılır — nereye gidileceği App'in |

**`App.test.jsx`** — çubuk ekranların üstünde:

| # | Ne |
|---|---|
| 5 | İlk yüklemede, iskelet dururken, çubuk `app-shell`'in ilk çocuğu; kenar çubuğu ve `main` `app-shell__body`'nin içinde |
| 6 | Projesiz açılışta çubukta yalnız marka: ortada ad yok, `Exit project` yok |
| 7 | Sohbette ortada projenin adı, sağda `Exit project` |
| 8 | İkinci projenin sohbetinde `Exit project`'e basınca açılışa dönülür, ve açılış ilk projeye iner (`/p/p1`) — sohbetin kendi projesine değil |

**`Sidebar.test.jsx`** — marka gitti, katlama kaldı:

| # | Ne |
|---|---|
| 9 | Kenar çubuğunda `QueenAgent` de sürüm de yok, `sidebar__brand` yok |
| 10 | Kenar çubuğunun ilk çocuğu katlama düğmesi |

Madde 209'un üç testi kalkar, çünkü tuttukları artık yanlış: *"the sidebar says which run this is"*
(1'e taşınır), *"there is no logo mark beside the wordmark"* (marka artık kenar çubuğunda yok; 9
tutar) ve *"folded, the version folds with the name"* (kenar çubuğunda sürüm hiç yok; 9 tutar). İlk
testin adı *"with no project selected only the wordmark and the projects remain"* — markasız olur.

**`workspace.css.test.js`** — tasarımın ölçüleri, kilit olarak:

| # | Ne |
|---|---|
| 11 | `.bar` 56 yüksek, `flex: none`, üç sütunlu ızgara `minmax(0, 1fr) minmax(0, auto) minmax(0, 1fr)` — orta sütun hep pencerenin ortasında |
| 12 | `.bar__name` Newsreader (`var(--font-heading)`), 21, tek satır; `.bar__version` `font-weight: 400`, kendi `font-size`'ı ve `color`'ı yok |
| 13 | `.bar__project` tek satırda kesilir, en çok 640; `.bar__exit` üçüncü sütunda, sağa yaslı |
| 14 | Stil dosyasında `sidebar__brand`, `sidebar__name`, `sidebar__wordmark`, `sidebar__version` yok |

Madde 209'un *"the version sits under the name and reads as a note"* testi kalkar: 12 onun tersini
tutar.

**`app.css.test.js`** — kabuk:

| # | Ne |
|---|---|
| 15 | `.app-shell` `flex-direction: column`; `.app-shell__body` `display: flex`, `flex: 1`, `min-height: 0` — çubuk üstte, altı pencerenin kalanı, ve sayfa yine kaymaz |

**Tutmaz:** çubuğun ekranda gerçekten 56 durduğunu ve ekran değişince oynamadığını — jsdom stil
dosyasını yüklemez. O, Claude'un tarayıcısında görülür.

## Bu turda yazılmayanlar

- `Bar.jsx`, `App.jsx`, `Sidebar.jsx`, `workspace.css`, `app.css` değişmez; uygulama turunda.
- `dist` derlenmez: Claude birleştirirken derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` yeni testlerde kırmızı verir —
`Bar.test.jsx` `Bar.jsx` olmadığı için hiç yüklenemez. queen-agent'ın arka ucu ve queen-editor'ün ön
ucu yeşil; queen-editor'ün arka ucu 377'nin bilinen iki kırmızısıyla kalır. Kırmızı hâliyle commit
edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m338-ust-cubuk-testler-plan.md).
