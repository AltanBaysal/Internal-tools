# Madde 101 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m101-akis-testler-design.md](../specs/2026-08-28-queenagent-m101-akis-testler-design.md)
**Tur:** ikiden birincisi — **yalnız testler**. Kod yazılmıyor, kırmızı commit'leniyor.
**Komut:** `python -m pytest queen-agent -q` ve `npm test --prefix queen-agent/frontend`

---

## 1 · `queen-agent/backend/tests/test_skills.py`

`ALL_SKILLS` ikinciyi alıyor:

```python
# Written out rather than imported: the picker's ids live in the frontend's skills.js and Python
# cannot read it. If the two ever drift apart, a skill answers with no instruction at all -- so the
# match is pinned here, in words.
ALL_SKILLS = ["generate-prompts-plus", "start-a-scenario"]
```

`test_only_one_skill_is_offered` **gidiyor** — bu maddenin devirdiği cümle. Yerine:

```python
def test_the_menu_and_the_instructions_carry_the_same_names():
    # Two since Madde 101: the one that builds from a file that exists, and the one that walks the
    # user through making one. A name in the menu with no instruction here is a turn that quietly
    # runs on the base text.
    assert sorted(INSTRUCTIONS) == sorted(ALL_SKILLS)
```

Dosyanın sonuna, akışın kendi kırmızıları:

```python
# --- the flow that walks the user through it (Madde 101) -----------------------------------------


def _flow():
    return instruction_for("start-a-scenario")


def test_the_flow_writes_the_plan_before_it_asks_anything():
    # Step one whatever the user's opening sentence was. Without this the flow starts somewhere
    # different every time and has nowhere to keep its place.
    said = _flow()
    assert "write_plan" in said
    assert said.index("write_plan") < said.index("read_schema")


def test_the_flow_carries_on_from_a_plan_that_is_already_there():
    # How a conversation that grew too long is continued: files belong to the project, not the
    # chat, so a new chat finds the plan and picks up the step it left open.
    assert "carry on from the step it left open" in _flow()


def test_a_step_ends_when_the_user_approves_it():
    # Not when an answer is written. The two rules of the flow, and this is the one that keeps a
    # step from running away with the work.
    assert "approves" in _flow()


def test_what_nobody_described_becomes_a_placeholder():
    # K34. A flow that stops to ask for a description is a flow that never reaches the prompts.
    said = _flow()
    assert "placeholder" in said
    assert "never stop the flow" in said.lower()


def test_the_scenes_step_writes_a_readable_list_too():
    # K33, and its known cost: the same scene lives as tags in the structure file and as a sentence
    # in the list. Nothing in the code keeps the two together.
    assert "one sentence" in _flow()


def test_the_flow_builds_the_prompts_itself():
    # K32. The last step is the flow's own move -- the user does not change skill to finish what
    # they started.
    said = _flow()
    assert "build_prompts" in said
    assert "does not change skill" in said


def test_the_flow_reads_the_schema_before_it_writes_the_structure():
    # The same order the other skill keeps, and the same reason: the shape is fetched when it is
    # needed rather than carried in every request.
    said = _flow()
    assert said.index("read_schema") < said.index("build_prompts")
```

## 2 · `queen-agent/frontend/src/features/workspace/skills.test.js`

`test("the one skill left is the one that builds")` **gidiyor**. Yerine, ve iki test daha:

```js
test("the menu offers the flow and the builder, in that order", () => {
  // Madde 101. The flow comes first: it is the road for somebody with nothing yet, and the builder
  // is for somebody who already has a file.
  expect(SKILLS.map((skill) => skill.id)).toEqual(["start-a-scenario", "generate-prompts-plus"]);
});

test("the flow's name is the label, not the id", () => {
  expect(skillName("start-a-scenario")).toBe("Start a scenario");
});

test("the two rows tell each other apart", () => {
  // A picker whose rows describe the same job is a picker that says nothing. The builder's line is
  // the one that has to name its condition: a structure file that already exists.
  const builder = SKILLS.find((skill) => skill.id === "generate-prompts-plus");
  expect(builder.detail).toMatch(/already have/i);
});
```

## 3 · Koş

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Beklenen: arka yüzde **dokuz kırmızı** — parametreli testin yeni hâli, adları eşleyen test, ve
akışın yedisi. Ön yüzde **üç**. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 4 · Commit

```
test(queen-agent): red for the skill that walks the user through it
```
