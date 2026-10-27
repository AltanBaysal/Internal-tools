# Madde 34 — Durum ekranları ve erişilebilirlik · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m34-durum-erisim-design.md](../specs/2026-08-18-queenagent-m34-durum-erisim-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Yalnız ön uç: **bir tur**, önce testler (kırmızı), sonra uygulama.

---

## Adım 1 — Testler (kırmızı commit)

- `Skeleton.test.jsx` — `screen` biçimi üç blok çizer.
- `App.test.jsx` — ilk yükleme sürerken iskelet var, **hiçbir ekran yok**, kenar çubuğu duruyor;
  cevap gelince iskelet gidiyor; yükleme sürerken **"does not exist" çıkmıyor**, liste gelince
  gerçekten yoksa çıkıyor.
- `OfflineStrip.test.jsx` — yeni cümle ve nokta.
- `FileRow.test.jsx` — satır `button`; `×` kardeş, `title` taşıyor ve satırı açmıyor; Enter açıyor.
- `ProjectScreen.test.jsx` — sohbet satırı `button`, `×` kardeş ve `title` taşıyor.
- `workspace.css.test.js` — iskeletin üç ölçüsü ve kademeli gecikme, 1.4s; şeridin üç rengi;
  noktanın 7px'i ve **vurgu rengi olmadığı**; hover zemininin kutuda kaldığı.

---

## Adım 2 — Uygulama

`Skeleton.jsx` · `App.jsx` · `OfflineStrip.jsx` · `FileRow.jsx` · `ProjectScreen.jsx` ·
`workspace.css`.

---

## Kapanış denetimi

- Satırlarda `div` + `onClick` kalmadı.
- Uygulamada tek yanıp sönme ve tek süre (1.4s).
- Arka uçta değişiklik yok.

## Risk

Sekme sırası ve halka göz işi: Madde 35.
