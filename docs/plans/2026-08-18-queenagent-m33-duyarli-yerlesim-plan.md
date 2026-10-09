# Madde 33 — Duyarlı yerleşim · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m33-duyarli-yerlesim-design.md](../specs/2026-08-18-queenagent-m33-duyarli-yerlesim-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Yalnız ön uç: **bir tur**, önce testler (kırmızı), sonra uygulama.

---

## Adım 1 — Testler (kırmızı commit)

- yeni `useShellWidth.test.jsx` — `shellSteps` eşikleri (1200 · 1000 · 780 · 640 · **0**); kanca
  ölçüyü ResizeObserver'dan alır ve genişlik değişince sınıf değişir *(sahte observer)*.
- `App.test.jsx` — kabuk ölçüldüğü genişliğin sınıfını taşır.
- `ChatScreen.test.jsx` · `ProjectScreen.test.jsx` — okuma değiştiricisi yalnız okurken konur.
- `workspace.css.test.js` — **`@media` kalmadı**; kenar çubuğunun üç basamağı sınıflarla; dar
  basamakta yığılma, %44/250/150 bant, katlı ray tek satır, tek sütun ızgara, okurken gizlenen
  sütun; sıkı basamakta 20px dolgu (altı yüzey), 27px başlık, gizli zaman; küçük basamakta 172px
  ve 16/10.

---

## Adım 2 — Uygulama

yeni `shared/useShellWidth.js` · `App.jsx` · `ChatScreen.jsx` · `ProjectScreen.jsx` ·
`workspace.css`.

---

## Kapanış denetimi

- `grep @media` boş.
- Eşik sayıları tek yerde (`shellSteps`), CSS'te sayı yok — yalnız sınıf adı.
- Arka uçta değişiklik yok.

## Risk

Gerçek taşma yalnız gözle görülür: Madde 35, adım 21.
