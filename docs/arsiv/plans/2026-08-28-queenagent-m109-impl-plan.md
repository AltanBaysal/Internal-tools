# Madde 109 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m109-kiyafet-uygulama-design.md](../specs/2026-08-28-queenagent-m109-kiyafet-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `schema.py` — örnek

`characters`, `outfits` ve `frames` şu hâle gelir *(quality ve locations aynı)*:

```python
    '  "characters": { "aylin": "woman in her mid 20s, long teal hair, green eyes, mature '
    'female",\n'
    '                  "deniz": "man in his late 20s, short black hair, brown eyes, stubble" },\n'
    '  "outfits": { "gunluk": "jeans, black t-shirt", "atki": "red knit scarf",\n'
    '               "ceket": "denim jacket, white t-shirt" },\n'
```

ve `frames` listesine, var olan karenin ardından:

```python
    "  ]\n"  ->
    '    { "people": "1boy, 1girl",\n'
    '      "characters": { "aylin": ["gunluk"], "deniz": ["ceket"] },\n'
    '      "location": "bedroom",\n'
    '      "action": "standing by the window, talking, looking at each other, soft smiles",\n'
    '      "camera": "upper body, from the side" }\n'
    "  ]\n"
```

Var olan karenin sonuna virgül eklenir.

## B. `schema.py` — düzyazı

Kıyafet paragrafının sonuna:

```python
    "An entry dresses one person: the text it holds is copied whole to whoever names it, so two "
    "people dressed differently are two entries. One entry trying to cover both -- or, for the "
    "man, for the woman -- puts the man in the dress and the woman in the trousers."
```

## C. `schema.py` — kural defteri

Yedinci kuralın ardına:

```python
    "8. One outfit entry covering two people -- or, for the man, for the woman. Whoever names it "
    "is handed the whole text, so split it into one entry per set of clothes."
```

## D. Doğrulama ve kapanış

1. İki suite; üç kırmızı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `dist` derlenmez — ön yüz değişmiyor.
3. Commit: `schema.py` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **`build_prompts` ellenmez.**
- **`quality` ve kamera işleri ellenmez** *(110, 111)*.
- **Test dosyaları değişmez.**
