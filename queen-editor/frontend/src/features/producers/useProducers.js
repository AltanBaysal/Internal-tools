import { useCallback, useEffect, useRef, useState } from "react";

import { cancelInstall, installProducer, listProducers } from "../../shared/api.js";

const POLL_MS = 2000;

// What is installed changes only while something is being installed, so the list is asked for once
// and then polled for exactly as long as a download is running -- the card has to see it land.
export function useProducers() {
  // null = not known yet; the panel draws neither rows nor an error until the answer lands.
  const [producers, setProducers] = useState(null);
  const [error, setError] = useState(null);
  const alive = useRef(true);
  const timer = useRef(null);

  const refresh = useCallback(() => (
    listProducers()
      .then((rows) => {
        if (!alive.current) return;
        setProducers(rows);
        setError(null);
        clearTimeout(timer.current);        // never let two chains tick at once
        if (rows.some((row) => row.installing)) timer.current = setTimeout(refresh, POLL_MS);
      })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), []);

  useEffect(() => {
    alive.current = true;
    refresh();
    return () => {
      alive.current = false;
      clearTimeout(timer.current);
    };
  }, [refresh]);

  // Believe it started right away, the way the queue does: the answer is 202 and the truth arrives
  // with the next read.
  const install = useCallback((kind) => (
    installProducer(kind)
      .then(() => refresh())
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [refresh]);

  const cancel = useCallback((kind) => (
    cancelInstall(kind)
      .then(() => refresh())
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [refresh]);

  return { producers, error, install, cancel };
}
