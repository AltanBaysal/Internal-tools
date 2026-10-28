# Madde 116 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m116-sohbet-adi-uygulama-design.md](../specs/2026-08-28-queenagent-m116-sohbet-adi-uygulama-design.md)
**Testler kırmızı commit'te** *(tur 1)*; bu tur `chatTitle.js`'i doğurur ve `useChat.js`'e bir
çağrı ekler.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/frontend/src/features/workspace/chatTitle.js` — yeni dosya

Tasarımdaki gövde, başında kuralın neden iki yerde durduğunu söyleyen yorumla.

## B. `queen-agent/frontend/src/features/workspace/useChat.js` — ayağa dikilen kayıt

`{ id: null, title: text, ... }` → `{ id: null, title: chatTitle(text), ... }`, ve dosyanın
başına import.

## C. `dist` aynı commit'te

`npm run build --prefix queen-agent/frontend` — ön yüz kaynağı değişti; defter tarafı ancak
derlenip push'lanınca görür.

## Beklenen yeşil

Frontend suite'in tamamı, tur 1'in üçü dahil. Backend olduğu gibi; `test_notebook`'un ikisi dal
yaşadıkça bilinen kırmızı.

## Bilerek yapılmayanlar

- **Backend ellenmez.**
- **Baloncuğun metni ellenmez** — kırpılan yalnız ad.
