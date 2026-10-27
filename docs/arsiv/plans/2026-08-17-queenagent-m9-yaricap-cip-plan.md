# Madde 9 — Yarıçaplar, çip, dosya satırı · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m9-yaricap-cip-design.md](../specs/2026-08-17-queenagent-m9-yaricap-cip-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra implementasyon. Arka uca dokunulmuyor.

---

## Adım 1 — Testler (kırmızı commit)

### 1.1 · Davranış testleri (gerçek DOM)

**`FileRail.test.jsx`**
- `a row says how long ago the file was written` → ikincil satırın tamamına bakar:
  `project file · 2h ago`.

**`ProjectScreen.test.jsx`**
- *(yeni)* `a file row says whose file it is`: proje sütununda da aynı ikincil satır.

**`Sidebar.test.jsx`**
- *(yeni)* `a project with no files still holds the badge's place`: rozet `0` çizer ve
  `sidebar__row-badge--none` taşır.
- *(yeni)* `a project with files shows the count plainly`: sayı çizilir, modifier yoktur.

### 1.2 · Kilit testleri (`workspace.css.test.js`)

- Üç denetim `var(--radius-control)` kullanır.
- Dosyada `border-radius: 9px` ve `border-radius: 16px` geçmez.
- `.composer` 14px yarıçaplı, `14px 16px 10px` dolgulu.
- `.file-chip` 30×30, 7px yarıçap, `#f0e7de` zemin, 9.5px yazı.

**Ölçülen kırmızı: ön yüzde 6.** (Arka uç hiç kırmızı vermedi — bu madde ona dokunmuyor.)

Tahmin 8–9'du. İki test ilk koşuda **yeşil** geldi ve ikisi de doğru sebeple: rozetin dolu hâli
zaten sayıyı çiziyordu, dolayısıyla o testi yeni bir şey istemiyor, var olanı koruyor.

**Bir testim yanlış bloğu okuyordu.** `CSS.indexOf(".composer {")` `.chat__composer .composer {`
bloğunu yakalıyordu; kırmızıydı ama yanlış sebeple. Seçici satır başına sabitlendi.

---

## Adım 2 — Implementasyon

1. `workspace.css`: üç `9px` → `var(--radius-control)`; `.composer` 16px→14px ve dolgu
   `14px 16px 10px`; `.file-chip` sabit kareye; `.file-row` iki satırlı yerleşime
   (`.file-row__text` sarmalı, `.file-row__meta`).
2. `FileRow.jsx`: ad ve ikincil satır alt alta; ikincil satır `project file · ${relativeTime}`.
3. `Sidebar.jsx`: rozet her zaman sayıyı çizer, sıfırken modifier alır.

### Kapanış denetimi

- `grep "border-radius: 9px"` ve `grep "border-radius: 16px"` → boş.
- `.file-row__when` hiçbir yerde kalmamalı.
- Geri alma şeridinin yarıçapına dokunulmadı mı — Madde 19 onu siliyor.

---

## Risk

`2h ago` tam eşleşmeyle aranan testler. İkincil satır tek düğüm olduğu için o metin artık parça;
kırmızı çıkan her yer parça eşleşmeye çevrilir, iddia değişmez.
