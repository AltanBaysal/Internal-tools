import { useCallback, useEffect, useState } from "react";

import { getJson, postJson } from "../../shared/api.js";

export function useChat(projectId, chatId) {
  const [chat, setChat] = useState(null);
  const [error, setError] = useState(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    if (!projectId || !chatId) return undefined;
    let cancelled = false;
    setChat(null);
    setError(null);
    setMissing(false);
    getJson(`/api/projects/${projectId}/chats/${chatId}`)
      .then((loaded) => {
        if (!cancelled) setChat(loaded);
      })
      .catch((failure) => {
        if (cancelled) return;
        if (failure.status === 404) setMissing(true);
        else setError(failure.message);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, chatId]);

  const send = useCallback(
    async (text) => {
      const at = new Date().toISOString();
      // The bubble appears before the server answers -- the design says so in as many words.
      setChat((current) =>
        current ? { ...current, messages: [...current.messages, { role: "user", at, text }] } : current,
      );
      setError(null);
      try {
        setChat(await postJson(`/api/projects/${projectId}/chats/${chatId}/messages`, { text }));
      } catch (failure) {
        // Refused: the optimistic bubble is taken back out so the screen never claims something
        // was said when it was not.
        setChat((current) =>
          current
            ? {
                ...current,
                messages: current.messages.filter(
                  (message) => !(message.at === at && message.text === text),
                ),
              }
            : current,
        );
        setError(failure.message);
      }
    },
    [projectId, chatId],
  );

  return { chat, error, missing, send };
}
