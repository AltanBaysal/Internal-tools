import { useCallback, useEffect, useState } from "react";

import { deleteJson, patchJson, postJson } from "../../shared/api.js";
import { useList } from "../../shared/useList.js";

// The directory is the list. Nothing is kept beyond this array and a new file is a reload rather
// than an insert, because the order and the times are the server's answer, not ours to guess.
export function useFiles(projectId, onChanged) {
  const base = `/api/projects/${projectId}`;
  const { items, reload, loading } = useList(`${base}/files`, Boolean(projectId));
  // What was deleted lives here and nowhere else: the trash name is the only handle on the file,
  // and it is never written to disk. When this goes, the offer goes with it.
  const [deleted, setDeleted] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setDeleted(null);
    setError(null);
  }, [projectId]);

  const remove = useCallback(
    async (name) => {
      setError(null);
      try {
        const { trashed } = await deleteJson(`${base}/files/${encodeURIComponent(name)}`);
        setDeleted({ name, trashed });
        await reload();
        await onChanged?.();
      } catch (failure) {
        setError(failure.message);
      }
    },
    [base, reload, onChanged],
  );

  const undo = useCallback(async () => {
    if (!deleted) return;
    try {
      await postJson(`${base}/trash/${encodeURIComponent(deleted.trashed)}/restore`, {
        name: deleted.name,
      });
      setDeleted(null);
      setError(null);
      await reload();
      await onChanged?.();
    } catch (failure) {
      // The offer stands: a refusal means the file is still in the trash.
      setError(failure.message);
    }
  }, [base, deleted, reload, onChanged]);

  const rename = useCallback(
    async (name, wanted) => {
      setError(null);
      try {
        // The answer carries the name actually used: asking for a taken one gets a numbered one.
        const renamed = await patchJson(`${base}/files/${encodeURIComponent(name)}`, {
          name: wanted,
        });
        await reload();
        return renamed;
      } catch (failure) {
        setError(failure.message);
        return null;
      }
    },
    [base, reload],
  );

  return {
    files: projectId ? items : [],
    reloadFiles: reload,
    loadingFiles: loading,
    rename,
    deleting: { deleted, error, remove, undo },
  };
}
