# Madde 11 — Kaydırma sözleşmesi · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m11-kaydirma-design.md](../specs/2026-08-17-queenagent-m11-kaydirma-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra stil. Arka uca dokunulmuyor.

---

## Adım 1 — Testler (kırmızı commit)

**`shared/app.css.test.js`** — kabuk `100dvh`, `min-height` yok.

**`workspace.css.test.js`**
- `.chat__scroll` `min-height: 0` taşır.
- `.chat__composer` `flex: none` — **bu ilk koşuda yeşil geldi**, doğrusu da bu: composer zaten
  sabit ve test onu koruyor.
- 1100px bloğunda yerleşimler `overflow-y: auto` almaz; ray ve panel `max-height: 44%` ve
  `overflow-y: auto` alır.

**Ölçülen kırmızı: 3.**

---

## Adım 2 — Stil

1. `app.css`: `.app-shell` → `height: 100dvh`, `min-height: 600px` gider.
2. `workspace.css`: `.chat__scroll` → `min-height: 0`.
3. 1100px bloğu: yerleşimlerden `overflow-y: auto` çıkar; ray/panel kuralı `overflow: visible` ve
   `max-height: none` yerine `overflow-y: auto` + `max-height: 44%` + `flex: none` alır.

### Kapanış denetimi

- `grep "min-height: 600px"` → boş.
- Geniş penceredeki ray/panel kuralları değişmedi mi.

---

## Risk

Kilit testleri jsdom'un göremediğini yazıyor; gerçek doğrulama Madde 35. `100dvh` için yedek değer
yazılmıyor: uygulama yerel çalışıyor ve tek kullanıcısı güncel bir tarayıcı.
