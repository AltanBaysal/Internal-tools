// What a frame's layers are called on screen, and the one sentence that counts them.
// The gallery's tile badges and the two delete confirms have to agree: a window that promises a
// video the tile never showed would be promising a file the user does not believe they have.
import { LOOP } from "./production_modes.js";

// What a frame can own, in layer order. The photo is not here: a frame without one is not a frame
// yet, so it is never something the frame "also" has.
export const OWNED = [{ layer: "video", word: "video" }, { layer: "audio", word: "ses" }];

// The frame's own suffix for each layer, for the sentence rather than the badge.
const OWNS_WORD = { video: "videosu", audio: "sesi" };

// What a loop video wears instead of the plain word. Lower case unlike the panel's own label: that
// one is a row in a list of choices, this one is a word laid on a picture beside video and ses.
const LOOP_WORD = "loop";

/** Which of OWNED this frame really has. A layer that blew up holds its slot but is not owned --
 *  that one is the status pill's to name.
 *
 *  A loop video takes the word rather than standing beside it: one row per layer, so the two can
 *  never be read together. Swapped after the filter, so a loop video that blew up says nothing at
 *  all. A fresh row each time -- OWNED is shared, and writing over it would rename every frame. */
export function owned(frame) {
  return OWNED
    .filter(({ layer }) => (frame.layers || {})[layer] && !(frame.failed || []).includes(layer))
    .map((row) => (row.layer === "video" && (frame.modes || {}).video === LOOP
      ? { ...row, word: LOOP_WORD } : row));
}

/**
 * What deleting these frames would take with them, as the confirm's first sentence -- e.g.
 * "Karelerin videosu ve sesi de birlikte silinir (2 video · 1 ses). ".
 * Empty when the selection is pictures and nothing else: there is no second thing to promise, and
 * a kind nobody has is left out rather than written as a zero (madde 62).
 */
export function lostLayers(frames) {
  const held = OWNED
    .map(({ layer, word }) => ({ layer, word, count: frames.filter(
      (frame) => owned(frame).some((row) => row.layer === layer)).length }))
    .filter(({ count }) => count > 0);
  if (!held.length) return "";
  const owner = frames.length === 1 ? "Karenin" : "Karelerin";
  const named = held.map(({ layer }) => OWNS_WORD[layer]).join(" ve ");
  // Vowel harmony decides the particle, and the last word named is the one it hangs on.
  const also = held[held.length - 1].layer === "video" ? "da" : "de";
  const counts = held.map(({ word, count }) => `${count} ${word}`).join(" · ");
  return `${owner} ${named} ${also} birlikte silinir (${counts}). `;
}

// What the bar's two layer buttons say, and what each one's window promises. Here beside the
// counting sentence for the reason that one is here: the tile's badges and every window that names
// a layer have to be using one set of words.
export const LAYER_ACTIONS = [
  { layer: "video", label: "Videoları sil", noun: "videosu",
    stays: "Kareler ve fotoğrafları kalır. Videoya bindirilen sesler de gider." },
  { layer: "audio", label: "Sesleri sil", noun: "sesi",
    stays: "Kareler, fotoğrafları ve videoları kalır." },
];

/**
 * One of those windows: how many frames really lose the layer, and what survives.
 * `held` is how many of the selection carry it, `selected` is the whole selection.
 *
 * The skipped frames get a sentence of their own and it comes first, because it is what explains
 * the number in the title. Written as a count of frames rather than of the number itself: Turkish
 * hangs a suffix on a number that changes with its last digit, and a table for that would be more
 * machinery than one sentence is worth.
 *
 * The width travels with the words (madde 105): the skip sentence makes the window a size wider.
 */
export function layerConfirm(layer, held, selected) {
  const { noun, stays } = LAYER_ACTIONS.find((one) => one.layer === layer);
  const skipped = selected - held;
  return {
    title: `${held} karenin ${noun} silinsin mi?`,
    body: skipped
      ? `Seçili ${selected} kareden ${noun} olmayan ${skipped} kare atlanır. ${stays}`
      : stays,
    width: skipped ? 420 : 400,
  };
}
