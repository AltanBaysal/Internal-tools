import { useCallback, useEffect, useRef, useState } from "react";

import { listModels } from "../../shared/api.js";
import { failureText } from "../../shared/failure_text.js";

// Which models can render, asked once when the project screen opens. There is no list here and no
// list on the server either: the notebook decides what is installed and the renderer reports it.
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
  // null = not known yet (first fetch still flying), [] = nothing installed, or nothing readable.
  const [models, setModels] = useState(remembered);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  const reload = useCallback(() => (
    listModels()
      .then((list) => { if (alive.current) { setModels(list); setError(null); } })
      .catch((err) => {
        if (!alive.current) return;
        // Only a first read empties the box, so the panel can stop waiting and the queue stays
        // usable. Over a list the visit already has, a refresh that fell over changes nothing.
        if (!remembered) setModels([]);
        setError(failureText(err));
      })
  ), []);

  useEffect(() => {
    alive.current = true;
    reload();
    return () => { alive.current = false; };
  }, [reload]);

  // An empty list is a real answer -- nothing installed -- and an unreadable one looks exactly like
  // it. The error beside it is what tells them apart, so only a list that arrived without one is
  // remembered.
  useEffect(() => {
    if (models && !error) remembered = models;
  }, [models, error]);

  return { models, error, reload };
}
