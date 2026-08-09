import { useCallback, useEffect, useState } from "react";

import { getJson, postJson } from "../../shared/api.js";

// A chat whose last message is the user's is owed an answer. Stating it that way means a chat
// started from home and a follow-up inside a chat travel the same road: send, then ask.
function isOwedAnAnswer(chat) {
  const last = chat?.messages[chat.messages.length - 1];
  // A message still in flight does not count -- asking for an answer before the question has
  // reached disk would answer the wrong conversation.
  return Boolean(last) && last.role === "user" && !last.pending;
}

export function useChat(projectId, chatId) {
  const [chat, setChat] = useState(null);
  const [error, setError] = useState(null);
  const [missing, setMissing] = useState(false);
  const [thinking, setThinking] = useState(false);

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

  const ask = useCallback(async () => {
    setThinking(true);
    try {
      setChat(await postJson(`/api/projects/${projectId}/chats/${chatId}/answer`));
    } catch (failure) {
      setError(failure.message);
    } finally {
      setThinking(false);
    }
  }, [projectId, chatId]);

  useEffect(() => {
    // Not while one is already running, and not after a failure -- otherwise a broken engine would
    // be asked again forever.
    if (thinking || error || !isOwedAnAnswer(chat)) return;
    ask();
  }, [chat, thinking, error, ask]);

  const send = useCallback(
    async (text) => {
      const at = new Date().toISOString();
      // The bubble appears before the server answers -- the design says so in as many words.
      setChat((current) =>
        current
          ? { ...current, messages: [...current.messages, { role: "user", at, text, pending: true }] }
          : current,
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

  return { chat, error, missing, thinking, send };
}
