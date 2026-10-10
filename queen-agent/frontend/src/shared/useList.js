import { useCallback, useEffect, useRef, useState } from "react";

import { getJson } from "./api.js";

// Every list on screen has the same shape: read it, and read it again when something changed it.
// The one wrinkle is `enabled` -- a list that hangs off a project cannot be asked for until there
// is a project to ask about.
export function useList(path, enabled = true) {
  // What came back is held with the path it is about, and drawn only while that is still the path
  // (Madde 457): the moment the user opens another project, the last one's rows are not its rows.
  const [answer, setAnswer] = useState({ path: null, items: [] });
  // Neither rows nor none is "we asked and got nothing back". Swallowed, the failure came out as the
  // teaching sentence -- the screen answering a question it never got an answer to.
  const [failure, setFailure] = useState(null);
  // Which read is the newest asked. Only its answer and its failure are kept: an older one is about
  // a project the user has left, or is an older order of the same list.
  const latest = useRef(0);

  const reload = useCallback(() => {
    // Counted even when nothing is asked: with no project open, the one just left is not current.
    const asked = ++latest.current;
    if (!enabled) return Promise.resolve();
    const current = () => asked === latest.current;
    setFailure(null);
    return getJson(path)
      .then((items) => {
        if (current()) setAnswer({ path, items });
      })
      // A failure answers nothing about what the list holds, so the rows already on screen are left
      // alone: emptying them would show a project with files in it as empty, a second untruth on top
      // of the first.
      .catch((refused) => {
        if (current()) setFailure({ path, message: refused.message });
      });
  }, [path, enabled]);

  useEffect(() => {
    reload();
  }, [reload]);

  const answered = answer.path === path;
  const error = failure?.path === path ? failure.message : null;
  return {
    items: answered ? answer.items : [],
    reload,
    // An empty array cannot tell "not here yet" from "there is none", and the two want opposite
    // things on screen. Not here yet is a path asked about and neither answered nor refused.
    loading: enabled && !answered && !error,
    error,
  };
}
