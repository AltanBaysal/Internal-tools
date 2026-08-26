import { useEffect, useRef, useState } from "react";

import { clockTime } from "../../shared/time.js";
import Composer from "./Composer.jsx";
import FileRail from "./FileRail.jsx";
import Markdown from "./Markdown.jsx";
import ModelLabel from "./ModelLabel.jsx";
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

// Madde 78's shape: the step's mark, the tool, and its subject in brackets. The brackets carry the
// file rather than a separator element -- a call about no file in particular really has none, and a
// mark standing where a name would have been announces something that is not there. Written as one
// string so the text reads as a whole rather than as neighbouring fragments.
function headOf(call) {
  return `⏺ ${call.tool}${call.target ? `(${call.target})` : ""}`;
}

// What the turn did before it spoke, behind one door. Above the answer, because that is the order it
// happened in.
//
// Shut, the door says which step is happening while the turn runs and how many there were once it is
// over: waiting, a reader wants to know what is going on; afterwards, what it did. Open, the handle
// stops repeating the last call -- that call is on a card right below it.
//
// A card you can press does something; a card you cannot is a record. The handle opens the list, so
// it is a button; a step that already happened opens nothing, so it is not. That is Madde 78's rule,
// and the only part of it this drops is the unspoken half -- that a record has to be faint.
function ToolCalls({ calls, running }) {
  // Per message and per box: the loop draws one of these for each, so a new answer is born shut and
  // a reload shuts them all. A way of looking rather than a fact about the chat, which is why it
  // reaches neither disk nor browser storage.
  const [open, setOpen] = useState(false);
  if (!calls?.length) return null;
  const summary = `⏺ ${calls.length} step${calls.length === 1 ? "" : "s"}`;
  return (
    <div className="tool-calls">
      <button
        type="button"
        className="tool-calls__handle"
        aria-expanded={open}
        onClick={() => setOpen((shown) => !shown)}
      >
        <span className="tool-calls__summary">
          {running && !open ? headOf(calls[calls.length - 1]) : summary}
        </span>
        <span className="tool-calls__chevron">{open ? "⌃" : "⌄"}</span>
      </button>
      {open
        ? calls.map((call, index) => (
            <div className="tool-call" key={`${call.tool}-${call.target}-${index}`}>
              <span className="tool-call__head">{headOf(call)}</span>
              {/* Absent on anything recorded before outcomes existed, and an empty half would
                  claim a result nobody wrote down. */}
              {call.outcome ? <span className="tool-call__outcome">{call.outcome}</span> : null}
            </div>
          ))
        : null}
    </div>
  );
}

// A thousand and up loses its exact digits. The number answers "was this turn expensive", and four
// significant figures do not help with that question.
function shorten(count) {
  return count < 1000 ? String(count) : `${(count / 1000).toFixed(1)}k`;
}

// The note that closes a message: when it was said, and -- for an answer that was measured -- what
// it cost. Under the message rather than over it, because a note about a thing is read after it.
// One line rather than two at the two ends, and no name in it: the sidebar carries the name, and
// which side a message sits on says who wrote it.
//
// One number out of the three the record keeps. The other two say what the cache saved, and that is
// a question about how requests are built rather than something a reader of the chat is asking. The
// count drops at zero -- an answer from before this existed reads back as zero, and a number there
// would claim a measurement nobody took. The time never drops: it was said at a time either way.
function Stamp({ at, usage }) {
  // The wait is stamped by an effect, so the first draw of a pending box has no time yet. Nothing
  // rather than an empty line.
  if (!at) return null;
  const spent = (usage?.sent ?? 0) + (usage?.answered ?? 0);
  const when = clockTime(at);
  return <div className="msg__stamp">{spent ? `${when} · ${shorten(spent)} tokens` : when}</div>;
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
  skill,
  skillsOpen,
  onToggleSkills,
  onBack,
  onSend,
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
                {/* Only an answer has steps; a question is what was typed and nothing else. */}
                {message.role === "ai" ? <ToolCalls calls={message.calls} /> : null}
                {/* What the user typed stays what they typed -- `**test**` keeps its asterisks. */}
                {message.role === "user" ? (
                  <div className="msg__bubble">{message.text}</div>
                ) : /* Only when there is something to draw: an answer stopped before its first
                       word would otherwise put the rule down the side of nothing at all. */
                message.text ? (
                  <div className="msg__text">
                    <Markdown text={message.text} />
                  </div>
                ) : null}
                {/* Where the text stops and why. Above the cards and the count -- those are notes
                    about the turn, this is the end of the sentence. Nobody but the user can stop
                    an answer, so the word says what happened and invents no cause for it. */}
                {message.stopped ? <div className="msg__stopped">Stopped</div> : null}
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
                {/* Closes the turn. Only an answer carries a count: spending is what an answer
                    does, and a number under the question would read as its price. The server sends
                    the user's own message a usage of zeros, so this would hold without the check --
                    but a rule that leans on someone else's zeros breaks the day they change. */}
                <Stamp at={message.at} usage={message.role === "ai" ? message.usage : null} />
              </div>
            ))}
            {streamingText ? (
              <div className="msg msg--ai" data-testid="streaming">
                <ToolCalls calls={streamingCalls} running />
                <div className="msg__text">
                  {/* Formatted from the first frame: raw first and formatted afterwards would read
                      as a flicker rather than a stream. */}
                  <Markdown text={streamingText} caret />
                </div>
                {creatingFile ? <CreatingFile /> : null}
                {/* The count arrives in a single frame at the very end, so an answer still running
                    carries only its time -- and that is the whole answer to "when did I ask". */}
                <Stamp at={askedAt} />
              </div>
            ) : null}

            {thinking && !streamingText ? (
              // Three blinking dots and nothing else, and only until the first piece lands: the
              // design refuses a fake partial answer.
              <div className="msg msg--ai msg--waiting" data-testid="thinking">
                <ToolCalls calls={streamingCalls} running />
                <div className="dots">
                  <span className="dots__dot" />
                  <span className="dots__dot" />
                  <span className="dots__dot" />
                </div>
                {creatingFile ? <CreatingFile /> : null}
                <Stamp at={askedAt} />
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
            /* karar 1's order: Skills · model · Send. The middle one stopped being a control in
               Madde 82 -- one model, nothing to pick. The skill is handed in rather than read off
               the chat: since Madde 86 the selection is the session's, and the session is App's.
               Whether the menu is open is App's too, because Escape closes it in a fixed order
               with the rest. */
            /* Stopping is the send button's other state rather than a control of its own: while an
               answer runs there is nothing to send. No red -- cutting your own answer short is not
               destruction. */
            running={thinking}
            onStop={onStop}
            foot={
              <>
                <SkillPicker
                  skill={skill}
                  open={skillsOpen}
                  onToggle={onToggleSkills}
                  onChange={onSkillChange}
                />
                <ModelLabel />
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
