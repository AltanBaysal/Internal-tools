import { useCallback, useEffect, useRef, useState } from "react";

import { generatePhoto, getStatus } from "../../shared/api.js";

const POLL_MS = 2000;

// The photo takes 30-90s, so the server answers 202 and we ask /api/status until it settles.
// Polling also runs once on mount: a reload during or after a job picks the state back up.
export function useGeneration(project) {
  const [job, setJob] = useState({ status: "idle" });
  const [error, setError] = useState(null);   // rejected request (400/404/409), not a failed render
  const timer = useRef(null);

  const poll = useCallback(() => {
    getStatus()
      .then((state) => {
        setJob(state);
        if (state.status === "running") {
          timer.current = setTimeout(poll, POLL_MS);
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    poll();
    return () => clearTimeout(timer.current);
  }, [poll]);

  const generate = useCallback(
    (prompt) => {
      setError(null);
      return generatePhoto(project, prompt)
        .then(() => {
          setJob({ status: "running", project });
          timer.current = setTimeout(poll, POLL_MS);
        })
        .catch((err) => setError(err.message));
    },
    [project, poll],
  );

  return { job, error, generate };
}
