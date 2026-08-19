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
  // The file is held together with the project it belongs to, and read back only while that is
  // still the project on screen. That pairing is what makes the frame between a project changing
  // and the effect below running draw nothing rather than the wrong project's file.
  const [opened, setOpened] = useState(null);
  const [file, setFile] = useState(null);
  const [missing, setMissing] = useState(false);
  const [error, setError] = useState(null);

  const name = opened && opened.projectId === projectId ? opened.name : null;
  const path = name ? `/api/projects/${projectId}/files/${encodeURIComponent(name)}` : null;

  // Leaving the project closes the file rather than hiding it: coming back and finding it open again
  // would be the panel deciding for the user. Watching the project alone is what keeps the case
  // above working -- a file opened in the same breath as the navigation to its project arrives here
  // before the project does, and this effect does not run then.
  useEffect(() => {
    setOpened((current) => (current && current.projectId !== projectId ? null : current));
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

  // A caller can open a file that lives in another project, so where it lives travels with it.
  const open = useCallback(
    (fileName, inProject) => setOpened({ projectId: inProject ?? projectId, name: fileName }),
    [projectId],
  );

  const close = useCallback(() => setOpened(null), []);

  return { name, file, missing, error, open, close, download };
}
