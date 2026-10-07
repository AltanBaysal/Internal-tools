# Madde 338 — Üst çubuk · uygulama turu

**Kaynak:** [yol haritasının 338'i (v9-2a)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m338-ust-cubuk-testler-design.md) ve onun commit'lenmiş
kırmızı testleri. Tasarım: queen-design `queen-agent-v3`, 150, 159, 161, 166 — `shell.js`'in `bar()`'ı,
`kit.css`'in `.bar` kuralları, `DESIGN-STANDARD.md`'nin *Shell* ve *Bar*'ı.

**Kullanıcıdan gereken:** hiçbir şey.

## Yaklaşım

Tasarım çubuğu bir bileşen olarak çiziyor ve App'in bütün ekranlarının üstüne koyuyor; uygulama da
aynısını yapar. İki yol daha düşünüldü ve bırakıldı:

- **Çubuğu her ekranın kendi içinde çizmek** — üç ekran üç kopya, ve "her ekranda aynı yerde" bir
  kurala değil dikkate kalır. Çubuk App'te bir kez durur.
- **Çubuğu yeni bir `features/shell/` klasörüne koymak** (tasarımın `shell.js`'i böyle adlandırıyor) —
  CODE-STANDARD'a göre yeni bir feature ayrı bir sınırlı bağlam için açılır; çubuk projenin adını ve
  projeden çıkışı taşıyor, yani `workspace`'in. `shared/` de olmaz: orada hiçbir şey çizmez.

## Parçalar

**`features/workspace/Bar.jsx` (yeni).** `Bar({ project, onExit })`. Bir `header.bar`; içinde
`span.bar__name` — `span.bar__wordmark` (`QueenAgent`), bir boşluk, `span.bar__version`
(`VERSION`). `project` varsa `span.bar__project` (ad, `title`'ında da ad) ve
`button.ghost.bar__exit` (`Exit project`, basınca `onExit`). Yoksa ikisi de çizilmez. Nereye
çıkılacağını bilmez; App söyler. Sürüm Madde 209'un tek kaynağından, `shared/version.js`'ten gelir.

**`App.jsx`.** `app-shell`'in ilk çocuğu `<Bar project={project} onExit={() => navigate("/")} />`;
ardından `div.app-shell__body` — içinde bugünkü `Sidebar` ve `main`, değişmeden. `ConfirmDialog`
yerinde, gövdenin dışında kalır: karartması hâlâ bütün pencereyi örter, çubuk dahil.
`project` App'in zaten bulduğu proje: adresin projesi listede varsa. `/`'a gitmek açılışa dönmek —
çatal ilk projeye iner ya da proje yoksa boş ekranı gösterir; kural yine tek yerinde, çatalda.

**`Sidebar.jsx`.** `sidebar__brand` bloğu ve `VERSION` importu kalkar; katlama düğmesi (`Fold`)
kenar çubuğunun ilk çocuğu olur. Düğmenin kendisi ve davranışı değişmez.

**`workspace.css`.** Sidebar'ın dört kuralı — `.sidebar__brand`, `.sidebar__wordmark`,
`.sidebar__name`, `.sidebar__version` — kalkar. Dosyanın başına, `.main`'in altına, kendi başlığıyla
çubuğun dört kuralı gelir, `kit.css`'teki değerlerle:

- `.bar` — 56 yüksek, `flex: none`, üç sütunlu ızgara `minmax(0, 1fr) minmax(0, auto) minmax(0,
  1fr)`, `gap: 16px`, `padding: 0 12px`, `--sidebar` zemin, altında `--line` çizgi.
- `.bar__name` — `var(--font-heading)`, 21, `letter-spacing: 0.2px`, `white-space: nowrap`. Renk
  yazılmaz: gövdenin `--ink`'i.
- `.bar__version` — yalnız `font-weight: 400`.
- `.bar__project` — ortada, en çok 640, tek satırda kesilir, `500 18px` Newsreader, `--ink`.
- `.bar__exit` — `grid-column: 3`, `justify-self: end`.

`.sidebar__fold`'un yorumu bugünü söyler: artık bir markanın yanında değil, kenar çubuğunun başında;
`margin-left: auto` onu sütun düzeninde sağa yaslar.

**`app.css`.** `.app-shell`'e `flex-direction: column`; altına `.app-shell__body` — `flex: 1`,
`min-height: 0`, `display: flex`, `overflow: hidden`. Kabuk yine pencerenin boyu ve kaymaz; kayan
yalnız içteki bölgeler.

**`shared/version.js`.** Yorumu "kenar çubuğu çizer" diyor; "çubuk çizer" olur.

**`App.test.jsx`'in bir eski testi.** *"a renamed project shows the new name in both places at once"*
yeni adı ekranda iki kez sayıyor: başlık ve kenar çubuğunun satırı. Proje ekranında ad artık çubukta
da duruyor, aynı diziden okunarak; test üç yeri sayar, ve adı *"in every place at once"* olur. Test
turunda gözden kaçtı, ilk yeşil koşuda göründü.

## Bu turda yapılmayanlar

- `dist` derlenmez; Claude birleştirirken derler.
- Sohbet başlığındaki `← proje /` yerinde (v9-2d); proje ekranı yerinde (v9-2n); katlama düğmesi
  yerinde (v9-2w).

## Nasıl görülür

Dört satır yeşil: queen-agent'ın ön ucunda test turunun on beş iddiası, geri kalan her şeyle birlikte;
queen-editor'ün arka ucu 377'nin bilinen iki kırmızısıyla.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m338-ust-cubuk-uygulama-plan.md).
