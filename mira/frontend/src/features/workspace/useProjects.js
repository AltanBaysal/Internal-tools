import { useCallback, useEffect, useState } from "react";

import { getJson, patchJson, postJson } from "../../shared/api.js";

// One array feeds both lists on screen -- the sidebar and the home cards -- so a new project shows
// up in both without a second round trip and without them ever disagreeing.
export function useProjects() {
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState(null);

  const reload = useCallback(
    () =>
      getJson("/api/projects")
        .then(setProjects)
        .catch((failure) => setError(failure.message)),
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

  return { projects, error, createProject, editProject, reloadProjects: reload };
}
