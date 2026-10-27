# Madde 112 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m112-secenek-listesi-testler-design.md](../specs/2026-08-28-queenagent-m112-secenek-listesi-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/tests/test_prompt.py` — dosyanın sonuna

```python
def test_a_turn_does_not_end_with_a_menu_of_options():
    # 28 Aug: every answer closed with five things the user could ask for next. A turn ends with
    # the one question that decides what happens, or with nothing -- a list is the work handed
    # back rather than an ending.
    said = SYSTEM_PROMPT.lower()
    assert "list of things you could do next" in said
    assert "ask the one question" in said
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_prompt.py` | 1 |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **`prompt.py` açılmaz** — tur 2'nin işi.
- **`dist` derlenmez.**
