# Madde 25 — Menü deseni · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m25-menu-deseni-design.md](../specs/2026-08-18-queenagent-m25-menu-deseni-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uç değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**`shared/menuPlacement.test.js`** *(yeni)* — saf aritmetik:
- sağdan hizalar: `left = anchor.right - menu.width`.
- sol kenardan taşarsa 8px'e çeker; sağ kenardan taşarsa geri çeker.
- altına sığıyorsa `anchor.bottom + 6`; sığmıyorsa yukarı kayar, **çevrilmez** (üstte de kalmaz,
  pencerenin dibine yaslanır).
- azami yükseklik 320'yi ve pencerenin kendisini aşmaz.

**`Menu.test.jsx`** *(`RowMenu.test.jsx`'ten taşınır)* — var olan altı test aynen, artı:
- ekranı kaplayan yakalayıcı çizilir ve ona tıklamak kapatır.
- `document`'e `mousedown` dinleyicisi asılmaz *(dinleyici yakalayıcıya bıraktı)*.
- tetikleyici verilince kutu bir konum alır.

**`workspace.css.test.js`** — `.menu` 176px yerine genişlik dayatmaz; `.menu` `position: fixed` ve
`overflow-y: auto`; `.menu__catcher` `position: fixed; inset: 0`; `.row-menu` adı kalmaz.

**`Sidebar.test.jsx`** — ⋯ menüsü hâlâ açılıyor ve iki öğesini taşıyor *(var olan testler)*.

---

## Adım 2 — Uygulama

1. `shared/menuPlacement.js` — saf yerleştirme.
2. `RowMenu.jsx` → `Menu.jsx`: yakalayıcı, `anchor`, `useLayoutEffect` ile konum.
3. `Sidebar.jsx` — ⋯ düğmesini kendi ref'inde tutar, menüye verir.
4. `workspace.css` — `.row-menu*` → `.menu*`, yakalayıcı, genişlik satır menüsüne iner.

### Kapanış denetimi

- `grep row-menu` boş.
- `grep "addEventListener(\"mousedown\"" ` menüde kalmadı.
- App'in Esc zinciri değişmedi.

---

## Risk

6/8/320 tasarımdan gelmiyor; gözle doğrulama Madde 35.
