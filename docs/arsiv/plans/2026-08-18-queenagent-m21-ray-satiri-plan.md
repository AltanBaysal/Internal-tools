# Madde 21 — Ray satırı ve zemin · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m21-ray-satiri-design.md](../specs/2026-08-18-queenagent-m21-ray-satiri-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uç değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**`FileRail.test.jsx`**
- rayda "×" yok — var olan "the × deletes the row without opening it" testi **proje ekranına
  taşınıyor**, çünkü sınadığı davranış oraya taşındı.
- rayda silme hata satırı yok.

**Yeni `FileRow.test.jsx`** — seçili satır sınıfını taşır; verilmezse taşımaz; silme düğmesi yalnız
`onDelete` verilince çizilir.

**`ProjectScreen.test.jsx`** — "×" hâlâ orada ve silmeyi ister.

**`workspace.css.test.js`** — ray zemini `#fbf9f5`; seçili satır `#efebe4`; hover `#f0ece5`.

---

## Adım 2 — Uygulama

1. `FileRow.jsx` — `selected`.
2. `FileRail.jsx` — `deleting` gider, satıra `selected` verilir.
3. `ChatScreen.jsx` / `App.jsx` — rayın artık istemediği özellik kesilir.
4. `workspace.css`.

### Kapanış denetimi

- `grep row-x` yalnız proje ekranının çizdiği yolda.

---

## Risk

Seçili satır bu maddede ekranda görünmüyor — fark 53 yol haritasında yok. Spec bunu yazıyor ve
kullanıcıya soruluyor.
