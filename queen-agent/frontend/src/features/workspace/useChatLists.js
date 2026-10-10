import { getJson } from "../../shared/api.js";
import { useList } from "../../shared/useList.js";

// What this project holds, for the sidebar, which lists all of it (Madde 362) -- and, when the read
// failed, what came back instead (Madde 386), so the sidebar never takes a failure for no chats;
// and, while no answer about this project is in hand, that it has none yet (Madde 457), so it never
// takes the wait for no chats either.
export function useProjectChats(projectId) {
  const { items, reload, loading, error } = useList(
    `/api/projects/${projectId}/chats`,
    Boolean(projectId),
  );
  return {
    projectChats: projectId ? items : [],
    loadingChats: projectId ? loading : false,
    projectChatsError: projectId ? error : null,
    reloadProjectChats: reload,
  };
}

// Starting a chat is not a separate call any more: since Madde 88 the draft sends through the same
// road as a reply, and the answer streams back down it.

// Which chat a project opens on (OpenProject.jsx) is asked once, apart from the list above: it is a
// step taken on one answer -- go to the newest chat, or the draft -- and dropped if the user has
// left, not rows kept on screen; the list above is state, and would have to be watched for its first
// answer to take the step.
export function readChats(projectId) {
  return getJson(`/api/projects/${projectId}/chats`);
}
