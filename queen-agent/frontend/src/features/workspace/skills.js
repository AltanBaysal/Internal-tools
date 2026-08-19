// The six skills, settled with the user on 2026-08-18. The design drew four placeholders -- Web
// search, Deep research, Data & tables, Code -- belonging to a product that does something else;
// karar 18 replaced them and the design conversation grew the set to these.
//
// The second line says what a skill does and, for two of them, where it stops: producing nothing on
// disk is their most surprising property, so the menu says it before the user finds out.
export const SKILLS = [
  {
    id: "create-scenario",
    name: "Create scenario",
    detail: "A short outline, 10-15 sentences.",
  },
  {
    id: "create-character-prompt",
    name: "Create character prompt",
    detail: "SDXL character tags. Stays in the chat.",
  },
  {
    id: "split-into-frames",
    name: "Split into frames",
    detail: "Turn the scenario into frames. Stays in the chat.",
  },
  {
    id: "generate-prompts",
    name: "Generate prompts",
    detail: "Write every prompt in one piece.",
  },
  {
    id: "generate-prompts-plus",
    name: "Generate prompts+",
    detail: "Build from parts, so a character never drifts.",
  },
  {
    id: "verify-prompts",
    name: "Verify prompts",
    detail: "Check the structure files against the rules.",
  },
];

// No skill is the ordinary state, so the empty case is the button's own word rather than a gap.
export function skillName(id) {
  if (!id) return "Skills";
  return SKILLS.find((skill) => skill.id === id)?.name ?? id;
}
