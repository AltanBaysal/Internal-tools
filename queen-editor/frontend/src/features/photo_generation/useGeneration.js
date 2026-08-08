import { useCallback, useEffect, useRef, useState } from "react";

import {
  cancelGeneration,
  deletePhotos,
  generateBatch,
  getQueue,
  getStatus,
  listPhotos,
  resumeBatch,
  retryFrame,
  saveOrder,
  stopGeneration,
} from "../../shared/api.js";

const POLL_MS = 2000;

// A batch runs for minutes, so the server answers 202 and we ask /api/status until it settles.
// The gallery refreshes on every poll: Drive is the truth about what exists.
export function useGeneration(project) {
  const [job, setJob] = useState({ status: "idle" });
  // null = not known yet (first fetch still flying), [] = the project truly has no photos.
  const [photos, setPhotos] = useState(null);
  const [error, setError] = useState(null);   // rejected request or unreachable server
  // Which input the server blamed, when it named one: "prompts" | "variants" | null.
  const [errorField, setErrorField] = useState(null);
  const [stopPressed, setStopPressed] = useState(false);
  // What the plan still owes, read from Drive rather than from this session's memory: a run that
  // died with the tab (or with Colab) is only visible here.
  const [queue, setQueue] = useState({ pending: [], total: 0 });
  const timer = useRef(null);
  // Flips false on unmount so an in-flight promise that resolves afterwards cannot setState or
  // re-arm the timer -- without this the catch branch's retry makes the chain immortal.
  const alive = useRef(true);
  // Was the previous poll's status "running"? Lets us catch the transition out of it and fetch
  // once more, so the batch's last photo (still landing on Drive when status flips) isn't stranded
  // until a manual reload.
  const wasRunning = useRef(false);
  // While a drag is being saved the gallery on screen is ahead of the server: a poll's older list
  // would snap the tiles back for one frame and then forward again.
  const savingOrder = useRef(false);

  const refreshPhotos = useCallback(() => {
    listPhotos(project)
      .then((data) => { if (alive.current && !savingOrder.current) setPhotos(data); })
      .catch((err) => { if (alive.current) setError(err.message); });
  }, [project]);

  const refreshQueue = useCallback(() => {
    getQueue(project)
      .then((data) => { if (alive.current) setQueue(data); })
      .catch(() => {});   // the queue is extra knowledge; its absence is not worth an error card
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
        if (wasRunning.current && state.status !== "running") {
          refreshPhotos();
          refreshQueue();     // a run that just ended changes what is still owed
        }
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
  }, [refreshPhotos, refreshQueue]);

  useEffect(() => {
    alive.current = true;
    poll();
    refreshQueue();
    return () => {
      alive.current = false;
      clearTimeout(timer.current);
    };
  }, [poll, refreshQueue]);

  const clearError = useCallback(() => {
    setError(null);
    setErrorField(null);
  }, []);

  const generate = useCallback(
    (form) => {
      setError(null);
      setErrorField(null);
      // Resolves with the server's answer (it carries how many frames the queue took) or null
      // when the queue refused it -- the panel needs to tell those two apart.
      return generateBatch(project, form)
        .then((body) => {
          if (!alive.current) return null;
          setJob({ status: "running", project, done: 0, failed: 0, total: 0 });
          wasRunning.current = true;
          clearTimeout(timer.current);        // drop any chain already ticking, avoid a parallel one
          timer.current = setTimeout(poll, POLL_MS);
          refreshQueue();                     // the new frames are owed from this moment on
          return body;
        })
        .catch((err) => {
          if (!alive.current) return null;
          setError(err.message);
          setErrorField(err.field || null);
          return null;
        });
    },
    [project, poll, refreshQueue],
  );

  // Resuming and cancelling are the paused view's two ways out. Both re-arm the poll: after a
  // resume the run is alive again, and after a cancel the screen has to see "idle" once.
  const resume = useCallback(() => {
    clearError();
    return resumeBatch(project)
      .then(() => {
        if (!alive.current) return;
        setJob({ status: "running", project, done: 0, failed: 0, total: 0 });
        wasRunning.current = true;
        clearTimeout(timer.current);
        timer.current = setTimeout(poll, POLL_MS);
      })
      .catch((err) => { if (alive.current) setError(err.message); });
  }, [project, poll, clearError]);

  const cancel = useCallback(() => (
    cancelGeneration(project)
      .then(() => {
        if (!alive.current) return;
        poll();
        refreshQueue();
      })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project, poll, refreshQueue]);

  // One frame, produced again with the prompt and seed the plan gave it.
  const retry = useCallback((file) => (
    retryFrame(project, file)
      .then(() => {
        if (!alive.current) return;
        setJob({ status: "running", project, done: 0, failed: 0, total: 1 });
        wasRunning.current = true;
        clearTimeout(timer.current);
        timer.current = setTimeout(poll, POLL_MS);
      })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project, poll]);

  const stop = useCallback(() => {
    setStopPressed(true);                     // instant feedback; the server confirms via polls
    return stopGeneration()
      .then((state) => { if (alive.current) setJob(state); })
      .catch((err) => { if (alive.current) setError(err.message); });
  }, []);

  // Optimistic: the tiles move the moment they are dropped, because the drag already showed the
  // user where they land. If the write fails we say so and put the server's own order back --
  // the screen never keeps an order the server does not have.
  const reorder = useCallback(
    (files) => {
      savingOrder.current = true;
      setPhotos((current) => {
        if (!current) return current;
        const byFile = new Map(current.map((photo) => [photo.file, photo]));
        return files.map((file) => byFile.get(file)).filter(Boolean);
      });
      return saveOrder(project, files)
        .then(() => { savingOrder.current = false; })
        .catch((err) => {
          savingOrder.current = false;
          if (!alive.current) return;
          setError(`Sıra kaydedilemedi.\n${err.message}`);
          refreshPhotos();
        });
    },
    [project, refreshPhotos],
  );

  // Only what the server says it deleted leaves the screen: a name that was already gone changes
  // nothing here, and the gallery keeps matching Drive.
  const removePhotos = useCallback((files) => (
    deletePhotos(project, files)
      .then((body) => {
        if (!alive.current) return;
        const gone = new Set(body?.deleted || []);
        setPhotos((current) => (current
          ? current.filter((photo) => !gone.has(photo.file))
          : current));
      })
      .catch((err) => {
        if (alive.current) setError(`Fotoğraflar silinemedi.\n${err.message}`);
      })
  ), [project]);

  // The server also reports "stopping" (survives a reload); either source disables the button.
  const stopping = stopPressed || Boolean(job.stopping);

  // While the run is alive the worker's own queue is the fresher answer; otherwise Drive's is the
  // only one -- and after a dead session, the only one there has ever been.
  const mine = job.project === project;
  const pending = mine && job.status === "running" ? (job.pending || []) : queue.pending;
  const failures = mine ? (job.failures || []) : [];

  return { job, photos, error, errorField, stopping, queue, pending, failures,
           generate, stop, resume, cancel, retry, clearError, reorder, removePhotos };
}
