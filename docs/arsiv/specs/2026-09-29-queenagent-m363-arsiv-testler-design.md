# Madde 363 — Arşiv · test turu

**Kaynak:** [yol haritasının 363'ü (v9-2t)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de, tasarımı queen-design'ın `queen-agent-v3` dalında 135 (*Archive onaysız ve "Undo" ile geri
alınır*; *"All projects" sayfası: arama, "Archived" sekmesi, arşivden geri almak*), 161 (*işler
projenin dışında*), 190 (*`Archive` sonrası projenin yerinde `<ad> archived · Undo`*) ve 191
(*arşivdeki satırda yalnız `⋯`; menü `Rename`, `Unarchive`, çizgi, `Delete`*) —
`projects/queen-agent/projects/index.html` (`menuHtml`, `rowHtml`, `archivedRowHtml`,
`projectsWithUndo`, `bodyHtml`, `frameHtml`, `paintCounts`, `settleUndoing`, `act`),
`BEHAVIOUR.md`'nin *All projects*'i, `DESIGN-STANDARD.md`'nin *All projects*'i ve `kit.css`'in
`.all-projects__tabs`, `.all-projects__tab`, `.all-projects__count`, `.all-projects__row-text`,
`.all-projects__undo` kuralları. Üstüne kurulduğu: 339 (`PATCH /api/projects/<id>` `archived` alır;
liste her projenin `archived`'ını söyler; arşiv sabitlemeye dokunmaz), 346 (listenin sırası
sunucunun), 353 (`AllProjectsScreen`), 359 (arama, `ProjectList`), 360 (`ProjectRow`, `⋯` menüsü,
`Menu`'nün `divided`'ı, `useProjects.editProject` PATCH'ten sonra listeyi yeniden okur).

**Kullanıcıdan gereken:** hiçbir şey. Sunucu 339'da hazır; bu parça yalnız ön uç. Koşu subagent'ta;
iki yöne okunabilen kararlar aşağıda *Kararlar*'da yazılı ve raporda Claude'a gider.

## Ne kanıtlanacak

All projects'te aramanın sağında iki sekme: `Projects` ve `Archived`, her biri sayısıyla. `Projects`
arşivde olmayanları gösterir, `Archived` arşivdekileri. Satırın `⋯`'sinde `Archive` var, çizginin
üstünde: proje onaysız arşive gider ve yerinde `<ad> archived · Undo` satırı kalır; `Undo` onu eski
yerine koyar. Arşivdeki satır açılmaz; `⋯`'sinde `Rename`, `Unarchive`, çizgi, `Delete`. `Unarchive`
projeyi `Projects`'e geri koyar. Arşiv boşken `No archived projects.`; hepsi arşivdeyse
`Every project is archived.`

## Kararlar

1. **İki sekme, ikisi de sayısıyla** — tasarımın `frameHtml`'i: `Projects <n>` ve `Archived <n>`,
   aramanın sağında, `.all-projects__tools`'un içinde. Satır yalnız *`Archived` sekmesi sayısıyla*
   diyor; `Projects` sekmesi olmadan `Archived`'dan dönülemez, o yüzden tasarımınki alınır. Sayılar
   listenin `archived` alanından: `Projects` arşivde olmayanları, `Archived` arşivdekileri sayar.
   Açık sekme `is-on` sınıfını taşır. Ekran `Projects`'le açılır.
2. **Sekme ekranın kendi durumu**, arama gibi (359): adrese ve sunucuya gitmez; All projects'ten
   çıkıp dönünce `Projects`'le açılır. Tasarım sekmeyi adresten okuyor, ama bunu tuvalin kartı
   basamadığı için yapıyor (`BEHAVIOUR.md`).
3. **Liste yüklenirken sekmeler durur, sayıları yazmaz** — tasarımın `paintCounts`'u yalnız liste
   gelince sayar. Gelmemiş listenin sayısı `0` değil, bilinmiyor. (Spinner ve hata 364'ün.)
4. **Arama iki sekmede de aynı kutu**: yazılan sekme değişince kalır, ve açık sekmenin listesini
   daraltır — tasarımın `bodyHtml`'i.
5. **Boş cümleler, tasarımın `bodyHtml`'i sırasıyla:**
   - Hiç proje yoksa — arşivdekiler de yoksa — iki sekmede de `No projects yet.`
   - Arama bir şey bulmazsa `No projects match "…".`
   - `Archived`'da arşiv boşsa `No archived projects.`
   - `Projects`'te bütün projeler arşivdeyse `Every project is archived.`
6. **`Archived`'ın listesi bölümsüz tek liste**, sunucunun sırasıyla: `PINNED` / `RECENT` başlığı yok.
   Sunucu arşivde de sabitlemeyi tutuyor (339: *the archive leaves the pin alone*), o yüzden arşivdeki
   sabitli bir proje bu listede önde durur; sırayı ekranda yeniden kurmak sunucunun kuralını
   kopyalamak olurdu (FOUNDATION, Karar 4). Tasarım arşivde sabitlemeyi siliyor ve bu listeyi yalnız
   son kullanıma göre diziyor — iki yöne okunabilir, raporda.
7. **Arşivdeki satır açılmaz** (tasarım 135, `kit.css`: *an archived project does not open*): açan
   düğmenin yerinde aynı üç sütunlu bir `.all-projects__row-text`; `⋯`'si var.
8. **Menüler, tasarımın `menuHtml`'i:** arşivde olmayan satırda `Rename`, `Pin`/`Unpin`, `Archive`,
   çizgi, kırmızı `Delete`; arşivdekinde `Rename`, `Unarchive`, çizgi, kırmızı `Delete`. Arşivdeki
   satırın `Rename`'i ötekinin gibi yerinde çalışır.
9. **`Archive` onaysız:** `PATCH /api/projects/<id>` `{ "archived": true }`, pencere yok. Proje
   `Projects`'ten gider, ama yerinde — aynı bölümde, aynı sırada — `.all-projects__undo` satırı durur:
   `<strong>ad</strong> archived · Undo`. Satır basıldığı anda çıkar, liste sunucudan geri gelmeden;
   `Undo` odağı alır (tasarımın `act("archive")`'ı). Sabitli bir proje arşivlenince satırı `PINNED`'da
   kalır: sunucu sabitlemeyi tutuyor, o yüzden liste onu yine orada veriyor.
10. **`Undo`** `PATCH` `{ "archived": false }` gönderir. Liste sunucudan geri gelene kadar `Undo`
    satırı yerinde kalır, sonra satır eski hâline döner — araya satırın kaybolduğu bir an girmez.
    Sabitli proje `PINNED`'a döner.
11. **`Undo` satırı ne zaman gider** — tasarımın `settleUndoing`'i, *bir sonraki iş*: başka bir satırın
    `⋯`'si açılınca (Rename, Pin, Archive, Delete hep oradan geçer), sekme değişince, ve ekrandan
    çıkınca. Yazıldığı gibi yalnız bir satır: yeni bir `Archive` öncekinin `Undo`'sunu — `⋯` açılırken
    — zaten kaldırmış olur. Arama yazmak onu kaldırmaz (tasarım da kaldırmıyor); arama onu adıyla
    daraltır.
12. **`Unarchive`** `PATCH` `{ "archived": false }` gönderir; `Undo` satırı bırakmaz. Proje `Archived`'dan
    gider ve `Projects`'te sunucunun koyduğu yerde durur.
13. **Arşivdeki satırın `Delete`'i** bugünkü onay penceresi, sayılarıyla — öteki satırınki gibi.
14. **361'in ad sorma ekranı arşivdekileri de sayar, ve bu doğru okunuyor:** bütün projeler
    arşivdeyken `+ New project` `Name your project` der ve `Cancel` sunar — ilk proje değil, ve
    dönülecek All projects var (orada `Every project is archived.` yazıyor). Değişmez; bir test tutar.
15. **Kenar çubuğunun proje listesi** arşivdekileri de gösteriyor; 362 o listeyi kaldırıyor, bu parça
    dokunmaz.

## Testler ne tutar

### Ön uç — `ProjectRow.test.jsx`

**Değişen:** R2 ve R3 — menüler `["Rename", "Pin", "Archive", "Delete"]` ve
`["Rename", "Unpin", "Archive", "Delete"]`; çizgi yine yalnız `Delete`'in üstünde. Dosyanın başındaki
yorum `Archive`'ı da sayar.

| # | Ne |
|---|---|
| P1 | `Archive` → `onArchive("p2", true)` |
| P2 | Arşivdeki satırda açan düğme yok: `.all-projects__row-text` adı, `1 chat · 1 file`'ı ve anı taşıyor; basmak `onOpen`'ı çağırmıyor; `⋯` var |
| P3 | Arşivdekinin menüsü `["Rename", "Unarchive", "Delete"]`; `Delete` kırmızı, üstünde tek çizgi |
| P4 | `Unarchive` → `onArchive("p2", false)` |
| P5 | Arşivdeki satırda `Rename` yerinde: alan, Enter → `onRename("p2", "Harbour")` |

### Ön uç — `AllProjectsScreen.test.jsx`

Yeni sabit: `SHELVED` — arşivde, sabitsiz bir proje. *the search stands under the head* testinin
yorumu sekmeleri söyler.

| # | Ne |
|---|---|
| T1 | Aramanın satırında, kutudan sonra `.all-projects__tabs`: `Projects 2` ve `Archived 1` (`.all-projects__tab`, sayı `.all-projects__count`'ta); `Projects` `is-on` |
| T2 | `Projects`'te arşivdeki proje yok; `Pinned` / `Recent` yalnız ötekilerden |
| T3 | `Archived`'a basınca yalnız arşivdekiler, tek `.all-projects__list`'te, başlıksız; satırı `.all-projects__row-text`; `Archived` `is-on`, `Projects` değil; geri basınca `Projects` listesi |
| T4 | Arşiv boşken `Archived`'da `No archived projects.` |
| T5 | Hepsi arşivdeyse `Projects`'te `Every project is archived.`; `Archived`'da hepsi |
| T6 | Hiç proje yokken iki sekmede de `No projects yet.` ve sayılar `0` |
| T7 | `Archived`'da arama arşivdekileri daraltır; bulamazsa `No projects match "zzz".`; yazılan sekme değişince kutuda kalır |
| T8 | Liste yüklenirken iki sekme duruyor, sayıları boş |
| U1 | `Archive` → `onArchiveProject("p2", true)`; liste daha değişmeden projenin yerinde `.all-projects__undo`: `Night market archived · Undo`, `Recent`'te aynı sırada; odak `Undo`'da; pencere yok |
| U2 | Liste proje arşivde diye gelince de `Undo` satırı yerinde; sayılar `Projects 2` / `Archived 1` gibi arşive göre |
| U3 | Sabitli proje arşivlenince `Undo` satırı `Pinned`'da |
| U4 | `Undo` → `onArchiveProject("p2", false)`; cevap gelene kadar `Undo` satırı duruyor; liste arşivsiz gelince satır eski hâlinde, `Undo` yok |
| U5 | Başka bir satırın `⋯`'si açılınca `Undo` satırı gidiyor, arşivdeki proje `Projects`'te yok |
| U6 | Sekme değişip geri gelince `Undo` satırı yok |
| U7 | `Archived`'daki satırın `Unarchive`'ı → `onArchiveProject(id, false)`; `Undo` satırı çıkmıyor |

### Ön uç — `App.test.jsx`

`serverForRows`'un sahte sunucusu `archived`'ı da tutar: PATCH gövdeyi projeye katıyor zaten; arşiv
sırayı ve sabitlemeyi değiştirmez. Yardımcı `tab(name)` sekmeye basar.

| # | Ne |
|---|---|
| B1 | `Archive` onaysız: `PATCH /api/projects/p2 {archived: true}`, pencere yok; `Notes archived · Undo` `Recent`'te, `Thesis`'in altında; sekmeler `Projects 1`, `Archived 1` |
| B2 | `Undo` → ikinci PATCH `{archived: false}`; `Notes` `Recent`'te eski yerinde, `Undo` yok; `Projects 2`, `Archived 0` |
| B3 | Sabitli proje arşivlenip `Undo`'yla dönünce yine `Pinned`'da |
| B4 | Arşivdeki proje yalnız `Archived`'da; `Unarchive` → `PATCH {archived: false}`; `Archived`'da `No archived projects.`, `Projects`'te proje sunucunun yerinde |
| B5 | Arşivdeki satırın `Delete`'i sorar: `Delete "Notes"?`, sayılarıyla; onay `DELETE /api/projects/p2` |
| B6 | Bütün projeler arşivdeyken All projects `Every project is archived.` der; `+ New project` `Name your project` ve `Cancel` (Karar 14) |

### Ön uç — CSS kilitleri (`workspace.css.test.js`)

| # | Ne |
|---|---|
| C1 | `.all-projects__tab`: `padding: 7px 12px`, `font-size: 13px`; `.all-projects__tab.is-on`: `background: #e5dfd5`; `.all-projects__count`: `var(--font-mono)`, `11px` |
| C2 | `.all-projects__row-text`: `flex: 1`, `min-width: 0` — açan düğmenin sütunları |
| C3 | `.all-projects__undo`: `color: #6b6259`; `.all-projects__undo button`: `color: var(--accent)` — satırın tek işi |

## Tutmadıkları

- Yüklenirken spinner, okunamayan listenin cümlesi, `Try again` ve `Copy` (364).
- Kenar çubuğunun proje listesi (362 kaldırıyor), arşivdeki bir projenin adresle açılması (bugünkü
  gibi açılır; tasarım bunu söylemiyor).
- Aramada Enter'ın ilk eşleşmeyi açması — tasarımda var, 359'un satırında yok; bu parçanın da değil.
- Yazma başarısız olunca ne olduğu: `editProject` bugünkü gibi hatayı ekrana verir.
- `dist` — Claude derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` P1–P4, R2–R3, T1–T8,
U1–U7, B1–B6 ve C1–C3'te kırmızı — 30 test; P5 bugün de yeşil, çünkü yerinde rename 360'ta var ve
bugünkü satır arşivi bilmeden onu da çiziyor. Öteki üç süit yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m363-arsiv-testler-plan.md).
