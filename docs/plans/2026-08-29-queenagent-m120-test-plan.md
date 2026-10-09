# Madde 120 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-29-queenagent-m120-baglam-testler-design.md](../specs/2026-08-29-queenagent-m120-baglam-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `queen-agent/backend/tests/test_skills.py` — akış bölümünün sonuna

```python
@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_every_skill_opens_with_what_the_work_is_for(skill):
    # 29 Aug, the user's own sentence: if we never give the model the context of what we are
    # doing, where would it know it from? Neither text said what the prompts are for.
    assert "prompts for an SDXL-family image model" in instruction_for(skill)


def test_the_plan_carries_the_context_too():
    # The plan is the fresh chat's memory; a plan that holds only steps hands over the steps
    # and not the work.
    said = _flow()
    assert "opens with one line of context" in said
    assert "inherits the work" in said
```

## Beklenen kırmızı: `test_skills.py` 3 *(2 parametrik + 1)*.

## Bilerek yapılmayanlar: `skills.py` açılmaz; `dist` derlenmez.
