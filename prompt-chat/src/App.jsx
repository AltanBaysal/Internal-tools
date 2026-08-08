import { useEffect, useRef, useState } from "react";
import Message from "./Message.jsx";
import { sendChat } from "./api.js";

const DEFAULT_MODEL = "grok-4.3";

// The key and the model name outlive the page; the conversation deliberately does not.
function usePersisted(storageKey, fallback) {
  const [value, setValue] = useState(() => localStorage.getItem(storageKey) ?? fallback);
  useEffect(() => {
    localStorage.setItem(storageKey, value);
  }, [storageKey, value]);
  return [value, setValue];
}

export default function App() {
  const [apiKey, setApiKey] = usePersisted("xai_key", "");
  const [model, setModel] = usePersisted("xai_model", DEFAULT_MODEL);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const chatRef = useRef(null);

  useEffect(() => {
    const el = chatRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  async function send() {
    const text = draft.trim();
    if (!text || pending) return;

    // The request carries the new message too, so the array is built first and used for both.
    const asked = [...messages, { role: "user", content: text }];
    setMessages(asked);
    setDraft("");
    setPending(true);
    try {
      const reply = await sendChat({ key: apiKey, model, messages: asked });
      setMessages([...asked, { role: "assistant", content: reply }]);
    } catch (err) {
      // Covers a non-200 response and a request that never left: network, CORS, unparsable body.
      setMessages([...asked, { role: "error", content: err.message }]);
    }
    setPending(false);
  }

  return (
    <div className="app">
      <header>
        <input
          type="password"
          placeholder="xAI API anahtarı"
          autoComplete="off"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
        />
        <input
          className="model"
          placeholder="model"
          autoComplete="off"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        />
      </header>

      <main className="chat" ref={chatRef}>
        {messages.map((m, i) => (
          <Message key={i} role={m.role} content={m.content} />
        ))}
      </main>

      <footer>
        <textarea
          placeholder="Mesaj yaz — Enter gönderir, Shift+Enter alt satıra geçer"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
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
    </div>
  );
}
