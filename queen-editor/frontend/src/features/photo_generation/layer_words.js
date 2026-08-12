// What a frame's layers are called on screen, and the one sentence that counts them.
// The gallery's tile badges and the two delete confirms have to agree: a window that promises a
// video the tile never showed would be promising a file the user does not believe they have.

// What a frame can own, in layer order. The photo is not here: a frame without one is not a frame
// yet, so it is never something the frame "also" has.
export const OWNED = [{ layer: "video", word: "video" }, { layer: "audio", word: "ses" }];

// The frame's own suffix for each layer, for the sentence rather than the badge.
const OWNS_WORD = { video: "videosu", audio: "sesi" };

/** Which of OWNED this frame really has. A layer that blew up holds its slot but is not owned --
 *  that one is the status pill's to name. */
export function owned(frame) {
  return OWNED.filter(({ layer }) => (frame.layers || {})[layer]
    && !(frame.failed || []).includes(layer));
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
