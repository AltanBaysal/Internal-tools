import { useCallback, useEffect, useRef, useState } from "react";

import {
  cancelGeneration,
  generateBatch,
  getStatus,
  listFrames,
  removeFrames,
  queueVideos,
  resumeBatch,
  retryFailed,
  retryFrame,
  saveOrder,
  stopGeneration,
} from "../../shared/api.js";

const POLL_MS = 2000;

// The order the engine works in: it finishes one kind before it starts the next, so the queue
// panel's cards stand in this sequence too. The words are the server's own layer names.
const KINDS = ["photo", "video", "audio"];

// A batch runs for minutes, so the server answers 202 and we ask /api/status until it settles.
// The gallery refreshes on every poll: Drive is the truth about what exists and what is owed.
export function useGeneration(project) {
  const [job, setJob] = useState({ status: "idle" });
  // The whole gallery sequence -- produced, pending and failed frames in display order.
  // null = not known yet (first fetch still flying), [] = the project truly has nothing.
  const [frames, setFrames] = useState(null);
  const [error, setError] = useState(null);   // rejected request or unreachable server
  // Which input the server blamed, when it named one: "prompts" | "variants" | null.
  const [errorField, setErrorField] = useState(null);
  const [stopPressed, setStopPressed] = useState(false);
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

  const refreshFrames = useCallback(() => {
    listFrames(project)
      .then((data) => { if (alive.current && !savingOrder.current) setFrames(data); })
      .catch((err) => { if (alive.current) setError(err.message); });
  }, [project]);

  const poll = useCallback(() => {
    // The gallery is asked for regardless of the status call's fate -- a dead status endpoint must
    // not leave it lying about what exists.
    refreshFrames();
    getStatus()
      .then((state) => {
        if (!alive.current) return;
        setJob(state);
        setError(null);                       // a successful poll clears a stale connection error
        if (state.status !== "running") setStopPressed(false);
        if (wasRunning.current && state.status !== "running") refreshFrames();
        wasRunning.current = state.status === "running";
        clearTimeout(timer.current);          // never let two chains tick at once
        if (state.status === "running") {
          timer.current = setTimeout(poll, POLL_MS);
        }
      })
      .catch((err) => {
        if (!alive.current) return;
        setError(err.message);
        // One bad poll must not kill the chain -- otherwise the screen freezes as "fake alive"
        // and never notices the tunnel coming back.
        clearTimeout(timer.current);
        timer.current = setTimeout(poll, POLL_MS);
      });
  }, [refreshFrames]);

  useEffect(() => {
    alive.current = true;
    poll();
    return () => {
      alive.current = false;
      clearTimeout(timer.current);
    };
  }, [poll]);

  const clearError = useCallback(() => {
    setError(null);
    setErrorField(null);
  }, []);

  // Every way of putting the worker back to work ends the same: believe it is running, re-arm the
  // poll, and read the gallery again. Written once so the three callers cannot drift apart.
  const startPolling = useCallback(() => {
    setJob({ status: "running", project });
    wasRunning.current = true;
    clearTimeout(timer.current);
    timer.current = setTimeout(poll, POLL_MS);
    refreshFrames();
  }, [project, poll, refreshFrames]);

  const generate = useCallback(
    (form) => {
      setError(null);
      setErrorField(null);
      // Resolves with the server's answer (it carries how many frames the queue took) or null when
      // the queue refused it -- the panel needs to tell those two apart.
      return generateBatch(project, form)
        .then((body) => {
          if (!alive.current) return null;
          startPolling();
          return body;
        })
        .catch((err) => {
          if (!alive.current) return null;
          setError(err.message);
          setErrorField(err.field || null);
          return null;
        });
    },
    [project, startPolling],
  );

  const resume = useCallback(() => {
    clearError();
    return resumeBatch(project)
      .then(() => { if (alive.current) startPolling(); })
      .catch((err) => { if (alive.current) setError(err.message); });
  }, [project, startPolling, clearError]);

  // Emptying the queue does not start anything: it only changes what is owed, so the screen has to
  // see "idle" once and read the gallery again.
  const cancel = useCallback(() => (
    cancelGeneration(project)
      .then(() => { if (alive.current) poll(); })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project, poll]);

  // One frame, put back in line with the prompt and seed the plan gave it.
  const retry = useCallback((file) => (
    retryFrame(project, file)
      .then(() => { if (alive.current) startPolling(); })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project, startPolling]);

  // Hang a video on every frame in scope. Resolves with the server's answer so the panel can quote
  // how many the queue took, or null when it was refused.
  const queueVideo = useCallback((files, variants) => (
    queueVideos(project, files, variants)
      .then((body) => {
        if (!alive.current) return null;
        startPolling();
        return body;
      })
      .catch((err) => {
        if (!alive.current) return null;
        setError(err.message);
        return null;
      })
  ), [project, startPolling]);

  // Every red job at once. Same endpoint as one frame's Tekrar dene, with no frame named.
  const retryAll = useCallback(() => (
    retryFailed(project)
      .then(() => { if (alive.current) startPolling(); })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project, startPolling]);

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
      setFrames((current) => {
        if (!current) return current;
        const byFile = new Map(current.map((frame) => [frame.file, frame]));
        return files.map((file) => byFile.get(file)).filter(Boolean);
      });
      return saveOrder(project, files)
        .then(() => { savingOrder.current = false; })
        .catch((err) => {
          savingOrder.current = false;
          if (!alive.current) return;
          setError(`Sıra kaydedilemedi.\n${err.message}`);
          refreshFrames();
        });
    },
    [project, refreshFrames],
  );

  // Only what the server says really went leaves the screen: a name that was already gone changes
  // nothing here, and the gallery keeps matching Drive. Both lists count -- a photo that left the
  // disk and a frame that only left the queue are equally out of the gallery.
  // Resolves with the server's answer, or null when the request was refused: the detail page must
  // not walk away from a frame that is still sitting in the queue.
  const removePhotos = useCallback((files) => (
    removeFrames(project, files)
      .then((body) => {
        if (!alive.current) return null;
        const gone = new Set([...(body?.deleted || []), ...(body?.removed || [])]);
        setFrames((current) => (current
          ? current.filter((frame) => !gone.has(frame.file))
          : current));
        return body;
      })
      .catch((err) => {
        // The server's own sentence, with no framing of ours wrapped around it -- the card that
        // shows it supplies the heading, and it is the only side that knows what was attempted.
        if (alive.current) setError(err.message);
        return null;
      })
  ), [project]);

  // The server also reports "stopping" (survives a reload); either source disables the button.
  const stopping = stopPressed || Boolean(job.stopping);

  // One list, one answer: what is owed and what blew up are read off the gallery rather than kept
  // in a second place that could disagree with it.
  const shown = frames || [];
  // The frame being rendered has no status on disk; only the live worker knows it, and only while
  // it is this project's run. Its name comes from the job's identity -- the one thing about a frame
  // that never changes.
  const current = job.project === project && job.status === "running" && job.current
    ? `${job.current.id}.png`
    : null;
  // What the queue still owes, kind by kind. The frame being rendered has no line on disk either,
  // so the gallery draws it as pending too -- it is not waiting, it is being made, and it comes out
  // of the count. Pause puts it back: the worker stops reporting it and the half-done job is owed
  // again.
  //
  // Every owed job is a photo job today, because the gallery is the only place this can be counted
  // from. When video and audio jobs join the queue the server will count them; the panel does not
  // change, because a card is drawn from this list either way.
  const owedByKind = {
    photo: shown.filter((frame) => frame.status === "pending" && frame.file !== current).length,
    video: 0,
    audio: 0,
  };
  const queue = KINDS
    .map((layer) => ({ layer, owed: owedByKind[layer] }))
    .filter((card) => card.owed > 0);

  // What failed, kind by kind, in the same shape as what is owed -- the same question asked about
  // the other end of the run. Only photo jobs can fail today, for the same reason only photo jobs
  // are owed: the gallery is where this is counted from.
  const failedByKind = {
    photo: shown.filter((frame) => frame.status === "failed").length,
    video: 0,
    audio: 0,
  };
  const failures = KINDS
    .map((layer) => ({ layer, count: failedByKind[layer] }))
    .filter((card) => card.count > 0);

  return { job, frames, error, errorField, stopping, queue, failures, current, retryAll, queueVideo,
           generate, stop, resume, cancel, retry, clearError, reorder, removePhotos };
}
