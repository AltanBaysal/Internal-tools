# Madde 24 — Panel açıkken dosya sütunu kalkar · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m24-dosya-sutunu-design.md](../specs/2026-08-18-queenagent-m24-dosya-sutunu-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uç değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**`ProjectScreen.test.jsx`**
- panel açıkken dosyalar sütunu (başlık, satırlar, boş satır) çizilmez.
- solda başlık, composer ve sohbet listesi kalır.
- panel kapanınca sütun geri gelir.
- panel açıkken silinecek satır yok: `deleting.remove` verilse de `Delete outline.md` yoktur.

---

## Adım 2 — Uygulama

1. `ProjectScreen.jsx` — dosya sütunu `reading?.name` yokken çizilir.
2. `workspace.css` — `.project-grid--reading` yorumunu gerçeğe çevir (sütun inmiyor, yok).

### Kapanış denetimi

- Madde 23'ün `×` testi ve `--reading` testi yerinde mi.
- `App.test.jsx` proje ekranında dosya açan koşularda hâlâ yeşil mi.

---

## Risk

Yok.
