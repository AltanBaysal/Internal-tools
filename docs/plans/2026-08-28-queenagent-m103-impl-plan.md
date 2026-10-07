# Madde 103 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m103-plan-cumlesi-uygulama-design.md](../specs/2026-08-28-queenagent-m103-plan-cumlesi-uygulama-design.md)
**Tur 1:** bir kırmızı commit'lendi *(`30209f6`)*. Bu turda test yazılmaz.
**Komut:** `python -m pytest queen-agent -q` ve `npm test --prefix queen-agent/frontend`

---

## 1 · `queen-agent/backend/features/workspace/domain/tools.py`

`write_plan`'ın açıklaması:

```python
"description": (
    "Break the work into numbered steps and save the plan. Writes over the plan of "
    "that name if there is one, so read it first and hand back the whole plan rather "
    "than the part you changed. A turn asked only to plan ends with this call -- the "
    "user reads the plan, fixes it in the file if they want to, and runs it "
    "themselves. A plan that is the first step of a larger job is an ordinary step: "
    "carry on from it."
),
```

## 2 · Koş

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Bir kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` derlenmiyor — ön yüz dokunulmuyor.

## 3 · Commit

```
fix(queen-agent): write_plan binds the turn ending to the ask, not to itself
```
