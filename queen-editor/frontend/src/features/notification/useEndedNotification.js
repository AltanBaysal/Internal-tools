import { useEffect } from "react";

import { waitForEnded } from "../../shared/api.js";
import { notify } from "./notification.js";

// What a queue waiting for a producer names it by: the server's layer names.
const PRODUCER = { photo: "fotoğraf", video: "video", audio: "ses" };

// What the notification says about how the queue ended: done, or stopped -- by an error, in the
// server's own words, or by a producer that is not installed. The server tells no other ending.
function sentence(last) {
  if (last.status === "done") return "Sıradaki bütün fotoğraf ve videolar bitti.";
  if (last.status === "waiting") {
    return `Sıra durdu: ${PRODUCER[last.waitingFor] || last.waitingFor} üreticisi kurulu değil.`;
  }
  return `Sıra durdu.\n${last.error}`;
}

// After an ask that did not arrive -- the tunnel dropped, Colab went away -- the next one waits this
// long, so a server that is gone is not asked in a tight loop.
const AGAIN_MS = 10_000;

// One notification each time the queue ends (madde 509). The server counts the endings and keeps
// the last; the screen only listens: one ask held open at a time, asked again from the count each
// answer brings. The first ask names no count and is answered at once with where it stands, which
// rings nothing. A count that grew is the queue ending. One that shrank is a server that came up
// again and counts from nought: it is taken as the new start, without a sound.
export function useEndedNotification() {
  useEffect(() => {
    // Per run of the effect: a run taken down must not listen again when its ask lands, though the
    // next run has the hook mounted again (StrictMode does that to every effect).
    let alive = true;
    let timer = null;
    let seen = null;
    const listen = () => {
      waitForEnded(seen).then(
        (said) => {
          if (!alive) return;
          if (seen !== null && said.ended > seen) notify(sentence(said.last));
          seen = said.ended;
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
