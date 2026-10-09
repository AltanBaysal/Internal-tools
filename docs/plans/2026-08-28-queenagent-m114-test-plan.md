# Madde 114 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m114-ornek-sozlugu-testler-design.md](../specs/2026-08-28-queenagent-m114-ornek-sozlugu-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/tests/test_schema.py` — dört test

Kamera pinlerinin *(`test_the_schema_says_what_a_camera_is_made_of`)* ve süpürme pininin
*(`test_the_schema_never_calls_a_frame_a_shot`)* yanına, dosyanın kendi sırasını bozmadan.

```python
def test_no_example_value_carries_an_article():
    # Madde 114: rule 7 banned articles and Madde 109 slipped one into the example a week later.
    # What guards the next one is a sweep, not a memory -- the example is what gets copied.
    import re

    said = _schema()
    example = said[said.index("{") : said.index("\n}\n") + 2]
    for value in re.findall(r': "([^"]+)"', example):
        assert not re.search(r"\b(the|a|an)\b", value), value


def test_the_example_writes_a_camera_in_the_models_own_words():
    # A camera value goes into the prompt as written, so the example's spelling is the output's
    # spelling. "from slightly above" is English; "from above" is the tag.
    said = _schema()
    assert '"camera": "medium shot, from above"' in said
    assert '"camera": "upper body, from side"' in said


def test_the_camera_vocabulary_is_written_as_tags():
    # The prose lists the angles a camera can take. A vocabulary spelled wrong leaves the example
    # standing alone against it.
    said = _schema()
    assert "from side, from above, from behind" in said
    assert "from the side" not in said


def test_the_schema_says_an_article_is_not_a_tag():
    # Rule 7 names articles among the marks of a sentence, but the paragraph that teaches the form
    # says "brief phrases" -- and a weak model reads that as "sitting on the couch".
    assert "an article is not a tag" in _schema().lower()
```

## B. Kırmızıyı görme ve commit

1. `python -m pytest queen-agent -q` — dört yeni kırmızı, artı bilinen iki defter kırmızısı.
2. `npm test --prefix queen-agent/frontend` — dokunulmadı, yeşil kalmalı.
3. Commit: `test_schema.py` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **`schema.py` ellenmez.** Uygulama ikinci turun işi.
- **Var olan pinler ellenmez** — dördü de yeni test.
- `dist` derlenmez; ön yüz bu maddede yok.
