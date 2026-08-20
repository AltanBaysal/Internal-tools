import { useCallback, useEffect, useRef, useState } from "react";

import {
  cancelGeneration,
  generateBatch,
  getStatus,
  listFrames,
  removeFrames,
  removeLayer as deleteLayer,
  queueLayer as postLayer,
  regenerateFrame,
  resumeBatch,
  retryFailed,
  retryFrame,
  saveOrder,
  stopGeneration,
} from "../../shared/api.js";
import { failureText } from "../../shared/failure_text.js";

const POLL_MS = 2000;

// The two statuses that are a report rather than a state: the run is over, and this is how it went.
const REPORT = ["done", "error"];

// The last gallery each project answered with. Opening a frame's detail replaces the whole project
// screen, so this hook is torn down and built again on every step in and out; without this the
// screen would blank and refetch each time, though the answer it had was still good. Keyed by
// project: one project's gallery is never another's.
const REMEMBERED = new Map();

// The order the engine works in: it finishes one kind before it starts the next, so the queue
// panel's cards stand in this sequence too. The words are the server's own layer names.
const KINDS = ["photo", "video", "audio"];

// A batch runs for minutes, so the server answers 202 and we ask /api/status until it settles.
// The gallery refreshes on every poll: Drive is the truth about what exists and what is owed.
export function useGeneration(project) {
  const [job, setJob] = useState({ status: "idle" });
  // Has the server said anything about the worker yet? "idle" above is a placeholder, not an
  // answer, and a screen that acts on it decides on a state nobody reported.
  const [known, setKnown] = useState(false);
  // The whole gallery sequence -- produced, pending and failed frames in display order.
  // null = not known yet (nothing has ever answered for this project), [] = it truly has nothing.
  const [frames, setFrames] = useState(() => REMEMBERED.get(project) || null);
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
  // Has this page seen the engine in anything but an outcome? The engine keeps a finished run's
  // outcome in memory and /api/status answers with it until the next run starts, so a page opened
  // afterwards would draw a previous page's news -- and did, on top of the sound the user was
  // trying to queue (2026-08-14). Seeing one status that is not an outcome, or starting a run from
  // this page, is what makes the next outcome ours to show.
  const watched = useRef(false);
  // While a drag is being saved the gallery on screen is ahead of the server: a poll's older list
  // would snap the tiles back for one frame and then forward again.
  const savingOrder = useRef(false);
  // Which project the list on screen belongs to. The route can swap projects without unmounting,
  // and the previous one's tiles must not stay up while the new answer flies.
  const shownProject = useRef(project);
  if (shownProject.current !== project) {
    shownProject.current = project;
    setFrames(REMEMBERED.get(project) || null);
  }

  const refreshFrames = useCallback(() => {
    listFrames(project)
      .then((data) => { if (alive.current && !savingOrder.current) setFrames(data); })
      .catch((err) => { if (alive.current) setError(failureText(err)); });
  }, [project]);

  const poll = useCallback(() => {
    // The gallery is asked for regardless of the status call's fate -- a dead status endpoint must
    // not leave it lying about what exists.
    refreshFrames();
    getStatus()
      .then((state) => {
        if (!alive.current) return;
        if (!REPORT.includes(state.status)) watched.current = true;
        setJob(state);
        setKnown(true);
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
        setError(failureText(err));
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

  // Whatever the list becomes -- answered, reordered, a frame removed -- is what a later mount
  // starts from. One effect rather than a write next to every setFrames: those are functional
  // updates, and a cache written inside one would be a side effect where there must be none.
  useEffect(() => {
    if (frames) REMEMBERED.set(project, frames);
  }, [project, frames]);

  const clearError = useCallback(() => {
    setError(null);
    setErrorField(null);
  }, []);

  // Every way of putting the worker back to work ends the same: believe it is running, re-arm the
  // poll, and know what the gallery looks like. Written once so the callers cannot drift apart.
  // A caller whose answer already carried the gallery passes it in: asking for it again would be a
  // second round-trip for a list the screen is holding, and that is the wait the user sees between
  // pressing Kuyruğa ekle and the frames appearing.
  const startPolling = useCallback((gallery) => {
    // Pressing the button is watching: a run that ends before the first poll would otherwise have
    // its report hidden from the very person who asked for it.
    watched.current = true;
    setJob({ status: "running", project });
    wasRunning.current = true;
    clearTimeout(timer.current);
    timer.current = setTimeout(poll, POLL_MS);
    if (gallery) setFrames(gallery);
    else refreshFrames();
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
          startPolling(body?.frames);
          return body;
        })
        .catch((err) => {
          if (!alive.current) return null;
          setError(failureText(err));
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
      .catch((err) => { if (alive.current) setError(failureText(err)); });
  }, [project, startPolling, clearError]);

  // Emptying the queue does not start anything: it only changes what is owed, so the screen has to
  // see "idle" once and read the gallery again.
  const cancel = useCallback(() => (
    cancelGeneration(project)
      .then(() => { if (alive.current) poll(); })
      .catch((err) => { if (alive.current) setError(failureText(err)); })
  ), [project, poll]);

  // One frame, put back in line with the prompt and seed the plan gave it.
  const retry = useCallback((frame) => (
    retryFrame(project, frame)
      .then(() => { if (alive.current) startPolling(); })
      .catch((err) => { if (alive.current) setError(failureText(err)); })
  ), [project, startPolling]);

  // Hang a layer on every frame in scope. Resolves with the server's answer so the panel can quote
  // how many the queue took, or null when it was refused.
  const queueLayer = useCallback((kind, files, variants) => (
    postLayer(project, kind, files, variants)
      .then((body) => {
        if (!alive.current) return null;
        startPolling(body?.frames);
        return body;
      })
      .catch((err) => {
        if (!alive.current) return null;
        setError(failureText(err));
        return null;
      })
  ), [project, startPolling]);

  // One layer of one frame, made again from the words on screen. Resolves with the server's answer
  // -- it names the frame the result will land on, which is never this one -- or null when it was
  // refused; the page has to tell those apart to know whether to say anything.
  const regenerate = useCallback((frame, kind, prompt) => (
    regenerateFrame(project, frame, kind, prompt)
      .then((body) => {
        if (!alive.current) return null;
        startPolling();
        return body;
      })
      .catch((err) => {
        if (!alive.current) return null;
        setError(failureText(err));
        return null;
      })
  ), [project, startPolling]);

  // One layer off one frame. Nothing starts running, so the screen only has to read the gallery
  // again -- the frame stays where it is and comes back with one layer fewer.
  const removeLayer = useCallback((frame, kind) => (
    deleteLayer(project, frame, kind)
      .then((body) => {
        if (!alive.current) return null;
        poll();
        return body;
      })
      .catch((err) => {
        if (!alive.current) return null;
        setError(failureText(err));
        return null;
      })
  ), [project, poll]);

  // Every red job at once. Same endpoint as one frame's Tekrar dene, with no frame named.
  const retryAll = useCallback(() => (
    retryFailed(project)
      .then(() => { if (alive.current) startPolling(); })
      .catch((err) => { if (alive.current) setError(failureText(err)); })
  ), [project, startPolling]);

  const stop = useCallback(() => {
    setStopPressed(true);                     // instant feedback; the server confirms via polls
    return stopGeneration()
      .then((state) => { if (alive.current) setJob(state); })
      .catch((err) => { if (alive.current) setError(failureText(err)); });
  }, []);

  // Optimistic: the tiles move the moment they are dropped, because the drag already showed the
  // user where they land. If the write fails we say so and put the server's own order back --
  // the screen never keeps an order the server does not have.
  const reorder = useCallback(
    (order) => {
      savingOrder.current = true;
      setFrames((current) => {
        if (!current) return current;
        const byId = new Map(current.map((frame) => [frame.id, frame]));
        return order.map((fid) => byId.get(fid)).filter(Boolean);
      });
      return saveOrder(project, order)
        .then(() => { savingOrder.current = false; })
        .catch((err) => {
          savingOrder.current = false;
          if (!alive.current) return;
          setError(`Sıra kaydedilemedi.\n${failureText(err)}`);
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
  const removePhotos = useCallback((frames) => (
    removeFrames(project, frames)
      .then((body) => {
        if (!alive.current) return null;
        const gone = new Set([...(body?.deleted || []), ...(body?.removed || [])]);
        setFrames((current) => (current
          ? current.filter((frame) => !gone.has(frame.id))
          : current));
        return body;
      })
      .catch((err) => {
        // The server's own sentence, with no framing of ours wrapped around it -- the card that
        // shows it supplies the heading, and it is the only side that knows what was attempted.
        if (alive.current) setError(failureText(err));
        return null;
      })
  ), [project]);

  // What the screen is told. The raw status stays as it is -- another tab may be watching the same
  // run, and the server is not wrong; only this page's reading of it changes.
  const told = !watched.current && REPORT.includes(job.status) ? { status: "idle" } : job;

  // The server also reports "stopping" (survives a reload); either source disables the button.
  const stopping = stopPressed || Boolean(job.stopping);

  // One list, one answer: what is owed and what blew up are read off the gallery rather than kept
  // in a second place that could disagree with it.
  const shown = frames || [];
  // The frame being rendered has no status on disk; only the live worker knows it, and only while
  // it is this project's run. Its identity, not its file: two frames can be showing one picture.
  const current = job.project === project && job.status === "running" && job.current
    ? job.current.id
    : null;
  // Which layer of it is being made. A photo render empties the card while it runs; a video render
  // must not, because the frame's picture is still there -- so the screen needs the job's type as
  // well as its frame. A job planned before the queue knew types can only be a photo.
  const currentLayer = current ? (job.current.type || "photo") : null;
  // What the queue still owes and what blew up, layer by layer -- read off the gallery, because
  // each frame already says which of its layers are still coming and which failed. The job being
  // made comes out of the owed count: it is not waiting, it is being made. Pause puts it back --
  // the worker stops reporting it and the half-done job is owed again.
  const owedByKind = { photo: 0, video: 0, audio: 0 };
  const failedByKind = { photo: 0, video: 0, audio: 0 };
  shown.forEach((frame) => {
    (frame.owed || []).forEach((layer) => {
      if (frame.id === current && layer === currentLayer) return;
      owedByKind[layer] += 1;
    });
    (frame.failed || []).forEach((layer) => { failedByKind[layer] += 1; });
  });
  const queue = KINDS
    .map((layer) => ({ layer, owed: owedByKind[layer] }))
    .filter((card) => card.owed > 0);
  const failures = KINDS
    .map((layer) => ({ layer, count: failedByKind[layer] }))
    .filter((card) => card.count > 0);

  return { job: told, known, frames, error, errorField, stopping, queue, failures,
           current, currentLayer,
           retryAll, queueLayer, regenerate, removeLayer,
           generate, stop, resume, cancel, retry, clearError, reorder, removePhotos };
}
