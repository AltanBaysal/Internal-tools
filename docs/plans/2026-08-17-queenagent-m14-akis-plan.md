# Madde 14 — Akış görselleri · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m14-akis-design.md](../specs/2026-08-17-queenagent-m14-akis-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uç ve ayrıştırıcı
değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**`Markdown.test.jsx`** — `caret` özelliği: paragrafın ucunda, kod bloğunun içinde, son maddenin
sonunda, tablonun altında; özellik verilmeyince hiç yok.

**`markdown.test.js`** — akışın her adımında çit bloğu bozmadan büyür (fark 41, akış tarafından).

**`ChatScreen.test.jsx`**
- akan metin imleci taşır, kayıtlı cevap taşımaz.
- yeni mesaj listeyi dibe atar.
- dibe uzakken gelen parça kaydırmaz, yakınken kaydırır.

**`workspace.css.test.js`** — imleç 7×15 ve `blink` ile yanıp söner, rengi vurgu değil.

**Ölçülen kırmızı: 11.** İki test ilk koşuda yeşil geldi ve ikisi de yerinde duruyor:
- akan çit testi — ayrıştırıcı bunu Madde 13'te zaten yapıyordu; test onu akış tarafından kilitliyor.
- "yukarı çıkan okuyucu çekilmez" — kod yokken hiçbir şey kaydırmadığı için doğru sebeple değil,
  sebepsiz yeşil. Uygulamadan sonra asıl işini görüyor.

---

## Adım 2 — Uygulama

1. `Markdown.jsx` — `caret` özelliği; son bloğa göre yerini bulan çizim.
2. `ChatScreen.jsx` — kaydırma kabına ref; iki `useEffect` (yeni mesaj / akan parça) ve 220px eşiği.
3. `workspace.css` — `.caret`.

### Kapanış denetimi

- `grep "var(--accent)"` imleçte geçmiyor.
- Yeni keyframe eklenmedi.

---

## Risk

jsdom kaydırmaz; testler ölçüleri tanımlayıp kararı sınıyor. Gözle doğrulama Madde 35.
