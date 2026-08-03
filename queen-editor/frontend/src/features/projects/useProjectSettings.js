import { useCallback, useEffect, useState } from "react";

import { getSettings, saveSettings } from "../../shared/api.js";

// The panel's content belongs to the project, not to the tab: loading | ready | error(server text).
// Saving does not touch this state -- what is on screen is already what was sent.
export function useProjectSettings(project) {
  const [state, setState] = useState({ status: "loading", settings: null, error: null });

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading", settings: null, error: null });
    getSettings(project)
      .then((settings) => {
        if (!cancelled) setState({ status: "ready", settings, error: null });
      })
      .catch((err) => {
        if (!cancelled) setState({ status: "error", settings: null, error: err.message });
      });
    return () => {
      cancelled = true;
    };
  }, [project]);

  const save = useCallback((settings) => saveSettings(project, settings), [project]);

  return { ...state, save };
}
