# Madde 123 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-29-queenagent-m123-persona-testler-design.md](../specs/2026-08-29-queenagent-m123-persona-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `queen-agent/backend/tests/test_skills.py` — dosyanın sonuna

```python
def test_the_flow_opens_as_a_persona():
    # Madde 123, the user's own framing: you are an expert scenario writer laying the ground,
    # and an expert prompt writer takes over. A role holds a weak model better than a rule list.
    assert _flow().startswith("You are an expert scenario writer")


def test_the_builder_opens_as_a_persona():
    assert instruction_for("generate-prompts-plus").startswith("You are an expert SDXL prompt writer")


def test_the_texts_stay_short_enough_to_be_read():
    # Five runs of patches doubled the texts, and a weak model stops reading the middle. The cap
    # is the guard against swelling back: from here a sentence enters only by deleting one.
    assert len(_flow().split()) <= 450
    assert len(instruction_for("generate-prompts-plus").split()) <= 300
```

## Beklenen kırmızı: `test_skills.py` 3.

## Bilerek yapılmayanlar: `skills.py` açılmaz; mevcut pinler ellenmez; `dist` derlenmez.
