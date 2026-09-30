# Madde 374 — Edit prompts kontrollerle biter — test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Edit prompts'un `THE_CHECKS` ile bittiğini, kontrollerin yalnız değişikliğin ulaştığı
karelere baktığını ve Check 4'ün yalnız senaryonun kadrosu değiştiyse koştuğunu isteyen testler, kırmızı.

**Mimari:** Tek test dosyası, `test_skills.py`. Yeni bölüm Edit prompts'un adımlarını ve 4. adımını
(başlığından `THE_CHECKS`'in başladığı yere kadar) keser, olgularını sorar. İki mevcut test maddenin
değiştirdiği şeyi yeniden tutar; tavan testi Edit prompts'a 830 verir.

**Teknoloji:** pytest.

**Spec:** [testler spec'i](../specs/2026-09-30-queenagent-m374-edit-prompts-kontroller-testler-design.md)

## Genel kısıtlar

- Dört test satırı, yazıldığı gibi, paralel; boru, filtre, daraltma yok.
- `skip` / `xfail` yok.
- Tavanlar: akış 1025, Edit prompts 830 (700'den), Improve 700.
- Edit prompts'un adımları: `Step 1 -- what the request is about`, `Step 2 -- the fix`,
  `Step 3 -- the prompts`, `Step 4 -- the checks`.
- Test adları ve yorumlar İngilizce.

---

### Görev 1: Edit prompts'un kontrolleri

**Dosyalar:**
- Değişir: `queen-agent/backend/tests/test_skills.py` — 373 bölümünün arkası
  (`test_the_closing_names_the_negative_file_too`'dan sonra); `test_the_editor_writes_no_frames_at_all`;
  `test_the_editor_closes_with_the_file_rather_than_a_menu`; `test_the_texts_stay_short_enough_to_be_read`.

- [ ] **Adım 1: 373 bölümünün arkasına**

```python
# --- Edit prompts ends with the checks (Madde 374) ------------------------------------------------
#
# 28 Sep, the user: when Edit prompts is done, it should call Improve too. A skill cannot call another,
# so the editor carries the same checks the flow does -- the one constant. Two things differ, and both
# are written in the editor's own step: the checks read only the frames its change reached, and the
# negative prompt is written again only if the scenario's cast changed (the user's decision of 28
# September). 29 Sep: a changed frame gets its photo prompt again, never a video prompt.

EDIT_STEPS = (
    "Step 1 -- what the request is about",
    "Step 2 -- the fix",
    "Step 3 -- the prompts",
    "Step 4 -- the checks",
)


def _edits_checks_step():
    # From the step's heading to where the shared checks start: what the editor adds of its own.
    said = _edit()
    return said[said.index(EDIT_STEPS[3]) : said.index(_checks())]


def test_edit_prompts_ends_with_the_checks():
    checks = _checks()
    said = _edit()
    assert said.endswith(checks)
    assert said.count(checks) == 1


def test_edit_prompts_runs_its_steps_in_order():
    said = _edit()
    places = [said.index(step) for step in EDIT_STEPS]
    assert places == sorted(places)


def test_edit_prompts_goes_on_to_the_checks_in_the_same_turn():
    # The build is no longer the end, as in the flow: the change is said, and the checks follow it.
    said = _edit()
    step = said[said.index(EDIT_STEPS[2]) : said.index(EDIT_STEPS[3])]
    assert "build_prompts again" in step
    assert "which frames it reached" in step
    assert "waits for no approval" in step
    assert "Step 4" in step
    assert "last word" not in step


def test_after_an_edit_the_checks_read_only_the_frames_it_reached():
    # The checks read every frame by default and the step narrows them, so the flow and Improve read
    # the same block unchanged.
    assert "limits the checks to the frames your change reached" in _edits_checks_step()
    assert "every frame of the scenario unless this step limits them" in _checks()
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "your change reached" not in _flow()
    assert "your change reached" not in _improve()


def test_after_an_edit_the_negative_is_written_again_only_if_the_cast_changed():
    # The list is written from the scenario's cast (373), so an edit that left the cast alone left the
    # list true. The frame's cast is another thing (Check 2), so the step names the scenario's.
    step = _edits_checks_step()
    assert "Check 4 runs only if" in step
    assert "the scenario's cast" in step
    assert "added, changed or taken out" in step
    # In the flow and in Improve the negative is always written: the condition is the editor's alone.
    assert "runs only if" not in _checks()
```

- [ ] **Adım 2: `test_the_editor_writes_no_frames_at_all`** — `add_scene` yalnız Edit prompts'un kendi
  kısmında aranır:

```python
def test_the_editor_writes_no_frames_at_all():
    # Madde 128 put add_frames in this text; Madde 173 replaced the tool and Madde 178 moved the
    # job. The frames arrive written -- what this skill does to a file is correct it. A text still
    # naming the adding tools would have two skills writing frames into one file, each from a
    # different idea of what is already there.
    #
    # Madde 374 ends the editor with the checks, and the first of them splits a frame with add_scene.
    # That is the checks' own road, so the editor's part is asked without them.
    said = _edit()
    own = said.removesuffix(_checks())
    assert "add_scene" not in own
    assert "add_frames" not in said
```

- [ ] **Adım 3: `test_the_editor_closes_with_the_file_rather_than_a_menu`**

```python
def test_the_editor_closes_with_the_file_rather_than_a_menu():
    # Madde 130. The base already forbids the closing menu (112), but the skill text is the last
    # thing in the request (93) and said nothing about closing -- so the trial's build turn read
    # its own output back, printed 25 prompts into the chat, and offered three choices over a file
    # already sitting in the project. A text that goes quiet is a text a weak model writes over.
    #
    # Madde 374 moves the closing to the checks the editor now ends with. It names the files and
    # prints no prompt back, which is what this test held of the editor's own last step.
    checks = _checks()
    assert _edit().endswith(checks)
    assert "Do not print the prompts back" in checks[checks.index(CLOSING) :]
```

- [ ] **Adım 4: Tavan testi** — yorumun sonuna 374'ün gerekçesi, Edit prompts'un satırı `<= 830`:

```python
    # Madde 374 raises the editor's to 830. It ends with the checks now, as the flow does, and its own
    # part gains the step that says which frames they read and when the negative is written again.
    # That part stays near 300 words; the rest is the block the flow's cap already binds.
    assert len(_flow().split()) <= 1025
    assert len(_edit().split()) <= 830
    assert len(_improve().split()) <= 700
```

### Görev 2: Kırmızıyı gör ve commit

- [ ] **Adım 1: Dört satırı paralel çalıştır** — `python -m pytest queen-agent -q`,
  `npm test --prefix queen-agent/frontend`, `python -m pytest queen-editor -q`,
  `npm test --prefix queen-editor/frontend`. Beklenen kırmızılar `test_skills.py`'de: yeni beş test ve
  `test_the_editor_closes_with_the_file_rather_than_a_menu`. Geri kalan her şey yeşil; frontend'ler
  değişmez.

- [ ] **Adım 2: Commit** — spec ve plan aynı commit'te.

```
test(queen-agent): Madde 374 red -- Edit prompts ends with the checks, on the frames it changed
```
