import { useEffect, useRef, useState } from "react";
import Sidebar from "./Sidebar.jsx";
import Message from "./Message.jsx";
import { sendChat } from "./api.js";
import { usePersisted, usePersistedJson } from "./usePersisted.js";
import { createChat, deleteChat, replaceMessages, setDraft } from "./storage.js";

const DEFAULT_MODEL = "grok-4.3";
const EMPTY = { id: null, messages: [], draft: "" };

export default function App() {
  const [apiKey, setApiKey] = usePersisted("xai_key", "");
  const [model, setModel] = usePersisted("xai_model", DEFAULT_MODEL);
  const [chats, setChats] = usePersistedJson("chats", []);
  const [activeId, setActiveId] = usePersistedJson("active_chat", null);
  const [pending, setPending] = useState(false);
  const chatRef = useRef(null);

  // There is never a moment without an open chat: not on a first visit, and not after the open one
  // is deleted. Both cases are repaired here rather than guarded at every use.
  useEffect(() => {
    if (chats.length === 0) {
      const { chats: withOne, id } = createChat(chats);
      setChats(withOne);
      setActiveId(id);
    } else if (!chats.some((c) => c.id === activeId)) {
      setActiveId(chats[0].id);
    }
  }, [chats, activeId, setChats, setActiveId]);

  const active = chats.find((c) => c.id === activeId) ?? chats[0] ?? EMPTY;

  useEffect(() => {
    const el = chatRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [active.messages]);

  async function send() {
    const text = active.draft.trim();
    if (!text || pending) return;

    // The reply belongs to the chat that asked for it, so its id is captured before the await: the
    // user may well be looking at a different chat by the time the answer lands.
    const askedIn = active.id;
    const asked = [...active.messages, { role: "user", content: text }];

    setChats((cs) => setDraft(replaceMessages(cs, askedIn, asked), askedIn, ""));
    setPending(true);
    try {
      const reply = await sendChat({ key: apiKey, model, messages: asked });
      setChats((cs) =>
        replaceMessages(cs, askedIn, [...asked, { role: "assistant", content: reply }])
      );
    } catch (err) {
      // Covers a non-200 response and a request that never left: network, CORS, unparsable body.
      setChats((cs) =>
        replaceMessages(cs, askedIn, [...asked, { role: "error", content: err.message }])
      );
    }
    setPending(false);
  }

  function newChat() {
    const { chats: next, id } = createChat(chats);
    setChats(next);
    setActiveId(id);
  }

  return (
    <div className="layout">
      <Sidebar
        chats={chats}
        activeId={active.id}
        onSelect={setActiveId}
        onNew={newChat}
        onDelete={(id) => setChats(deleteChat(chats, id))}
        apiKey={apiKey}
        onApiKey={setApiKey}
        model={model}
        onModel={setModel}
      />

      <main className="main">
        <div className="chat" ref={chatRef}>
          {active.messages.map((m, i) => (
            <Message key={i} role={m.role} content={m.content} />
          ))}
        </div>

        <footer>
          <textarea
            placeholder="Mesaj yaz — Enter gönderir, Shift+Enter alt satıra geçer"
            value={active.draft}
            onChange={(e) => {
              const value = e.target.value;
              setChats((cs) => setDraft(cs, active.id, value));
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
          />
          <button onClick={send} disabled={pending}>
            {pending ? "…" : "Gönder"}
          </button>
        </footer>
      </main>
    </div>
  );
}
