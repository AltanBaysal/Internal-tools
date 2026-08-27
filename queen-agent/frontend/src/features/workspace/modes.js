// The three modes, in the order the item names them. What the model may do is a control now rather
// than a sentence inside a skill's text -- and the second line says what each one costs the model.
export const MODES = [
  { id: "plan", name: "Plan", detail: "Break the work into steps and write the plan to a file." },
  // Nothing was written here until Madde 99. Now a write is possible and stops to ask, and a line
  // saying otherwise would send the user looking for a bug that is a feature.
  { id: "ask", name: "Ask", detail: "Read and answer. A write stops and asks." },
  { id: "edit", name: "Edit", detail: "Read, write and build. The full set." },
];

// Two names for two reasons: the mode an approval arrives in, and the mode the app starts in --
// edit being what the app did before there were modes at all. The same value today, and nothing
// says the two have to stay the same one.
export const EDIT = "edit";
export const DEFAULT_MODE = EDIT;

// Unlike a skill, there is no such thing as no mode -- so this never answers with a placeholder.
export function modeName(id) {
  return MODES.find((mode) => mode.id === id)?.name ?? modeName(DEFAULT_MODE);
}
