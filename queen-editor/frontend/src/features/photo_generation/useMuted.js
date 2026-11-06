import { useEffect, useRef, useState } from "react";

import { getMuted, saveMuted } from "../../shared/api.js";

/** The list with `frame` in it or out of it, everything else as it was. */
function marked(frame, on) {
  return (list) => {
    const others = (list || []).filter((one) => one !== frame);
    return on ? [...others, frame] : others;
  };
}

/** Which of the project's frames have their sound turned off (madde 510), and the press that turns
 * one off or on.
 *
 * `muted` is the server's list of identities, or null until it is read -- and while it cannot be:
 * nothing is promised about a sound nobody has asked after. Read once per mount; the frame page
 * stays mounted while the arrows walk it from frame to frame, so a walk costs no request.
 *
 * `mute(frame, on)` shows the press at once and then writes it. Each answer speaks for its own frame
 * only, and only while no later press on that frame is in flight: presses on two frames can be
 * served in either order, and an answer written before the other press was served does not know
 * about it -- taken whole, it would turn that frame back on screen. A refused press puts back its
 * own frame alone and rejects with the server's words; one a later press on the same frame replaced
 * resolves and says nothing.
 */
export function useMuted(project) {
  const [muted, setMuted] = useState(null);
  // The number of the last press on each frame. Drawn nowhere, so a ref.
  const latest = useRef(new Map());

  useEffect(() => {
    let alive = true;
    setMuted(null);
    getMuted(project)
      .then((frames) => { if (alive) setMuted(frames); })
      // Unread, it stays unknown: the page draws no switch rather than one that may be wrong.
      .catch(() => {});
    return () => { alive = false; };
  }, [project]);

  function mute(frame, on) {
    const press = (latest.current.get(frame) || 0) + 1;
    latest.current.set(frame, press);
    const last = () => latest.current.get(frame) === press;
    const was = (muted || []).includes(frame);
    setMuted(marked(frame, on));
    return saveMuted(project, frame, on).then(
      (frames) => { if (last()) setMuted(marked(frame, frames.includes(frame))); },
      (err) => {
        if (!last()) return;
        setMuted(marked(frame, was));
        throw err;
      });
  }

  return { muted, mute };
}
