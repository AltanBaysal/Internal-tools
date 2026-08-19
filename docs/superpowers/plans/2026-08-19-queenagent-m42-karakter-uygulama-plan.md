# Madde 42 — Karakter dosyaya, sayı kullanıcıya · Uygulama Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m42-karakter-uygulama-design.md](../specs/2026-08-19-queenagent-m42-karakter-uygulama-design.md)
**Kırmızı commit:** `e2742c2` — altı düşen test
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `skills.py`, `CREATE_CHARACTER_PROMPT`

Metin baştan yazılır. Taşıyacakları:

- SDXL etiket biçimi ve kimliğin kıyafet taşımaması *(Madde 40'tan, olduğu gibi)*
- sayı kullanıcıdan gelir; söylenmediyse **sorulur**, "iki üç aday" gider
- çıktı `create_file` ile bir JSON dosyasına; sohbette kalma cümlesi gider
- dosyanın adı karakterden (`aylin.json`), şekli yapı dosyasının haritalarıyla aynı
- birden çok aday numaralı adlarla ayrılır; farkın bir satırlık açıklaması sohbette
- kıyafet `outfits` girdisi olur, istenmemişse hiç yazılmaz
- yapıştırılan prompt biçim örneğidir; kareye ait olanlar ayıklanır

## Adım 2 — Yeşili gör, commitle

---

## Kapanış denetimi

- `git status` yalnız `skills.py`'ı gösteriyor.
