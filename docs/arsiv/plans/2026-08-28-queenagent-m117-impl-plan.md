# Madde 117 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m117-sen-karar-ver-uygulama-design.md](../specs/2026-08-28-queenagent-m117-sen-karar-ver-uygulama-design.md)
**Testler kırmızı commit'te** *(tur 1)*; bu tur yalnız `skills.py`'a dokunur.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/features/workspace/domain/skills.py` — `START_A_SCENARIO` döngü paragrafı

*"Never stop the flow waiting for a description."* ile *"When a step is approved"* arasına:

```python
    "description. A fourth way is a delegation -- you decide. It answers only the question that "
    "was asked: the flow chooses for that one step, shows what it chose, and the step still ends "
    "when the user approves it; the next step's question is asked as ever, because deciding one "
    "step is not authority over the flow. The plan writes a delegation with the name of the step "
    "it closed, never as a standing authority -- a fresh chat reads the plan and inherits exactly "
    "what is written there. When a step is approved, its line in the plan is marked done -- the "
```

## Beklenen yeşil

`test_skills.py` 3 yenisiyle beraber tamamı; `test_notebook`'un ikisi dal yaşadıkça kırmızı ve bu
maddenin değil. Frontend'e dokunulmadı, suite olduğu gibi yeşil.

## Bilerek yapılmayanlar

- **`prompt.py`, prompt+ metni, `modes.py` ellenmez** — gerekçeleri tasarımda.
- **`dist` derlenmez.**
