import { deleteJson, postJson } from "../../shared/api.js";
import { useList } from "../../shared/useList.js";

// Two lists, two questions. The sidebar asks what was touched recently across the whole workspace;
// the project screen asks what this project holds. Filtering one out of the other works today, but
// the day the recent list is capped the project screen would quietly go short.
export function useRecentChats() {
  const { items, reload } = useList("/api/chats");
  return { recentChats: items, reloadRecentChats: reload };
}

export function useProjectChats(projectId) {
  const { items, reload, loading } = useList(`/api/projects/${projectId}/chats`, Boolean(projectId));
  return {
    projectChats: projectId ? items : [],
    reloadProjectChats: reload,
    loadingChats: loading,
  };
}

export function startChatInProject(projectId, text) {
  return postJson(`/api/projects/${projectId}/chats`, { text });
}

export function deleteChat(projectId, chatId) {
  return deleteJson(`/api/projects/${projectId}/chats/${chatId}`);
}
