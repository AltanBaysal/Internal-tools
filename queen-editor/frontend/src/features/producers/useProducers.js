import { useEffect, useState } from "react";

import { listProducers } from "../../shared/api.js";

// Asked once when the screen mounts: what is installed changes only when something is installed,
// and that is a moment the app knows about.
export function useProducers() {
  // null = not known yet; the panel draws neither rows nor an error until the answer lands.
  const [producers, setProducers] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let alive = true;
    listProducers()
      .then((rows) => { if (alive) { setProducers(rows); setError(null); } })
      .catch((err) => { if (alive) setError(err.message); });
    return () => { alive = false; };
  }, []);

  return { producers, error };
}
