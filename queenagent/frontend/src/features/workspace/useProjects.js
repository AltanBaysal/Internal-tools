import { useCallback, useEffect, useState } from "react";

import { getJson, patchJson, postJson } from "../../shared/api.js";

// One array answers two questions -- what the sidebar lists, and which project the app opens on --
// so the two can never disagree and a new project needs no second round trip.
export function useProjects() {
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState(null);
  // An empty array cannot tell "not here yet" from "there is none".
  const [loading, setLoading] = useState(true);

  const reload = useCallback(
    () =>
      getJson("/api/projects")
        .then(setProjects)
        .catch((failure) => setError(failure.message))
        .finally(() => setLoading(false)),
    [],
  );

  useEffect(() => {
    reload();
  }, [reload]);

  const createProject = useCallback(async () => {
    try {
      const created = await postJson("/api/projects");
      // Appended, not prepended: the server lists projects oldest first.
      setProjects((current) => [...current, created]);
      return created;
    } catch (failure) {
      setError(failure.message);
      return null;
    }
  }, []);

  const editProject = useCallback(async (id, changes) => {
    try {
      const edited = await patchJson(`/api/projects/${id}`, changes);
      setProjects((current) => current.map((p) => (p.id === id ? edited : p)));
      return edited;
    } catch (failure) {
      setError(failure.message);
      return null;
    }
  }, []);

  return { projects, error, loading, createProject, editProject, reloadProjects: reload };
}
