# Madde 360 — Satırın `⋯` menüsü: Rename, Pin, Delete · test turu

**Kaynak:** [yol haritasının 360'ı (v9-2q)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de, tasarımı queen-design'ın `queen-agent-v3` dalında 135 (*Rename yerinde; Delete onay ister,
sohbet ve dosya sayısını söyler*), 161 (*`⋯` menüsünün tamamı proje içinden kalkar*) ve 167 —
`projects/queen-agent/projects/index.html` (`menuHtml`, `rowOpenHtml`, `moreHtml`, `act`,
`settleRename`, rename alanının tuşları), `BEHAVIOUR.md`'nin *All projects*'i, `DESIGN-STANDARD.md`'nin
*All projects*'i ve `kit.css`'in `.all-projects__row-more`, `.all-projects__row .menu`,
`.all-projects__rename`, `.menu__divider` kuralları. Üstüne kurulduğu: 339 (`PATCH /api/projects/<id>`
`pinned` alır), 346 (sabitlenenler sabitlendikleri sırayla önde, sonra son kullanılan), 353
(`AllProjectsScreen`, satır projeyi açan düğme, `countOf`).

**Kullanıcıdan gereken:** hiçbir şey. Koşu subagent'ta; iki yöne okunabilen kararlar aşağıda
*Kararlar*'da yazılı ve raporda Claude'a gider.

## Ne kanıtlanacak

All projects'te her satırın sonunda bir `⋯` var; menüsünde `Rename`, `Pin` ya da `Unpin`, bir çizgi ve
kırmızı `Delete`. `Rename` satırın adını yerinde bir alana çevirir: Enter ya da başka bir yere basmak
kaydeder, Esc vazgeçer, boş ad hiçbir şey göndermez. `Pin` projeyi `PINNED`'a alır, `Unpin` sunucunun
koyduğu yere geri koyar. `Delete` bugünkü onay penceresini açar, sohbet ve dosya sayısıyla; onaylanınca
proje listeden gider. Projenin içinde — kenar çubuğunda — hiç `⋯` yok, ve ad tarayıcının kutusuyla
(`window.prompt`) hiçbir yerde sorulmaz.

## Kararlar

1. **Kenar çubuğunun `⋯`'si ve menüsü bu parçada kalkar** (satır: *Projenin içinde hiç `⋯` yok*;
   tasarım 161). Kenar çubuğunun proje listesi 362'ye kadar durur, yalnız satırın `⋯`'si gider;
   satır yine projeyi açan tek düğme. `window.prompt`'lu yeniden adlandırma da onunla gider: tek
   çağıranı o menüydü.
2. **Menü tasarımın sırasıyla:** `Rename`, `Pin` (sabitliyse `Unpin`), bir çizgi, `Delete`. `Archive`
   363'ün; bu parçada menüde yok. Çizgi `Menu`'nün yeni bir seçeneği: bir öğe üstünde çizgiyle
   ayrılabilir (`.menu__divider`, tasarımın kuralı). Bugün hiçbir menüde çizgi yok.
3. **`⋯`'nin adı tasarımın: `Actions for <ad>`.** Kenar çubuğununki `More for <ad>`'dı; o gidiyor.
   Satırın açan düğmesinin adı projenin adıyla *başladığı* için testler onu `/^Ad/` ile arar —
   `⋯`'nin adı da adı içeriyor.
4. **Menü App'in `menuFor`'unda açılır**, kenar çubuğununki gibi: Escape App'in tek dinleyicisinin, ve
   o yalnız gördüğünü kapatabilir. Aynı anda tek menü açık; açık olanın satırında `.menu` var.
5. **Rename yerinde** (tasarım 135, `BEHAVIOUR.md`: *Renaming here is in place, not the browser's
   `prompt()`*): açan düğmenin yerine `.all-projects__rename` alanı gelir, adı `Project name`, içinde
   projenin adı, odak onda; `⋯` yerinde kalır.
   - **Enter** yazılanı kaydeder ve alanı kapatır. **Başka bir yere basmak** (alanın odağı gitmesi)
     da kaydeder — tasarımın `settleRename`'i: *never silently dropped*.
   - **Esc** hiçbir şey göndermez, alan kapanır, ad eskisi.
   - **Boş ad** (yalnız boşluk) hiçbir şey göndermez; alan kapanır, ad eskisi. Sunucu da boş adı
     reddediyor; kural oradadır, burası isteği hiç atmaz.
   - Enter'dan sonra odağın gitmesi ikinci bir istek atmaz: bir rename bir istektir.
   - Aynı adla kaydetmek istek atar — tasarım da atıyor; ayırmak bir parça daha olurdu.
6. **Pin/Unpin** `PATCH /api/projects/<id>` `{ "pinned": true | false }` gönderir, sonra listeyi
   sunucudan yeniden okur: nereye gideceği sunucunun sırası (`list_projects.py`) — sabitlenen
   sabitlenenlerin sonuna, bırakılan son kullanıldığı yere. Yerinde değiştirmek bırakılanı
   `RECENT`'in başına koyardı.
7. **Delete bugünkü onay penceresi:** başlık `Delete "<ad>"?`, gövde `The N chats and N files in this
   project are deleted with it. This can't be undone.` Onay düğmesi tasarımın All projects sayfasındaki
   gibi **`Delete`** (`projects/index.html`: `confirmLabel: "Delete"`); bugün `Delete project`'ti.
   İki yöne okunabilir — satır *bugünkü onay penceresi* diyor, tasarımın sayfası düğmeyi `Delete`
   yazıyor — raporda.
8. **Silinen projenin içinde durulmuyor artık:** silmenin tek yeri All projects ve orada açık proje
   yok. *İçinde bulunulan proje silinince All projects'e dönülür* ve *başka proje silinince yer
   değişmez* testleri, tuttukları durum kalmadığı için kalkar.

## Testler ne tutar

### Ön uç — yeni `ProjectRow.test.jsx`

Satır kendi dosyasında (`ProjectRow.jsx`): `AllProjectsScreen.jsx`'i 359 ve 361 de değiştiriyor, ve
menüyle yeniden adlandırma satırın kendi işi.

| # | Ne |
|---|---|
| R1 | Satırda `Actions for <ad>` adlı bir `⋯` (`.all-projects__row-more`); basınca `onOpenMenu(id)`, proje açılmaz |
| R2 | Menü açıkken sırasıyla `Rename`, `Pin`, `Delete`; `Archive` yok; `Delete` kırmızı ve üstünde çizgi |
| R3 | Sabitli projede `Pin` yerine `Unpin` |
| R4 | `Pin` → `onPin(id, true)`; `Unpin` → `onPin(id, false)` |
| R5 | `Delete` → `onDelete(id)` |
| R6 | `Rename` → açan düğme yerine `Project name` adlı alan, içinde ad, odak onda; `⋯` duruyor |
| R7 | Yeni ad + Enter → `onRename(id, "yeni ad")` bir kez; alan kapanıyor |
| R8 | Esc → `onRename` çağrılmıyor; alan kapanıyor, ad eskisi |
| R9 | Odak gidince yazılan kaydediliyor → `onRename(id, …)` |
| R10 | Boş ad + Enter → `onRename` çağrılmıyor; alan kapanıyor, ad eskisi |

### Ön uç — `Menu.test.jsx`

| # | Ne |
|---|---|
| M1 | `divided` bir öğenin üstünde `.menu__divider` çizgisi var; öteki öğelerde yok |

### Ön uç — `AllProjectsScreen.test.jsx`

| # | Ne |
|---|---|
| A1 | Her satırda `⋯`; yalnız `menuFor`'daki satırda menü var (bugün A9 `⋯` olmadığını tutuyordu — onun `⋯` yarısı kalkar, arama yarısı 359'a kadar durur) |

*Pressing a row opens that project* açan düğmeyi `/^Night market/` ile arar (Karar 3).

### Ön uç — `App.test.jsx`

**Yeni ya da yeniden yazılan** (bugünkü kodda kırmızı), hepsi `/`'de:

| # | Ne |
|---|---|
| B1 | `Actions for Thesis` → `Delete` → `Delete "Thesis"?` soruluyor |
| B2 | Pencere gidenleri sayıyor: `The 3 chats and 2 files …`; tek olan tekil: `The 1 chat and 0 files` |
| B3 | `Cancel` sunucuya bir şey sormuyor, pencere kapanıyor |
| B4 | Onay (`Delete`) `DELETE /api/projects/p1` gönderiyor, satır gidiyor, adres `/`; `Undo` yok |
| B5 | Son proje silinince `No projects yet.` |
| B6 | Esc önce menüyü, sonra soruyu kapatıyor |
| B7 | Rename yerinde: alana yeni ad + Enter → `PATCH {name}`, satırda yeni ad; `window.prompt` hiç çağrılmıyor |
| B8 | Boş ad `PATCH` göndermiyor |
| B9 | `Pin` → `PATCH {pinned: true}`; proje `Pinned` altında, öteki `Recent`'te |
| B10 | `Unpin` → `PATCH {pinned: false}`; proje sunucunun koyduğu yerde: `Recent`'in sonunda (en eski kullanılan), başında değil |
| B11 | Proje açıkken kenar çubuğunda hiç `⋯` yok (`More for …`, `Actions for …`, `.sidebar__row-more`) |

**Kalkan:** kenar çubuğunun menüsünden silen dokuz test (yerlerine B1–B6), *deleting the project you are
in…* ve *deleting another project…* (Karar 8), `window.prompt`'lu iki rename testi (yerlerine B7, B8),
`openMenuFor`.

**Değişen arama:** satıra basan üç test (*a row opens…*, *a project with no chats…*, *the way into a
project…*) açan düğmeyi `/^Thesis/` ile arar.

### Ön uç — `Sidebar.test.jsx`

Menüye dair beş test (*every project row carries a way into its menu*, *opening the menu does not open
the project*, *the menu offers the two things…*, *only the row whose menu is open…*, *each choice
names…*) kalkar; yerine:

| # | Ne |
|---|---|
| S1 | Hiçbir proje satırında `⋯` yok, menüsü de |

### Ön uç — CSS kilitleri

- **`workspace.css.test.js`:** *the sidebar's menu is the design's own width* `.all-projects__row .menu`'nün
  176'sını tutar. Yeni:
  - C1 — `⋯` 26 × 26, `opacity: 0`; satırın üstüne gelince ya da odakta görünür.
  - C2 — rename alanı satırı doldurur: `flex: 1`, `min-width: 0`, `var(--line)` kenar, `13px`.
  - C3 — menünün çizgisi: `border-top: 1px solid var(--line)`, `margin: 5px 10px`.
- **`app.css.test.js`:** iki odak kuralının biri `.sidebar__row-more:focus-visible` yerine
  `.all-projects__row-more:focus-visible`; `.sidebar__row-more` hiçbir yerde yok.

## Tutmadıkları

- `Archive`, `Undo` ve `Archived` sekmesi (363); arama (359); ad sorma ekranı (361); kenar çubuğunun
  proje listesinin kalkması (362); yazma başarısız olunca ne olduğu (bugünkü gibi, 364'ün ve
  `APP-BUGS.md` 26'nın).
- Rename'den sonra odağın `⋯`'ye dönmesi — tasarım yapıyor, satır istemiyor; bir parça daha olurdu.
- `dist` — Claude derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` R1–R10, M1, A1, B1–B11
(B5'in ve B3'ün bugün de geçebilecek yarıları dışında), S1 ve CSS kilitlerinde kırmızı; öteki üç süit
yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m360-satir-menusu-testler-plan.md).
