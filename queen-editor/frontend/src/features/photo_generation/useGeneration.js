import { useCallback, useEffect, useRef, useState } from "react";

import { generateBatch, getStatus, listPhotos, stopGeneration } from "../../shared/api.js";

const POLL_MS = 2000;

// A batch runs for minutes, so the server answers 202 and we ask /api/status until it settles.
// The gallery is refreshed alongside every poll: Drive is the truth about what exists, so the
// grid fills while the batch runs and survives a reload.
export function useGeneration(project) {
  const [job, setJob] = useState({ status: "idle" });
  const [photos, setPhotos] = useState([]);
  const [error, setError] = useState(null);   // rejected request (400/404/409), not a failed render
  const timer = useRef(null);

  const refreshPhotos = useCallback(() => {
    listPhotos(project)
      .then(setPhotos)
      .catch((err) => setError(err.message));
  }, [project]);

  const poll = useCallback(() => {
    getStatus()
      .then((state) => {
        setJob(state);
        refreshPhotos();
        if (state.status === "running") {
          timer.current = setTimeout(poll, POLL_MS);
        }
      })
      .catch((err) => setError(err.message));
  }, [refreshPhotos]);

  useEffect(() => {
    poll();
    return () => clearTimeout(timer.current);
  }, [poll]);

  const generate = useCallback(
    (form) => {
      setError(null);
      return generateBatch(project, form)
        .then(() => {
          setJob({ status: "running", project, done: 0, failed: 0, total: 0 });
          timer.current = setTimeout(poll, POLL_MS);
        })
        .catch((err) => setError(err.message));
    },
    [project, poll],
  );

  const stop = useCallback(
    () => stopGeneration().then(setJob).catch((err) => setError(err.message)),
    [],
  );

  return { job, photos, error, generate, stop };
}
