# Madde 360 — Satırın `⋯` menüsü · uygulama turu

**Kaynak:** [test turu](2026-09-29-queenagent-m360-satir-menusu-testler-design.md) ve onun commit ettiği
kırmızı testler; kararlar orada. Bu belge yalnız o testleri yeşile çeviren kodu anlatır. 359'un araması
dala girdi ve bu dala birleşti: satırlar `ProjectList`'in `found`'undan çizilen `Section`'larda.

## Parçalar

### `features/workspace/ProjectRow.jsx` — yeni

Bir All projects satırı: projeyi açan düğme ya da yerine gelen ad alanı, `⋯`, ve açıksa menüsü.
Arayüzü: `project`, `menuOpen`, `onOpen(id)`, `onOpenMenu(id)`, `onCloseMenu()`, `onRename(id, name)`,
`onPin(id, pinned)`, `onDelete(id)`.

- `⋯` bir `ref` tutar; menü ona asılır (`Menu`'nün `anchor`'ı). Kenar çubuğu tek bir `ref`'i
  paylaşıyordu; burada her satırın kendi düğmesi var, paylaşacak bir şey yok.
- Menü: `Rename` → satır kendi `renaming` durumunu açar; `Pin`/`Unpin` → `onPin(id, !pinned)`;
  `Delete` (`danger`, `divided`) → `onDelete(id)`.
- **`RenameField`** aynı dosyada, satırın içinde bir iş: taslağı kendi tutar (`EditMessage`'ın kuralı),
  `autoFocus`. Enter ve odağın gitmesi kaydeder, Esc vazgeçer. Üçü tek `finish`'ten geçer ve bir
  `ref` onu bir kez çalıştırır: Enter alanı kapatır, ve kapanan alan odağını götürürken tarayıcı bir
  blur daha verebilir — ikinci bir istek olmamalı. Satır `finish`'in verdiği adı alır: boşsa (ya da
  vazgeçildiyse) istek yok, değilse `onRename(id, ad.trim())`. Alan her durumda kapanır.
- Kod `AllProjectsScreen.jsx`'ten çıkan satır işaretlemesini taşır (ad, `N chats · N files`, zaman).

### `Menu.jsx`

Bir öğe `divided: true` taşırsa önünde `<hr className="menu__divider" />` çizilir. Öğe ve çizgi bir
`Fragment`'te, anahtar öğenin adı. Başlık yorumu menünün bugünkü çağıranlarını söyler.

### `AllProjectsScreen.jsx`

Yeni prop'lar: `menuFor`, `onOpenMenu`, `onCloseMenu`, `onRenameProject`, `onPinProject`,
`onDeleteProject`. Ekran bir `row(project)` fonksiyonu kurar — `ProjectRow`'u bu prop'larla, `menuOpen`
`menuFor === project.id` — ve `ProjectList` ile `Section`'a `onOpenProject` yerine onu verir; yedi prop
iki kat aşağı taşınmaz. Başlık yorumundan 360 düşer.

### `useProjects.js`

`editProject` PATCH'ten sonra listeyi sunucudan yeniden okur (`createProject`'in kuralı): bir pin ve bir
unpin satırın yerini değiştirir, ve yer sunucunun sırasıdır. Rename de aynı yoldan geçer — iki yol
olmasın; yeniden okuma bir GET. Silme listeden çıkarmaya devam eder: çıkan bir satır ötekilerin sırasını
değiştirmez.

### `App.jsx`

- `AllProjectsScreen`'e: `menuFor`, `onOpenMenu={setMenuFor}`, `onCloseMenu`, `onRenameProject={(id,
  name) => editProject(id, { name })}`, `onPinProject={(id, pinned) => editProject(id, { pinned })}`,
  `onDeleteProject={askToDelete}`.
- `Sidebar`'a menüye dair beş prop gitmez; `askForName` (`window.prompt`) kalkar.
- `askToDelete`'in onay düğmesi `Delete`.
- `deleteProject`'teki *içinde durulan proje silinince `/`'e dön* dalı kalkar: silmenin tek yeri All
  projects, ve orada açık proje yok. Onay `removeProject`'i çağırır, o kadar.
- `menuFor` ve `confirming`'in yorumu "inside the sidebar" yerine "inside the screen that opens them".

### `Sidebar.jsx`

`⋯`, `Menu`, `useRef`/`trigger` ve beş prop kalkar. Satır yine tek düğme; `⋯` için kurulmuş sarmalayıcı
`div.sidebar__row` de kalkar, anahtar düğmeye geçer. Kenar çubuğunun proje listesi 362'ye kadar durur.

### `workspace.css`

- Kalkar: `.sidebar__row`, `.sidebar__row-more` ve onun hover/odak kuralı, `.sidebar__row .menu`.
- Gelir (tasarımın `kit.css`'inden): `.all-projects__row-more` (26 × 26, `opacity: 0`, satırın
  hover'ında ya da `:focus-visible`'da `1`, kendi hover'ı), `.all-projects__row .menu` (176),
  `.all-projects__rename`, `.menu__divider`.
- `.all-projects__row`'un ve `.menu`'nün yorumları bugünü söyler.

## Tutmadıkları

`Archive`, `Undo`, `Archived` sekmesi (363); rename'den sonra odağın `⋯`'ye dönmesi; alanın açılınca
adı seçili getirmesi — testler istemiyor, tasarımın ince işleri, raporda.

## Nasıl görülür

Dört satır paralel, dördü yeşil. Kod tek commit: `feat: Madde 360 -- …`.
