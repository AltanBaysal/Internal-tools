import { useCallback, useEffect, useState } from "react";

import { getJson, postJson } from "../../shared/api.js";

function useList(path, enabled = true) {
  const [items, setItems] = useState([]);

  const reload = useCallback(() => {
    if (!enabled) return Promise.resolve();
    return getJson(path)
      .then(setItems)
      .catch(() => setItems([]));
  }, [path, enabled]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { items, reload };
}

// Two lists, two questions. The sidebar asks what was touched recently across the whole workspace;
// the project screen asks what this project holds. Filtering one out of the other works today, but
// the day the recent list is capped the project screen would quietly go short.
export function useRecentChats() {
  const { items, reload } = useList("/api/chats");
  return { recentChats: items, reloadRecentChats: reload };
}

export function useProjectChats(projectId) {
  const { items, reload } = useList(`/api/projects/${projectId}/chats`, Boolean(projectId));
  return { projectChats: projectId ? items : [], reloadProjectChats: reload };
}

export function startChatInNewProject(text) {
  return postJson("/api/chats", { text });
}

export function startChatInProject(projectId, text) {
  return postJson(`/api/projects/${projectId}/chats`, { text });
}
