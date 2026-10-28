# Madde 366 — Liste yeni biçimde çıkar: test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Prompt listesinin her karesinin `{"scene", "photo"}` kaydı olarak çıktığını söyleyen testler — yalnız testler, kod yok.

**Mimari:** `build_prompts` kayıt listesi döndürür, `render_module` onu yazar; testler iki ucu da, ve aracın yazdığı dosyayı sabitler.

**Teknoloji:** pytest, `ast`.

**Spec:** [2026-09-29-queenagent-m366-liste-kayit-testler-design.md](../specs/2026-09-29-queenagent-m366-liste-kayit-testler-design.md)

## Genel kısıtlar

- Testler İngilizce; yorum NEDEN'i söyler.
- `skip`/`xfail` yok.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşar.
- Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: `test_build_prompts.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_build_prompts.py`

- [ ] **Adım 1: `_photos` yardımcısı**, `_prompts_of`'un yanına:

```python
def _photos(structure):
    # Madde 366: a frame goes out as a record, and everything this file says about how a prompt is
    # assembled is said about one field of it. Read through here so those claims stay as written.
    return [record["photo"] for record in build_prompts(structure)]
```

- [ ] **Adım 2: Bugünkü prompt iddiaları `_photos`'tan okur.** `build_prompts(_structure` →
  `_photos(_structure`, `build_prompts(structure)` → `_photos(structure)` — `_photos`'un kendi
  gövdesi hariç. Yalnız reddi bekleyen iki çağrı (`{"quality": …}` ve `["a list"]`) `build_prompts`'ta
  kalır: dönüş değerine bakmıyorlar. `from … import build_prompts` modül içe aktarması dokunulmaz.

- [ ] **Adım 3: Kaydın kendisi.**

```python
def test_each_frame_goes_out_as_its_scene_and_its_photo():
    structure = _structure(frames=[_frame(scene="Aylin wakes up.")])
    assert build_prompts(structure) == [
        {
            "scene": "Aylin wakes up.",
            "photo": f"{DEFAULT_QUALITY}, {AYLIN}{BREAK}an action, a camera, {BEDROOM}",
        }
    ]


def test_every_frame_keeps_its_own_scene_in_order():
    frames = [_frame(scene="one"), _frame(scene="two")]
    assert [record["scene"] for record in build_prompts(_structure(frames=frames))] == ["one", "two"]


def test_a_record_holds_the_scene_and_the_photo_and_nothing_else():
    record = build_prompts(_structure(frames=[_frame(scene="s")]))[0]
    assert set(record) == {"scene", "photo"}


def test_a_frame_without_a_scene_goes_out_with_an_empty_one():
    assert build_prompts(_structure())[0]["scene"] == ""
```

- [ ] **Adım 4: Üç render testi kayda döner.**

```python
def test_the_written_module_is_valid_python_and_holds_the_records():
    records = [{"scene": "she wakes", "photo": "one, two"}, {"scene": "she stands", "photo": "three"}]
    assert _prompts_of(render_module(records)) == records


def test_the_module_writes_each_record_in_triple_quotes_scene_first():
    assert render_module([{"scene": "she wakes", "photo": "one"}]) == (
        "PROMPTS = [\n"
        "    {\n"
        '        "scene": """she wakes""",\n'
        '        "photo": """one""",\n'
        "    },\n"
        "]\n"
    )


def test_quotes_a_backslash_and_turkish_letters_still_parse():
    tricky = [
        {"scene": 'Aylin "günaydın" diyor', "photo": 'a """quoted""" tag'},
        {"scene": 'she says "hi"', "photo": "a back\\slash"},
        {"scene": "ışık söndü\\", "photo": 'ends with a quote"'},
    ]
    assert _prompts_of(render_module(tricky)) == tricky
```

### Görev 2: `test_tools.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_tools.py`

- [ ] **Adım 1:** Başa `import ast`.
- [ ] **Adım 2:** `test_the_build_tool_tells_the_model_it_assembles_frames`'in altına:

```python
def test_the_build_tool_says_each_frame_goes_out_with_its_scene():
    built = next(spec for spec in TOOL_SPECS if spec["function"]["name"] == "build_prompts")
    assert "scene" in built["function"]["description"].lower()
```

- [ ] **Adım 3:** `test_building_writes_a_file_named_after_the_source`'un altına:

```python
def test_the_built_file_holds_each_frames_scene_beside_its_photo(tmp_path):
    structure = json.loads(STRUCTURE)
    structure["frames"][0]["scene"] = "Aylin uyanıyor."
    structure["frames"][1]["scene"] = "Aylin pencereye bakıyor."
    files = _with(tmp_path, "frames.json", json.dumps(structure))
    _call(files, "build_prompts", name="frames.json")
    records = ast.literal_eval(ast.parse(files.read("p1", "frames.py")).body[0].value)
    assert [record["scene"] for record in records] == ["Aylin uyanıyor.", "Aylin pencereye bakıyor."]
    assert "long teal hair" in records[0]["photo"] and "one" in records[0]["photo"]
```

### Görev 3: Kırmızı

- [ ] Dört satır, paralel, olduğu gibi. Beklenen: `test_build_prompts.py`'nin `_photos`'tan ve
  `build_prompts`'tan kayıt okuyan testleri kırmızı (bugün string dönüyor), render testleri kırmızı,
  `test_tools.py`'nin iki yeni testi kırmızı; queen-editor ve frontend'ler değişmez.
- [ ] Commit: `test(queen-agent): Madde 366 red -- the prompt list goes out as scene and photo records`
