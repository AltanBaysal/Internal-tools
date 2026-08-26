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

// What the turn did before it spoke. Above the answer, because that is the order it happened in.
//
// No accent: the accent marks the primary action, and a step that has already happened is a record
// rather than something to press. The separator before a target is drawn in CSS rather than as an
// element -- a bullet standing where a missing name would have been announces something that is not
// there, and listing a directory genuinely has no file.
function ToolCalls({ calls }) {
  if (!calls?.length) return null;
  return (
    <div className="tool-calls">
      {calls.map((call, index) => (
        <div className="tool-call" key={`${call.tool}-${call.target}-${index}`}>
          <span className="tool-call__name">{call.tool}</span>
          {call.target ? <span className="tool-call__target">{call.target}</span> : null}
        </div>
      ))}
    </div>
  );
}

// A thousand and up loses its exact digits. The number answers "was this turn expensive", and four
// significant figures do not help with that question.
function shorten(count) {
  return count < 1000 ? String(count) : `${(count / 1000).toFixed(1)}k`;
}

// What the turn cost, under the answer that cost it -- last, because the cards above are what the
// answer produced and this is a note about the answer itself.
//
// One number out of the three the record keeps. The other two say what the cache saved, and that is
// a question about how requests are built rather than something a reader of the chat is asking.
// Nothing is drawn at zero: an answer from before this existed reads back as zero, and a line under
// it would claim a measurement nobody took.
function TokenCount({ usage }) {
  const spent = (usage?.sent ?? 0) + (usage?.answered ?? 0);
  if (!spent) return null;
  return <div className="token-count">{shorten(spent)} tokens</div>;
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
  railFoldedByWidth,
  railWidth,
  onResizeRail,
  onToggleRail,
  error,
  refused,
  missing,
  thinking,
  streamingText,
  creatingFile,
  createdFiles = [],
  streamingCalls = [],
  picker,
  onPicker,
  onBack,
  onSend,
  onModelChange,
  onSkillChange,
  onStop,
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
    /* A narrow shell hides the conversation while a file is open, and CSS cannot look at a later
       sibling to find that out. The screen knows already, so it says so. */
    <div className={reading?.name ? "chat-layout chat-layout--reading" : "chat-layout"}>
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
                className={
                  message.role === "user"
                    ? "msg msg--user"
                    : /* An answer the user cut short says so: half a sentence with no mark reads
                         as a model that finished on one. */
                      `msg msg--ai${message.stopped ? " msg--stopped" : ""}`
                }
              >
                {/* No name over the user's own bubble: the design draws one but never says where it
                    comes from, and the bubble sitting on the right already says who wrote it. */}
                <div className="msg__label">
                  {message.role === "user"
                    ? clockTime(message.at)
                    : `QueenAgent · ${clockTime(message.at)}`}
                </div>
                {/* Only an answer has steps; a question is what was typed and nothing else. */}
                {message.role === "ai" ? <ToolCalls calls={message.calls} /> : null}
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
                {/* Only under an answer: spending is what an answer does, and a number under the
                    question would read as its price. */}
                {message.role === "ai" ? <TokenCount usage={message.usage} /> : null}
              </div>
            ))}
            {streamingText ? (
              <div className="msg msg--ai" data-testid="streaming">
                <div className="msg__label">{waitingLabel}</div>
                <ToolCalls calls={streamingCalls} />
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
                <ToolCalls calls={streamingCalls} />
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
                  {/* The server's own words and nothing beside them. There used to be a way out
                      offered here -- a screen for typing a missing key -- and with the key coming
                      from the environment there is no longer anywhere for it to lead. */}
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
                {/* Only while there is something to stop. No accent -- the accent marks the primary
                    action, and that is Send; no red either, because cutting your own answer short
                    is not destruction. */}
                {thinking ? (
                  <button type="button" className="stop" onClick={onStop}>
                    Stop
                  </button>
                ) : null}
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
        deleting={deleting}
        collapsed={railCollapsed}
        foldedByWidth={railFoldedByWidth}
        width={railWidth}
        onResize={onResizeRail}
        onToggle={onToggleRail}
      />
    </div>
  );
}
