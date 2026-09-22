// The three ways a video can be made, as the user reads them. The identity is the engine's
// (domain/production_mode.py); only the Turkish name lives here.
//
// A list rather than three constants: the panel draws it in order. Standart comes first because it
// is the plainest of the three, not because it is what a panel opens on -- the video panel opens on
// Loop (madde 216).
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

// Where a video's pictures come from. A different question from the modes above, which say where a
// video ENDS: this one says what it is MADE OF -- the frame's own photo, or the project's reference
// pool (madde 301). Here beside them because one window asks both.
export const FROM_FRAME = "standard";
export const FROM_POOL = "reference";

// Named for what they are made FROM rather than "Standart / Referans": the row below already has a
// Standart, which says where a video ends, and one panel cannot carry that word twice.
export const SOURCES = [
  { id: FROM_FRAME, label: "Karelerden" },
  { id: FROM_POOL, label: "Referanstan" },
];

/** The mode's own name, for the places that report a mode rather than offer one.
 *
 * The id itself is the fallback: a value this list does not know is corrupted data, and printing it
 * says more than an empty row would.
 */
export function labelOf(mode) {
  return (MODES.find((one) => one.id === mode) || {}).label || mode;
}

// What each mode calls what it makes. No row for the plain one: what it makes is the layer's own
// noun -- video in one panel, ses in the other -- and this module has no layer.
const NOUN = { [LOOP]: "loop video", [LINKED]: "bağlı video" };

/** The mode's own noun for what it produces; `plain` is what the caller calls it otherwise. */
export function nounOf(mode, plain) {
  return NOUN[mode] || plain;
}
