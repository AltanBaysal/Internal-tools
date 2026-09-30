# Madde 394 — Improve · test turu planı

> **Ajanlar için:** bu plan satır satır, bu oturumda yürütülür (superpowers:executing-plans'ın
> biçimiyle); adımlar `- [ ]` kutularıyla.

**Amaç:** Improve'un üçüncü skill olarak kaydını, metninin biçimini ve seçicideki son satırını tutan
testleri yazmak, ve çalışma ağacında kırmızı olduklarını görmek.

**Yapı:** `test_skills.py` Improve'u kayıttan (`instruction_for("improve")`) okur; `IMPROVE_STEPS` ve
`_improve_step(number)` yeni testlerin ortak zemini, `STEPS` ve `_step` gibi. `test_prompt.py`'de bir satır,
ön uçta iki test dosyası. Kaynak koda (`prompt.py`, `skills.py`, `skills.js`) bu turda dokunulmaz.

**Araçlar:** pytest, vitest + Testing Library.

**Spec:** [2026-09-30-queenagent-m394-improve-testler-design.md](../specs/2026-09-30-queenagent-m394-improve-testler-design.md)

## Genel kısıtlar

- Dört test satırı, yazıldığı gibi, paralel: `python -m pytest queen-agent -q` ·
  `npm test --prefix queen-agent/frontend` · `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend`. Borulanmaz, süzülmez, daraltılmaz; iki `npm` satırı arka
  planda, özetleri kendi çıktı dosyalarından okunur.
- `skip`, `xfail`, `.skip`, `.todo` yok.
- `IMPROVE`, `START_A_SCENARIO`, `EDIT_PROMPTS`'un tek kelimesi değişmez.
- Test adları ve yorumları İngilizce; yorum neden'i ve yalnız bugün doğru olanı söyler. Satırlar 100 karakteri
  geçmez, dosyaların kendi biçimi gibi.
- Commit mesajı İngilizce, çift tırnaksız, PowerShell tek tırnaklı here-string ile; amend yok.

---

### Görev 1: Arka uç testleri

**Dosyalar:**
- Değişir: `queen-agent/backend/tests/test_skills.py`
- Değişir: `queen-agent/backend/tests/test_prompt.py`

**Arayüz:**
- Üretir: `_improve() -> str`, `IMPROVE_STEPS` (beş başlık), `IMPROVE_CHECKS = [1, 2, 3, 4]`,
  `_improve_step(number) -> str` (1'den sayan adım numarası; başlıktan sonraki başlığa ya da metnin sonuna).
- Kullanır: `LAST_WORD` (dosyada zaten var).

- [ ] **Adım 1: `ALL_SKILLS` ve `_improve()`**

```python
ALL_SKILLS = ["edit-prompts", "improve", "start-a-scenario"]
```

`_edit()`'in arkasına:

```python
def _improve():
    """Madde 394's skill: the flow's checks, run on a scenario that already exists."""
    return instruction_for("improve")
```

- [ ] **Adım 2: `test_the_menu_and_the_instructions_carry_the_same_names`'in yorumu**

```python
def test_the_menu_and_the_instructions_carry_the_same_names():
    # Three since Madde 394. Madde 186 made the first two the halves of the work rather than two
    # ways into it: one makes a scenario and finishes it, the other fixes what the user points at.
    # Improve runs the flow's checks again on a scenario that already exists. A name in the menu
    # with no instruction here is a turn that quietly runs on the base text alone.
    assert sorted(INSTRUCTIONS) == sorted(ALL_SKILLS)
```

- [ ] **Adım 3: `test_the_checks_are_written_in_the_flow_itself` `IMPROVE`'u dışarıda bırakır**

Yorumun ikinci paragrafına iki satır, ve koşula `"IMPROVE"`:

```python
    # The editor's text is left out: it is a skill of its own and joined into nothing, and since
    # Madde 393 both skills close a change with the same plain line, build the prompts again.
    # Improve's is left out as well: Madde 394, the owner's decision of 30 September, copies these
    # steps into it word for word, and it too is a skill of its own, joined into nothing.
    ...
        if isinstance(value, str) and name not in ("START_A_SCENARIO", "EDIT_PROMPTS", "IMPROVE"):
```

- [ ] **Adım 4: Improve'un bölümü** — `test_the_checks_are_written_in_the_flow_itself`'in hemen arkasına:

```python
# --- Improve: the checks on a scenario that already exists (Madde 394) ----------------------------
#
# 30 September, the owner: Improve is a skill of its own, like Edit prompts, and its text is Start a
# scenario's Steps 6 - 10 copied word for word -- only the context at the head differs. Written with
# the owner line by line: the steps are numbered 1 - 5, Step 5's six rules move into the context,
# and the prompts are built once before the steps.

IMPROVE_STEPS = (
    "Step 1 -- fit each scene into four seconds",
    "Step 2 -- fit each prompt into one photo",
    "Step 3 -- remove tags hidden by the camera angle",
    "Step 4 -- simplify prompts too hard to draw",
    "Step 5 -- write the negative list",
)
IMPROVE_CHECKS = [1, 2, 3, 4]


def _improve_step(number):
    """One step of Improve by its own number, cut the way _step cuts the flow's."""
    said = _improve()
    start = said.index(IMPROVE_STEPS[number - 1])
    if number == len(IMPROVE_STEPS):
        return said[start:]
    return said[start : said.index(IMPROVE_STEPS[number])]


def test_improve_opens_as_a_persona():
    # The owner: the same writer as the other two skills, and the context says the scenario is
    # already there -- Improve checks a scenario, it never starts one.
    said = _improve()
    assert said.startswith("You are an expert scenario writer and prompt writer.")
    assert "You improve an existing scenario JSON" in said


def test_improve_runs_five_numbered_steps():
    # Madde 108's reason holds here too: a stage outside the numbered list is a stage a weak model
    # walks past. The flow's ten are its own; Improve counts from one.
    said = _improve().lower()
    assert "five steps" in said
    assert "ten steps" not in said
    for step in IMPROVE_STEPS:
        assert step.lower() in said, step


def test_improves_steps_are_written_in_the_order_they_run():
    # The flow's order: the scenes are fitted before the prompts are cut, and the negative list is
    # written once the prompts are final.
    said = _improve()
    places = [said.index(step) for step in IMPROVE_STEPS]
    assert places == sorted(places)


@pytest.mark.parametrize("number", IMPROVE_CHECKS)
def test_every_improve_check_says_why_then_reviews_then_fixes(number):
    # The flow's checks, numbered from one: the reason first, then the review written to a file of
    # the check's own -- or no file when nothing fails -- then a fix of the listed frames alone.
    said = _improve_step(number)
    places = [said.index(part) for part in ("Context", "Part 1 -- review", "Part 2 -- fix")]
    assert places == sorted(places)
    assert f"-review-{number}.md" in said
    assert "write no review file" in said
    assert "Fix only the frames in the review file." in said


@pytest.mark.parametrize("number", IMPROVE_CHECKS)
def test_improves_checks_wait_for_no_approval(number):
    # The owner: update directly. Nothing in Improve asks for a yes, so each check says it goes on.
    said = _improve_step(number)
    assert "This step waits for no approval." in said
    assert f"Go on to Step {number + 1} in the same turn." in said


def test_improve_ends_by_writing_the_negative_list():
    # The flow's last step, unchanged: one list for the whole scenario, in a file of its own, and
    # the user is told the work is complete -- no approval line at the end.
    said = _improve_step(5)
    assert "-negative.md" in said
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "approval" not in said
    assert _improve().endswith(LAST_WORD)


def test_improves_context_carries_the_six_rules():
    # The owner: the rules of the flow's Step 5 go into Improve's context, in front of the steps,
    # and a check that changes a frame updates the frame by them. Step 1 says the rules rather than
    # the rules of Step 5: Improve's own Step 5 is the negative list.
    said = _improve()
    context = said[: said.index("Before the steps:")]
    for number in range(1, 7):
        assert f"- Rule {number}:" in context, number
    assert "Update each changed frame and each new frame by the rules." in _improve_step(1)


def test_improve_builds_the_prompts_before_the_first_step():
    # The checks read the built prompt file, and a scenario changed since its last build would be
    # checked against an old one -- so the file is read and the prompts are built once, before
    # Step 1.
    said = _improve()
    before = said[said.index("Before the steps:") : said.index(IMPROVE_STEPS[0])]
    assert "- Read the scenario file named in the request." in before
    assert "- Build the prompts, so the built prompt file matches the scenario file." in before
```

- [ ] **Adım 5: `test_every_skill_says_what_the_prompts_are_for` noktayı bırakır**

```python
    # Madde 393, the owner: what the work is for is a video now. Every text opens with a context
    # that says the prompt makes a photo, the video starts from the photo, and the image model is
    # weak. The owner took the model's name out -- the context says what the model is like instead.
    #
    # Asked without the full stop since Madde 394: Improve says it in one sentence with what the
    # model does with a tag, "The image model is weak and draws every tag", and the claim is the
    # weakness rather than where the sentence ends.
    said = instruction_for(skill)
    assert "The prompt of the frame makes a photo. The video starts from the photo." in said
    assert "The image model is weak" in said
    assert "SDXL" not in said
```

- [ ] **Adım 6: Improve'un kelime tavanı** — `test_the_texts_stay_short_enough_to_be_read`'in yorumunun
  sonuna bir paragraf, ve üçüncü satır:

```python
    #
    # Madde 394 gives Improve a cap of its own, written here as the rule asks. The owner wrote its
    # text line by line as the flow's Steps 6 - 10 word for word, with Step 5's six rules in its
    # context and a short block before the steps that reads the file and builds the prompts. The cap
    # is what that text came to and a few words of room -- not room for the next sentence.
    assert len(_flow().split()) <= 1830
    assert len(_edit().split()) <= 205
    assert len(_improve().split()) <= 1480
```

- [ ] **Adım 7: `test_prompt.py`'de `MUST_BE_FULL`**

```python
MUST_BE_FULL = (
    "SYSTEM_PROMPT",
    "LAST_ROUND",
    "SDXL_PROMPT_RULES",
    "START_A_SCENARIO",
    "EDIT_PROMPTS",
    "IMPROVE",
)
```

### Görev 2: Ön uç testleri

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/features/workspace/skills.test.js`
- Değişir: `queen-agent/frontend/src/features/workspace/SkillPicker.test.jsx`

- [ ] **Adım 1: `skills.test.js` — sıra üç satır, başlık, ve Improve en sonda**

```js
test("the menu offers the flow, the editor and Improve, in that order", () => {
  // The flow comes first: it is the road for somebody with nothing yet, and since Madde 186 it
  // runs the whole way to the prompts. The second row is for somebody who has them already, and
  // the third, since Madde 394, checks a scenario that is already there.
  expect(SKILLS.map((skill) => skill.id)).toEqual([
    "start-a-scenario",
    "edit-prompts",
    "improve",
  ]);
});

test("Improve stands last and says what it does", () => {
  // Madde 394. Its steps wait for no yes, so the line promises none -- the designer's placeholder
  // asked for one after each step, and that is not what happens.
  expect(SKILLS[SKILLS.length - 1]).toEqual({
    id: "improve",
    name: "Improve",
    detail: "Check a scenario you already have, fix what fails, and write its negative list again.",
  });
});

test("the rows tell each other apart", () => {
  // Yalnız ad değişir: "the two rows" doğru olmaktan çıktı; gövde ve yorumu olduğu gibi kalır.
});
```

- [ ] **Adım 2: `SkillPicker.test.jsx` — açık seçicide sıra**

```js
test("open, Improve is the last row, right after Edit prompts", () => {
  // Madde 394: the third row goes at the end, so the two that were there keep their places.
  const { container } = render(<SkillPicker skill="" open />);
  const names = [...container.querySelectorAll(".menu__item-name")].map(
    (name) => name.textContent,
  );
  expect(names).toEqual(["Start a scenario", "Edit prompts", "Improve"]);
  const detail =
    "Check a scenario you already have, fix what fails, and write its negative list again.";
  expect(screen.getByText(detail)).toBeTruthy();
});
```

### Görev 3: Kırmızıyı gör ve commit'le

- [ ] **Adım 1: Dört satırı paralel koş** — iki `npm` satırı arka planda.

Beklenen: `python -m pytest queen-agent -q`'da tam 17 test kırmızı — `test_every_skill_in_the_menu_carries_an_instruction[improve]`,
`test_the_menu_and_the_instructions_carry_the_same_names`, `test_every_skill_says_what_the_prompts_are_for[improve]`,
ve Improve bölümünün 14'ü (parametreliler dahil) —, geri kalanı yeşil; `test_the_checks_are_written_in_the_flow_itself`
yeşile dönmüş. `npm test --prefix queen-agent/frontend`'de 3 test kırmızı. queen-editor'ün iki süiti yeşil.

- [ ] **Adım 2: Commit** — yalnız dört test dosyası, spec ve bu plan; `prompt.py` staged edilmez.

```powershell
git add queen-agent/backend/tests/test_skills.py queen-agent/backend/tests/test_prompt.py queen-agent/frontend/src/features/workspace/skills.test.js queen-agent/frontend/src/features/workspace/SkillPicker.test.jsx docs/superpowers/specs/2026-09-30-queenagent-m394-improve-testler-design.md docs/superpowers/plans/2026-09-30-queenagent-m394-improve-testler-plan.md
git commit -m @'
test(queen-agent): 394 -- Improve is a third skill, pinned red

The menu and the instructions carry improve, and Improve's text is pinned
the way the flow's is: a persona, five steps in order, each check a
context, a review into its own -review-N.md and a fix, no approval, the
negative list last, the six rules in its context, and the prompts built
before the steps. The picker lists Improve last. Red until the skill is
registered; the text itself waits uncommitted in prompt.py.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
