# Madde 370 — Improve skill'i ve tek an kontrolü: test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Improve'u, tek yerde yazılan kontrolleri ve ilk kontrolü (tek an) tutan testler. Yalnız test;
metin ve kod yok.

**Mimari:** Kontroller `prompt.THE_CHECKS`'te duracak; testler kontrolün olgularını orada, iki skill'in
onunla bittiğini `instruction_for` üstünden sorar. Frontend'de yalnız `skills.test.js` değişir.

**Teknoloji:** pytest, vitest.

**Spec:** [2026-09-29-queenagent-m370-improve-tek-an-testler-design.md](../specs/2026-09-29-queenagent-m370-improve-tek-an-testler-design.md)

## Genel kısıtlar

- Testler İngilizce; yorum NEDEN'i söyler.
- `skip`/`xfail`/`.skip`/`.todo` yok.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşar.
- Commit mesajında çift tırnak yok, amend yok.
- Improve'un id'si `improve`, adı `Improve`, açıklaması birebir: `Run four checks on a scenario's frames and prompts, and say yes after each one.`

---

### Görev 1: `test_skills.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_skills.py`

**Arayüzler:** Kullanır: `instruction_for`, `INSTRUCTIONS` (`domain/skills.py`); ileride gelecek
`THE_CHECKS` (`domain/prompt.py`, str) — testin içinde import edilir, ki modül yüklenirken değil test
koşarken kırmızı versin.

- [ ] **Adım 1:** `ALL_SKILLS = ["edit-prompts", "improve", "start-a-scenario"]`, ve `_edit()`'in altına:

```python
def _improve():
    """Madde 370's skill: the checks, run on a scenario that is already built."""
    return instruction_for("improve")
```

- [ ] **Adım 2:** `test_no_step_is_ticked_off_the_plan_at_all`'ın yorumunun sonuna: kontroller plana
  hangi kontrolde olduğunu yazar (370, kullanıcının 28 Eylül kararı), çünkü düzeltilmiş kare
  bakılmamış kareyle aynı görünür; adım 1–5 yine hiçbir şeyi işaretlemez. İddialar aynı kalır.
- [ ] **Adım 3:** `STEPS`'e `"Step 6 -- the checks"`, docstring'e 370'in cümlesi; altı adım testi:

```python
def test_the_flow_runs_six_numbered_steps():
    # Madde 108: a stage outside the numbered list is a stage a weak model walks past, because it
    # stops when the list ends. Six since Madde 370: the checks are the flow's last step.
    said = _flow().lower()
    assert "six steps" in said
    assert "five steps" not in said
    for step in STEPS:
        assert step.lower() in said, step
```

- [ ] **Adım 4:** Madde 369'un bölümünün altına yeni bölüm:

```python
# --- the checks, and Improve (Madde 370) ----------------------------------------------------------
#
# 28 Sep, the user: the questions they ask the model by hand become checks, written in one place.
# Improve runs them on a scenario that is already built, and Start a scenario ends with them -- a
# skill cannot call another today, so both texts carry the same part, and it is one constant so it is
# said once. 29 Sep: a check that changes a frame refreshes its photo prompt only; the video's prompt
# is written in queen-editor.


def _checks():
    from backend.features.workspace.domain.prompt import THE_CHECKS

    return THE_CHECKS


def test_the_checks_are_written_once_and_both_skills_end_with_them():
    checks = _checks()
    assert checks.strip()
    for said in (_flow(), _improve()):
        assert said.endswith(checks)
        assert said.count(checks) == 1


def test_the_first_check_brings_a_frame_down_to_one_moment_or_splits_it():
    checks = _checks()
    assert "Check 1 -- one moment" in checks
    assert "more than one moment" in checks
    assert "split" in checks


def test_a_changed_or_split_frame_gets_its_photo_prompt_written_again():
    # A frame whose scene changed while its action stayed would build into the old picture, and a
    # frame split off would have no action at all. The tools that exist already do both.
    checks = _checks()
    for tool in ("update_frame", "add_scene", "write_missing_actions", "build_prompts"):
        assert tool in checks, tool
    assert "photo prompt" in checks


def test_each_check_shows_what_it_changed_and_waits_for_a_yes():
    # The user: I want to see what was done -- at the end of every check step.
    checks = _checks().lower()
    assert "show what" in checks
    assert "wait for their yes" in checks


def test_a_long_scenario_carries_the_checks_over_turns_through_the_plan():
    # The turn limit stays at 16 requests. Where the checks stopped is kept in the plan, and the
    # user says continue.
    checks = _checks().lower()
    assert "plan" in checks
    assert "continue" in checks


def test_the_checks_write_no_video_prompt():
    checks = _checks().lower()
    # Asked after the presence, so the absence cannot pass on a text nobody wrote.
    assert "photo prompt" in checks
    assert "video" not in checks
    assert "h3" not in checks


def test_the_closing_word_comes_after_the_checks():
    # The build is no longer the end: the checks follow it in the same flow, and the closing
    # sentence goes with the last of them, so the checks still to come land in front of it.
    said = _flow()
    assert "offer nothing, and ask nothing" in _checks()
    build = said[said.index(STEPS[4]) : said.index(STEPS[5])]
    assert "waits for no approval" in build
    assert "last word" not in build


def test_improve_opens_as_a_persona_on_a_scenario_already_built():
    said = _improve()
    assert said.startswith("You are an expert")
    assert "already" in said
    assert "start_scenario" not in said
```

- [ ] **Adım 5:** Tavan testinin yorumuna Improve'un kararı *(spec, karar 7)* ve
  `assert len(_improve().split()) <= 700`.

### Görev 2: `test_prompt.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_prompt.py`

- [ ] `MUST_BE_FULL`'a `"IMPROVE"` ve `"THE_CHECKS"`.

### Görev 3: `skills.test.js`

**Dosyalar:** Değişir: `queen-agent/frontend/src/features/workspace/skills.test.js`

- [ ] İlk test üç satırı ister; yeni test Improve'un satırını:

```js
test("the menu offers the flow, the editor and Improve, in that order", () => {
  // Improve stands last, after Edit prompts (design, items 138 and 179): it is run on what the
  // other two have made.
  expect(SKILLS.map((skill) => skill.id)).toEqual(["start-a-scenario", "edit-prompts", "improve"]);
});

test("Improve's row carries the design's own words", () => {
  const improve = SKILLS.find((skill) => skill.id === "improve");
  expect(improve.name).toBe("Improve");
  expect(improve.detail).toBe(
    "Run four checks on a scenario's frames and prompts, and say yes after each one.",
  );
});
```

### Görev 4: Kırmızı

- [ ] Dört satır, paralel, olduğu gibi. Beklenen kırmızı yalnız yeni ve değişen testler; queen-editor
  yeşil.
- [ ] Commit: `test(queen-agent): Madde 370 red -- Improve opens with its first check, one moment`
