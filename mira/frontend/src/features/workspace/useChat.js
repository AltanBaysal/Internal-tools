import { useCallback, useEffect, useState } from "react";

import { getJson, postJson } from "../../shared/api.js";
import { streamEvents } from "../../shared/sse.js";

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
  const [streamingText, setStreamingText] = useState("");

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
    setError(null);
    setStreamingText("");
    try {
      await streamEvents(`/api/projects/${projectId}/chats/${chatId}/answer`, (frame) => {
        if (frame.event === "chunk") setStreamingText((text) => text + frame.data.text);
        // What the browser piled up is a guess; what the server wrote is the record, so the record
        // replaces it rather than being reconciled with it.
        else if (frame.event === "done") setChat(frame.data);
        else if (frame.event === "error") setError(frame.data.error);
      });
    } catch (failure) {
      setError(failure.message);
    } finally {
      setStreamingText("");
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

  // Try again asks for the answer once more; it never re-sends the message, because the chat is
  // still owed one and the user's sentence must not be written twice.
  return { chat, error, missing, thinking, streamingText, send, retry: ask };
}
