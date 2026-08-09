import { useCallback, useEffect, useState } from "react";

import { getJson, postJson } from "../../shared/api.js";

// One array feeds both lists on screen -- the sidebar and the home cards -- so a new project shows
// up in both without a second round trip and without them ever disagreeing.
export function useProjects() {
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getJson("/api/projects")
      .then((loaded) => {
        if (!cancelled) setProjects(loaded);
      })
      .catch((failure) => {
        if (!cancelled) setError(failure.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

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

  return { projects, error, createProject };
}
