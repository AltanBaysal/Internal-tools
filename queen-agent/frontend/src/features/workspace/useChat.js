import { useCallback, useEffect, useRef, useState } from "react";

import { getJson, postJson } from "../../shared/api.js";

// One chat of one project, as the listeners below are kept by it.
const chatKey = (projectId, chatId) => `${projectId}/${chatId}`;

// How long an ask of the events door that failed -- the network, the tunnel's 502 -- waits before it
// is asked again: what EventSource waited before it reconnected, the job this took over (Madde 491).
const AGAIN_MS = 3000;

// The chat as the server says it stands (Madde 462): its record, its status and its running turn,
// read once and then listened to. The screen draws that and nothing of its own -- what is kept here
// is only what is being typed: the sentence on its way until the door answers, and a question just
// answered until the server says it is gone.
export function useChat(projectId, chatId, onFileCreated, onChatBorn, onTurnEnd) {
  const [chat, setChat] = useState(null);
  const [error, setError] = useState(null);
  // Kept apart from `error` on purpose, though both draw the same card (Madde 349): a message that
  // was never sent and an answer that never came are asked for again differently, and only this
  // hook knows which road the message came down.
  const [refused, setRefused] = useState(null);
  // Whether the refused send was a reply: its sentence went back to the box then, and the box is
  // what sends it again -- one owner, so it cannot go twice (Madde 349).
  const refusedReply = useRef(false);
  const [missing, setMissing] = useState(false);
  // Which message of the record the turn just ended on, so its words fade in once (design item
  // 214), or null.
  const [arrived, setArrived] = useState(null);
  // The sentence on its way: {key, text, at, from}. The design draws the bubble before the server
  // answers; once it has, the record the door hands back carries the question itself.
  const [pending, setPending] = useState(null);
  // "turn:wait" of the question just answered: the card goes at once, not a round trip later.
  const [decided, setDecided] = useState(null);

  // Kept in refs rather than dependencies: the caller may hand over fresh functions on every
  // render, and that must not rebuild `send`.
  const announce = useRef(onFileCreated);
  announce.current = onFileCreated;
  const born = useRef(onChatBorn);
  born.current = onChatBorn;
  const ended = useRef(onTurnEnd);
  ended.current = onTurnEnd;
  // The chat the screen is on now, read wherever an answer lands: one that lands elsewhere draws
  // nothing here (Madde 106). The draft is null.
  const here = useRef(null);
  here.current = projectId && chatId ? chatKey(projectId, chatId) : null;
  // The record held now, for what a press needs of it -- the turn and the question it names.
  const held = useRef(null);
  held.current = chat;
  // The send whose sentence is on its way here (its `at`), and the one a Stop was pressed for
  // before the door said which turn it started -- or null.
  const onItsWay = useRef(null);
  const early = useRef(null);
  // The turns listened to now, one listener each. A turn this hook started keeps its listener until
  // it ends, wherever the screen is, so its end is heard (Madde 452); one the screen listened to is
  // let go when the screen leaves the chat.
  //
  // What follows is written as plain functions: each reads only refs and state setters, so the copy
  // an ask's answer reaches is as good as the newest.
  const listeners = useRef(new Map());

  // Kept is what lets an ask's answer through: one let go of draws nothing and asks no more, so an
  // ask still out when it was let go needs no cancelling.
  const kept = (listener) => listeners.current.get(listener.key) === listener;
  const letGo = (listener) => {
    if (kept(listener)) listeners.current.delete(listener.key);
  };

  const follow = (project, id, own, turnId) => {
    const key = `${chatKey(project, id)}/${turnId}`;
    const open = listeners.current.get(key);
    if (open) {
      open.own = open.own || own;
      return;
    }
    // `failed`: how many asks in a row have failed.
    const listener = { project, id, key, own, turnId, files: 0, failed: 0 };
    listeners.current.set(key, listener);
    ask(listener, null);
  };

  // The events door, asked once (Madde 491): with no version it answers at once with the turn and
  // where it stands, and asked from a version, once the turn has moved past it -- or after a quiet
  // while, as it was. Asked again from each answer until the turn is over. Long polling rather than
  // EventSource, because the Quick Tunnel holds a GET's body until it ends. The turn is named, so a
  // turn that ended between two asks still says how, its own fault included.
  const ask = (listener, after) => {
    const since = after === null ? "" : `&after=${after}`;
    const { project, id, turnId } = listener;
    getJson(`/api/projects/${project}/chats/${id}/events?turn=${turnId}${since}`).then(
      (said) => {
        if (!kept(listener)) return;
        listener.failed = 0;
        heard(listener, said);
        if (kept(listener)) ask(listener, said.version);
      },
      (failure) => {
        if (!kept(listener)) return;
        listener.failed += 1;
        // Once: no card, the turn stays drawn as it stood and is asked about again, as EventSource
        // mended a drop. Twice in a row: the server is not coming back by itself.
        if (listener.failed > 1) return lost(listener, failure);
        setTimeout(() => kept(listener) && ask(listener, after), AGAIN_MS);
      },
    );
  };

  // The turn can no longer be followed. On screen the card takes the wait's place, as the failure
  // card does -- a turn nobody can hear is not drawn as one -- and its Try again is the retry door,
  // which hands a running turn back to be listened to. Off screen nobody will hear its end, so its
  // upkeep is done now, once: the lists it refreshes are read from memory either way.
  const lost = (listener, failure) => {
    letGo(listener);
    if (chatKey(listener.project, listener.id) === here.current) {
      setChat((current) => (current?.id === listener.id ? { ...current, turn: null } : current));
      setError(failure.message);
    } else if (listener.own) ended.current?.();
  };

  const heard = (listener, said) => {
    const { turn } = said;
    // A turn other than the one it listens for -- that one ended before the ask arrived -- is the
    // end of this one: the record read then names the next.
    if (!turn || turn.id !== listener.turnId) return finished(listener, said.error);
    // A file exists this instant, so every list that shows it is out of date -- on every screen.
    if (turn.files.length > listener.files) {
      listener.files = turn.files.length;
      announce.current?.();
    }
    if (chatKey(listener.project, listener.id) !== here.current) return;
    setChat((current) => (current?.id === listener.id ? { ...current, turn } : current));
  };

  const finished = (listener, fault) => {
    letGo(listener);
    // However the turn ended, wherever the screen is: what it wrote is on disk (Madde 192, 452).
    if (listener.own) ended.current?.();
    const key = chatKey(listener.project, listener.id);
    if (key !== here.current) return;
    // The record has one home (Madde 89): the turn is over, and what it wrote is read. Until it
    // lands the turn still shows, so the wait does not blink out before the answer comes in.
    getJson(`/api/projects/${listener.project}/chats/${listener.id}`)
      .then((record) => {
        if (key !== here.current) return;
        setChat(record);
        setArrived(record.messages.length - 1);
        // The turn's own fault wrote nothing, and no record will say it: only those listening hear.
        if (fault) setError(fault);
      })
      .catch((unreadable) => {
        if (key !== here.current) return;
        setChat((current) => (current?.id === listener.id ? { ...current, turn: null } : current));
        // A fault already said is the real one; otherwise the read speaks for itself.
        setError(fault || unreadable.message);
      });
  };

  // What the door answered a send or a Try again with: the chat as reading it gives it. `at` names
  // the send, whose Stop may have been pressed before the door said which turn it would stop.
  const took = (project, answer, key, at = null) => {
    if (answer.turn) {
      follow(project, answer.id, true, answer.turn.id);
      if (early.current !== null && early.current === at) {
        postJson(`/api/projects/${project}/chats/${answer.id}/stop`, { turn: answer.turn.id }).catch(
          () => {},
        );
      }
    }
    // Over before the door could answer: what it wrote is already in the answer.
    else ended.current?.();
    if (early.current === at) early.current = null;
    if (key !== here.current) return;
    setChat(answer);
    if (!answer.turn) setArrived(answer.messages.length - 1);
  };

  useEffect(() => {
    // No chat at this address: the draft, or no chat screen at all. A refusal belongs to the chat
    // it was said in: its Try again sends the box, which pressed here would write the sentence into
    // this chat.
    if (!projectId || !chatId) {
      setChat(null);
      setError(null);
      setRefused(null);
      setMissing(false);
      setArrived(null);
      return undefined;
    }
    // Madde 88's birth guard: the door's answer already drew the chat the draft was born as.
    if (held.current?.id === chatId) return undefined;
    let cancelled = false;
    setChat(null);
    setError(null);
    setRefused(null);
    setMissing(false);
    setArrived(null);
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

  // The chat on screen has a turn running: listen to it. Its own record's turn only -- for the one
  // render after the address moves, the record held is still the last chat's.
  const running = chat && chat.id === chatId ? (chat.turn?.id ?? null) : null;
  useEffect(() => {
    if (!running) return undefined;
    follow(projectId, chatId, false, running);
    const key = `${chatKey(projectId, chatId)}/${running}`;
    return () => {
      const listener = listeners.current.get(key);
      if (listener && !listener.own) letGo(listener);
    };
  }, [projectId, chatId, running]);

  // Coming back to the tab -- switched to, or clicked into beside another -- reads the chat once,
  // unless a listener already follows a turn in it: a turn another tab started is then drawn, and
  // the effect above listens to it. One read per return, nothing asked while away.
  useEffect(() => {
    if (!projectId || !chatId) return undefined;
    const key = chatKey(projectId, chatId);
    let reading = false;
    // Something newer than a look owns the screen: a listener following a turn here, or a sentence
    // on its way, whose answer is the newer record.
    const busy = () =>
      onItsWay.current !== null ||
      [...listeners.current.values()].some((l) => chatKey(l.project, l.id) === key);
    const back = () => {
      if (document.visibilityState === "hidden" || reading || busy()) return;
      if (held.current?.id !== chatId) return;
      reading = true;
      getJson(`/api/projects/${projectId}/chats/${chatId}`)
        // Asked again as it lands: a send may have been answered while the look was out.
        .then((record) => key === here.current && !busy() && setChat(record))
        // Nothing is said of a look that failed: the screen keeps what it had, as it was.
        .catch(() => {})
        .finally(() => {
          reading = false;
        });
    };
    window.addEventListener("focus", back);
    document.addEventListener("visibilitychange", back);
    return () => {
      window.removeEventListener("focus", back);
      document.removeEventListener("visibilitychange", back);
    };
  }, [projectId, chatId]);

  // Nothing outlives the hook: a turn still asked about is asked about for nobody.
  useEffect(() => () => listeners.current.clear(), []);

  // A sentence, or an edit of one (`from`, Madde 195). The skill travels with the message rather
  // than being read off the chat: what governed a turn is settled when the turn is sent. So does
  // the mode, which the browser holds and the server keeps nowhere (Madde 467).
  const send = useCallback(
    async (text, skill = "", mode, from = null) => {
      const key = here.current;
      const at = new Date().toISOString();
      setPending({ key, text, at, from });
      setRefused(null);
      setError(null);
      setArrived(null);
      try {
        const answer = await postJson(`/api/projects/${projectId}/messages`, {
          chat: chatId ?? "",
          text,
          skill,
          mode,
          // An ordinary reply carries no such field, and the server tells the two apart by its
          // absence rather than by a number meaning nothing.
          ...(from === null ? {} : { from }),
        });
        took(projectId, answer, key, at);
        // Madde 88: a chat this screen was not on has just been born, and the address follows it.
        if (key === here.current && answer.id !== chatId) born.current?.(answer.id);
      } catch (failure) {
        // Refused, or the server never answered: nothing was written, so the transcript is the
        // server's as it was -- the bubble alone goes, and a Stop pressed for it with it. A turn
        // holding the chat (409) is followed, and its answer is the chat as that turn holds it: a
        // tab that was out of date draws the question it never saw, under the wait. The box keeps
        // the sentence for when the turn ends.
        if (early.current === at) early.current = null;
        if (key === here.current) {
          setRefused(failure.message);
          const { error: _words, ...stands } = failure.body ?? {};
          if (stands.messages && chatId) {
            setChat((current) => (current?.id === chatId ? stands : current));
          }
        }
        refusedReply.current = from === null;
        // Thrown on: the field holding the only copy of the sentence has to know to keep it.
        throw failure;
      } finally {
        setPending((current) => (current?.at === at ? null : current));
      }
    },
    [projectId, chatId],
  );

  // Try again, through its own door (Madde 462): what it does is the chat's status, and the
  // server's to decide -- reconnect to a running turn, answer a question nobody answered or a
  // failed answer, or nothing. The question is never written again; the mode goes with it, as with
  // a send (Madde 467).
  const retry = useCallback(
    async (mode) => {
      if (!chatId) return;
      const key = here.current;
      setRefused(null);
      setError(null);
      setArrived(null);
      try {
        took(projectId, await postJson(`/api/projects/${projectId}/chats/${chatId}/retry`, { mode }), key);
      } catch (failure) {
        if (key === here.current) setRefused(failure.message);
        refusedReply.current = false;
      }
    },
    [projectId, chatId],
  );

  // Which version of the conversation is open (Madde 195). The record is read back rather than
  // guessed at: the server keeps which line is open.
  const version = useCallback(
    async (wanted) => {
      try {
        await postJson(`/api/projects/${projectId}/chats/${chatId}/version`, { version: wanted });
        setChat(await getJson(`/api/projects/${projectId}/chats/${chatId}`));
        // Another line is drawn, and nothing on it has just arrived.
        setArrived(null);
      } catch (failure) {
        setError(failure.message);
      }
    },
    [projectId, chatId],
  );

  // Continue here (Madde 352): the server trims, and the record is read back the way a version is.
  // A refusal met while the chat was full said it was full, which stops being true here.
  const trim = useCallback(async () => {
    try {
      await postJson(`/api/projects/${projectId}/chats/${chatId}/trim`);
      setChat(await getJson(`/api/projects/${projectId}/chats/${chatId}`));
      setRefused(null);
    } catch (failure) {
      setError(failure.message);
    }
  }, [projectId, chatId]);

  // Stop names the turn it was pressed for: one landing after it reaches nothing (Madde 462). What
  // it amounts to is heard on the events door, so this door's answer is not read. Pressed while the
  // sentence is still on its way, it is kept for that send, and sent once the door names the turn.
  const stop = useCallback(async () => {
    const current = held.current;
    if (!current?.turn) {
      early.current = onItsWay.current;
      return;
    }
    await postJson(`/api/projects/${projectId}/chats/${current.id}/stop`, {
      turn: current.turn.id,
    }).catch(() => {});
  }, [projectId]);

  // And the answer names the question too, within its turn.
  const answer = useCallback(
    async (allowed, reason) => {
      const current = held.current;
      const asked = current?.turn?.permission;
      if (!asked) return;
      setDecided(`${current.turn.id}:${asked.wait}`);
      await postJson(`/api/projects/${projectId}/chats/${current.id}/permission`, {
        turn: current.turn.id,
        wait: asked.wait,
        ...(allowed ? { allowed: true } : { allowed: false, reason }),
      })
        // Not left, so the question still stands: its card comes back to be answered again.
        .catch(() => setDecided(null));
    },
    [projectId],
  );

  // The sentence on its way stands in the transcript it was sent from: an edit where the old
  // message stood (Madde 195), a reply at the end. A draft draws none (withSentence).
  const sending = pending && pending.key === here.current ? pending : null;
  onItsWay.current = sending?.at ?? null;
  const shown = sending ? withSentence(chat, sending) : chat;
  const turn = chat && chat.id === chatId ? chat.turn : null;
  const asked = turn?.permission;
  return {
    chat: shown,
    error,
    refused,
    missing,
    // The wait and its Stop stand from the moment the sentence leaves.
    thinking: Boolean(turn || sending),
    // When it left: the wait's time where no bubble stands to read it from -- the draft.
    sentAt: sending?.at ?? null,
    arrived,
    creatingFile: Boolean(turn?.creating),
    createdFiles: turn?.files ?? [],
    streamingCalls: turn?.calls ?? [],
    progress: turn?.progress ?? null,
    // The turn says `arguments` and this says `args` -- a language rule rather than a rename,
    // since `arguments` cannot be destructured as a prop inside a module.
    permission:
      asked && `${turn.id}:${asked.wait}` !== decided ? { tool: asked.tool, args: asked.arguments } : null,
    send,
    stop,
    answer,
    version,
    trim,
    // The transient card's Try again. A refused reply is the composer's to send: its sentence went
    // back there. Anything else -- a turn that broke, a refused Try again or edit -- asks the chat's
    // own door.
    retry: (sendBox, mode) => (refused && refusedReply.current ? sendBox() : retry(mode)),
    // The recorded failed answer's Try again (Madde 440): never the composer -- what it holds is the
    // next thing to say.
    answerAgain: retry,
  };
}

function withSentence(chat, { text, at, from }) {
  // A draft has no record to stand it in, and draws none: the screen shows the draft until the
  // door's answer names the newborn, and that answer is its record, under the name the server gave.
  if (!chat) return chat;
  const before = from === null ? chat.messages : chat.messages.slice(0, from);
  return { ...chat, messages: [...before, { role: "user", at, text }] };
}
