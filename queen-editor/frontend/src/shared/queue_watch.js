import { useEffect } from "react";

import { waitForQueue } from "./api.js";

// Who wants to hear the queue move: the notification, and every page that reads the gallery.
const listeners = new Set();

// After an ask that did not arrive -- the tunnel dropped, Colab went away -- the next one waits this
// long, so a server that is gone is not asked in a tight loop.
const AGAIN_MS = 10_000;

// `listener(said, before)` hears every answer whose counts differ from the last one heard; the
// returned function stops it. Module-level, so a page's listener and the tab's one ask need no
// wiring between them.
export function onQueueMoved(listener) {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
}

// The tab's one held ask for the queue starting and ending (madde 509, 518), mounted once in App so
// moving between screens does not take it down. The server counts both and keeps the last ending;
// the tab asks from the counts each answer brings. The first ask names none and is answered at once
// with where they stand, which nobody is told: a page reads the gallery as it opens anyway.
// Any count that moved is told, not only a start that grew: a server that came up again counts
// from nought, and a start after it can bring back a start count the tab has already heard.
export function useQueueWatch() {
  useEffect(() => {
    // Per run of the effect: a run taken down must not listen again when its ask lands, though the
    // next run has the hook mounted again (StrictMode does that to every effect).
    let alive = true;
    let timer = null;
    let seen = null;
    const listen = () => {
      waitForQueue(seen).then(
        (said) => {
          if (!alive) return;
          const before = seen;
          seen = said;
          if (before && (said.started !== before.started || said.ended !== before.ended)) {
            listeners.forEach((listener) => listener(said, before));
          }
          listen();
        },
        () => { if (alive) timer = setTimeout(listen, AGAIN_MS); },
      );
    };
    listen();
    return () => {
      alive = false;
      clearTimeout(timer);
    };
  }, []);
}
