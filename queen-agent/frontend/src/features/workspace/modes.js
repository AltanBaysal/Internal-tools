// The three modes, in the order the item names them. What the model may do is a control now rather
// than a sentence inside a skill's text -- and the second line says what each one costs the model.
export const MODES = [
  { id: "plan", name: "Plan", detail: "Break the work into steps and write the plan to a file." },
  { id: "ask", name: "Ask", detail: "Read and answer. Nothing is written." },
  { id: "edit", name: "Edit", detail: "Read, write and build. The full set." },
];

// Edit is what the app did before there were modes, so it is what it still does by default.
export const DEFAULT_MODE = "edit";

// Unlike a skill, there is no such thing as no mode -- so this never answers with a placeholder.
export function modeName(id) {
  return MODES.find((mode) => mode.id === id)?.name ?? modeName(DEFAULT_MODE);
}
