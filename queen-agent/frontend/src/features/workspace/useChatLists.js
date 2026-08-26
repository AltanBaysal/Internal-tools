import { deleteJson } from "../../shared/api.js";
import { useList } from "../../shared/useList.js";

// One question, one list: both the sidebar and the project screen ask what this project holds. The
// sidebar draws the first eight of it, which is a matter of how much room a column has, not of a
// second answer worth fetching.
export function useProjectChats(projectId) {
  const { items, reload, loading, error } = useList(
    `/api/projects/${projectId}/chats`,
    Boolean(projectId),
  );
  return {
    projectChats: projectId ? items : [],
    reloadProjectChats: reload,
    loadingChats: loading,
    chatsError: error,
  };
}

// Starting a chat is not a separate call any more: since Madde 88 the draft sends through the same
// road as a reply, and the answer streams back down it.

export function deleteChat(projectId, chatId) {
  return deleteJson(`/api/projects/${projectId}/chats/${chatId}`);
}
