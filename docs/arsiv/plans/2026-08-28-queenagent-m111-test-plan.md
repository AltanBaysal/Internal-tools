# Madde 111 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m111-kamera-testler-design.md](../specs/2026-08-28-queenagent-m111-kamera-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/tests/test_schema.py`

`test_the_schema_teaches_the_form_of_a_value` testinin ardına:

```python
def test_the_schema_says_what_a_camera_is_made_of():
    # Madde 111: seven of ten frames came out as a plain medium shot. The field existed and the
    # example showed one value; nothing said the value is two decisions.
    said = _schema().lower()
    assert "how much of the body" in said
    assert "where it is looking from" in said
```

## B. `queen-agent/backend/tests/test_skills.py`

`test_the_sentence_is_a_brief_never_the_frames_text` testinin ardına:

```python
def test_the_builder_varies_the_camera_between_frames():
    # Ten scenes came back as one framing. The craft licence was there; the reason to use it was
    # not.
    said = instruction_for("generate-prompts-plus")
    assert "the same framing and angle" in said
    assert "differ in at least one" in said
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_schema.py` | 1 |
| `test_skills.py` | 1 |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **`schema.py`, `skills.py` açılmaz** — tur 2'nin işi.
- **`dist` derlenmez.**
