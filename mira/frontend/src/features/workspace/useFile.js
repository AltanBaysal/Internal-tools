import { useCallback, useEffect, useState } from "react";

import { getJson } from "../../shared/api.js";

// Saving is the browser's own step: a blob, a link, a click. Nothing is kept afterwards, so the
// object URL is handed back as soon as the click has been made.
function save(name, text) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/plain" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  URL.revokeObjectURL(url);
}

// Which file is open is a question about the project, not about the address bar: the design gives a
// file no URL of its own.
export function useFile(projectId) {
  const [name, setName] = useState(null);
  const [file, setFile] = useState(null);
  const [missing, setMissing] = useState(false);
  const [error, setError] = useState(null);

  const path = name ? `/api/projects/${projectId}/files/${encodeURIComponent(name)}` : null;

  useEffect(() => {
    // Another project is another set of files, so whatever was being read is not open any more.
    setName(null);
  }, [projectId]);

  useEffect(() => {
    if (!path) return undefined;
    let cancelled = false;
    setFile(null);
    setMissing(false);
    setError(null);
    getJson(path)
      .then((loaded) => {
        if (!cancelled) setFile(loaded);
      })
      .catch((failure) => {
        if (cancelled) return;
        if (failure.status === 404) setMissing(true);
        else setError(failure.message);
      });
    return () => {
      cancelled = true;
    };
  }, [path]);

  const download = useCallback(async () => {
    // Read again rather than saving what is on screen: the panel's copy may be a minute old, and
    // what lands on disk should be what the project holds now.
    const fresh = await getJson(path);
    save(fresh.name, fresh.text);
  }, [path]);

  const close = useCallback(() => setName(null), []);

  return { name, file, missing, error, open: setName, close, download };
}
