# Madde 351 — Kenar çubuğunu katlama · uygulama turu

**Kaynak:** [yol haritasının 351'i (v9-2w)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m351-katlama-testler-design.md) ve onun commit'lenmiş
testleri (`1373dc7b`). Tasarım: queen-design `queen-agent-v3`'ün 174 ve 187'si — `shell.js`'in
`sidebar()`, `panelFold()` ve `foldShortcut()`'ı, `kit.css`'in `.sidebar__foot`, `.sidebar__fold`,
`.sidebar__panel-icon` ve `.sidebar__new-chat--icon` kuralları.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

Üç dosya: `Sidebar.jsx`, `App.jsx`, `workspace.css`. Katlanmanın durumu yine App'in
`sidebarCollapsed`'i; yeni durum, yeni dosya, yeni prop yok.

### `Sidebar.jsx`

- **`Fold` kendi satırını çizer:** `div.sidebar__foot` içinde `button.sidebar__fold`, içinde boş bir
  `span.sidebar__panel-icon`. Adları bugünkü gibi `Hide the sidebar` / `Show the sidebar`. `‹` ve `›`
  gider.
- **Açıkken** `Fold` `aside`'ın ilk çocuğu değil son çocuğu olur: `New chat`, projeler ve sohbetler
  bugünkü sırayla üstte kalır.
- **Katlıyken** `aside.sidebar.sidebar--collapsed` içinde, proje açıksa önce
  `button.sidebar__new-chat.sidebar__new-chat--icon` (`aria-label="New chat"`, içinde
  `span.sidebar__plus` `+`, `onClick={onNewChat}`), sonra `Fold`. Proje açık değilse yalnız `Fold`.
  `+` kenar çubuğunu açmaz — tasarımın dediği gibi, açık `New chat`'in yaptığını yapar.
- Dosyanın başındaki not (katlı şeridin *"yalnız geri getiren düğmeyi"* taşıdığını söylüyor) ikon
  sütununu anlatacak şekilde düzeltilir.

### `App.jsx`

`window`'daki tek `keydown` dinleyicisi — *"One listener owns the keyboard"* — `Escape`'ten önce
`Ctrl + .`'ya bakar: `event.ctrlKey && event.key === "."` ise `event.preventDefault()`,
`setSidebarCollapsed((folded) => !folded)`, ve dönülür. İkinci bir dinleyici açılmaz: ikisi aynı
olaya asılır ve sıralarını kimse belirleyemez — dinleyicinin kendi notu bunu söylüyor. Durum App'te,
dinleyici de App'te.

**Yazmayla çakışmaz:** olay yazma kutusundan `window`'a kabarcıklanır, yani kutudayken de duyulur.
`Ctrl` basılıyken tarayıcı kutuya karakter yazmaz; varsayılanın engellenmesi tarayıcıya tuşla
yapacak başka bir şey bırakmaz. Tek başına `.` `ctrlKey` taşımaz ve kutuya yazılır. Yazma kutusunun
kendi dinleyicisi (`Composer.jsx`) yalnız Enter'e bakıyor, düzenleme kutusununki (`EditMessage.jsx`)
Enter ve Escape'e; ikisi de `.`'ya dokunmuyor.

Yalnız `Ctrl`: madde `Ctrl + .` diyor. `Shift` ya da `Alt` da basılıysa ayrıca bakılmaz — tasarımın
`foldShortcut()`'ı da bakmıyor.

### `workspace.css`

Yalnız kenar çubuğunun kendi kuralları, yerlerinde:

- `.sidebar--collapsed`'in notu ikon sütununu anlatır; kuralın kendisi aynı (52, `align-items:
  center`, `overflow: hidden`). Basamakların iki sınıflı kuralları katlıyken de genişliklerini
  tutar — değişmez.
- `.sidebar__fold` tasarımın kuralı olur: `display: flex`, ortalı, `flex: none`, 30 × 30, çerçevesiz,
  `border-radius: var(--radius-control)`, saydam, `cursor: pointer`. `margin-left: auto`, yazı boyu
  ve rengi gider. `:hover`'ı `#e5dfd5` kalır.
- `.sidebar--collapsed .sidebar__fold { margin-left: 0 }` kalkar: sıfırladığı pay artık yok.
- Yeni `.sidebar__foot`: `display: flex`, `justify-content: flex-end`, `margin-top: auto`. Açıkken
  sohbet listesinin altında, sağda; proje yokken de en altta. Katlıyken sütunun `align-items:
  center`'ı satırı düğmeye daraltır ve ortalar.
- Yeni `.sidebar__panel-icon` ve `::after`: 16 × 16, `box-sizing: border-box`, `1.5px solid
  var(--ink)`, 3px köşe; çizgi soldan 6px'te, `top`/`bottom` `-1.5px`, `border-left: 1.5px solid
  var(--ink)`. CSS'le çizilir, `.dot` gibi: uygulamada ikon dosyası yok.
- Yeni `.sidebar__new-chat--icon` (`.sidebar__plus`'tan sonra, `.sidebar__new-chat`'in payını
  ezebilsin diye): 30 × 30, `padding: 0`, `justify-content: center`, `flex: none`.

Hareket yeni değil: kenar çubuğunun 220ms genişlik geçişi zaten var (CODE-STANDARD'ın *"the only
motion that is not a fade"*i ray için; kenar çubuğununki 338'den önce de vardı ve bu madde ona
dokunmaz).

## Yapılmayanlar

- Arama ikonu ve `Search chats`: v9-2v. Kenar çubuğunun içeriği (projeler listesinin kalkması): v9-2s.
- `dist` derlenmez: Claude birleştirirken derler.
- CODE-STANDARD'ın tablolarına dokunulmaz: dosya eklenmiyor, kalkmıyor.

## Nasıl görülür

Dört satır yeşil; `npm test --prefix queen-agent/frontend` 695 + 11 = 706 test. Tarayıcıda: sohbet
ekranında panel ikonu kenar çubuğunun sağ altında; basınca ya da `Ctrl + .` ile sütunda `+` ve en
altta aynı ikon kalıyor; yeniden basınca açılıyor. Yazma kutusunda yazarken `Ctrl + .` kutuya bir
şey yazmıyor.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m351-katlama-uygulama-plan.md).
