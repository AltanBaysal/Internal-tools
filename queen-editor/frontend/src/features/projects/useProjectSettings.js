import { useCallback, useEffect, useRef, useState } from "react";

import { getSettings, saveSettings } from "../../shared/api.js";

// The last record each project answered with. Opening a frame's detail replaces the whole project
// screen, so this hook is torn down and built again on every step in and out; without this the
// photo panel would wait for an answer the visit already has (madde 32). Keyed by project: one
// project's record is never another's.
//
// Memory only, like the gallery's own two: a reload asks for everything again.
const REMEMBERED = new Map();

// Where a mount starts -- what this project last answered, or nothing yet.
function opening(project) {
  return REMEMBERED.has(project)
    ? { status: "ready", settings: REMEMBERED.get(project), error: null }
    : { status: "loading", settings: null, error: null };
}

// The panel's content belongs to the project, not to the tab: loading | ready | error(server text).
// Saving does not touch this state -- what is on screen is already what was sent.
export function useProjectSettings(project) {
  const [state, setState] = useState(() => opening(project));
  // Tracks which project the most recent reload() belongs to. Switching projects quickly can let an
  // earlier project's response resolve after a later one has already loaded -- without this guard it
  // would land (and could later be saved) into the wrong project's screen.
  const currentProject = useRef(project);
  // Which project the state on screen belongs to. The route can swap projects without unmounting,
  // and the previous one's record must not stay up while the new answer flies.
  const shownProject = useRef(project);
  if (shownProject.current !== project) {
    shownProject.current = project;
    setState(opening(project));
  }

  const reload = useCallback(() => {
    currentProject.current = project;
    // Only a project nothing has answered for is emptied: a refresh over a record already on
    // screen is silent, which is the whole of madde 32.
    setState(opening(project));
    return getSettings(project)
      .then((settings) => {
        if (currentProject.current !== project) return; // a newer project has since loaded
        setState({ status: "ready", settings, error: null });
      })
      .catch((err) => {
        if (currentProject.current !== project) return;
        // Losing a refresh costs the user nothing, and emptying the panel over it would be the
        // opposite of quiet -- a dead tunnel is the status poll's to report, and it does.
        if (REMEMBERED.has(project)) return;
        setState({ status: "error", settings: null, error: err.message });
      });
  }, [project]);

  useEffect(() => {
    reload();
  }, [reload]);

  // Whatever the record becomes is what a later mount starts from. One effect rather than a write
  // beside every setState: only an answer that really arrived may be remembered, and `ready` is
  // the one state that means exactly that.
  useEffect(() => {
    if (state.status === "ready") REMEMBERED.set(project, state.settings);
  }, [project, state]);

  const save = useCallback((settings) => saveSettings(project, settings), [project]);

  return { ...state, save, reload };
}
