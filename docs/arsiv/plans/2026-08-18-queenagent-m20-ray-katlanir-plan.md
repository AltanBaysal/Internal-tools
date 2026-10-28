# Madde 20 — Ray katlanır · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m20-ray-katlanir-design.md](../specs/2026-08-18-queenagent-m20-ray-katlanir-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uç değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**`FileRail.test.jsx`**
- başlık bir düğmedir, "Project files" ve dosya sayısını taşır.
- basınca `onToggle` çağrılır.
- katlıyken liste çizilmez, etiket ve sayı durur, `aria-expanded` yanlıştır.
- dosya açıkken katlama denetimi yoktur (panel çiziliyor).

**`App.test.jsx`**
- katlamak rayı katlı bırakır; başka sohbete geçince katlı kalır.
- katlıyken bir dosya açmak rayı açar.

**`workspace.css.test.js`** — katlı ray 46px; etiket `writing-mode` ile döner; dar pencerede katlı
ray tek satırdır (dikey değil).

---

## Adım 2 — Uygulama

1. `FileRail.jsx` — başlık düğmesi, iki hâl.
2. `App.jsx` — `railCollapsed` durumu ve dosya açmayı saran tek kural.
3. `workspace.css` — `.rail--collapsed`, `.rail__head`, `.rail__label`, `.rail__count`, dar pencere.

### Kapanış denetimi

- `grep column__title` rayda kalmadı mı (proje ekranında kalıyor).
- Yeni bir kırılma noktası açılmadı mı.

---

## Risk

Döndürülmüş etiketin görünümü jsdom'da ölçülemiyor; gözle doğrulama Madde 35.
