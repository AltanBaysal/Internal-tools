import { getJson } from "../../shared/api.js";
import { useList } from "../../shared/useList.js";

// What this project holds, for the sidebar, which lists all of it (Madde 362) -- and, when the read
// failed, what came back instead (Madde 386), so the sidebar never takes a failure for no chats.
export function useProjectChats(projectId) {
  const { items, reload, error } = useList(`/api/projects/${projectId}/chats`, Boolean(projectId));
  return {
    projectChats: projectId ? items : [],
    projectChatsError: projectId ? error : null,
    reloadProjectChats: reload,
  };
}

// Starting a chat is not a separate call any more: since Madde 88 the draft sends through the same
// road as a reply, and the answer streams back down it.

// Which chat a project opens on (OpenProject.jsx) is asked once, apart from the list above: that
// list keeps the last project's rows until the next project's answer comes.
export function readChats(projectId) {
  return getJson(`/api/projects/${projectId}/chats`);
}
