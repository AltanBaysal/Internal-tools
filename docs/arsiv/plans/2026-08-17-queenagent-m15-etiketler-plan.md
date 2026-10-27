# Madde 15 — Mesaj etiketleri ve bekleme bloğu · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m15-etiketler-design.md](../specs/2026-08-17-queenagent-m15-etiketler-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uç değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**`ChatScreen.test.jsx`**
- kullanıcı etiketi yalnız saat; "You" hiçbir yerde yok. *(var olan test değişiyor)*
- bekleme etiketi "QueenAgent · saat"; saat sahte saatten okunuyor.
- akış sürerken aynı saat duruyor.
- "creating file…" bekleme bloğunun içinde; yanında boş rozet.
- metin akarken doğan dosyanın kutusu akan bloğun içinde.

**`workspace.css.test.js`** — bekleme bloğu 10px boşluk; kutu en çok 340px; rozet yeri 30×30, 7px.

**Ölçülen kırmızı: 7.**

---

## Adım 2 — Uygulama

1. `ChatScreen.jsx`
   - kullanıcı etiketi yalnız `clockTime(message.at)`.
   - `askedAt`: `thinking` doğru olduğunda bir kez damgalanır, düştüğünde silinir.
   - bekleme ve akış bloklarının etiketi bu damgayı taşır.
   - `creatingFile` kutusu bekleyen bloğun içine girer; boş rozet yeri kazanır.
2. `workspace.css` — `.msg--waiting`, `.creating`, `.creating__chip`.

### Kapanış denetimi

- `grep "You"` ön yüzde boş.
- Kutu tek yerde çiziliyor mu (iki kopya yok).

---

## Risk

Sahte saat ile Testing Library'nin birlikte çalışması: saat ilerletilmiyor, yalnız sabitleniyor, o
yüzden `act()` gerekmiyor.
