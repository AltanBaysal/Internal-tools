import { useCallback, useEffect, useState } from "react";

import { listProjects } from "../../shared/api.js";

// The screen's data lives here: loading | ready | error(server message). Drive is the single
// source of truth, so every change ends with a reload instead of patching local state.
export function useProjects() {
  const [state, setState] = useState({ status: "loading", projects: [], error: null });

  const reload = useCallback(() => {
    setState({ status: "loading", projects: [], error: null });
    return listProjects()
      .then((projects) => setState({ status: "ready", projects, error: null }))
      .catch((err) => setState({ status: "error", projects: [], error: err.message }));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  return { ...state, reload };
}
