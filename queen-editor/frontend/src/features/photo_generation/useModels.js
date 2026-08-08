import { useCallback, useEffect, useRef, useState } from "react";

import { listModels } from "../../shared/api.js";

// Which models can render, asked once when the project screen opens. There is no list here and no
// list on the server either: the notebook decides what is installed and the renderer reports it.
//
// Not knowing the list is not a reason to stop working: on failure the list reads as empty and the
// error is handed to the panel, which says so while the button stays pressable -- a frame with no
// model renders with the graph's own checkpoint.
export function useModels() {
  // null = not known yet (first fetch still flying), [] = nothing installed, or nothing readable.
  const [models, setModels] = useState(null);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  const reload = useCallback(() => (
    listModels()
      .then((list) => { if (alive.current) { setModels(list); setError(null); } })
      .catch((err) => { if (alive.current) { setModels([]); setError(err.message); } })
  ), []);

  useEffect(() => {
    alive.current = true;
    reload();
    return () => { alive.current = false; };
  }, [reload]);

  return { models, error, reload };
}
