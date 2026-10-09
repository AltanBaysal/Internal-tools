import { useEffect, useRef, useState } from "react";

import { getHappyEnding, getVideoLength, saveHappyEnding,
         saveVideoLength } from "../../shared/api.js";

/** A hook for one of the project's video settings: read through `read`, chosen through `write`.
 *
 * `videoRow` is the producers' video row. H3 is the one video model (madde 435), so every session
 * has the setting to choose; no row means the model is not read yet, and nothing is drawn until it
 * is -- the design's rule (424). `value` is null there, and while the setting is not known: nothing
 * drawn and nothing promised, rather than a value that may be wrong.
 */
function videoSetting(read, write) {
  // What the server last confirmed, per project, for the length of a visit. The video panel is built
  // afresh on every opening and every step in and out of a frame; without this its block would come
  // in a beat after the panel each time and push everything under it down. Asked again on every
  // mount all the same: the record on disk is the answer.
  const confirmed = new Map();

  return function useVideoSetting(project, videoRow) {
    const asked = Boolean(videoRow);
    const [known, setKnown] = useState(() => confirmed.get(project) ?? null);
    // A press made while the read was on its way is newer than what the read will answer.
    const pressed = useRef(false);

    useEffect(() => {
      if (!asked) return undefined;
      let alive = true;
      read(project)
        .then((value) => {
          if (pressed.current) return;
          confirmed.set(project, value);
          if (alive) setKnown(value);
        })
        // Unread, the setting stays unknown: its block stays out and no sentence promises it. A
        // dead server is already said by the gallery's own poll, in the panel's card.
        .catch(() => {});
      return () => { alive = false; };
    }, [project, asked]);

    // Shown at once, the design's way, then written. A write that fails takes the screen back to
    // what the project holds: a choice shown that the queue will not use would be a lie.
    function choose(value) {
      pressed.current = true;
      setKnown(value);
      return write(project, value)
        .then(() => { confirmed.set(project, value); })
        .catch((err) => {
          setKnown(confirmed.get(project) ?? null);
          throw err;
        });
    }

    return { value: asked ? known : null, choose };
  };
}

// Looked up at the call rather than when this module loads, as before the hooks shared a body: the
// frame page writes no setting, and its tests' api mock carries no writer.
const useLength = videoSetting((project) => getVideoLength(project),
                               (project, seconds) => saveVideoLength(project, seconds));
const useEnding = videoSetting((project) => getHappyEnding(project),
                               (project, on) => saveHappyEnding(project, on));

/** The project's H3 video length (madde 424): the number to show and say, and how to choose one. */
export function useVideoLength(project, videoRow) {
  const { value, choose } = useLength(project, videoRow);
  return { seconds: value, choose };
}

/** The project's Mutlu son switch (madde 426): true, false, or null while it is not known. */
export function useHappyEnding(project, videoRow) {
  const { value, choose } = useEnding(project, videoRow);
  return { on: value, choose };
}

/** What a video put in the queue now will be, said once at the end of whichever sentence is on show:
 * " 8 sn.", " 8 sn, mutlu son." -- or " Mutlu son." when the length is not known. The space before
 * the unit is unbreakable, so the number never ends a line with its unit alone on the next.
 */
export function videoSaid(seconds, on) {
  const parts = [];
  if (seconds !== null) parts.push(`${seconds} sn`);
  if (on) parts.push("mutlu son");
  if (!parts.length) return "";
  const said = parts.join(", ");
  return ` ${said[0].toUpperCase()}${said.slice(1)}.`;
}
