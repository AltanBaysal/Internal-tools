import { clockTime } from "../../shared/time.js";
import Composer from "./Composer.jsx";

export default function ChatScreen({
  project,
  chat,
  error,
  missing,
  thinking,
  streamingText,
  onBack,
  onSend,
  onRetry,
}) {
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
          {streamingText ? (
            <div className="msg msg--ai" data-testid="streaming">
              <div className="msg__label">Mira</div>
              <div className="msg__text">{streamingText}</div>
            </div>
          ) : null}

          {thinking && !streamingText ? (
            // Three blinking dots and nothing else, and only until the first piece lands: the
            // design refuses a fake partial answer.
            <div className="msg msg--ai" data-testid="thinking">
              <div className="msg__label">Mira</div>
              <div className="dots">
                <span className="dots__dot" />
                <span className="dots__dot" />
                <span className="dots__dot" />
              </div>
            </div>
          ) : null}

          {error ? (
            <div className="failure">
              <div className="failure__body">
                {/* The design also said "The connection dropped." That is a guessed cause -- a bad
                    key and a wrong model name raise this same card -- so the card states what
                    happened and the server's own words sit underneath. */}
                <span className="failure__line">Couldn&apos;t get a response.</span>
                <span className="failure__detail">{error}</span>
              </div>
              {onRetry ? (
                <button type="button" className="failure__retry" onClick={onRetry}>
                  Try again
                </button>
              ) : null}
            </div>
          ) : null}
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
