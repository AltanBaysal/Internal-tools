import { clockTime } from "../../shared/time.js";
import Composer from "./Composer.jsx";

export default function ChatScreen({ project, chat, error, missing, thinking, onBack, onSend }) {
  if (!chat) {
    // Nothing is drawn while the chat is still on its way; only a real absence speaks up.
    return missing ? (
      <div className="screen">
        <div className="screen__column">
          <button type="button" className="back" onClick={onBack}>
            ← back
          </button>
          <p className="screen__missing">That chat does not exist.</p>
        </div>
      </div>
    ) : null;
  }

  return (
    <div className="chat">
      <header className="chat__header">
        <button type="button" className="back back--inline" onClick={onBack}>
          ← {project ? project.name : "back"}
        </button>
        <span className="chat__slash">/</span>
        <span className="chat__title">{chat.title}</span>
      </header>

      <div className="chat__scroll">
        <div className="chat__column">
          {chat.messages.map((message, index) => (
            <div
              key={`${message.at}-${index}`}
              className={message.role === "user" ? "msg msg--user" : "msg msg--ai"}
            >
              <div className="msg__label">
                {message.role === "user" ? "You" : "Mira"} · {clockTime(message.at)}
              </div>
              <div className={message.role === "user" ? "msg__bubble" : "msg__text"}>
                {message.text}
              </div>
            </div>
          ))}
          {thinking ? (
            // Three blinking dots and nothing else: the design refuses a fake partial answer.
            <div className="msg msg--ai" data-testid="thinking">
              <div className="msg__label">Mira</div>
              <div className="dots">
                <span className="dots__dot" />
                <span className="dots__dot" />
                <span className="dots__dot" />
              </div>
            </div>
          ) : null}

          {error ? <p className="chat__error">{error}</p> : null}
        </div>
      </div>

      <div className="chat__composer">
        <Composer
          rows={2}
          placeholder="Reply..."
          note="save the answer as a file"
          action="Send"
          onSubmit={onSend}
        />
      </div>
    </div>
  );
}
