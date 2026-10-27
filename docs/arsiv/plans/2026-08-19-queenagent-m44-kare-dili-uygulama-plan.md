# Madde 44 — Kare listesi konuşulan dilde ve dosyada · Uygulama Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m44-kare-dili-uygulama-design.md](../specs/2026-08-19-queenagent-m44-kare-dili-uygulama-design.md)
**Kırmızı commit:** `b50e039` — altı + iki düşen test
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `skills.py`, `SPLIT_INTO_FRAMES`

Son iki paragraf değişir:

- Dil: liste kullanıcının dilinde; İngilizceye çeviriyi prompt üreten beceriler yapar, JSON ve
  `PROMPTS` İngilizce kalır.
- Dosya: `create_file`, ad konudan türer ve `-frames.md` ile biter, düzeltme `edit_file` ile işler,
  sohbete de yazılır.
- "This stays in the chat. Do not create a file." gider.

## Adım 2 — `skills.js`

İki açıklama: karakter satırı ve kare satırı dosyadan söz eder.

## Adım 3 — Yeşili gör, commitle

---

## Kapanış denetimi

- Diske bir şey yazmayan tek beceri Verify prompts.
