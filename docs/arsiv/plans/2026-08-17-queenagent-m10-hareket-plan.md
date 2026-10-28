# Madde 10 — Hareket bandı · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m10-hareket-design.md](../specs/2026-08-17-queenagent-m10-hareket-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra implementasyon. Arka uca dokunulmuyor.

---

## Adım 1 — Testler (kırmızı commit)

**`shared/app.css.test.js`** — dört kilit testi:
1. Yalnız iki keyframe: `fadeIn`, `blink`; `riseIn`, `slideIn`, `spin` yok.
2. Hiçbir keyframe `transform` kullanmıyor.
3. `blink` dışında her `animation` süresi ≤ 0.22s; `animation: spin` hiç geçmiyor.
4. Rayın `transition: width 220ms ease` kuralı yerinde.

**`FilePanel.test.jsx`** — *(yeni)* `preparing is said in words, not spun`: hazırlanırken
`.spinner` çizilmez, "preparing…" yazar.

**Ölçülen kırmızı: 4** (3 kilit + 1 panel). Dördüncü kilit testi (rayın geçişi) ilk koşuda yeşil
geldi — doğrusu bu: o geçiş kalıyor ve test onu koruyor.

---

## Adım 2 — Implementasyon

1. `app.css`: `riseIn`, `slideIn`, `spin` silinir; tek bir `fadeIn` (yalnız saydamlık) kalır.
   Keyframe'lerin üstündeki yorum bugünü anlatacak şekilde düzeltilir.
2. `workspace.css`: `riseIn` kullanan iki yer ve `slideIn` kullanan üç yer `fadeIn 0.2s`e geçer
   (250ms olan da 200ms'e iner); `.spinner` kuralı silinir.
3. `FilePanel.jsx`: `<span className="spinner" />` silinir.
4. `CODE-STANDARD.md`: "the four keyframes" → ikisi.

### Kapanış denetimi

- `grep riseIn|slideIn|spin` → boş.
- `.rail`'in genişlik geçişine dokunulmadı mı.

---

## Risk

`spin`'i silmek bilgi kaybı değil: düğmenin sözü ve `disabled` hâli aynı şeyi söylüyor ve testi
zaten vardı.
