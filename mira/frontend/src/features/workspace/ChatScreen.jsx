import { clockTime } from "../../shared/time.js";
import Composer from "./Composer.jsx";
import FileRail from "./FileRail.jsx";

const CHIP_LENGTH = 3;

// A message remembers names, not rows, so the chip's letters are read off the name here -- the same
// three the server puts on a listed file.
function extensionOf(name) {
  const dot = name.lastIndexOf(".");
  return name.slice(dot + 1, dot + 1 + CHIP_LENGTH).toLowerCase();
}

function FileCard({ name }) {
  return (
    <div className="file-card">
      <span className="file-chip">{extensionOf(name)}</span>
      <span className="file-card__name">{name}</span>
      <span className="file-card__saved">✓ saved to project</span>
    </div>
  );
}

export default function ChatScreen({
  project,
  chat,
  files = [],
  reading,
  error,
  missing,
  thinking,
  streamingText,
  creatingFile,
  createdFiles = [],
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
    <div className="chat-layout">
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
                {/* One turn can produce more than one file, so the card is not a single slot. */}
                {message.files?.length ? (
                  <div className="file-cards">
                    {message.files.map((name) => (
                      <FileCard key={name} name={name} />
                    ))}
                  </div>
                ) : null}
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

            {/* Born during this answer, so they are drawn from the stream. Once the server's record
                arrives it carries the same names and these are dropped. */}
            {createdFiles.length ? (
              <div className="file-cards">
                {createdFiles.map((name) => (
                  <FileCard key={name} name={name} />
                ))}
              </div>
            ) : null}

            {creatingFile ? (
              // Nameless on purpose: the model's wish is not the name until it has been cleaned and
              // a clash resolved, and the tool has not run yet.
              <div className="creating">creating file…</div>
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

      <FileRail files={files} reading={reading} />
    </div>
  );
}
