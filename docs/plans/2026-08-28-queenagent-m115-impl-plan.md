# Madde 115 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m115-kadrajda-gorunen-uygulama-design.md](../specs/2026-08-28-queenagent-m115-kadrajda-gorunen-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/features/workspace/domain/schema.py` — yeni paragraf

Biçim paragrafının *("… match its density.")* ardına, kamera paragrafından önce:

```python
    "An action holds only what the camera sees. A scene sentence carries why something is "
    "happening and what came before it; a frame carries neither, because nothing in the picture "
    "shows them. A cause is written as what it looks like -- turned away, downcast eyes, tense "
    "shoulders -- or it is left out.\n"
    "\n"
```

## B. Aynı dosya — `RULEBOOK`'a 9. kural

8. kuralın ardına:

```python
    "\n9. A cause or a moment outside the frame written into an action -- after the argument, "
    "later, again. Nothing in the picture shows it, so write what it looks like instead."
```

## C. Doğrulama ve kapanış

1. İki suite; üç kırmızı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `dist` derlenmez — ön yüz değişmiyor.
3. Commit: `schema.py` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **Test dosyaları değişmez.**
- **`skills.py` ellenmez.**
- Örnek kareler ellenmez — 114 onları kendi turunda kapattı.
