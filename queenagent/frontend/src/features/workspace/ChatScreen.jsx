import { useEffect, useRef, useState } from "react";

import { clockTime } from "../../shared/time.js";
import Composer from "./Composer.jsx";
import FileRail from "./FileRail.jsx";
import Markdown from "./Markdown.jsx";
import ModelPicker from "./ModelPicker.jsx";
import Skeleton from "./Skeleton.jsx";
import SkillPicker from "./SkillPicker.jsx";

const CHIP_LENGTH = 3;
// A reader further from the bottom than this is reading, not watching, and the answer must not pull
// them away from it. The design's own number.
const STICK_WITHIN = 220;

// A message remembers names, not rows, so the chip's letters are read off the name here -- the same
// three the server puts on a listed file.
function extensionOf(name) {
  const dot = name.lastIndexOf(".");
  return name.slice(dot + 1, dot + 1 + CHIP_LENGTH).toLowerCase();
}

// The skeleton of the card about to be born: an empty badge slot where the chip will go, and no
// name -- the model's wish is not the name until it has been cleaned and a clash resolved.
function CreatingFile() {
  return (
    <div className="creating">
      <span className="creating__chip" />
      <span>creating file…</span>
    </div>
  );
}

// The primary way into a file: the card is a door rather than a receipt. Which one is open is the
// caller's answer, and telling someone to open what is already open would be the wrong sentence --
// so the hint drops to "open" and the arrow, having nowhere to point, drops with it.
function FileCard({ name, selected, onOpen }) {
  return (
    <button
      type="button"
      className={selected ? "file-card file-card--selected" : "file-card"}
      onClick={() => onOpen?.(name)}
    >
      <span className="file-chip">{extensionOf(name)}</span>
      <span className="file-card__name">{name}</span>
      <span className="file-card__saved">✓ saved to project</span>
      <span className="file-card__hint">{selected ? "open" : "Open ›"}</span>
    </button>
  );
}

export default function ChatScreen({
  project,
  chat,
  files = [],
  loadingFiles,
  filesError,
  reading,
  deleting,
  railCollapsed,
  onToggleRail,
  error,
  refused,
  missing,
  thinking,
  streamingText,
  creatingFile,
  createdFiles = [],
  picker,
  onPicker,
  onBack,
  onSend,
  onModelChange,
  onSkillChange,
  onRetry,
}) {
  // Stamped once, when the wait starts. There is nothing on the server to read it from yet, and the
  // label answers "when was this asked for" -- an answer that stops being new the moment it is given.
  const [askedAt, setAskedAt] = useState(null);
  useEffect(() => {
    setAskedAt(thinking ? (at) => at ?? new Date().toISOString() : null);
  }, [thinking]);

  const scroll = useRef(null);
  const toBottom = () => {
    const list = scroll.current;
    if (list) list.scrollTop = list.scrollHeight;
  };

  // A message the user just sent is theirs to see, so the list always jumps.
  useEffect(toBottom, [chat?.messages.length]);

  // An answer is different: it follows the reader rather than the other way round.
  useEffect(() => {
    const list = scroll.current;
    if (!list) return;
    if (list.scrollHeight - list.scrollTop - list.clientHeight <= STICK_WITHIN) toBottom();
  }, [streamingText]);

  if (!chat) {
    return (
      <div className="screen">
        <div className="screen__column">
          <button type="button" className="back" onClick={onBack}>
            ← back
          </button>
          {missing ? (
            <p className="screen__missing">That chat does not exist.</p>
          ) : (
            <Skeleton rows={2} variant="message" />
          )}
        </div>
      </div>
    );
  }

  // A message remembers what it produced and is never rewritten -- that sentence was true when it
  // was said. The card claims something else, that the file exists and is called this, so it is
  // drawn from the crossing of the two: once the file is deleted it simply stops having a card.
  const onDisk = new Set(files.map((file) => file.name));
  const waitingLabel = askedAt ? `QueenAgent · ${clockTime(askedAt)}` : "QueenAgent";

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

        <div className="chat__scroll" ref={scroll}>
          <div className="chat__column">
            {chat.messages.map((message, index) => (
              <div
                key={`${message.at}-${index}`}
                className={message.role === "user" ? "msg msg--user" : "msg msg--ai"}
              >
                {/* No name over the user's own bubble: the design draws one but never says where it
                    comes from, and the bubble sitting on the right already says who wrote it. */}
                <div className="msg__label">
                  {message.role === "user"
                    ? clockTime(message.at)
                    : `QueenAgent · ${clockTime(message.at)}`}
                </div>
                {/* What the user typed stays what they typed -- `**test**` keeps its asterisks. */}
                {message.role === "user" ? (
                  <div className="msg__bubble">{message.text}</div>
                ) : (
                  <div className="msg__text">
                    <Markdown text={message.text} />
                  </div>
                )}
                {/* One turn can produce more than one file, so the card is not a single slot. */}
                {message.files?.some((name) => onDisk.has(name)) ? (
                  <div className="file-cards">
                    {message.files
                      .filter((name) => onDisk.has(name))
                      .map((name) => (
                        <FileCard
                          key={name}
                          name={name}
                          selected={name === reading?.name}
                          onOpen={reading?.open}
                        />
                      ))}
                  </div>
                ) : null}
              </div>
            ))}
            {streamingText ? (
              <div className="msg msg--ai" data-testid="streaming">
                <div className="msg__label">{waitingLabel}</div>
                <div className="msg__text">
                  {/* Formatted from the first frame: raw first and formatted afterwards would read
                      as a flicker rather than a stream. */}
                  <Markdown text={streamingText} caret />
                </div>
                {creatingFile ? <CreatingFile /> : null}
              </div>
            ) : null}

            {thinking && !streamingText ? (
              // Three blinking dots and nothing else, and only until the first piece lands: the
              // design refuses a fake partial answer.
              <div className="msg msg--ai msg--waiting" data-testid="thinking">
                <div className="msg__label">{waitingLabel}</div>
                <div className="dots">
                  <span className="dots__dot" />
                  <span className="dots__dot" />
                  <span className="dots__dot" />
                </div>
                {creatingFile ? <CreatingFile /> : null}
              </div>
            ) : null}

            {/* Born during this answer, so they are drawn from the stream. Once the server's record
                arrives it carries the same names and these are dropped. */}
            {createdFiles.length ? (
              <div className="file-cards">
                {createdFiles.map((name) => (
                  <FileCard
                          key={name}
                          name={name}
                          selected={name === reading?.name}
                          onOpen={reading?.open}
                        />
                ))}
              </div>
            ) : null}

            {/* A message that was never sent has no answer to try again for -- it has a sentence to
                write again, and that sentence is already back in the composer. */}
            {refused ? <p className="refused">{refused}</p> : null}

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
            action="Send"
            /* karar 1's order: Skills · model · Send. Both choices belong to the chat on the
               server, so the screen asks and App sends; which picker is open is App's too, because
               Escape closes them in a fixed order. */
            foot={
              <>
                <SkillPicker
                  skill={chat.skill}
                  open={picker === "skills"}
                  onToggle={() => onPicker?.("skills")}
                  onChange={onSkillChange}
                />
                <ModelPicker
                  model={chat.model}
                  open={picker === "model"}
                  onToggle={() => onPicker?.("model")}
                  onChange={onModelChange}
                />
              </>
            }
            onSubmit={onSend}
          />
        </div>
      </div>

      <FileRail
        files={files}
        loading={loadingFiles}
        error={filesError}
        reading={reading}
        collapsed={railCollapsed}
        onToggle={onToggleRail}
      />
    </div>
  );
}
