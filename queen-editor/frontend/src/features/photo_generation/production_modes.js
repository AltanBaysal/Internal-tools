// The three ways a video can be made, as the user reads them. The identity is the engine's
// (domain/production_mode.py); only the Turkish name lives here.
//
// A list rather than three constants: the panel draws it in order, and Standart comes first because
// it is what a panel opens on.
export const STANDARD = "standard";

export const MODES = [
  { id: STANDARD, label: "Standart" },
  { id: "loop", label: "Loop" },
  { id: "linked", label: "Sonrakine bağla" },
];
