import { useCallback, useEffect, useRef, useState } from "react";

import { getSettings, saveSettings } from "../../shared/api.js";

// The panel's content belongs to the project, not to the tab: loading | ready | error(server text).
// Saving does not touch this state -- what is on screen is already what was sent.
export function useProjectSettings(project) {
  const [state, setState] = useState({ status: "loading", settings: null, error: null });
  // Tracks which project the most recent reload() belongs to. Switching projects quickly can let an
  // earlier project's response resolve after a later one has already loaded -- without this guard it
  // would land (and could later be saved) into the wrong project's screen.
  const currentProject = useRef(project);

  const reload = useCallback(() => {
    currentProject.current = project;
    setState({ status: "loading", settings: null, error: null });
    return getSettings(project)
      .then((settings) => {
        if (currentProject.current !== project) return; // a newer project has since loaded
        setState({ status: "ready", settings, error: null });
      })
      .catch((err) => {
        if (currentProject.current !== project) return;
        setState({ status: "error", settings: null, error: err.message });
      });
  }, [project]);

  useEffect(() => {
    reload();
  }, [reload]);

  const save = useCallback((settings) => saveSettings(project, settings), [project]);

  return { ...state, save, reload };
}
