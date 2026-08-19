import { useCallback, useEffect, useRef, useState } from "react";

import { getJson, patchJson, postJson } from "../../shared/api.js";
import { streamEvents } from "../../shared/sse.js";

// A chat whose last message is the user's is owed an answer. Stating it that way means the message
// that opens a chat and a follow-up inside one travel the same road: send, then ask.
function isOwedAnAnswer(chat) {
  const last = chat?.messages[chat.messages.length - 1];
  // A message still in flight does not count -- asking for an answer before the question has
  // reached disk would answer the wrong conversation.
  return Boolean(last) && last.role === "user" && !last.pending;
}

export function useChat(projectId, chatId, onFileCreated, online = true) {
  const [chat, setChat] = useState(null);
  const [error, setError] = useState(null);
  // Kept apart from `error` on purpose: a message that was never sent and an answer that never came
  // are different failures, and only this hook knows which road the message came down.
  const [refused, setRefused] = useState(null);
  const [missing, setMissing] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [creatingFile, setCreatingFile] = useState(false);
  const [createdFiles, setCreatedFiles] = useState([]);

  // Kept in a ref rather than a dependency: the caller may hand over a fresh function on every
  // render, and that must not rebuild `ask` and restart the effect below.
  const announce = useRef(onFileCreated);
  announce.current = onFileCreated;

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
    setCreatingFile(false);
    setCreatedFiles([]);
    try {
      await streamEvents(`/api/projects/${projectId}/chats/${chatId}/answer`, (frame) => {
        if (frame.event === "chunk") setStreamingText((text) => text + frame.data.text);
        else if (frame.event === "file-start") setCreatingFile(true);
        else if (frame.event === "file") {
          setCreatedFiles((names) => [...names, frame.data.name]);
          setCreatingFile(false);
          // The file exists on disk this instant, so every list that shows it is now out of date.
          announce.current?.();
        }
        // What the browser piled up is a guess; what the server wrote is the record, so the record
        // replaces it rather than being reconciled with it.
        else if (frame.event === "done") setChat(frame.data);
        else if (frame.event === "error") setError(frame.data.error);
      });
    } catch (failure) {
      setError(failure.message);
    } finally {
      // The cards drawn from the stream go too: the stored answer carries the same names, and a
      // stream that broke wrote no answer at all.
      setStreamingText("");
      setCreatingFile(false);
      setCreatedFiles([]);
      setThinking(false);
    }
  }, [projectId, chatId]);

  useEffect(() => {
    // Not while one is already running, and not after a failure -- otherwise a broken engine would
    // be asked again forever. Not while the connection is gone either: the chat stays owed an
    // answer, so this effect asks for it by itself the moment the connection is back.
    if (!online || thinking || error || !isOwedAnAnswer(chat)) return;
    ask();
  }, [chat, thinking, error, online, ask]);

  // The skill travels with the message rather than being read off the chat on the server: what
  // governed a turn is settled when the turn is sent.
  const send = useCallback(
    async (text, skill = "") => {
      const at = new Date().toISOString();
      // The bubble appears before the server answers -- the design says so in as many words.
      setChat((current) =>
        current
          ? { ...current, messages: [...current.messages, { role: "user", at, text, pending: true }] }
          : current,
      );
      setRefused(null);
      try {
        setChat(
          await postJson(`/api/projects/${projectId}/chats/${chatId}/messages`, { text, skill }),
        );
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
        setRefused(failure.message);
        // Thrown on rather than swallowed: the composer is holding the only copy of the sentence,
        // and it has to know to keep it.
        throw failure;
      }
    },
    [projectId, chatId],
  );

  // The record on the server is the truth about what a chat answers with, so a choice goes there
  // and what comes back replaces what is held here. One road for both: the endpoint takes either.
  const choose = useCallback(
    async (choice) => {
      setChat(await patchJson(`/api/projects/${projectId}/chats/${chatId}`, choice));
    },
    [projectId, chatId],
  );

  // Try again asks for the answer once more; it never re-sends the message, because the chat is
  // still owed one and the user's sentence must not be written twice.
  return {
    chat,
    choose,
    error,
    refused,
    missing,
    thinking,
    streamingText,
    creatingFile,
    createdFiles,
    send,
    retry: ask,
  };
}
