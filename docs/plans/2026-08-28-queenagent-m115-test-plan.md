# Madde 115 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m115-kadrajda-gorunen-testler-design.md](../specs/2026-08-28-queenagent-m115-kadrajda-gorunen-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/tests/test_schema.py` — iki düzyazı pini

114'ün pinlerinin ardına:

```python
def test_the_schema_keeps_the_story_out_of_an_action():
    # Madde 115: the run wrote "facing each other after argument, reconciling". The argument is
    # not in the picture -- it came over from the Turkish scene sentence, which is where it
    # belongs. Saying what an action carries was not enough; the ban has to be said.
    said = _schema().lower()
    assert "only what the camera sees" in said
    assert "what came before" in said


def test_the_schema_turns_a_cause_into_what_it_looks_like():
    # A ban on its own empties the frame. The cause is kept -- written as the thing a camera can
    # actually see.
    assert "downcast eyes" in _schema()
```

## B. Aynı dosya — kural defteri pini

Kural defterinin pinlerinin arasına, 8. kuralınkinden sonra:

```python
def test_the_rulebook_catches_a_cause_written_into_an_action():
    said = _rulebook()
    assert "9." in said and "cause" in said.lower()
```

## C. Kırmızıyı görme ve commit

1. `python -m pytest queen-agent -q` — üç yeni kırmızı, artı bilinen iki defter kırmızısı.
2. `npm test --prefix queen-agent/frontend` — dokunulmadı, yeşil kalmalı.
3. Commit: `test_schema.py` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **`schema.py` ellenmez.** Uygulama ikinci turun işi.
- **`skills.py` hiç ellenmez** — bu maddede de, sonraki turda da.
- `dist` derlenmez; ön yüz bu maddede yok.
