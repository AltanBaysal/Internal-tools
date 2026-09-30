# Madde 373 — Negatif prompt — test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** `THE_CHECKS`'in dördüncü kontrolünü (negatif prompt) ve onu ayrı dosyaya yazan
`write_negative` aracını isteyen testler, kırmızı.

**Mimari:** Üç test dosyası. `test_skills.py` Check 4 bloğunu ve kapanışı keser, olgularını sorar;
akışın tavanı 1025'e çıkar. `test_tools.py` aracı gerçek dosya deposuyla (`tmp_path`) çağırır.
`test_modes.py` ask modunun onu sorduğunu ister.

**Teknoloji:** pytest.

**Spec:** [testler spec'i](../specs/2026-09-29-queenagent-m373-negatif-prompt-testler-design.md)

## Genel kısıtlar

- Dört test satırı, yazıldığı gibi, paralel; boru, filtre, daraltma yok.
- `skip` / `xfail` yok.
- Tavanlar: akış 1025 (1000'den), Edit prompts 700, Improve 700.
- Negatif dosyanın adı: `<yapının kökü>-negative.txt`; içeriği yalnız verilen etiketler.
- Test adları ve yorumlar İngilizce.

---

### Görev 1: Check 4'ün ve kapanışın testleri

**Dosyalar:**
- Değişir: `queen-agent/backend/tests/test_skills.py` — 372 bölümünün arkası; tavan testi.

- [ ] **Adım 1: 372 bölümünün (`test_the_third_check_does_not_tell_the_model_is_weak_again`) arkasına**

```python
# --- the fourth check: the negative prompt (Madde 373) --------------------------------------------
#
# 28 Sep, the user: a negative prompt of the scenario's and its characters' own, so the characters'
# features do not mix. One list per scenario, from its cast, as the last of the checks; it goes into a
# file of its own beside the prompt list, and the user copies it into queen-editor's negative field by
# hand (v9-7). The user's lessons are the rules: a negative works on the whole picture, never on one
# person, so a character's own feature never goes in -- dark skin there turned the man white -- and
# tags that fit only the other one go in instead (pale male, white man). 374 writes the list again
# when the cast changes, so it is written whole each time rather than added to.

FOURTH_CHECK = "Check 4 -- the negative prompt"


def _fourth_check():
    checks = _checks()
    start = checks.index(FOURTH_CHECK)
    return checks[start : checks.index("\n\n", start)]


def test_the_fourth_check_comes_after_the_third_and_before_the_closing():
    checks = _checks()
    assert FOURTH_CHECK in checks
    assert checks.index(THIRD_CHECK) < checks.index(FOURTH_CHECK) < checks.index(CLOSING)


def test_the_negative_prompt_is_one_list_written_whole_from_the_cast():
    said = _fourth_check()
    assert "one negative prompt" in said
    assert "cast" in said
    assert "write_negative" in said
    assert "never added to" in said


def test_the_negative_prompt_never_holds_a_characters_own_feature():
    said = _fourth_check()
    assert "whole picture" in said
    assert "own feature" in said
    assert "pale male" in said
    assert "white man" in said


def test_the_negative_check_changes_no_frame_and_waits_for_a_yes():
    said = _fourth_check()
    assert "no frame" in said
    assert "wait for their yes" in said


def test_the_closing_names_the_negative_file_too():
    # Two files come out of the checks now, and the user copies the second by hand: a closing that
    # named one would leave them looking for the other.
    checks = _checks()
    assert "negative file" in checks[checks.index(CLOSING) :]
```

- [ ] **Adım 2: Tavan testi** — `test_the_texts_stay_short_enough_to_be_read`'in yorumuna 373'ün
  gerekçesi eklenir, akışın satırı `<= 1025` olur:

```python
    # Madde 373 raises the flow's to 1025. The fourth check carries the user's own lessons about the
    # negative prompt, and with them it does not fit in the hundred words the first three left; the
    # closing names the second file as well. Improve carries the same block and stays inside its 700.
    assert len(_flow().split()) <= 1025
```

### Görev 2: `write_negative`'in testleri

**Dosyalar:**
- Değişir: `queen-agent/backend/tests/test_tools.py` — `test_every_tool_is_declared_to_the_model`'in
  kümesi; `test_a_python_source_is_refused_so_it_is_not_written_over`'ın arkasına yeni bölüm.
- Değişir: `queen-agent/backend/tests/test_modes.py` — `WRITES`.

**Arayüz (uygulamanın üreteceği):** araç adı `write_negative`, argümanlar `file` (yapı dosyası) ve
`tags`; `ToolResult.created` yazılan dosya, `.target` yapı dosyası, `.outcome` `Written`; boş liste
`needs tags` der; yapı yoksa `no file by that name`.

- [ ] **Adım 1: `test_every_tool_is_declared_to_the_model`'in kümesine, `write_missing_actions`'tan sonra**

```python
        # Madde 373. The scenario's negative prompt, in a file of its own beside the prompt list: the
        # name is the code's, and the file is written whole every time.
        "write_negative",
```

- [ ] **Adım 2: Yeni bölüm**

```python
# --- the scenario's negative prompt, in a file of its own (Madde 373) -----------------------------
#
# 28 Sep, the user: the negative list stays apart from the prompt list, and the user copies it into
# queen-editor's negative field by hand. So the file holds the tags and nothing else -- the panel's
# Copy takes a file whole (Madde 193) -- and its name is the code's, beside the prompt list, so it
# comes out the same every time. Written over rather than refused when it is there: 374 writes it
# again when the cast changes, and that is a rewrite, not an edit of the old list.


def _negative(files, **arguments):
    return run_tool(files, "p1", "write_negative", json.dumps(arguments))


def test_the_negative_list_is_written_beside_the_prompt_list(tmp_path):
    from backend.features.workspace.domain.tools import WRITES_FILES

    files = _with(tmp_path, "bar-scene.json", STRUCTURE)
    written = _negative(files, file="bar-scene.json", tags="pale male, white man")
    assert written.created == "bar-scene-negative.txt"
    assert files.read("p1", "bar-scene-negative.txt") == "pale male, white man"
    assert "write_negative" in WRITES_FILES


def test_writing_the_negative_again_replaces_it(tmp_path):
    files = _with(tmp_path, "bar-scene.json", STRUCTURE)
    _negative(files, file="bar-scene.json", tags="pale male")
    _negative(files, file="bar-scene.json", tags="white man")
    assert sorted(files.list_names("p1")) == ["bar-scene-negative.txt", "bar-scene.json"]
    assert files.read("p1", "bar-scene-negative.txt") == "white man"


def test_a_negative_for_a_scenario_that_is_not_there_is_refused(tmp_path):
    files = _with(tmp_path, "plan.md", "one")
    assert "no file by that name" in _negative(files, file="ghost.json", tags="pale male").text
    assert files.list_names("p1") == ["plan.md"]


def test_a_negative_with_no_tags_is_refused(tmp_path):
    files = _with(tmp_path, "bar-scene.json", STRUCTURE)
    assert "needs tags" in _negative(files, file="bar-scene.json", tags="  ").text
    assert files.list_names("p1") == ["bar-scene.json"]


def test_the_negative_call_reports_the_structure_and_says_it_wrote(tmp_path):
    # The structure rather than the output, as a build does: the card already names what was written.
    files = _with(tmp_path, "bar-scene.json", STRUCTURE)
    written = _negative(files, file="bar-scene.json", tags="pale male")
    assert written.target == "bar-scene.json"
    assert written.outcome == "Written"


def test_the_negative_tool_says_the_file_is_one_list_to_copy_whole():
    said = _said_by("write_negative").lower()
    assert "negative" in said
    assert "copy" in said
    assert "replaces" in said
```

- [ ] **Adım 3: `test_modes.py`'de `WRITES`'a, `remove_frame`'den sonra**

```python
    # Madde 373. It writes a file beside the prompt list, and a file appearing is what the quieter
    # modes gate.
    "write_negative",
```

### Görev 3: Kırmızıyı gör ve commit

- [ ] **Adım 1: Dört satırı paralel çalıştır** — `python -m pytest queen-agent -q`,
  `npm test --prefix queen-agent/frontend`, `python -m pytest queen-editor -q`,
  `npm test --prefix queen-editor/frontend`. Beklenen kırmızılar: `test_skills.py`'de yeni beş test,
  `test_tools.py`'de küme testi ve yeni altı test, `test_modes.py`'de
  `test_ask_mode_asks_before_it_writes`. Geri kalan her şey yeşil; frontend'ler değişmez.

- [ ] **Adım 2: Commit** — spec ve plan aynı commit'te.

```
test(queen-agent): Madde 373 red -- the negative prompt is the fourth check, in a file of its own
```
