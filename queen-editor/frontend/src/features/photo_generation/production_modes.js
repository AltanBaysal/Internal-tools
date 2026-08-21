// The three ways a video can be made, as the user reads them. The identity is the engine's
// (domain/production_mode.py); only the Turkish name lives here.
//
// A list rather than three constants: the panel draws it in order, and Standart comes first because
// it is what a panel opens on.
// Each one named, because the panel has rules and words of its own for them -- linking asks for
// neighbouring frames, loop and linking each say what they make in the estimate. A mode id written
// out there as a bare string would be the same word owned twice.
export const STANDARD = "standard";
export const LOOP = "loop";
export const LINKED = "linked";

export const MODES = [
  { id: STANDARD, label: "Standart" },
  { id: LOOP, label: "Loop" },
  { id: LINKED, label: "Sonrakine bağla" },
];
