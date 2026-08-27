// One row since Madde 94, which deleted the other five. Not zero rows: having no skill selected is
// an ordinary state, so even a one-row list carries two -- and the list will grow again.
//
// The second line says what a skill does and, where it applies, that a file comes out of it: a file
// appearing unasked is the surprising part, so the menu says it before the user finds out.
export const SKILLS = [
  {
    id: "generate-prompts-plus",
    name: "Generate prompts+",
    detail: "Build from parts, so a character never drifts.",
  },
];

// No skill is the ordinary state, so the empty case is the button's own word rather than a gap. A
// record can still name one of the five: the button says its id rather than going blank.
export function skillName(id) {
  if (!id) return "Skills";
  return SKILLS.find((skill) => skill.id === id)?.name ?? id;
}
