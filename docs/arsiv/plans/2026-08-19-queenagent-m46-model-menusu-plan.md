# Madde 46 — `grok-4.5` menüden kalkar · Plan (iki tur)

**Tasarım belgesi:** [2026-08-19-queenagent-m46-model-menusu-testler-design.md](../specs/2026-08-19-queenagent-m46-model-menusu-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

Uygulamanın ayrı bir tasarım belgesi yok: silinen tek şey bir satır, ve sebebi test turunun
belgesinde yazıyor.

---

## Tur 1 — Testler (kırmızı commit)

`models.test.js`:

- Liste iddiasından `grok-4.5` çıkar — altı satır kalır.
- **Yeni:** `a chat that picked the model we stopped offering still says what it is` —
  `modelName("grok-4.5")` ham kimliği döndürür.

İkisi de düşer: satır listede durduğu sürece `modelName` ham kimliği değil görünen adı veriyor.

## Tur 2 — Uygulama (yeşil commit)

`models.js`: `grok-4.5` satırı silinir. Dosyanın başındaki yorum, listenin **sunulan** modeller
olduğunu ve neden bir satırın eksik olduğunu söyler — yoksa bir sonraki okuyan onu eksik sanıp geri
ekler.

---

## Kapanış denetimi

- Varsayılan (`grok-4.3`) hâlâ listede: `models.test.js`'in Madde 45'te eklenen testi.
