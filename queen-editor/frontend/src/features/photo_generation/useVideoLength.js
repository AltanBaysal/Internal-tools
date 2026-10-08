import { useEffect, useRef, useState } from "react";

import { getVideoLength, saveVideoLength } from "../../shared/api.js";

// The length the server last confirmed, per project, for the length of a visit. The video panel is
// built afresh on every opening and every step in and out of a frame; without this its length block
// would come in a beat after the panel each time and push everything under it down. Asked again on
// every mount all the same: the record on disk is the answer.
const CONFIRMED = new Map();

/** The project's H3 video length (madde 424): the number to show and say, and how to choose one.
 *
 * `videoRow` is the producers' video row. H3 is the one video model (madde 435), so every session
 * has a length to choose; no row means the model is not read yet, and nothing is drawn until it is
 * -- the design's rule (424). `seconds` is null there, and while the length is not known: nothing
 * drawn and nothing promised, rather than a number that may be wrong.
 */
export function useVideoLength(project, videoRow) {
  const read = Boolean(videoRow);
  const [known, setKnown] = useState(() => CONFIRMED.get(project) ?? null);
  // A press made while the read was on its way is newer than what the read will answer.
  const pressed = useRef(false);

  useEffect(() => {
    if (!read) return undefined;
    let alive = true;
    getVideoLength(project)
      .then((seconds) => {
        if (pressed.current) return;
        CONFIRMED.set(project, seconds);
        if (alive) setKnown(seconds);
      })
      // Unread, the length stays unknown: the block stays out and no sentence promises one. A dead
      // server is already said by the gallery's own poll, in the panel's card.
      .catch(() => {});
    return () => { alive = false; };
  }, [project, read]);

  // Shown at once, the design's way, then written. A write that fails takes the screen back to what
  // the project holds: a length shown as chosen that the queue will not use would be a lie.
  function choose(seconds) {
    pressed.current = true;
    setKnown(seconds);
    return saveVideoLength(project, seconds)
      .then(() => { CONFIRMED.set(project, seconds); })
      .catch((err) => {
        setKnown(CONFIRMED.get(project) ?? null);
        throw err;
      });
  }

  return { seconds: read ? known : null, choose };
}
