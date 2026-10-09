# Madde 117 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m117-sen-karar-ver-testler-design.md](../specs/2026-08-28-queenagent-m117-sen-karar-ver-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/tests/test_skills.py` — akış bölümünün sonuna

```python
def test_a_delegation_answers_only_the_question_that_was_asked():
    # 28 Aug: "you decide" arrived with the places answer and the flow read it as authority over
    # everything left -- the scenes question was never asked. A delegation is an answer, and an
    # answer belongs to its question.
    said = _flow()
    assert "answers only the question that was asked" in said
    assert "asked as ever" in said


def test_a_delegated_step_still_ends_on_approval():
    # The flow choosing for the user is not the user approving the choice: the step shows what
    # was chosen and waits, like every other step.
    assert "still ends when the user approves" in _flow()


def test_the_plan_records_a_delegation_with_the_step_it_closed():
    # The plan wrote "user said you decide" with no step name, and the fresh chat that read it
    # inherited an authority the user never gave.
    assert "never as a standing authority" in _flow()
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_skills.py` | 3 |

## Bilerek yapılmayanlar

- **`skills.py` açılmaz** — tur 2'nin işi.
- **`dist` derlenmez.**
