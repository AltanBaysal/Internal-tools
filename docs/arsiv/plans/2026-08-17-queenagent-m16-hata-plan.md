# Madde 16 — Hata dili · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m16-hata-design.md](../specs/2026-08-17-queenagent-m16-hata-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama. Arka uç değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**`api.test.js`** — sunucunun cümlesi, JSON olmayan gövde, boş gövde; durum kodu yine taşınıyor.

**`Composer.test.jsx`** — reddedilen metin kutuya geri gelir; kullanıcı yeni bir şey yazdıysa gelmez;
kabul edilen metin geri gelmez.

**`ChatScreen.test.jsx`** — reddedilen mesaj tek satır çıkarır, kart çıkarmaz; ölen akış kartı
çıkarır.

**`App.test.jsx`** — reddedilen mesajın cümlesi ekrana ulaşır (uçtan uca).

Ayrıca **beş testte sahte cevap `json` yerine `text` veriyor**: istek yolu artık gövdeyi metin
olarak okuyup JSON'u kendisi çözüyor, çünkü JSON olmayan bir gövdeyi de göstermesi gerekiyor.
Bu, testin uydurduğu bir şey değil — sözleşmenin kendisi değişti.

**Kırmızı:** `api.test.js`'in dört yeni testi, `Composer`'ın üçü, `ChatScreen`'in reddedilen mesaj
testi ve `App`'in iki hata testi.

---

## Adım 2 — Uygulama

1. `api.js` — gövdeyi oku, cümleyi çıkar, kod ayrı alanda kalsın.
2. `useChat.js` — `refused` alanı; `send` hatayı kaydedip yeniden fırlatsın.
3. `Composer.jsx` — `onSubmit` reddedilirse metni geri koy (yalnız kutu boşsa).
4. `ChatScreen.jsx` — `refused` için tek satır.
5. `App.jsx` — `refused` geçişi.
6. `workspace.css` — `.refused`.

### Kapanış denetimi

- `grep "failed with"` yalnız yedek yolda.
- `grep "connection dropped"` boş.

---

## Risk

`send` artık fırlatıyor; tek çağıran Composer ve yakalıyor.
