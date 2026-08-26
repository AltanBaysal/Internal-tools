import { useCallback, useEffect, useRef, useState } from "react";

import { getJson, postJson } from "../../shared/api.js";
import { streamEvents } from "../../shared/sse.js";

export function useChat(projectId, chatId, onFileCreated, onChatBorn) {
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
  // What the turn has done so far. Held only while the answer runs: the record that arrives at the
  // end carries the same steps, and drawing from both sources would read one step as two.
  const [streamingCalls, setStreamingCalls] = useState([]);

  // Kept in refs rather than dependencies: the caller may hand over fresh functions on every
  // render, and that must not rebuild `send`.
  const announce = useRef(onFileCreated);
  announce.current = onFileCreated;
  const born = useRef(onChatBorn);
  born.current = onChatBorn;
  // Which chat a stream is running into. The first frame moves the address, and the effect below
  // must not answer that move by throwing away what is still arriving.
  const streamingInto = useRef(null);

  useEffect(() => {
    if (!projectId || !chatId) return undefined;
    if (chatId === streamingInto.current) return undefined;
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

  // One road for both jobs since Madde 88: a sentence and a second attempt are the same request
  // with and without text, and the answer comes back down it either way. Nothing here runs by
  // itself -- what used to ask on a reload and on a reconnection is a rule on the server now.
  //
  // The skill travels with the message rather than being read off the chat: what governed a turn
  // is settled when the turn is sent.
  const send = useCallback(
    async (text = null, skill = "") => {
      const at = new Date().toISOString();
      if (text !== null) {
        // The bubble appears before the server answers -- the design says so in as many words. In
        // a draft there is no record to add it to, so one is stood up to hold it.
        setChat((current) =>
          current
            ? {
                ...current,
                messages: [...current.messages, { role: "user", at, text, pending: true }],
              }
            : { id: null, title: text, messages: [{ role: "user", at, text, pending: true }] },
        );
      }
      setRefused(null);
      setError(null);
      setThinking(true);
      setStreamingText("");
      setCreatingFile(false);
      setCreatedFiles([]);
      setStreamingCalls([]);
      // No text at all is how Try again asks: the question is already on disk and must not be
      // written a second time. A blank one would be refused, which is a different thing.
      const body = text === null ? { chat: chatId } : { chat: chatId ?? "", text, skill };
      try {
        await streamEvents(
          `/api/projects/${projectId}/messages`,
          (frame) => {
            if (frame.event === "chat") {
              streamingInto.current = frame.data.chat;
              if (frame.data.chat !== chatId) born.current?.(frame.data.chat);
            } else if (frame.event === "chunk") {
              setStreamingText((current) => current + frame.data.text);
            } else if (frame.event === "call") {
              setStreamingCalls((calls) => [...calls, frame.data]);
            } else if (frame.event === "file-start") setCreatingFile(true);
            else if (frame.event === "file") {
              setCreatedFiles((names) => [...names, frame.data.name]);
              setCreatingFile(false);
              // The file exists on disk this instant, so every list that shows it is out of date.
              announce.current?.();
            }
            // What the browser piled up is a guess; what the server wrote is the record, so the
            // The closing frame carries nothing since Madde 89: it says the turn is over, and what
            // the turn wrote is read below.
            else if (frame.event === "error") setError(frame.data.error);
          },
          body,
        );
        // The record has one home, so the turn ends by reading it -- before the finally below
        // clears what streamed, or the transcript blinks empty between the two. Whatever the turn
        // ended as: a fault still leaves the user's own sentence on disk, and it has to stay on
        // the screen.
        const landed = streamingInto.current ?? chatId;
        if (landed) {
          try {
            setChat(await getJson(`/api/projects/${projectId}/chats/${landed}`));
          } catch (unreadable) {
            // A fault already reported is the turn's real one, and replacing it with this would
            // show the wrong cause. Otherwise the read speaks for itself: the answer was written,
            // and what was lost is the showing of it.
            setError((current) => current ?? unreadable.message);
          }
        }
      } catch (failure) {
        // Refused before a byte came back, so nothing was written: the optimistic bubble is taken
        // back out and the screen never claims something was said when it was not.
        if (text !== null) {
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
        }
        setRefused(failure.message);
        // Thrown on rather than swallowed, but only when there was a sentence: the composer is
        // holding the only copy of it and has to know to keep it. Try again carries none, and a
        // throw there would be nobody's to catch.
        if (text !== null) throw failure;
      } finally {
        // The cards drawn from the stream go too: the stored answer carries the same names, and a
        // stream that broke wrote no answer at all.
        setStreamingText("");
        setCreatingFile(false);
        setCreatedFiles([]);
        setStreamingCalls([]);
        setThinking(false);
      }
    },
    [projectId, chatId],
  );

  const stop = useCallback(async () => {
    // The server's answer carries nothing; what matters is that the flag is set before the running
    // turn looks at it again. A refusal is not worth a message -- the stream ends either way.
    await postJson(`/api/projects/${projectId}/chats/${chatId}/stop`, {}).catch(() => {});
  }, [projectId, chatId]);

  return {
    chat,
    error,
    refused,
    missing,
    thinking,
    streamingText,
    creatingFile,
    createdFiles,
    streamingCalls,
    send,
    stop,
    // Try again is the same road with no sentence on it.
    retry: () => send(null),
  };
}
