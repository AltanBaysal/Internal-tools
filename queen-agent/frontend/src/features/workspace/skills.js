// Three rows since Madde 370. Not zero rows even at one: having no skill selected is an ordinary
// state.
//
// The flow comes first because that is the answer to "which do I want": somebody with nothing yet
// takes the flow, somebody who already has prompts takes the editor. Since Madde 186 the two are
// the halves of the work rather than two roads into it -- the flow runs all the way to the built
// file, so nobody comes out of it needing a second row to finish. Improve stands last (design,
// items 138 and 179): it checks what the other two made, and its line is the design's own.
export const SKILLS = [
  {
    id: "start-a-scenario",
    name: "Start a scenario",
    detail: "Answer a few questions and get the characters, the places and the prompts.",
  },
  {
    id: "edit-prompts",
    name: "Edit prompts",
    detail: "Fix what is wrong in prompts you already have, and build them again.",
  },
  {
    id: "improve",
    name: "Improve",
    detail: "Run four checks on a scenario's frames and prompts, and say yes after each one.",
  },
];

// No skill is the ordinary state, so the empty case is the button's own word rather than a gap. A
// record can still name one of the deleted five: the button says its id rather than going blank.
export function skillName(id) {
  if (!id) return "Skills";
  return SKILLS.find((skill) => skill.id === id)?.name ?? id;
}
