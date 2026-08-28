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
  // The question a paused turn is waiting on: {tool, args}, or null. The frame says `arguments` and
  // this says `args` -- a language rule rather than a rename, since `arguments` cannot be
  // destructured as a prop inside a module.
  const [permission, setPermission] = useState(null);

  // Kept in refs rather than dependencies: the caller may hand over fresh functions on every
  // render, and that must not rebuild `send`.
  const announce = useRef(onFileCreated);
  announce.current = onFileCreated;
  const born = useRef(onChatBorn);
  born.current = onChatBorn;
  // Which chat a stream is running into. The first frame moves the address, and the effect below
  // must not answer that move by throwing away what is still arriving.
  const streamingInto = useRef(null);
  // The same fact for the screen: state rather than a ref, because what the hook returns is gated
  // on it and the gate has to move a render (Madde 106).
  const [streamingChatId, setStreamingChatId] = useState(null);
  // The chat the screen is on now, read where a stream ends: a turn that lands elsewhere must not
  // repaint this one.
  const live = useRef(chatId);
  live.current = chatId;
  // The record the hook holds now, read by the loading effect: the birth guard may only skip the
  // load when what is held already belongs here.
  const held = useRef(null);
  held.current = chat;
  // The send that owns the shared stream states -- the newest one. An older stream keeps running
  // on the server; what it may not do is draw on, or clear, a screen that is no longer its own.
  const owner = useRef(null);

  useEffect(() => {
    // No chat at this address: the draft, or no chat screen at all. Dropped rather than kept -- a
    // held record is the chat that was left, the draft's first bubble lands on it, and the birth
    // then shows that transcript at the newborn's address (Madde 104).
    if (!projectId || !chatId) {
      setChat(null);
      setError(null);
      setMissing(false);
      return undefined;
    }
    // Madde 88's birth guard, narrowed by Madde 106: skip the load only while what is held
    // already belongs here -- the stood-up draft record (id null) or this chat's own. A return
    // from another chat holds that chat's record, and the transcript comes back from disk.
    if (chatId === streamingInto.current && held.current) {
      const heldId = held.current.id;
      if (heldId === null || heldId === chatId) return undefined;
    }
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
  // is settled when the turn is sent. The mode travels the same way and is kept nowhere -- what it
  // decides is which tools the request carries, and that is decided the moment it is sent.
  const send = useCallback(
    async (text = null, skill = "", mode = "") => {
      const at = new Date().toISOString();
      const token = {};
      owner.current = token;
      // Where this turn lands. Starts as the chat it was sent from; the first frame can name a
      // newborn instead. Local, so a send that lost the screen still knows its own chat.
      let target = chatId;
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
      streamingInto.current = chatId;
      setStreamingChatId(chatId);
      // No text at all is how Try again asks: the question is already on disk and must not be
      // written a second time. A blank one would be refused, which is a different thing.
      const body = text === null ? { chat: chatId } : { chat: chatId ?? "", text, skill, mode };
      try {
        await streamEvents(
          `/api/projects/${projectId}/messages`,
          (frame) => {
            if (frame.event === "chat") {
              target = frame.data.chat;
              if (owner.current !== token) return;
              streamingInto.current = target;
              setStreamingChatId(target);
              if (target !== chatId) born.current?.(target);
              return;
            }
            // A newer send owns the screen: this stream still lands on disk and is read from
            // there, but it draws nothing any more -- except a born file, which is true for
            // every screen.
            if (owner.current !== token) {
              if (frame.event === "file") announce.current?.();
              return;
            }
            if (frame.event === "chunk") {
              setStreamingText((current) => current + frame.data.text);
            } else if (frame.event === "call") {
              setStreamingCalls((calls) => [...calls, frame.data]);
              // The dashed card lives between "the model asked" and "the tool answered", and this
              // frame is the second. Only a born file used to take it down, so a tool that wrote
              // nothing left it up until the turn ended.
              setCreatingFile(false);
            } else if (frame.event === "file-start") setCreatingFile(true);
            else if (frame.event === "file") {
              setCreatedFiles((names) => [...names, frame.data.name]);
              setCreatingFile(false);
              // The file exists on disk this instant, so every list that shows it is out of date.
              announce.current?.();
            } else if (frame.event === "permission") {
              // The turn has stopped and is reading for an answer. Nothing else about the screen
              // changes: it is still running, so the send button is still a stop.
              setPermission({ tool: frame.data.tool, args: frame.data.arguments });
            }
            // The closing frame carries nothing since Madde 89: it says the turn is over, and what
            // the turn wrote is read below.
            else if (frame.event === "error") {
              // The turn's fault belongs to the chat it ran in: standing elsewhere, the screen
              // does not wear it -- the unanswered message in the record says it on a visit.
              if ((target ?? null) === (live.current ?? null)) setError(frame.data.error);
            }
          },
          body,
        );
        // The record has one home, so the turn ends by reading it -- before the finally below
        // clears what streamed, or the transcript blinks empty between the two. Whatever the turn
        // ended as: a fault still leaves the user's own sentence on disk, and it has to stay on
        // the screen. Read either way; what it may not do is dress a screen standing in another
        // chat (Madde 106) -- that chat's own visit reads the same record.
        const landed = target ?? chatId;
        if (landed) {
          try {
            const record = await getJson(`/api/projects/${projectId}/chats/${landed}`);
            if (landed === live.current) setChat(record);
          } catch (unreadable) {
            // A fault already reported is the turn's real one, and replacing it with this would
            // show the wrong cause. Otherwise the read speaks for itself: the answer was written,
            // and what was lost is the showing of it.
            if (landed === live.current) setError((current) => current ?? unreadable.message);
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
        if ((target ?? null) === (live.current ?? null)) setRefused(failure.message);
        // Thrown on rather than swallowed, but only when there was a sentence: the composer is
        // holding the only copy of it and has to know to keep it. Try again carries none, and a
        // throw there would be nobody's to catch.
        if (text !== null) throw failure;
      } finally {
        // Only the send that owns the screen clears it: an older stream sweeping these would wipe
        // one that is still drawing (Madde 106).
        if (owner.current === token) {
          // The cards drawn from the stream go too: the stored answer carries the same names, and
          // a stream that broke wrote no answer at all.
          setStreamingText("");
          setCreatingFile(false);
          setCreatedFiles([]);
          setStreamingCalls([]);
          // However the turn ended. A question left standing would hang over the next turn,
          // offering to allow something nobody is waiting on any more.
          setPermission(null);
          setThinking(false);
          // Cleared so a later visit loads from disk: while a stream runs its chat reads from
          // these states, and once it ends the record is the only home (Madde 89).
          streamingInto.current = null;
          setStreamingChatId(null);
          owner.current = null;
        }
      }
    },
    [projectId, chatId],
  );

  const stop = useCallback(async () => {
    // The server's answer carries nothing; what matters is that the running turn's connection is
    // cut. A refusal is not worth a message -- the stream ends either way.
    await postJson(`/api/projects/${projectId}/chats/${chatId}/stop`, {}).catch(() => {});
  }, [projectId, chatId]);

  const answer = useCallback(
    async (allowed, reason) => {
      // The card goes first: the turn carries on down the stream that is already open, and waiting
      // for the door to reply would leave the question on screen after it was settled.
      setPermission(null);
      // The chat the stream went into rather than the address: a chat born by this very message
      // has no address yet, and the answer would knock at chats/null.
      const landed = streamingInto.current ?? chatId;
      await postJson(
        `/api/projects/${projectId}/chats/${landed}/permission`,
        allowed ? { allowed: true } : { allowed: false, reason },
      ).catch(() => {});
    },
    [projectId, chatId],
  );

  // What the stream draws belongs to the chat it runs into (Madde 106): standing elsewhere, none
  // of it shows -- and coming back, it shows again. The draft is its own chat here: null equals
  // null until the first frame names the newborn, and the address follows it.
  const visible = streamingChatId === (chatId ?? null);
  return {
    chat,
    error,
    refused,
    missing,
    thinking: visible && thinking,
    streamingText: visible ? streamingText : "",
    creatingFile: visible && creatingFile,
    createdFiles: visible ? createdFiles : [],
    streamingCalls: visible ? streamingCalls : [],
    permission: visible ? permission : null,
    send,
    stop,
    answer,
    // Try again is the same road with no sentence on it.
    retry: () => send(null),
  };
}
