# Madde 22 — Dosya kartı kapı olur · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m22-kart-kapi-design.md](../specs/2026-08-18-queenagent-m22-kart-kapi-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uç değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**`ChatScreen.test.jsx`**
- kart bir düğmedir, `Open ›` yazar, basınca `reading.open` çağrılır.
- açık dosyanın kartı seçili sınıfı taşır ve ipucu `open` olur.

**`FileRail.test.jsx`**
- bir dosya açıkken hem panel hem liste çizilir.
- açık dosyanın satırı seçilidir *(Madde 21'de yazılan kural artık ekranda)*.
- başka bir satıra basmak paneli kapatmadan o dosyayı açar.
- okurken katlama denetimi yok *(var olan test yerinde kalıyor)*.

**`App.test.jsx`** — katlı rayda transkriptteki karta basmak rayı açar ve dosyayı gösterir.

**`workspace.css.test.js`** — kart 340px ve 12px; seçili kart `#f4efe7` / `#cfc3b2`; okurken ray iki
sütun ve liste 200px.

---

## Adım 2 — Uygulama

1. `ChatScreen.jsx` — `FileCard` düğme olur, `selected` ve `onOpen` alır.
2. `FileRail.jsx` — okurken liste + panel.
3. `workspace.css` — kart, seçili kart, iki sütun.

### Kapanış denetimi

- Rayı açan kural hâlâ tek yerde mi (`openFile`).
- `grep "Open ›"` yalnız kartta.

---

## Risk

200px bölünme tasarımdan gelmiyor; gözle doğrulama Madde 35.
