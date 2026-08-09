import { useList } from "../../shared/useList.js";

// The directory is the list. Nothing is kept beyond this array and a new file is a reload rather
// than an insert, because the order and the times are the server's answer, not ours to guess.
export function useFiles(projectId) {
  const { items, reload } = useList(`/api/projects/${projectId}/files`, Boolean(projectId));
  return { files: projectId ? items : [], reloadFiles: reload };
}
