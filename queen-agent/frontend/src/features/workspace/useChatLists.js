import { deleteJson, postJson } from "../../shared/api.js";
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

export function startChatInProject(projectId, text, skill = "") {
  // No chat named: Madde 87's way of saying there is not one yet, and the server makes it.
  return postJson(`/api/projects/${projectId}/messages`, { text, skill });
}

export function deleteChat(projectId, chatId) {
  return deleteJson(`/api/projects/${projectId}/chats/${chatId}`);
}
