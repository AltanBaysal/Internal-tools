# Madde 98 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m98-karakter-denemesi-testler-design.md](../specs/2026-08-27-queenagent-m98-karakter-denemesi-testler-design.md)
**Bu turda kod yazılmaz.** On bir test kırmızıya döner.
**Komut:** `python -m pytest queen-agent -q`

---

## 1 · `backend/tests/test_build_prompts.py` — altı

İki yeni ad **testin içinden** import ediliyor, dosyanın başından değil. Sebebi denenerek görüldü:
başa konunca toplama hatası bütün suite'i durduruyor ve turun öteki kırmızıları hiçbir yerde
görünmüyor. `test_modes.py` aynı kuralı aynı sebeple yazmış.

```python
def _tried(structure, character):
    # Imported inside rather than at the top: a name that does not exist yet fails this whole
    # file's collection, and a collection error stops the suite before any other red is seen.
    from backend.features.workspace.domain.build_prompts import build_character_prompts

    return build_character_prompts(structure, character)


def _try_name(source, character):
    from backend.features.workspace.domain.build_prompts import character_prompts_name

    return character_prompts_name(source, character)
```

Testler, `prompts_name`'in parametrik testinin üstüne:

```python
def test_a_character_is_tried_once_for_every_outfit():
    # Character times outfits, in the order the map wrote them. No model in it: the same joining
    # that builds a frame builds this, so what is seen here is what a frame will show.
    assert build_character_prompts(_structure(), "aylin") == [
        f"{QUALITY}, {AYLIN}, {GECELIK}",
        f"{QUALITY}, {AYLIN}, {GUNLUK}",
        f"{QUALITY}, {AYLIN}, {TAKIM}",
    ]


def test_a_file_with_no_outfits_gives_the_identity_once():
    structure = _structure()
    del structure["outfits"]
    assert build_character_prompts(structure, "aylin") == [f"{QUALITY}, {AYLIN}"]


def test_a_try_without_quality_still_builds():
    structure = _structure()
    del structure["quality"]
    assert build_character_prompts(structure, "aylin")[0] == f"{AYLIN}, {GECELIK}"


def test_trying_a_character_nobody_knows_names_what_is_known():
    # The same sentence a frame gets, minus the frame number: there is no frame here.
    with pytest.raises(BadStructure) as refused:
        build_character_prompts(_structure(), "aylinn")
    said = str(refused.value)
    assert "aylinn" in said and "aylin" in said and "deniz" in said
    assert "frame" not in said


@pytest.mark.parametrize(
    "source,character,expected",
    [
        ("bar-scene.json", "aylin", "bar-scene-aylin.py"),
        ("intro-frames.json", "deniz", "intro-frames-deniz.py"),
        ("noextension", "aylin", "noextension-aylin.py"),
    ],
)
def test_the_try_is_named_after_the_source_and_the_character(source, character, expected):
    assert character_prompts_name(source, character) == expected


def test_a_character_name_with_spaces_still_makes_a_clean_file_name():
    # The name comes from the model like every other one, and a file name is not the place to find
    # out what it did with it.
    assert character_prompts_name("bar-scene.json", "yan karakter") == "bar-scene-yan-karakter.py"
```

## 2 · `backend/tests/test_tools.py` — dört

Küme testine sekizinci ad:

```python
        # Eighth since Madde 98: the same joining, one character at a time, so a character can be
        # looked at before it enters a frame.
        "build_character_prompts",
```

Ve `test_building_reports_a_born_file`'ın altına:

```python
def test_trying_a_character_writes_a_file_named_after_both(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "build_character_prompts", name="scene.json", character="aylin")
    assert "scene-aylin.py" in files.list_names("p1")


def test_trying_a_character_reports_a_born_file(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    result = run_tool(
        files,
        "p1",
        "build_character_prompts",
        json.dumps({"name": "scene.json", "character": "aylin"}),
    )
    assert result.created == "scene-aylin.py"


def test_trying_a_character_nobody_knows_writes_nothing(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    said = _call(files, "build_character_prompts", name="scene.json", character="ghost")
    assert "ghost" in said
    assert files.list_names("p1") == ["scene.json"]


def test_a_character_try_says_how_many_prompts_it_wrote(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    result = run_tool(
        files,
        "p1",
        "build_character_prompts",
        json.dumps({"name": "scene.json", "character": "aylin"}),
    )
    # One outfit in this structure, so the singular is the answer -- counted() decides that.
    assert result.outcome == "1 prompt"
```

Dosyanın başındaki `STRUCTURE` sabiti bir karakter ve bir kıyafet taşıyor; ikisi de yeterli.

## 3 · `backend/tests/test_modes.py` — bir

```python
def test_edit_mode_can_write_a_plan_too():
    # Madde 97: the flow works in this mode because it writes files, and it keeps its place in a
    # plan. Without the tool here its first step cannot be taken at all.
    assert _offered("edit") == READS | {
        "create_file",
        "edit_file",
        "build_prompts",
        "build_character_prompts",
        "write_plan",
    }
```

`ask` ile `plan` testleri ellenmiyor: kümeleri zaten `READS`, ve yeni araç oraya girmiyor.

## 4 · Koş

```
python -m pytest queen-agent -q
```

Beklenen: `test_build_prompts.py` toplanamıyor *(ImportError)*, `test_tools.py`'den dört,
`test_modes.py`'den bir. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 5 · Commit

```
test(queen-agent): red for looking at a character before it enters a frame
```
