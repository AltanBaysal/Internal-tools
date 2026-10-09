# Madde 108 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m108-devir-testler-design.md](../specs/2026-08-28-queenagent-m108-devir-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/tests/test_skills.py` — dosyanın sonuna

```python
def test_the_handoff_is_a_step_of_its_own():
    # Madde 108: the handoff sat outside the numbered list, and a weak model stops when the list
    # ends -- so the flow went on to write frames instead of naming its heir.
    said = _flow()
    assert "Five steps" in said
    assert "5. The handoff" in said
    assert said.index("5. The handoff") < said.rindex("Generate prompts+")


def test_the_flow_never_writes_a_frame_even_when_asked():
    # What happened: asked for the frames, the flow wrote all ten in one edit. The batching rule
    # and the craft licence live in the other skill, so the ask is answered by pointing there.
    said = _flow()
    assert "never written here" in said
    assert "not even when the user asks" in said
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_skills.py` | 2 |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **`skills.py` açılmaz** — tur 2'nin işi.
- **prompt+ ve seçici satırı ellenmez** *(113)*.
- **`dist` derlenmez.**
