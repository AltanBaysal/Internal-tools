// The three ways a video can be made, as the user reads them. The identity is the engine's
// (domain/production_mode.py); only the Turkish name lives here.
//
// A list rather than three constants: the panel draws it in order, and Standart comes first because
// it is what a panel opens on.
export const STANDARD = "standard";
// Named because the panel has a rule of its own about this one: linking asks for neighbouring
// frames. A second "linked" written out there would be the same word owned twice.
export const LINKED = "linked";

export const MODES = [
  { id: STANDARD, label: "Standart" },
  { id: "loop", label: "Loop" },
  { id: LINKED, label: "Sonrakine bağla" },
];
