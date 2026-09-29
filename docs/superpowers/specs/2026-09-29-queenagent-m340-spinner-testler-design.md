# Madde 340 — Yüklenirken spinner, önce dosya listesinde · test turu

**Kaynak:** [yol haritasının 340'ı](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2c);
kararları v9-2'nin; tasarım: `queen-agent-v3`'ün 173'ü ve 181'i.

**Kullanıcıdan gereken:** hiçbir şey. Görünüş tasarımda yazılı, madde hizalandı.

## Ne kanıtlanacak

Dosya listesi yüklenirken bugün parlayan bir iskelet (`Skeleton rows={3}`) çiziliyor. Tasarımın
173'ü ve 181'i onun yerine küçük bir dönen halka koyuyor; başlık ve düğmeler yerinde duruyor, yalnız
listenin satırlarının yeri spinner oluyor.

Tasarımın ölçüleri (`DESIGN-STANDARD.md`, *Waiting and offline*; `kit.css`):

- **`spinner`** — `.msg__spinner`'ın halkası, 20px: `1.5px solid var(--line)` kenar, üstü
  `var(--accent)`, `border-radius: 50%`, `msg-spin 0.8s linear infinite` — bir tam tur. Yeni bir
  animasyon yok: `msg-spin` uygulamada canlı satırın spinner'ı için zaten var.
- **`file-list__spinner`** — spinner'ın dosya listesindeki yeri: `display: flex`,
  `justify-content: center`, `padding: 24px 12px`.
- Halka `aria-hidden="true"`: hiçbir şey söylemez, tasarımdaki gibi.

Spinner bir kez kurulur, ve sonraki parçalar — v9-2l sohbetin açılışı, v9-2u All projects ve ad
sorma ekranı — aynısını kendi yerlerine koyar. Her yerin kendi kutusu var (`chat__spinner`,
`all-projects__spinner`), halka tek. O yüzden bileşen yalnız halkayı çizer; kutuyu yeri çizer.

## Testler ne tutar

| # | Dosya | Ne |
|---|---|---|
| 1 | `Spinner.test.jsx` (yeni) | Spinner `spinner` sınıflı bir halka çizer, `aria-hidden`, içinde yazı yok |
| 2 | `FileRail.test.jsx` | Liste yüklenirken spinner listenin kutusunda, `file-list__spinner`'ın içinde dönüyor; iskelet yok; `No files yet` da yok (bugünkü *a rail still loading says neither* testi iskelet yerine spinner'ı sorar) |
| 3 | `FileRail.test.jsx` | Spinner dönerken başlık (`Project files` düğmesi) ve `Refresh` yerinde |
| 4 | `FileRail.test.jsx` | Liste gelince spinner yok, satırlar var — bugün de yeşil: spinner'ın gelen listeyle kalmamasının bekçisi |
| 5 | `workspace.css.test.js` | `.spinner`'ın ölçüleri tasarımınki: 20×20, kenar, üst renk, yuvarlak, `msg-spin 0.8s linear infinite` |
| 6 | `workspace.css.test.js` | `.file-list__spinner` ortalar, `padding: 24px 12px` |

Testler `data-testid="spinner"` ile bulur, iskeletin `data-testid="skeleton"`'ı gibi: halka
`aria-hidden` olduğu için rolüyle bulunamaz.

## Tutmaz

- **İskelet başka yerlerde kalır:** `App.jsx`'in ilk yüklemesi, `ChatScreen.jsx`'in açılışı,
  `ProjectScreen.jsx`'in iki listesi. Onları v9-2l, v9-2n ve v9-2u kaldırır; `Skeleton.jsx` ve
  testleri bu parçada değişmez.
- **Refresh'in yeri** v9-2m'nin; bu parçada liste kutusunun içinde, bugünkü yerinde kalır.
- **Halkanın gerçekten döndüğü** jsdom'da görülmez; tarayıcıda görülür.

## Bu turda yazılmayanlar

- `Spinner.jsx`, `FileRail.jsx` ve `workspace.css` değişmez; uygulama turunda.
- `dist` derlenmez: birleştirirken conductor derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` kırmızı verir: `Spinner.test.jsx`
bileşen olmadığı için yüklenemez, FileRail'in 2'si ve 3'ü ve CSS'in iki iddiası düşer; 4 yeşil.
queen-editor'ün arka ucu 377'nin bilinen iki kırmızısıyla kalır; öteki iki süit yeşil. Kırmızı
hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m340-spinner-testler-plan.md).
