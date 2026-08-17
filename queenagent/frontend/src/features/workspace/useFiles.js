import { useCallback, useEffect, useState } from "react";

import { deleteJson } from "../../shared/api.js";
import { useList } from "../../shared/useList.js";

// The directory is the list. Nothing is kept beyond this array and a new file is a reload rather
// than an insert, because the order and the times are the server's answer, not ours to guess.
export function useFiles(projectId, onChanged) {
  const base = `/api/projects/${projectId}`;
  const { items, reload, loading } = useList(`${base}/files`, Boolean(projectId));
  // Nothing is remembered about what went: the trash name was held only for as long as there was an
  // undo to offer, and there is none. What is kept is a failure, which is not an offer.
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
  }, [projectId]);

  const remove = useCallback(
    async (name) => {
      setError(null);
      try {
        await deleteJson(`${base}/files/${encodeURIComponent(name)}`);
        await reload();
        await onChanged?.();
      } catch (failure) {
        setError(failure.message);
      }
    },
    [base, reload, onChanged],
  );

  return {
    files: projectId ? items : [],
    reloadFiles: reload,
    loadingFiles: loading,
    deleting: { error, remove },
  };
}
