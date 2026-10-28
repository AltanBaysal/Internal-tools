# Madde 103 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m103-plan-cumlesi-testler-design.md](../specs/2026-08-28-queenagent-m103-plan-cumlesi-testler-design.md)
**Tur:** ikiden birincisi — **yalnız testler**. Kod yazılmıyor, kırmızı commit'leniyor.
**Komut:** `python -m pytest queen-agent -q` ve `npm test --prefix queen-agent/frontend`

---

## 1 · `queen-agent/backend/tests/test_tools.py`

`test_every_tool_is_declared_to_the_model`'ın ardına:

```python
def test_write_plan_ends_only_the_turn_that_was_asked_to_plan():
    # Madde 103. The server ends the turn after write_plan in plan mode alone (Madde 97), and the
    # flow writes a plan as its first step and asks its first question in the same turn. The model
    # never sees the mode, so the description binds the ending to the ask instead: a turn asked
    # only to plan ends, a plan that is step one of a larger job carries on.
    plan = next(spec for spec in TOOL_SPECS if spec["function"]["name"] == "write_plan")
    said = plan["function"]["description"]
    assert "asked only to plan" in said
    assert "carry on" in said
```

## 2 · Koş

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Beklenen: arka yüzde **bir kırmızı**, ön yüz yeşil. **İki kırmızı bu maddenin değildir:**
`test_notebook`'un ikisi.

## 3 · Commit

```
test(queen-agent): red for a plan sentence that ends the turn in every mode
```
