# Madde 119 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-29-queenagent-m119-okur-testler-design.md](../specs/2026-08-29-queenagent-m119-okur-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `queen-agent/backend/tests/test_schema.py` — dosyanın sonuna

```python
def test_the_schema_names_its_reader():
    # 28 Aug: the file carried stage direction -- head moving back and forth -- because nothing
    # the model reads says who the prompts are for. The fact lived in the roadmap and the
    # decision notebook, two documents the model never sees.
    said = _schema()
    assert "SDXL-family" in said
    assert "tags, never sentences" in said


def test_the_schema_says_a_frame_is_one_frozen_instant():
    # "The camera sees" alone also describes a video camera, and the model wrote for one.
    said = _schema().lower()
    assert "one single still picture" in said
    assert "frozen instant" in said
    assert "no motion" in said


def test_a_movement_is_written_as_the_pose_it_passes_through():
    # The ban alone would empty the frame -- the movement is kept, written as what a still
    # camera can hold, the way the cause became downcast eyes.
    assert "the pose it passes through" in _schema().lower()


def test_a_camera_half_comes_from_the_lists():
    # "from side profile" three times in one file: the vocabulary read as examples, not as the
    # set to choose from.
    assert "come from the lists" in _schema().lower()
```

## Beklenen kırmızı: `test_schema.py` 4.

## Bilerek yapılmayanlar: `schema.py` açılmaz; `dist` derlenmez.
