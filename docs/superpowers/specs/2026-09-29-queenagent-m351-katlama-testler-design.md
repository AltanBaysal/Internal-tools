# Madde 351 — Kenar çubuğunu katlama · test turu

**Kaynak:** [yol haritasının 351'i (v9-2w)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
kararları roadmap'in *v9-2 — Tasarım* başlığında. Tasarım: queen-design'ın `queen-agent-v3` dalında
174 ve 187; ölçüler ve sınıf adları `projects/queen-agent/DESIGN-STANDARD.md`'nin *Layout*, *Small
marks* ve *Sidebar* başlıklarında, çizimi `shell.js`'in `sidebar()` ve `panelFold()`'unda, `Ctrl + .`
`foldShortcut()`'ta, stili `kit.css`'in `.sidebar__foot`, `.sidebar__fold`, `.sidebar__panel-icon` ve
`.sidebar__new-chat--icon` kurallarında.

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı, kararları yazılı; geri kalan teknik.

## Ne kanıtlanacak

Bugün (338'den beri) katlama düğmesi kenar çubuğunun ilk çocuğu, bir `‹` yazısı; katlanınca kenar
çubuğu 52'lik bir şeride iner ve şeritte yalnız `›` kalır. Katlanma App'te tutulur
(`sidebarCollapsed`), adres değişince kalır — bu değişmez. Olacak:

- **Katlama düğmesi bir panel ikonu.** `sidebar__fold`, içinde çizilmiş bir `sidebar__panel-icon`
  (16 × 16 kare, 1.5px `--ink` çerçeve, 3px köşe, soldan 6px'te boydan boya bir çizgi); düğme
  30 × 30, zemini saydam. Yazı yok: ne `‹` ne `›`. Adları bugünkü gibi `Hide the sidebar` /
  `Show the sidebar`.
- **Düğme kenar çubuğunun en altında, sağda.** Kendi satırında, `sidebar__foot`'ta: kenar çubuğunun
  son çocuğu, iki hâlde de. Satır sağa yaslı ve `margin-top: auto` ile en alta itilir — proje açık
  değilken sohbet listesi yokken de.
- **Katlanınca ikon sütunu:** proje açıkken en üstte `+` (`sidebar__new-chat sidebar__new-chat--icon`,
  30 × 30, adı `New chat`), basınca bugünkü `New chat` ne yapıyorsa o — kenar çubuğu katlı kalır. En
  altta aynı panel ikonu, `Show the sidebar`. Proje açık değilken `+` yok, yalnız panel ikonu —
  açıkken de `New chat` yalnız proje açıkken var. Projeler ve sohbetler katlı sütunda yok. Arama
  ikonu v9-2v'nin.
- **`Ctrl + .` her yerde açıp kapar**, yazma kutusunda yazarken de. Kutuya bir şey yazmaz: tuşun
  varsayılanı engellenir, kutunun metni değişmez. Tek başına `.` yalnız bir nokta — kenar çubuğuna
  dokunmaz.

**Yazmayla çakışmaması:** `Ctrl` basılıyken tarayıcı bir kutuya karakter yazmaz; `.` ancak `Ctrl`
ile birlikte gelince kısayoldur, ve o an varsayılanı engellenir. Kısayol `window`'daki tek dinleyicide
— App'in bugün Escape'i dinleyen dinleyicisinde ("One listener owns the keyboard") — okunur, ve olay
yazma kutusundan oraya kabarcıklanır. Yazma kutusunun kendi dinleyicisi yalnız Enter'e bakıyor.

## Testler ne tutar, ne tutmaz

**`Sidebar.test.jsx`** — düğme ve ikon sütunu:

| # | Ne |
|---|---|
| 1 | Açıkken kenar çubuğunun son çocuğu `sidebar__foot`, içinde `Hide the sidebar` |
| 2 | Katlıyken de son çocuk `sidebar__foot`, içinde `Show the sidebar` |
| 3 | Düğme bir panel ikonu: içinde `sidebar__panel-icon`, yazısı boş — `‹` ya da `›` yok |
| 4 | Katlı, proje açıkken: `New chat` adlı `sidebar__new-chat--icon` düğmesi, yazısı `+`; basınca `onNewChat` |
| 5 | Katlı, proje açık değilken: `New chat` yok, yalnız katlama düğmesi |

Değişen testler: *"folded, nothing is left but the way back"* artık doğru değil — katlı sütunda `+`
de var. Adı *"folded, the projects and chats are gone"* olur ve `New chat`'i sormaz (4 tutar).
*"the fold still leads the sidebar"* kalkar: 1 onun tersini tutar. Dosyanın başındaki Madde 51 notu
katlı şeridi *"the one thing that brings it back"* diye anlatıyor; ikon sütununa göre düzeltilir.

**`App.test.jsx`** — kısayol:

| # | Ne |
|---|---|
| 6 | Sohbette `window`'a `Ctrl + .` basınca kenar çubuğu katlanır (`Projects` gider, `Show the sidebar` gelir); yeniden basınca açılır |
| 7 | Yazma kutusunda, içinde `hello` varken `Ctrl + .`: kenar çubuğu katlanır, olayın varsayılanı engellenir, kutuda yine `hello` |
| 8 | Yazma kutusunda tek başına `.`: kenar çubuğu açık kalır |

**`workspace.css.test.js`** — tasarımın ölçüleri, kilit olarak:

| # | Ne |
|---|---|
| 9 | `.sidebar__foot` `display: flex`, `justify-content: flex-end`, `margin-top: auto` |
| 10 | `.sidebar__fold` 30 × 30, `background: transparent`; `font-size` yok (artık yazı değil) |
| 11 | `.sidebar__panel-icon` 16 × 16, `border: 1.5px solid var(--ink)`, `border-radius: 3px`; `.sidebar__panel-icon::after` `left: 6px`, `border-left: 1.5px solid var(--ink)` |
| 12 | `.sidebar__new-chat--icon` 30 × 30, `padding: 0`, `justify-content: center` |

Değişen test: *"both folding controls are big enough and dark enough to find"* iki kontrolü birlikte
`font-size: 20px` ile tutuyordu; kenar çubuğununki artık ikon. Test yalnız rayın `‹`'sini tutar, adı
*"the rail's folding control is big enough and dark enough to find"* olur; kenar çubuğunun düğmesini
10 ve 11 tutar. *"a folded sidebar is a strip"* (52, `overflow: hidden`, 220ms) aynen kalır.

**Tutmaz:** düğmenin ekranda gerçekten sağ altta durduğunu, katlı sütunda ortalandığını ve ikonun
çizildiğini — jsdom stil dosyasını yüklemez. O, Claude'un tarayıcısında görülür.

## Bu turda yazılmayanlar

- `Sidebar.jsx`, `App.jsx`, `workspace.css` değişmez; uygulama turunda.
- `dist` derlenmez: Claude birleştirirken derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` yeni testlerde kırmızı verir:
Sidebar'ın 1–4'ü, App'in 6 ve 7'si, stilin 9–12'si. 5 ve 8 bugün de yeşil: katlı şeritte bugün de
yalnız düğme var, ve kısayol yok; ikisi uygulama turunun bozmaması gerekeni tutar. Öteki üç satır
yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m351-katlama-testler-plan.md).
