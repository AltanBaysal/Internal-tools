import { useCallback, useEffect, useState } from "react";

import { getJson } from "./api.js";

// Every list on screen has the same shape: read it, and read it again when something changed it.
// The one wrinkle is `enabled` -- a list that hangs off a project cannot be asked for until there
// is a project to ask about.
export function useList(path, enabled = true) {
  const [items, setItems] = useState([]);

  const reload = useCallback(() => {
    if (!enabled) return Promise.resolve();
    return getJson(path)
      .then(setItems)
      .catch(() => setItems([]));
  }, [path, enabled]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { items, reload };
}
