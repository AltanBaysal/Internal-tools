import { useCallback, useEffect, useRef, useState } from "react";

import { generateBatch, getStatus, listPhotos, stopGeneration } from "../../shared/api.js";

const POLL_MS = 2000;

// A batch runs for minutes, so the server answers 202 and we ask /api/status until it settles.
// The gallery refreshes on every poll: Drive is the truth about what exists.
export function useGeneration(project) {
  const [job, setJob] = useState({ status: "idle" });
  // null = not known yet (first fetch still flying), [] = the project truly has no photos.
  const [photos, setPhotos] = useState(null);
  const [error, setError] = useState(null);   // rejected request or unreachable server
  const [stopPressed, setStopPressed] = useState(false);
  const timer = useRef(null);
  // Flips false on unmount so an in-flight promise that resolves afterwards cannot setState or
  // re-arm the timer -- without this the catch branch's retry makes the chain immortal.
  const alive = useRef(true);
  // Was the previous poll's status "running"? Lets us catch the transition out of it and fetch
  // once more, so the batch's last photo (still landing on Drive when status flips) isn't stranded
  // until a manual reload.
  const wasRunning = useRef(false);

  const refreshPhotos = useCallback(() => {
    listPhotos(project)
      .then((data) => { if (alive.current) setPhotos(data); })
      .catch((err) => { if (alive.current) setError(err.message); });
  }, [project]);

  const poll = useCallback(() => {
    // Photos are asked for regardless of the status call's fate -- a dead status endpoint must
    // not leave the gallery lying about what exists.
    refreshPhotos();
    getStatus()
      .then((state) => {
        if (!alive.current) return;
        setJob(state);
        setError(null);                       // a successful poll clears a stale connection error
        if (state.status !== "running") setStopPressed(false);
        if (wasRunning.current && state.status !== "running") refreshPhotos();
        wasRunning.current = state.status === "running";
        clearTimeout(timer.current);          // never let two chains tick at once
        if (state.status === "running") {
          timer.current = setTimeout(poll, POLL_MS);
        }
      })
      .catch((err) => {
        if (!alive.current) return;
        setError(err.message);
        // One bad poll must not kill the chain -- otherwise the bar freezes as "fake alive"
        // and the screen never notices the tunnel coming back.
        clearTimeout(timer.current);
        timer.current = setTimeout(poll, POLL_MS);
      });
  }, [refreshPhotos]);

  useEffect(() => {
    alive.current = true;
    poll();
    return () => {
      alive.current = false;
      clearTimeout(timer.current);
    };
  }, [poll]);

  const generate = useCallback(
    (form) => {
      setError(null);
      return generateBatch(project, form)
        .then(() => {
          if (!alive.current) return;
          setJob({ status: "running", project, done: 0, failed: 0, total: 0 });
          wasRunning.current = true;
          clearTimeout(timer.current);        // drop any chain already ticking, avoid a parallel one
          timer.current = setTimeout(poll, POLL_MS);
        })
        .catch((err) => { if (alive.current) setError(err.message); });
    },
    [project, poll],
  );

  const stop = useCallback(() => {
    setStopPressed(true);                     // instant feedback; the server confirms via polls
    return stopGeneration()
      .then((state) => { if (alive.current) setJob(state); })
      .catch((err) => { if (alive.current) setError(err.message); });
  }, []);

  // The server also reports "stopping" (survives a reload); either source disables the button.
  const stopping = stopPressed || Boolean(job.stopping);

  return { job, photos, error, stopping, generate, stop };
}
