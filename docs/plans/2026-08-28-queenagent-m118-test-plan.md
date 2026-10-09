# Madde 118 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m118-kurucu-testler-design.md](../specs/2026-08-28-queenagent-m118-kurucu-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/tests/test_skills.py` — akış bölümünün sonuna

```python
def test_the_flow_never_calls_the_builder():
    # 28 Aug: told never to write a frame, the flow offered to run build_prompts instead -- a ban
    # that names the deed invites the road around it. The builder is the other skill's too, and
    # the file this flow leaves holds no frames for it to build from.
    assert "build_prompts is never called here" in _flow()


def test_the_handoff_offers_nothing_and_asks_nothing():
    # The closing message came back as an offer wearing a question mark. "It is the last word"
    # was already pinned; this pins that no offer and no question ride on it.
    assert "offers nothing and asks nothing" in _flow()
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_skills.py` | 2 |

## Bilerek yapılmayanlar

- **`skills.py` açılmaz** — tur 2'nin işi.
- **`dist` derlenmez.**
