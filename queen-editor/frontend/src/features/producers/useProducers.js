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

  // Say it on screen before the server has answered. Otherwise two round-trips stand between the
  // click and any change at all, and behind a tunnel that is long enough for the user to press Kur
  // a second time. The first real read overwrites it either way; a refused request takes it back.
  const said = useCallback((kind, installing) => {
    setProducers((rows) => (rows || []).map((row) => (
      row.id === kind ? { ...row, installing } : row)));
  }, []);

  const install = useCallback((kind) => {
    said(kind, { file: null });
    return installProducer(kind)
      .then(() => refresh())
      .catch((err) => {
        if (!alive.current) return;
        said(kind, undefined);
        setError(err.message);
      });
  }, [refresh, said]);

  const cancel = useCallback((kind) => (
    cancelInstall(kind)
      .then(() => refresh())
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [refresh]);

  return { producers, error, install, cancel };
}
