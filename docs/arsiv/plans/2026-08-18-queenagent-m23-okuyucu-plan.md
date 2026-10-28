# Madde 23 — Okuyucu · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m23-okuyucu-design.md](../specs/2026-08-18-queenagent-m23-okuyucu-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uç değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**`FilePanel.test.jsx`**
- gövde Markdown çizilir: `# Title` bir `h1`, `**bold**` bir `strong` olur.
- alt bilgi `2h ago · project file` der; boyut ve uzantı orada değildir.
- proje ekranının paneli (`back` yok): `×` kapatır, `←` yoktur.
- rayın paneli (`back`): `←` kapatır, `×` yoktur.
- *(var olan "412 B" testi yerini "alt bilgi artık ölçmüyor" testine bırakıyor.)*

**`FileRail.test.jsx`** — raydaki okuyucu geri okuyla kalır.

**`ProjectScreen.test.jsx`** — proje ekranındaki panel `×` ile kapanır.

**`workspace.css.test.js`**
- `.reader__body .md h1/h2/h3` 25 / 20 / 15.5px; baloncuğun ölçeği yerinde.
- `.reader__body` 14.5px, 1.8, 26px 28px dolgu ve `white-space` yok.
- kayan tek yer gövde: `.reader__head` ve `.reader__meta` `flex: none`, gövde `overflow-y: auto`.
- kap artık okuyucuyu dolgulamıyor: `.panel` ve `.rail--open` dolgusuz, dolgu `.rail__list`'te.

---

## Adım 2 — Uygulama

1. `FilePanel.jsx` — `back` bayrağı, `×`, `<Markdown>` gövdesi, yeni alt bilgi; `formatSize` silinir.
2. `FileRail.jsx` — panele `back` verir.
3. `workspace.css` — üç parçalı sütun, belge ölçeği, dolgunun kaptan okuyucuya taşınması.

### Kapanış denetimi

- `grep formatSize` boş; `grep "reader__body"` yalnız bir yerde çiziliyor.
- `.reader` içindeki hata/eksik satırları da 28px hizasında mı.

---

## Risk

Başlık ve alt bilginin dikey dolgusu (18/12) tasarımdan gelmiyor; gözle doğrulama Madde 35.
