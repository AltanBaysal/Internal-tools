# Madde 111 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m111-kamera-uygulama-design.md](../specs/2026-08-28-queenagent-m111-kamera-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `schema.py` — biçim paragrafının sonuna

```python
    "A camera is two decisions: how much of the body is in the picture -- close-up, upper body, "
    "medium shot, full body -- and where it is looking from -- from the side, from above, from "
    "behind, looking at viewer. Both are written, and the pair is chosen for the scene rather "
    "than kept from the frame before."
```

## B. `skills.py` — prompt+ craft paragrafına

`"asking is for names never settled, not for craft."` cümlesinin ardına:

```python
    "Two frames carrying the same framing and angle read as one picture twice, so neighbours "
    "differ in at least one. "
```

## C. Doğrulama ve kapanış

1. İki suite; iki kırmızı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `dist` derlenmez — ön yüz değişmiyor.
3. Commit: `schema.py` + `skills.py` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **Koda kamera listesi girmez.**
- **Örnek ellenmez** — 109 zaten iki farklı kamera bıraktı.
- **Test dosyaları değişmez.**
