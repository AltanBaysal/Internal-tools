import { useCallback, useEffect, useState } from "react";

import { deleteJson, getJson, patchJson, postJson } from "../../shared/api.js";
import { inTurn } from "./inTurn.js";

// One array answers every place a project is named -- All projects, the sidebar and the bar -- so
// they can never disagree.
export function useProjects() {
  const [projects, setProjects] = useState([]);
  // Two failures, two values, as the file list keeps them (Madde 364): a list that could not be read
  // leaves nothing known to show, while a write that was refused leaves the list standing. One value
  // for both turned All projects into a failure over a rename that did not land.
  const [error, setError] = useState(null);
  const [writeError, setWriteError] = useState(null);
  // An empty array cannot tell "not here yet" from "there is none".
  const [loading, setLoading] = useState(true);

  const reload = useCallback(
    () =>
      getJson("/api/projects")
        .then((listed) => {
          setProjects(listed);
          setError(null);
        })
        .catch((failure) => setError(failure.message))
        .finally(() => setLoading(false)),
    [],
  );

  useEffect(() => {
    reload();
  }, [reload]);

  // Try again waits the way the first read did (the design's 173); the screens put the wait before
  // the failure, so the failure need not be cleared first. It is that first read again, asked while
  // no list stands to be pressed on, so it is not queued below.
  const retry = useCallback(() => {
    setLoading(true);
    return reload();
  }, [reload]);

  // Once the list has come, every read of it and every write reaches the server one at a time, in
  // the order asked (Madde 450): each sets out once the one before it -- a PATCH with the list read
  // after it, a DELETE, a read -- has come back. Sent side by side, an Unarchive pressed while its
  // Archive was on its way could be handled first, and the server would keep the press the user
  // took back; or a list read before a write could land after the write's own list and draw what
  // it undid -- an archive taken back, a deleted project. One queue for every project, not one
  // each: any list names them all. A new project stays out (see createProject).
  const [queued] = useState(() => inTurn());
  const reloadInTurn = useCallback(() => queued(reload), [queued, reload]);

  // A refusal is not kept here: it goes to the caller, the naming screen, which says it under the
  // name it refused -- kept here, it would outlive that screen as a stale line on All projects.
  // Not in the queue: the naming screen stands between it and every press on All projects, and a
  // name typed takes longer than what is still queued.
  const createProject = useCallback(
    async (name) => {
      const created = await postJson("/api/projects", { name });
      // Read again rather than put in by hand: where it belongs is the server's order
      // (list_projects.py), and a copy of that rule here would drift from it.
      await reload();
      return created;
    },
    [reload],
  );

  const editProject = useCallback(
    (id, changes) =>
      queued(async () => {
        setWriteError(null);
        try {
          const edited = await patchJson(`/api/projects/${id}`, changes);
          // Read again for the reason a new project is: a pin or an unpin moves the row, and where
          // to is the server's order. Read inside the edit's own turn, so the next write waits for it.
          await reload();
          return edited;
        } catch (failure) {
          setWriteError(failure.message);
          return null;
        }
      }),
    [queued, reload],
  );

  const removeProject = useCallback(
    (id) =>
      queued(async () => {
        setWriteError(null);
        try {
          await deleteJson(`/api/projects/${id}`);
          setProjects((current) => current.filter((project) => project.id !== id));
          return true;
        } catch (failure) {
          setWriteError(failure.message);
          return false;
        }
      }),
    [queued],
  );

  return {
    projects,
    error,
    writeError,
    loading,
    createProject,
    editProject,
    removeProject,
    reloadProjects: reloadInTurn,
    retryProjects: retry,
  };
}
