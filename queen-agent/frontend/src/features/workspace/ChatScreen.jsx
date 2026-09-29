import { useEffect, useRef, useState } from "react";

import Composer from "./Composer.jsx";
import ContextGauge from "./ContextGauge.jsx";
import EditMessage from "./EditMessage.jsx";
import FileCard, { CreatingFile } from "./FileCard.jsx";
import FileRail from "./FileRail.jsx";
import Markdown from "./Markdown.jsx";
import MessageFoot from "./MessageFoot.jsx";
import ModelPicker from "./ModelPicker.jsx";
import ModePicker from "./ModePicker.jsx";
import PermissionCard from "./PermissionCard.jsx";
import Skeleton from "./Skeleton.jsx";
import SkillPicker from "./SkillPicker.jsx";
import Stamp, { LiveStrip } from "./Stamp.jsx";
import ToolCalls from "./ToolCalls.jsx";

// A reader further from the bottom than this is reading, not watching, and the answer must not pull
// them away from it. The design's own number.
const STICK_WITHIN = 220;

export default function ChatScreen({
  project,
  chat,
  files = [],
  loadingFiles,
  filesError,
  reading,
  deleting,
  onRefresh,
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
  progress,
  streamingCalls = [],
  permission,
  onAllow,
  onDeny,
  skill,
  skillsOpen,
  onToggleSkills,
  model,
  modelOpen,
  onToggleModel,
  onModelChange,
  mode,
  modeOpen,
  onToggleMode,
  onModeChange,
  onBack,
  onSend,
  onSkillChange,
  onStop,
  onRetry,
  onVersion,
}) {
  // Which message is being edited, and the token that puts its sentence in the box (Madde 195).
  // Held here rather than in App: it is a state of this screen, and it ends the moment the sentence
  // is sent.
  const [editing, setEditing] = useState(null);
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
                {/* What the user typed stays what they typed -- `**test**` keeps its asterisks.
                    Correcting it happens here rather than in the composer (Madde 197): the sentence
                    is on the message, so the field that changes it is too. Only a question can be
                    gone back to -- an answer is a whole turn with its own calls, and stepping into
                    the middle of one would mean nothing on disk. */}
                {message.role === "user" ? (
                  editing?.index === index ? (
                    <EditMessage
                      text={editing.text}
                      onConfirm={(text) => {
                        setEditing(null);
                        onSend?.(text, index);
                      }}
                      onCancel={() => setEditing(null)}
                    />
                  ) : (
                    <div className="msg__bubble">{message.text}</div>
                  )
                ) : /* Only when there is something to draw: an answer stopped before its first
                       word would otherwise put the rule down the side of nothing at all. */
                message.text ? (
                  <div className="msg__text">
                    <Markdown text={message.text} />
                  </div>
                ) : null}
                {/* The pencil is handed over only where there is something to correct: a question,
                    and not one already open for correction -- a second door onto an open field is
                    one whose meaning nobody can state. Named for the message rather than Edit
                    alone, which the mode picker already wears. */}
                <MessageFoot
                  standing={message.variants}
                  onVersion={onVersion}
                  onEdit={
                    message.role === "user" && editing?.index !== index
                      ? () => setEditing({ index, text: message.text })
                      : null
                  }
                />
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
                  <Markdown text={streamingText} />
                </div>
                {creatingFile ? <CreatingFile /> : null}
                {/* Until Madde 194 an answer still running carried only its time. Now it carries
                    where the turn is, and falls back to the time until the first frame says so --
                    round 0/16 would claim a measurement nobody took. */}
                {progress ? <LiveStrip {...progress} /> : <Stamp at={askedAt} />}
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
                {progress ? <LiveStrip {...progress} /> : <Stamp at={askedAt} />}
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

            {/* Where the turn stopped: the answer's text is still above it, or the dots are, and
                the question stands underneath them. */}
            {permission ? (
              <PermissionCard
                tool={permission.tool}
                args={permission.args}
                onAllow={onAllow}
                onDeny={onDeny}
              />
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
            /* Read off the record like everything else on this screen: the same number the stamp
               under the last answer shows, and nothing counts it a second time. A record written
               before Madde 92 carries none, and then there is no circle. */
            gauge={<ContextGauge sent={chat.context?.sent} ceiling={chat.context?.ceiling} />}
            /* karar 1's order, with Madde 91's mode in front of it: Mode · Skills · model · Send.
               What the model may do at all comes before which job it is doing. The model is a
               control again since Madde 146 -- three of them, so there is something to pick. All
               three selections are handed in rather than read off the chat: they are the session's,
               and the session is App's. Which picker is open is App's too, because only one may
               stand open and Escape closes it in a fixed order with the rest. */
            /* Stopping is the send button's other state rather than a control of its own: while an
               answer runs there is nothing to send. No red -- cutting your own answer short is not
               destruction. */
            running={thinking}
            onStop={onStop}
            foot={
              <>
                <ModePicker
                  mode={mode}
                  open={modeOpen}
                  onToggle={onToggleMode}
                  onChange={onModeChange}
                />
                <SkillPicker
                  skill={skill}
                  open={skillsOpen}
                  onToggle={onToggleSkills}
                  onChange={onSkillChange}
                />
                <ModelPicker
                  model={model}
                  open={modelOpen}
                  onToggle={onToggleModel}
                  onChange={onModelChange}
                />
              </>
            }
            /* The box only ever sends a reply. An edit starts from a message and is sent from that
               message's own field (Madde 197), so the second argument here is always nothing. */
            onSubmit={(text) => onSend?.(text, null)}
          />
        </div>
      </div>

      <FileRail
        files={files}
        loading={loadingFiles}
        error={filesError}
        reading={reading}
        deleting={deleting}
        onRefresh={onRefresh}
        collapsed={railCollapsed}
        foldedByWidth={railFoldedByWidth}
        width={railWidth}
        onResize={onResizeRail}
        onToggle={onToggleRail}
      />
    </div>
  );
}
