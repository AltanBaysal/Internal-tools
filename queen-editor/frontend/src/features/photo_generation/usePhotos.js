import { useCallback, useEffect, useRef, useState } from "react";

import { removeFrames, listFrames } from "../../shared/api.js";

// The detail page's own view of the gallery: the same sequence in the same order, without the
// polling the project screen needs. Deleting is the only thing that changes it, so there is nothing
// to refresh on a timer.
export function usePhotos(project) {
  // null = not known yet (first fetch still flying), [] = the project truly has no frames.
  const [photos, setPhotos] = useState(null);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  const reload = useCallback(() => (
    listFrames(project)
      .then((data) => { if (alive.current) { setPhotos(data); setError(null); } })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project]);

  useEffect(() => {
    alive.current = true;
    reload();
    return () => { alive.current = false; };
  }, [reload]);

  // The server says which files it really deleted, but the list is trimmed here rather than
  // re-read: one frame left the set, and the order of the rest cannot have changed.
  const remove = useCallback((file) => (
    removeFrames(project, [file])
      .then(() => {
        if (!alive.current) return;
        setPhotos((current) => (current ? current.filter((photo) => photo.file !== file) : current));
      })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project]);

  return { photos, error, remove, reload };
}
