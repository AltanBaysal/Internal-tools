import { useCallback, useEffect, useState } from "react";

import { getJson } from "./api.js";

// Every list on screen has the same shape: read it, and read it again when something changed it.
// The one wrinkle is `enabled` -- a list that hangs off a project cannot be asked for until there
// is a project to ask about.
export function useList(path, enabled = true) {
  const [items, setItems] = useState([]);
  // An empty array cannot tell "not here yet" from "there is none", and the two want opposite
  // things on screen: blocks in one case, a sentence teaching what to do in the other.
  const [loading, setLoading] = useState(enabled);
  // And neither of those is "we asked and got nothing back". Swallowed, the failure came out as the
  // teaching sentence -- the screen answering a question it never got an answer to.
  const [error, setError] = useState(null);

  const reload = useCallback(() => {
    if (!enabled) return Promise.resolve();
    setError(null);
    return getJson(path)
      .then(setItems)
      // The list already on screen is left alone: emptying it would show a project with files in it
      // as empty, which is a second untruth on top of the first.
      .catch((failure) => setError(failure.message))
      .finally(() => setLoading(false));
  }, [path, enabled]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { items, reload, loading, error };
}
