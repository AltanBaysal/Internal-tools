# Madde 364 — All projects ve ad sorma ekranı yüklenirken ve yüklenemeyince · test turu

**Kaynak:** [yol haritasının 364'ü (v9-2u)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de, tasarımı queen-design'ın `queen-agent-v3` dalında 172 ve 173 —
`projects/queen-agent/projects/index.html` (`spinnerHtml`, `frameHtml`, `screenHtml`'in `failed`'i),
`new-project/index.html` (`loadingHtml`, `draw`'ın hata dalı), `BEHAVIOUR.md`'nin *All projects* ve
*Name project* bölümleri, `DESIGN-STANDARD.md`'nin *Screen and empty* ve *Waiting and offline*'ı,
`kit.css`'in `.all-projects__spinner`, `.empty__error`, `.empty__actions`, `.empty__copy` kuralları.
Üstüne kurulduğu: 340 (`Spinner.jsx`, `.spinner`), 342 (açık dosyanın `Copy`'si: `Copied` /
`Could not copy`), 353 (All projects), 359 (arama), 361 (`NameProjectScreen.jsx`).

**Kullanıcıdan gereken:** hiçbir şey. Koşu subagent'ta; iki yöne okunabilen kararlar aşağıda
*Kararlar*'da yazılı ve raporda Claude'a gider.

## Ne kanıtlanacak

Proje listesi gelene kadar All projects'te başlık, `+ New project` ve arama yerinde, listenin yerinde
spinner dönüyor; ad sorma ekranında ortada aynı spinner. Liste okunamayınca iki ekranda da tek cümle,
`Couldn't load projects.`, `Try again` ve `Copy`: `Try again` listeyi yeniden okur — beklerken yine
spinner —, `Copy` gelen hatayı olduğu gibi panoya koyar. Bir yazma — yeniden adlandırma, sabitleme,
silme, oluşturma — reddedilince ekran hata ekranına dönmez: All projects listesiyle kalır, ad sorma
ekranı yazılan adla kalır, ve sunucunun sözü görünür.

## Kararlar

1. **İki hata, iki satır.** Bugün `useProjects`'in tek `error`'u hem listenin okunamamasını hem bir
   yazmanın reddini tutuyor; reddedilen bir yeniden adlandırma All projects'i hata ekranına çeviriyor,
   reddedilen oluşturma ad formunu ve yazılan adı siliyor. FOUNDATION'ın 1. ilkesi (kullanıcının işi
   kutsal) ve tasarımın 172'si (hata ekranı *listenin* yüklenemediği hâl) ikisini ayırır:
   - `error` yalnız **listenin okunamaması**. Başarılı bir okuma onu kaldırır.
   - `writeError` **reddedilen bir yeniden adlandırma, sabitleme ya da silme**; sıradaki yazma
     başlarken kalkar. `useFiles`'ın `filesError` / `deleting.error` ayrımının aynısı.
   - **Oluşturmanın reddi çağırana gider** (`createProject` fırlatır): tek çağıranı ad sorma ekranı,
     ve ret, koruduğu adın yanında, ekranın kendi durumunda tutulur. Böylece ret, `Cancel`'dan sonra
     All projects'te bayat bir satır olarak kalmaz.
2. **All projects yüklenirken** (tasarımın `frameHtml(spinnerHtml())`'i): başlık, `+ New project` ve
   `.all-projects__tools` (arama odakta — 359; sekmeler 363'le aynı satıra gelir, bu yüzden onlar da
   yerinde durur) çizili; listenin yerinde `.all-projects__spinner` içinde 340'ın `Spinner`'ı. `No
   projects yet.` ve satır yok.
3. **Liste okunamayınca** (tasarımın `screenHtml`'inin `failed`'i): ekranın tamamı `.empty`; içinde
   `p.empty__error` `Couldn't load projects.`, altında `.empty__actions` içinde
   `button.failure__retry` `Try again` ve `button.ghost.empty__copy` `Copy`. Başlık, arama ve liste
   yok; sunucunun ham sözü ekranda **yok** — tasarımın 172'si: tek sade cümle, ham metin panoya.
4. **`Copy`** `error`'u olduğu gibi panoya koyar: `failure.js`'in okuduğu söz — sunucunun JSON'daki
   `error`'u, yoksa `HTTP <kod>: <gövde>`, sunucuya ulaşılamadıysa tarayıcının sözü. Cevabı 342'nin
   `Copy`'sinin aynısı: düğmenin kendi yazısı `Copied` ya da `Could not copy`, `data-said` `yes` /
   `no`. İkinci bir kopyalama yazılmaz: açık dosyanın düğmesi kendi dosyasına taşınır ve iki yer onu
   kullanır (uygulama turunun işi; testler davranışı tutar).
5. **`Try again`** listeyi yeniden okur ve beklerken yüklenme hâlini gösterir (tasarımın `retry`'ı,
   173: "`Try again` da onu gösteriyor"). Yüklenme hatadan önce gelir: `loading` ve `error` birlikte
   verilirse spinner çizilir.
6. **Ad sorma ekranı yüklenirken** (tasarımın `loadingHtml`'i): `.empty` içinde yalnız `Spinner`;
   başlık ve alan yok — ilk proje mi bilinmiyor. **Liste okunamayınca** All projects'in aynı hata
   ekranı, `Try again` ve `Copy` ile. Çubuğun sağında `Cancel` yok — liste okunamadı, `projects.length`
   sıfır; tasarımda da `failed` `many` değil.
7. **Oluşturma reddedilince** ad sorma ekranı yerinde kalır, alan yazılan adı tutar, ve sunucunun sözü
   `.empty__row`'un altında `p.empty__refused`'da görünür. Tasarım bu hâli çizmiyor (`APP-BUGS.md`
   26: "no write fails in the pages"); söz, sohbetin ret kartındaki `failure__detail` gibi sunucunun
   kendi sözü, aynı sesle (mono, `#a4735a`).
8. **All projects'te reddedilen yazma**: liste yerinde kalır; sunucunun sözü aramanın satırıyla liste
   arasında, 353'ün dosya listesindeki gibi tek `.list-error` satırında. Sıradaki yazma onu kaldırır.
   Tasarım bunu da çizmiyor (`APP-BUGS.md` 26); `.list-error` uygulamanın "bir listede ne ters gitti"
   satırı, yeni bir görünüş icat edilmez.
9. **CSS** (`kit.css`'ten): `.all-projects__spinner` (`display: flex`, `justify-content: center`,
   `padding: 40px 12px`), `.empty__actions` (`display: flex`, `gap: 10px`, `margin-top: 16px`),
   `.empty__copy[data-said="yes"]` `var(--accent)`, `[data-said="no"]` `var(--destructive)`. Kendi:
   `.empty__refused` (`var(--font-mono)`, `11.5px`, `#a4735a`, `overflow-wrap: anywhere`).

## Testler ne tutar

### `AllProjectsScreen.test.jsx`

353'ün *a list that could not be read says what the server said, and nothing else* testi kalkar
(ham söz artık ekranda değil). Yeni:

| # | Ne |
|---|---|
| P1 | `loading` iken `.all-projects__tools`'un hemen ardında `.all-projects__spinner`, içinde spinner; satır ve `No projects yet.` yok |
| P2 | `error` iken `.empty > .empty__error` `Couldn't load projects.`; ham söz, `All projects` başlığı ve arama yok |
| P3 | `.empty__actions` içinde sırayla `Try again` (`failure__retry`) ve `Copy` (`ghost empty__copy`); `Try again` `onRetry`'ı çağırır |
| P4 | `Copy` hatayı olduğu gibi panoya koyar, ve düğme `Copied` der |
| P5 | Pano reddedince düğme `Could not copy` der |
| P6 | `loading` ve `error` birlikte: spinner var, hata ekranı yok |
| P7 | `writeError` iken satırlar yerinde, `.list-error`'da sunucunun sözü, aramanın satırıyla liste arasında; hata ekranı yok |

### `NameProjectScreen.test.jsx`

361'in *while the list loads, nothing is asked yet* testi spinner'ı da ister; *a failure says what
the server said, and nothing else* kalkar. Yeni:

| # | Ne |
|---|---|
| N1 | `loading` iken `.empty`'nin tek çocuğu spinner; alan ve başlık yok |
| N2 | `error` iken `Couldn't load projects.`, `Try again`, `Copy`; ham söz ve alan yok; `Try again` `onRetry`'ı çağırır |
| N3 | `Copy` hatayı olduğu gibi panoya koyar |
| N4 | `onCreate` reddedilince alan yerinde ve yazılan adı tutuyor; sunucunun sözü `.empty__refused`'da, `.empty__row`'un ardında |

### `App.test.jsx`

353'ün *a list that fails to load says so instead of claiming there are none* testi `Couldn't load
projects.`'i ister, ham `HTTP 500`'ü değil. 361'in *a project the server will not make says what the
server said* testi alanın adı tuttuğunu da ister. Yeni:

| # | Ne |
|---|---|
| A1 | Liste okunamaz → `Try again` → beklerken başlık ve spinner → liste gelince satırlar |
| A2 | `/new`'de liste okunamaz → hata ekranı, çubuğun sağında `Cancel` yok → `Try again` → `Name your project` alanı |
| A3 | Sunucu yeniden adlandırmayı reddeder → All projects satırlarıyla yerinde, `.list-error`'da sunucunun sözü, `Couldn't load projects.` yok |
| A4 | Sunucu silmeyi reddeder → proje yerinde, `.list-error`'da sunucunun sözü |
| A5 | Reddedilen yazmadan sonra başarılı bir yazma satırı kaldırır |

### `workspace.css.test.js`

| # | Ne |
|---|---|
| C1 | `.all-projects__spinner`: `display: flex`, `justify-content: center`, `padding: 40px 12px` |
| C2 | `.empty__actions`: `display: flex`, `gap: 10px`, `margin-top: 16px` |
| C3 | `.empty__copy[data-said="yes"]` `var(--accent)`, `[data-said="no"]` `var(--destructive)` |
| C4 | `.empty__refused`: `var(--font-mono)`, `11.5px`, `#a4735a`, `overflow-wrap: anywhere` |

## Tutmadıkları

- Sekmeler ve sayıları (363); yeniden adlandırması reddedilen satırın yazılan adı geri getirmesi
  (360'ın satırı adı sunucu cevap vermeden kapatıyor — raporda açık nokta).
- Sunucu: değişmez.
- `dist` — Claude derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` P1–P7, N1–N4, A1–A5,
C1–C4 ve değişen üç testte kırmızı; öteki üç süit yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m364-yukleme-ve-hata-testler-plan.md).
