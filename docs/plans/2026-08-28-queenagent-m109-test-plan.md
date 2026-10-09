# Madde 109 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m109-kiyafet-testler-design.md](../specs/2026-08-28-queenagent-m109-kiyafet-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/tests/test_schema.py`

`test_the_schema_says_what_belongs_where` testinin ardına:

```python
def test_an_outfit_entry_dresses_one_person():
    # 28 Aug: one entry said "dark pants for man, black dress for woman" and the code handed the
    # whole text to both -- the man came out in the dress. The schema pushed sharing and never
    # said that two people dressed differently are two entries.
    said = _schema().lower()
    assert "dresses one person" in said
    assert "two entries" in said
```

`test_the_rulebook_calls_a_sentence_a_violation` testinin ardına:

```python
def test_the_rulebook_catches_one_entry_dressing_two_people():
    said = _rulebook()
    assert "8." in said and "for the man" in said.lower()
```

`test_the_schema_shows_a_frames_characters_as_a_map` testinin ardına:

```python
def test_the_example_shows_two_people_in_different_clothes():
    # The example is the teacher: the failure it has to rule out is one entry covering both, so
    # the second frame stands two characters side by side, each with their own outfit.
    said = _schema()
    assert '"people": "1boy, 1girl"' in said
    assert "deniz" in said
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_schema.py` | 3 |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **`schema.py` açılmaz** — tur 2'nin işi.
- **`quality` ve kamera işleri ellenmez** *(110, 111)*.
- **`dist` derlenmez.**
