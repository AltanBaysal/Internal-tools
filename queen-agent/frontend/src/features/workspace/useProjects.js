import { useCallback, useEffect, useState } from "react";

import { deleteJson, getJson, patchJson, postJson } from "../../shared/api.js";

// One array answers every place a project is named -- All projects, the sidebar and the bar -- so
// they can never disagree.
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

  const createProject = useCallback(async (name) => {
    try {
      const created = await postJson("/api/projects", { name });
      // Read again rather than put in by hand: where it belongs is the server's order
      // (list_projects.py), and a copy of that rule here would drift from it.
      await reload();
      return created;
    } catch (failure) {
      setError(failure.message);
      return null;
    }
  }, [reload]);

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

  const removeProject = useCallback(async (id) => {
    try {
      await deleteJson(`/api/projects/${id}`);
      setProjects((current) => current.filter((project) => project.id !== id));
      return true;
    } catch (failure) {
      setError(failure.message);
      return false;
    }
  }, []);

  return {
    projects,
    error,
    loading,
    createProject,
    editProject,
    removeProject,
    reloadProjects: reload,
  };
}
