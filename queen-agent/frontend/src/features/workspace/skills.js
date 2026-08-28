// Two rows since Madde 101, and Madde 94 said more would come. Not zero rows even at one: having no
// skill selected is an ordinary state.
//
// The flow comes first because that is the answer to "which do I want": somebody with nothing yet
// takes the flow, somebody already holding a structure file takes the builder. The second line says
// when to pick a row rather than how the row works -- with two of them side by side the condition
// is what tells them apart, and a file appearing unasked is the surprising part either way.
export const SKILLS = [
  {
    id: "start-a-scenario",
    name: "Start a scenario",
    detail: "Answer a few questions and get the characters, the places and the scene list.",
  },
  {
    id: "generate-prompts-plus",
    name: "Generate prompts+",
    detail: "Build the prompts from a structure file you already have.",
  },
];

// No skill is the ordinary state, so the empty case is the button's own word rather than a gap. A
// record can still name one of the deleted five: the button says its id rather than going blank.
export function skillName(id) {
  if (!id) return "Skills";
  return SKILLS.find((skill) => skill.id === id)?.name ?? id;
}
