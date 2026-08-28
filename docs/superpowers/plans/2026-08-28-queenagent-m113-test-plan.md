# Madde 113 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m113-duzenleme-testler-design.md](../specs/2026-08-28-queenagent-m113-duzenleme-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/tests/test_skills.py` — prompt+ testlerinin arasına

```python
def test_the_builder_changes_what_exists_too():
    # Madde 94's record gave prompt+ the job of updating what exists; the sentence never reached
    # the text, so the skill read as a one-way builder -- and Madde 108 now sends people here.
    said = instruction_for("generate-prompts-plus")
    assert "or changed" in said
    assert "build_prompts again" in said


def test_a_change_goes_through_the_file_rather_than_the_prompt_list():
    # The prompt file is derived: patched by hand it stops matching the structure it came from.
    assert "rebuilt rather than patched" in instruction_for("generate-prompts-plus")
```

## B. `queen-agent/frontend/src/features/workspace/skills.test.js` — `the two rows tell each other apart` testinin ardına

```js
test("the builder's row says it changes prompts too", () => {
  // Madde 113: the skill builds and edits. A row that only says "build" sends somebody looking
  // for an editor that is not there.
  const builder = SKILLS.find((skill) => skill.id === "generate-prompts-plus");
  expect(builder.detail).toMatch(/change/i);
});
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_skills.py` | 2 |
| `skills.test.js` | 1 |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **`skills.py`, `skills.js` açılmaz** — tur 2'nin işi.
- **`dist` derlenmez.**
