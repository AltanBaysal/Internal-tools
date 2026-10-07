# Madde 41 — Senaryo kısa ve madde madde · Uygulama Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m41-senaryo-uygulama-design.md](../specs/2026-08-19-queenagent-m41-senaryo-uygulama-design.md)
**Kırmızı commit:** `9f946d3` — beş düşen test
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `skills.py`, `CREATE_SCENARIO`

Metin baştan yazılır. Taşıyacakları:

- kısa ana hat, **madde madde**; sayı ve "plain prose" gider
- neden kısa: bu adım ne anlaşıldığını gösteriyor
- kare listesinin alanına girmeme kuralı (bugünkü paragraf, olduğu gibi)
- hem sohbete hem dosyaya; dosya cevabın yerine geçmez
- ad konudan türer, örneğiyle; sabit `scenario.md` gider
- düzeltme `edit_file` ile dosyaya da işler

## Adım 2 — Yeşili gör, commitle

---

## Kapanış denetimi

- `git status` yalnız `skills.py`'ı gösteriyor.
