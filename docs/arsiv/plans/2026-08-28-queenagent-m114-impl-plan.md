# Madde 114 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m114-ornek-sozlugu-uygulama-design.md](../specs/2026-08-28-queenagent-m114-ornek-sozlugu-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/features/workspace/domain/schema.py` — örnek

```python
    '      "camera": "medium shot, from above" },\n'
```

```python
    '      "action": "standing by window, talking, looking at each other, soft smiles",\n'
    '      "camera": "upper body, from side" }\n'
```

## B. Aynı dosya — biçim paragrafı

```python
    "Every value in this file is written the same way: short comma-separated fragments -- tags "
    "and brief phrases -- never a sentence telling the story. An article is not a tag, so it is "
    "dropped: sitting on couch, by window. An action carries the pose, the expression and where "
    "the eyes look; a camera carries the framing and the angle. The example is the measure: "
    "match its density.\n"
```

## C. Aynı dosya — kamera paragrafındaki sözlük

```python
    "A camera is two decisions: how much of the body is in the picture -- close-up, upper body, "
    "medium shot, full body -- and where it is looking from -- from side, from above, from "
    "behind, looking at viewer. Both are written, and the pair is chosen for the scene rather "
    "than kept from the frame before.\n"
```

## D. Doğrulama ve kapanış

1. İki suite; dört kırmızı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `dist` derlenmez — ön yüz değişmiyor.
3. Commit: `schema.py` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **Test dosyaları değişmez.**
- **Skill metinleri ve `build_prompts` ellenmez.**
- Karakter değerleri *(`in her mid 20s`)* ve `medium shot` olduğu gibi kalır.
