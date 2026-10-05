import { useEffect, useState } from "react";

import {
  askQuestion,
  listChats,
  newChat,
  openChat,
  stopAgent,
  workingChats,
} from "../../shared/api.js";

// How often the server is asked while an agent works. A step is a round with the model, seconds
// long, so once a second keeps the live line live; while nothing works nothing is asked.
const POLL_MS = 1000;

// What a visit remembers per project: which chat is open, whether the list is, and each chat's
// draft. Memory only, like the rest of the screen's memory (SidePanel's open panel, the gallery's
// list): a reload opens the newest chat, and a draft not sent goes with it.
const KEPT = new Map();

function kept(project) {
  if (!KEPT.has(project)) KEPT.set(project, { open: null, list: false, drafts: {} });
  return KEPT.get(project);
}

// The agent's chats in one project: the open one as the server last told it, which chats' agents
// work, the list, the box, and the presses. The agent runs on the server (madde 420), so the screen
// only asks -- and asks again only while something works.
export function useAgentChat(project) {
  const memory = kept(project);
  const [chat, setChat] = useState(null);
  const [working, setWorking] = useState([]);
  const [list, setList] = useState(memory.list);
  const [rows, setRows] = useState(null);
  const [draft, setDraft] = useState("");
  // The question on its way: drawn at once, before the server has it.
  const [pending, setPending] = useState(null);
  // { text, question, poll }: the request's own words, the question it carried if it was one, and
  // whether it was a look at the server -- which the next good look takes back.
  const [failure, setFailure] = useState(null);
  const id = chat ? chat.id : null;
  const busy = id !== null && (working.includes(id) || pending !== null);

  const fail = (err, question = null) => setFailure({ text: err.message, question });

  // The chat the server sent is the open one now, with its own draft.
  function take(fresh) {
    memory.open = fresh.id;
    memory.list = false;
    setList(false);
    setChat(fresh);
    setDraft(memory.drafts[fresh.id] || "");
    setFailure(null);
  }

  // Who works is asked before the chat is read: the server writes an answer and takes the chat off
  // the working list in one hold, so a chat read after "not working" carries its outcome.
  async function show(chatId) {
    try {
      const ids = await workingChats(project);
      const fresh = await openChat(project, chatId);
      setWorking(ids);
      take(fresh);
    } catch (err) {
      fail(err);
    }
  }

  // Nothing remembered: the newest chat, or the empty one waiting when nothing has been asked.
  async function first() {
    try {
      const found = await listChats(project);
      if (found.length) await show(found[0].id);
      else take(await newChat(project));
    } catch (err) {
      fail(err);
    }
  }

  const reopen = () => (memory.open === null ? first() : show(memory.open));

  async function openList() {
    memory.list = true;
    setList(true);
    setRows(null);
    setFailure(null);
    try {
      setRows(await listChats(project));
    } catch (err) {
      fail(err);
    }
  }

  useEffect(() => {
    if (memory.list) openList();
    else reopen();
  }, [project]);

  // While an agent works the server is looked at again: who works, then -- while the conversation is
  // on screen and its chat works or has just stopped -- the chat itself. Each new working list arms
  // the next look, so the loop runs for as long as the list is not empty.
  useEffect(() => {
    if (!working.length) return undefined;
    let gone = false;
    const timer = setTimeout(async () => {
      try {
        const ids = await workingChats(project);
        const read = !list && id !== null && (working.includes(id) || ids.includes(id));
        const fresh = read ? await openChat(project, id) : null;
        if (gone) return;
        if (fresh) setChat(fresh);
        setWorking(ids);
        setFailure((shown) => (shown && shown.poll ? null : shown));
      } catch (err) {
        if (gone) return;
        setFailure({ text: err.message, poll: true });
        // One look that did not arrive must not end the loop: the same list, new, arms the next.
        setWorking((ids) => [...ids]);
      }
    }, POLL_MS);
    // A look still in the air when the chat or the view changes is dropped: it would bring back a
    // chat that is no longer the open one.
    return () => {
      gone = true;
      clearTimeout(timer);
    };
  }, [project, working, list, id]);

  function write(text) {
    memory.drafts[id] = text;
    setDraft(text);
  }

  async function send() {
    const text = draft.trim();
    if (!text) return;
    const asked = id;
    write("");
    setPending(text);
    setFailure(null);
    try {
      const fresh = await askQuestion(project, asked, text);
      setWorking((ids) => (ids.includes(asked) ? ids : [...ids, asked]));
      setChat(fresh);
    } catch (err) {
      // The server never took it: the question stays on screen over the card.
      fail(err, text);
    } finally {
      setPending(null);
    }
  }

  // Nothing to stop while the question is on its way: no agent has started.
  async function stop() {
    if (pending !== null) return;
    const stopped = id;
    try {
      const fresh = await stopAgent(project, stopped);
      setWorking((ids) => ids.filter((one) => one !== stopped));
      setChat(fresh);
      setFailure(null);
    } catch (err) {
      fail(err);
    }
  }

  async function startNew() {
    try {
      take(await newChat(project));
    } catch (err) {
      fail(err);
    }
  }

  // Closing the list reads the open chat again: its agent may have finished meanwhile.
  const toggleList = () => (list ? reopen() : openList());

  return { chat, working, list, rows, open: memory.open, draft, pending, failure, busy,
           write, send, stop, startNew, toggleList, show };
}
