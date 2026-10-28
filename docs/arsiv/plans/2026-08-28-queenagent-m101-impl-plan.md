# Madde 101 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m101-akis-uygulama-design.md](../specs/2026-08-28-queenagent-m101-akis-uygulama-design.md)
**Tur 1:** on iki kırmızı commit'lendi *(`cd87124`)*. Bu turda test yazılmaz.
**Komut:** `python -m pytest queen-agent -q` ve `npm test --prefix queen-agent/frontend`

---

## 1 · `domain/skills.py` — ikinci metin

Modül başlığının *"One text since Madde 94"* diyen paragrafı iki metni anlatır hâle geliyor:

```
Two texts since Madde 101. Five others stood here and were deleted in Madde 94: what they said
about how to work now sits in prompt.py, where it holds whatever is selected, and what they said
about their own task either lives in the texts below or went with them on purpose.
```

`GENERATE_PROMPTS_PLUS`'ın ardına:

```python
START_A_SCENARIO = (
    "When the user wants a scenario made, this skill walks them through it by asking. Five steps in "
    "a fixed order -- the plan, the characters, the places, the scenes, the prompts -- and each one "
    "leaves the same thing behind however much or little the user said. What changes with a talkative "
    "user is how many turns a step takes, never what it produces.\n"
    "\n"
    "The first move is always the same: list_files, then write_plan. Whatever the opening sentence "
    "was, the plan is written before anything is asked, and it is where the flow keeps its place. A "
    "plan already in the project is that memory -- read it and carry on from the step it left open "
    "rather than writing a second one, which is how work continues in a fresh chat when a "
    "conversation has grown too long. With more than one plan there, ask which.\n"
    "\n"
    "Call read_schema before writing the structure file. It hands back what the file looks like and "
    "the rules it has to hold; neither is repeated here, so there is one copy of both and it arrives "
    "when it is needed.\n"
    "\n"
    "A step ends when the user approves it, not when an answer is written. Say what was saved and "
    "ask; if they want something changed, change it and ask again. Nothing moves on in between.\n"
    "\n"
    "An answer arrives three ways and all three end the same. Tags the user wrote themselves are "
    "taken as they are. A description in their own words becomes tags. Nothing at all becomes a "
    "placeholder -- a plain character, a plain background -- and the step still ends. Never stop the "
    "flow waiting for a description.\n"
    "\n"
    "Clothes are written where they are heard: somebody described in a dress at the character step "
    "goes into outfits there, and the places step does not ask about it again.\n"
    "\n"
    "The scenes step writes twice -- the frames into the structure file, and a list of its own where "
    "each scene is one sentence. The list is what the user reads.\n"
    "\n"
    "Then build_prompts, which is the flow's own last move: the user does not change skill to finish "
    "what they started. Do not assemble a prompt by hand.\n"
    "\n"
    "A character can be looked at before entering a frame -- build_character_prompts gives one "
    "character against every outfit the file names. Offer it at the character step; it is a side "
    "door rather than a step, so carry on from where the flow was if the user is not interested."
)
```

`INSTRUCTIONS`:

```python
INSTRUCTIONS = {
    "generate-prompts-plus": GENERATE_PROMPTS_PLUS,
    "start-a-scenario": START_A_SCENARIO,
}
```

## 2 · `frontend/src/features/workspace/skills.js` — ikinci satır

```js
// Two rows since Madde 101, and Madde 94 said more would come. Not zero rows even at one: having no
// skill selected is an ordinary state.
//
// The flow comes first because that is the answer to "which do I want": somebody with nothing yet
// takes the flow, somebody holding a structure file takes the builder. The second line says when to
// pick a row rather than how the row works -- with two of them side by side, the condition is what
// tells them apart, and a file appearing unasked is the surprising part either way.
export const SKILLS = [
  {
    id: "start-a-scenario",
    name: "Start a scenario",
    detail: "Answer a few questions and get the characters, the scenes and their prompts.",
  },
  {
    id: "generate-prompts-plus",
    name: "Generate prompts+",
    detail: "Build the prompts from a structure file you already have.",
  },
];
```

`skillName` değişmiyor.

## 3 · Koş

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

On iki kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 4 · `dist`

```
npm run build --prefix queen-agent/frontend
```

Aynı commit'te.

## 5 · Commit

```
feat(queen-agent): a second skill that walks the user through a scenario
```
