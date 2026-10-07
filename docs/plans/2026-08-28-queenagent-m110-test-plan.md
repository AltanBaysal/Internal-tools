# Madde 110 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m110-kalite-testler-design.md](../specs/2026-08-28-queenagent-m110-kalite-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `test_build_prompts.py`

`test_a_structure_without_quality_still_builds` yerine:

```python
def test_a_structure_without_quality_gets_the_chain_from_code():
    # Madde 110: the chain is the same in every scenario, so the file no longer carries it -- and
    # a model that never writes it cannot write a wrong one.
    from backend.features.workspace.domain.build_prompts import DEFAULT_QUALITY

    structure = _structure()
    del structure["quality"]
    assert build_prompts(structure) == [
        f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"
    ]


def test_a_file_that_writes_its_own_quality_keeps_it():
    # The door left open: a scenario that needs another chain writes the field, and code steps
    # aside rather than adding a second one.
    from backend.features.workspace.domain.build_prompts import DEFAULT_QUALITY

    built = build_prompts(_structure())[0]
    assert built.startswith(f"{QUALITY}, ")
    assert DEFAULT_QUALITY not in built
```

`test_a_try_without_quality_still_builds` yerine:

```python
def test_a_try_without_quality_gets_the_chain_from_code():
    from backend.features.workspace.domain.build_prompts import DEFAULT_QUALITY

    structure = _structure()
    del structure["quality"]
    assert _tried(structure, "aylin")[0] == f"{DEFAULT_QUALITY}, {AYLIN}, {GECELIK}"
```

## B. `test_schema.py`

Alan listesinden `quality` çıkar:

```python
@pytest.mark.parametrize(
    "field",
    ["characters", "outfits", "locations", "frames", "people", "action", "camera"],
)
```

`test_the_schema_says_what_belongs_where` testinin ardına:

```python
def test_the_example_carries_no_quality_field():
    # Madde 110: what the example shows is what gets copied, and this one was copying a chain that
    # mixed two model families into every scenario.
    assert '"quality"' not in _schema()


def test_the_schema_says_where_the_quality_chain_comes_from():
    said = _schema().lower()
    assert "quality chain is not in this file" in said
    assert "code puts it at the front" in said
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_build_prompts.py` | 3 |
| `test_schema.py` | 2 |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **`build_prompts.py` ve `schema.py` açılmaz** — tur 2'nin işi.
- **`dist` derlenmez.**
