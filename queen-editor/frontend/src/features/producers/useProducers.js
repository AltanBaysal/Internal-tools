import { useCallback, useEffect, useRef, useState } from "react";

import { listProducers } from "../../shared/api.js";
import { failureText } from "../../shared/failure_text.js";

/** What Kur answers now. The app installs nothing: the models come down in the Colab notebook,
 *  before this process starts (FOUNDATION 9). */
export const COLAB_INSTALL =
  "Bu üretici Colab defterinden kurulur — queeneditor.ipynb'de kutusunu işaretleyip çalıştır.";

// What is installed cannot change while the app is up -- installing happens in the notebook, which
// runs before the server does. So the list is asked for once, and never polled.
// What the machine answered, as the rows stand now. One slot rather than a map: what is installed
// belongs to the machine. Kept for the length of a visit, so coming back from a frame does not put
// the panel through not-knowing again for an answer that cannot have changed (madde 32).
let remembered = null;

export function useProducers() {
  // null = not known yet; the panel draws neither rows nor an error until the answer lands.
  const [producers, setProducers] = useState(remembered);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    listProducers()
      .then((rows) => {
        if (!alive.current) return;
        setProducers(rows);
        setError(null);
      })
      // A read that fell over leaves the rows where they are: null on a first visit, and whatever
      // the visit already has on any later one.
      .catch((err) => { if (alive.current) setError(failureText(err)); });
    return () => { alive.current = false; };
  }, []);

  // The rows as they stand, not as they arrived: Kur writes its sentence onto one of them, so what
  // is on screen is no longer what the server gave. Remembering the answer instead of the state
  // would take that sentence away on the way back. Only a real answer ever gets here -- a failed
  // read leaves this null.
  useEffect(() => {
    if (producers) remembered = producers;
  }, [producers]);

  // Kur asks a question the app can only answer with words: it puts the sentence on that row and
  // sends nothing. Kept as `install` because every caller means the same thing by it -- the user
  // wants this producer -- and only the answer changed.
  const install = useCallback((kind) => {
    setProducers((rows) => (rows || []).map((row) => (
      row.id === kind ? { ...row, note: COLAB_INSTALL } : row)));
  }, []);

  return { producers, error, install };
}
