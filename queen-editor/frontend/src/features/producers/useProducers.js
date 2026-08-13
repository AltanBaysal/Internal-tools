import { useCallback, useEffect, useRef, useState } from "react";

import { listProducers } from "../../shared/api.js";

/** What Kur answers now. The app installs nothing: the models come down in the Colab notebook,
 *  before this process starts (FOUNDATION 9). */
export const COLAB_INSTALL = "Bu üretici Colab defterinden kurulur — app.ipynb'yi çalıştır.";

// What is installed cannot change while the app is up -- installing happens in the notebook, which
// runs before the server does. So the list is asked for once, and never polled.
export function useProducers() {
  // null = not known yet; the panel draws neither rows nor an error until the answer lands.
  const [producers, setProducers] = useState(null);
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
      .catch((err) => { if (alive.current) setError(err.message); });
    return () => { alive.current = false; };
  }, []);

  // Kur asks a question the app can only answer with words: it puts the sentence on that row and
  // sends nothing. Kept as `install` because every caller means the same thing by it -- the user
  // wants this producer -- and only the answer changed.
  const install = useCallback((kind) => {
    setProducers((rows) => (rows || []).map((row) => (
      row.id === kind ? { ...row, note: COLAB_INSTALL } : row)));
  }, []);

  return { producers, error, install };
}
