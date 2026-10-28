# Madde 353 — All projects ekranı · test turu

**Kaynak:** [yol haritasının 353'ü (v9-2n)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de (29 Eylül: sohbet silme kalkar), tasarımı queen-design'ın `queen-agent-v3` dalında 135, 142,
165, 167, 170 — `projects/queen-agent/projects/index.html`, `BEHAVIOUR.md`'nin *The walk* ve *All
projects* bölümleri, `DESIGN-STANDARD.md`'nin *All projects*'i ve `kit.css`'in `.all-projects__*`
kuralları. Üstüne kurulduğu: 338 (üst çubuk, `Exit project`), 339 (`pinned`, `archived`), 346
(`lastActivity`, sabitlenenler önde sonra son kullanılan sırası).

**Kullanıcıdan gereken:** hiçbir şey. Koşu subagent'ta; iki yöne okunabilen kararlar aşağıda
*Kararlar*'da yazılı ve raporda Claude'a gider.

## Ne kanıtlanacak

Uygulama All projects ile açılıyor, ekranda kenar çubuğu yok; sabitlenenler üstte `PINNED`, sonra son
kullanılanlar `RECENT`; her satırda ad, `N chats · N files` ve son kullanıldığı an; satıra basınca
projenin son sohbeti, sohbeti yoksa boş sohbeti açılıyor; proje yoksa `No projects yet.`. Proje
ekranı, "No projects yet" ekranı, ilk yüklemenin parlayan iskeleti ve sohbet silme — ekranda ve
sunucuda — yok. `Exit project` All projects'e dönüyor.

## Kararlar

1. **`/` bir ekran, çatal değil.** Bugün `/` listeyi okuyup ilk projeye atlıyor, proje yoksa boş ekranı
   çiziyor. Artık All projects'i çizer ve hiçbir yere atlamaz; bilinmeyen bir adres de (`/settings`)
   aynı ekranı çizer, çünkü `parsePath` onu `/` okur.
2. **`/p/<id>`'nin kendi ekranı yok** (tasarım 170): projenin son sohbetini, yoksa boş sohbetini açar,
   ve kendi girdisinin üstüne yazar — geri tuşu All projects'e döner, `/p/<id>`'ye takılmaz. Satıra
   basmak `/p/<id>`'ye gider (tarihe yazılır), kenar çubuğundaki proje satırı da (362'ye kadar duruyor),
   elle yazılan adres de; üçü tek yoldan açılır. "Son sohbet" sunucunun sohbet listesinin ilki — sıra
   sunucunun (`list_chats`), ekran yalnız ilkini alır.
   - **Listeyi kendisi okur.** `useProjectChats`'in listesi proje değişince yeni cevap gelene kadar
     önceki projenin satırlarını tutuyor ve yüklenmiyor görünüyor; ona bakan bir çatal başka projenin
     sohbetini açardı.
   - **Cevap gelmeden ayrılan kullanıcı** gittiği yerde kalır: gelen cevap onu geri çekmez.
   - **Liste gelmiş ve proje onda yoksa** `That project does not exist.` kalır — elle yazılmış yanlış
     bir adres ayakta kalabilsin. Okuma başarısız olursa ekran sunucunun sözünü yazar; boş sohbete
     düşmez, çünkü o "sohbeti yok" demek olurdu.
3. **`+ New project` bugünkü gibi oluşturur** — `POST /api/projects`, ad sormadan (`New project N`) —
   **ve yeni projenin boş sohbetini açar** (`/p/<id>/c/new`). "Proje açar" ve 361'in de oraya
   götürmesi. Oluşturduktan sonra liste sunucudan yeniden okunur: yeni proje listenin sonuna
   eklenirse All projects'e dönünce en altta durur, oysa sunucunun sırasında en üstte.
4. **Yüklenirken** başlık ve `+ New project` yerinde, listenin yerinde hiçbir şey — ne iskelet ne
   `No projects yet.` (henüz bilinmiyor). Spinner 364'ün.
5. **Liste okunamayınca** ekran tasarımın *failed* hâlinin kalıbında: `.empty` içinde `.empty__error`,
   sunucunun kendi sözüyle. Cümle, `Try again` ve `Copy` 364'ün.
6. **Bölümler:** `pinned` olanlar `Pinned`, ötekiler `Recent` altında, sunucunun sırasıyla; yazı
   tasarımdaki gibi `Pinned` / `Recent`, büyük harfi CSS verir (`text-transform: uppercase`). Satırı
   olmayan bölüm çizilmez. Arşivdekiler ayrılmaz — sekme 363'ün.
7. **Satır:** `.all-projects__row` içinde tek düğme `.all-projects__row-open`: ad, `N chats · N files`
   (tek olan tekil: `1 chat · 1 file`), ve `relativeTime(lastActivity)`. `⋯` yok (360), arama yok
   (359). Tekil/çoğul kuralı onay penceresininkiyle aynı; iki yer tek fonksiyonu kullanır.
8. **İçinde bulunulan proje silinince** All projects'e dönülür (bugün "kalan ilk projeye" gidiyordu;
   o kuralı yazan çatal kalktı). Başka bir proje silinince yer değişmez.
9. **Olmayan bir sohbetin `← back`'i** All projects'e götürür (tasarım 170); bugün proje ekranına
   götürüyordu.
10. **Sohbet silme kalkar.** Ekranda tek yeri proje ekranının `×`'iydi; sunucunun kapısı
    (`DELETE /api/projects/<id>/chats/<id>`), `delete_chat` use case'i, `ChatStore.delete` portu ve
    `FileChatStore.delete` ölü kod olur ve kalkar. Kapı kalkınca aynı adrese `DELETE` 405 döner — adres
    `GET` için duruyor. CODE-STANDARD'ın çöp satırı "on a file's delete" olur (uygulama turunda).
11. **Proje ekranıyla gidenler:** `ProjectScreen`, `NoProjectsScreen`, App'in ilk yükleme iskeleti ve
    `.skeleton--screen`; yalnız proje ekranının kullandığı CSS (`.screen-layout`, `.project-grid`,
    `.chat-list`, `.chat-row*`, `.column__title`, `.screen__title-row`, `.screen__delete`,
    `.file-list__bar`, `.panel` ve dar adımdaki kuralları); `NoProjectsScreen`'in `.empty__title` ve
    `.empty__line`'ı. `FilePanel`'in `×`'i ve `back` seçeneği de: yalnız proje ekranının paneli
    kapanıyordu, rayınki hep geri dönüyor (testi zaten "until the project screen goes" diyor);
    `.reader__close` onunla gider.
12. **Kalanlar:** `Skeleton.jsx` sohbet ekranında hâlâ kullanılıyor; o yeri 355 kaldırıyor. İkisi
    birleşince `Skeleton` ve `.skeleton*` ölü kalır — raporda.

## Testler ne tutar

### Sunucu

**`test_chats_api.py`** — sohbet silen üç test (`test_a_chat_can_be_deleted_and_stops_being_listed`,
`test_deleting_a_chat_leaves_the_project_its_files`, `test_deleting_a_chat_that_is_not_there_is_a_404`)
kalkar; yerine:

| # | Ne |
|---|---|
| S1 | `test_a_chat_cannot_be_deleted` — `DELETE .../chats/<id>` 405, ve sohbet listede, kaydı okunuyor |

**`test_delete.py`** — sohbet silen beş test ve `_seeded` kalkar; dosyanınkiler kalır. Yerine:

| # | Ne |
|---|---|
| S2 | `test_the_delete_chat_use_case_is_gone` — modül `ModuleNotFoundError` verir (`rename_chat`'in kalıbı) |
| S3 | `test_neither_the_chat_store_nor_its_port_can_delete` — `FileChatStore` ve `ChatStore` `delete` taşımıyor |

### Ön uç — yeni `AllProjectsScreen.test.jsx`

| # | Ne |
|---|---|
| A1 | Başlık `All projects` (`.screen__title`) ve `+ New project` (`.empty__action`); basınca `onNewProject` |
| A2 | Sabitlenenler `Pinned` altında, ötekiler `Recent` altında, verilen sırayla |
| A3 | Sabitlenen yoksa `Pinned` bölümü yok |
| A4 | Satır adı, `3 chats · 2 files` ve `2h ago`'yu söylüyor; tek olan tekil: `1 chat · 1 file` |
| A5 | Satıra basınca `onOpenProject(id)` |
| A6 | Proje yoksa `No projects yet.` |
| A7 | Yüklenirken başlık ve `+ New project` duruyor, satır ve `No projects yet.` yok |
| A8 | Okunamayınca sunucunun sözü, `No projects yet.` ve başlık yok |
| A9 | Satırda `⋯` yok, ekranda arama kutusu yok |

### Ön uç — `App.test.jsx`

**Yeni ya da yeniden yazılan** (bugünkü kodda kırmızı):

| # | Ne |
|---|---|
| B1 | Uygulama `/`'de All projects ile açılıyor, adres `/` kalıyor, kenar çubuğu yok, satırda proje |
| B2 | İlk liste yüklenirken çubuk gövdenin üstünde, gövdede kenar çubuğu ve iskelet yok, `All projects` başlığı var; cevap gelince `No projects yet.` |
| B3 | Proje yoksa `No projects yet.`, adres `/`, `New chat` yok |
| B4 | `Exit project` All projects'e döner: adres `/`, başlık `All projects` |
| B5 | Satıra basınca projenin son sohbeti açılıyor (listenin ilki), adres `/p/p1/c/c2` |
| B6 | Sohbeti olmayan projenin satırı boş sohbeti açıyor, `/p/p1/c/new` |
| B7 | Satırın açtığı yol tarihe bir kez yazılıyor: `/p/p1` push, sohbetin adresi replace |
| B8 | Elle yazılan `/p/p1` son sohbete gidiyor |
| B9 | Sohbet listesi gelmeden `Exit project`'e basan `/`'de kalıyor |
| B10 | `+ New project` projeyi oluşturup boş sohbetine götürüyor; `Exit project`'ten sonra yeni proje listenin başında (sunucunun sırası) |
| B11 | İçinde bulunulan proje silinince All projects |
| B12 | Olmayan sohbetin `← back`'i `/`'e götürüyor |
| B13 | `/settings` All projects'i çiziyor |

**Kalkan** (tuttukları ekran ya da davranış kalktı): kök çatalın iki testi (*the fork asks the
browser…*, *the fork is not written into the history* — yerine B7, B9); proje ekranının seçicisine
dair *a skill can be picked before anything is typed*; *the draft chat is still reached from the
sidebar* (açılış artık proje ekranı değil; `New chat` testi aynı şeyi tutuyor); sohbet silen üç test
ve `withChats`; *opening a file unfolds the rail…* (katlanmış rayla dosyayı açmanın ikinci yolu proje
ekranıydı; kalan yol, transkriptteki kart, kendi testinde); *the first load is one skeleton…* ve
*no screen is drawn while the list is still on its way* (yerine B2).

**Taşınan** (bugün de yeşil; proje ekranında duruyorlardı, aynı iddia başka bir yerde): proje silmenin
testleri, yeniden adlandırma ve boş ad, dosya silme ve okuma, `Refresh`, `Escape` ile panel, çevrimdışı
kutu, modelin ve beceri seçiminin ilk mesajla gitmesi `/p/p1/c/new`'e — boş sohbetin de rayı, seçicileri
ve kutusu var; kenar çubuğunun menüsü 362'ye kadar duruyor. Proje ekranında panel `×` ile kapanıyordu,
rayda `←` ile döner. Proje ekranının `Delete`'i gidince *the sidebar menu and the header open the same
question* yalnız menüyü tutar; *no row anywhere offers a rename* projenin kendi `Rename`'ini aramaz;
*a renamed project…* iki yerde (kenar çubuğu, üst çubuk) sayar. *the sidebar folds away…* katlı hâli
`Exit project` yerine `New chat` ile başka bir adrese taşır — All projects'te kenar çubuğu yok.
*a skill picked in a chat does not ride into a chat born on the project screen* boş sohbette doğan
sohbete göre yazılır. `No projects yet` geçen tam eşleşmeler `No projects yet.` olur.

### Ön uç — öteki dosyalar

- **`FilePanel.test.jsx`:** `×`'in iki testi kalkar; *the rail's panel comes back* `back` vermeden
  çizer (kırmızı: bugün `back` yoksa `×` çiziliyor). Öteki testlerdeki `back` kalkar.
- **`ProjectScreen.test.jsx`, `NoProjectsScreen.test.jsx`** — ekranlarıyla birlikte silinir.
- **`Skeleton.test.jsx`:** `screen` varyantının testi kalkar.
- **`Composer.test.jsx`:** *the project screen's button…* (`Start`) kalkar.
- **`workspace.css.test.js`:** proje ekranının kurallarını tutan testler kalkar (dar adımdaki
  `.screen-layout`, `.panel`, `.project-grid`; `.screen__title-row`, `.screen__delete`; `.chat-row`;
  `.skeleton--screen`'in iki testi; `.panel`'in padding'i — `.rail--open`'ınki kalır). Yeni:
  - C1 — proje ekranının, "No projects yet" ekranının ve `×`'in kuralları hiçbir adla yok (satır başı
    taranır, `.rail__list` testi gibi).
  - C2 — `PINNED`/`RECENT` tasarımın `.d-label`'ı: 11px, `0.09em`, uppercase, `#6b6259`.
  - C3 — satır 48 yüksek, altında `#e9e3da` çizgi; liste üstünde aynı çizgi.
  - C4 — zaman tek sabit sütun: 96 genişlik, sağa yaslı, mono.
  - C5 — başlık satırı: flex, `space-between`, altında 24.
  - C6 — `No projects yet.` tasarımın `.all-projects__empty`'si: `padding: 18px 12px`, `#a79e93`.
  - Dar adımın `.chat-row__when`'i kalkar; `.screen__title`'ın 27'si kalır (All projects'in başlığı).

## Tutmadıkları

- Arama (359), `⋯` menüsü (360), ad sorma ekranı (361), kenar çubuğunun değişmesi (362), arşiv (363),
  spinner ve `Couldn't load projects.` (364).
- `dist` — Claude derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `python -m pytest queen-agent -q` S1–S3'te,
`npm test --prefix queen-agent/frontend` A1–A9, B1–B13'ün bugünkü kodla çelişenlerinde, FilePanel'in
`back`'siz testinde ve C1–C6'da kırmızı; queen-editor'ün iki süiti yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m353-all-projects-testler-plan.md).
