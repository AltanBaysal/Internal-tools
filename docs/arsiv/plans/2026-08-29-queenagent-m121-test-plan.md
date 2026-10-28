# Madde 121 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-29-queenagent-m121-defter-testler-design.md](../specs/2026-08-29-queenagent-m121-defter-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `queen-agent/backend/tests/test_schema.py` — dosyanın sonuna

```python
def test_the_rulebook_catches_a_movement_in_an_action():
    # 28 Aug: head moving back and forth -- stage direction for a video that will never exist.
    said = _rulebook()
    assert "10." in said and "frozen instant" in said


def test_the_rulebook_catches_camera_language_in_an_action():
    # full body view in the action while the camera field said medium shot: two framings fight.
    said = _rulebook()
    assert "11." in said and "full body view" in said


def test_the_rulebook_catches_a_story_role_in_an_action():
    # stepson thrusting: the camera sees a person, not a relationship, and who is in the frame
    # is the characters map's word.
    said = _rulebook()
    assert "12." in said and "stepson" in said.lower()


def test_the_rulebook_catches_an_or_in_any_value():
    # Rule 8 banned it in outfits; hands gripping wall or body walked around the fence.
    said = _rulebook()
    assert "13." in said and "any value" in said


def test_the_rulebook_catches_an_outfit_named_after_its_wearer():
    # milf_pink, male_nude: the prose said garments name outfits, and prose was not enough --
    # the rulebook is the list the writer is told to check against.
    said = _rulebook()
    assert "14." in said and "named after its wearer" in said
```

## Beklenen kırmızı: `test_schema.py` 5.

## Bilerek yapılmayanlar: `schema.py` açılmaz; `dist` derlenmez.
