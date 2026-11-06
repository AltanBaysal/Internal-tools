import { useEffect } from "react";

import { onQueueMoved } from "../../shared/queue_watch.js";
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

// One notification each time the queue ends (madde 509), heard through the tab's queue watch. An
// ending count that grew is the queue ending. One that shrank is a server that came up again and
// counts from nought: no sound. A start rings nothing.
export function useEndedNotification() {
  useEffect(() => onQueueMoved((said, before) => {
    if (said.ended > before.ended) notify(sentence(said.last));
  }), []);
}
