# Madde 112 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m112-secenek-listesi-uygulama-design.md](../specs/2026-08-28-queenagent-m112-secenek-listesi-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/features/workspace/domain/prompt.py` — son paragraf

```python
    "A file never stands in for the reply: always write your answer in the chat as well. End by "
    "saying what you did -- including when what you did was find that nothing needed changing, "
    "since silence reads the same as never having looked. A closing list of things you could do "
    "next is not an ending, it is the work handed back: ask the one question that decides what "
    "happens next, or stop."
```

## B. Doğrulama ve kapanış

1. İki suite; kırmızı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `dist` derlenmez — ön yüz değişmiyor.
3. Commit: `prompt.py` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **Akış metni ve prompt+ ellenmez.**
- **Test dosyaları değişmez.**
