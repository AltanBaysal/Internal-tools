import { useCallback, useEffect, useRef, useState } from "react";

import { listModels } from "../../shared/api.js";
import { failureText } from "../../shared/failure_text.js";

// Which models and loras can render, asked once when the project screen opens. There is no list
// here: the notebook decides which models are installed and the server reports them, with the loras
// in the same answer (madde 237).
//
// Not knowing the list is not a reason to stop working: on failure the list reads as empty and the
// error is handed to the panel, which says so while the button stays pressable -- a frame with no
// model renders with the graph's own checkpoint.
// What the machine last answered. One slot rather than a map: the renderer's list belongs to the
// machine, not to a project. Kept for the length of a visit -- coming back from a frame builds this
// hook again, and the box saying yükleniyor… over a list the screen already had is the flicker this
// removes (madde 32).
let remembered = null;

export function useModels() {
  // null = not known yet (first fetch still flying). An answer's `models` can be [] -- nothing
  // installed, or nothing readable.
  const [answer, setAnswer] = useState(remembered);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  const reload = useCallback(() => (
    listModels()
      .then((body) => { if (alive.current) { setAnswer(body); setError(null); } })
      .catch((err) => {
        if (!alive.current) return;
        // Only a first read empties the box, so the panel can stop waiting and the queue stays
        // usable. Over a list the visit already has, a refresh that fell over changes nothing. The
        // lora box needs no answer to stand: it opens on Standart either way.
        if (!remembered) setAnswer({ models: [], loras: null });
        setError(failureText(err));
      })
  ), []);

  useEffect(() => {
    alive.current = true;
    reload();
    return () => { alive.current = false; };
  }, [reload]);

  // An empty list is a real answer -- nothing installed -- and an unreadable one looks exactly like
  // it. The error beside it is what tells them apart, so only an answer that arrived without one is
  // remembered.
  useEffect(() => {
    if (answer && !error) remembered = answer;
  }, [answer, error]);

  return { models: answer ? answer.models : null, loras: answer ? answer.loras : null, error,
           reload };
}
