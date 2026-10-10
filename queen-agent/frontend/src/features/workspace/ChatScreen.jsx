import { Fragment, useEffect, useRef, useState } from "react";

import Composer from "./Composer.jsx";
import ContextGauge from "./ContextGauge.jsx";
import EditMessage from "./EditMessage.jsx";
import FailureCard from "./FailureCard.jsx";
import FileCard, { CreatingFile } from "./FileCard.jsx";
import FileRail from "./FileRail.jsx";
import FullNotice from "./FullNotice.jsx";
import Markdown from "./Markdown.jsx";
import MessageFoot from "./MessageFoot.jsx";
import ModePicker from "./ModePicker.jsx";
import PermissionCard from "./PermissionCard.jsx";
import SkillPicker from "./SkillPicker.jsx";
import Spinner from "./Spinner.jsx";
import Stamp, { LiveStrip } from "./Stamp.jsx";
import ToolCalls from "./ToolCalls.jsx";

// A reader further from the bottom than this is reading, not watching, and nothing arriving at the
// foot -- the answer, a card -- may pull them away from it. The design's own number.
const STICK_WITHIN = 220;

// The design's words for the trim (item 147). Where the line stands is the record's `trimmed` --
// the server's count, never one the screen works out (FOUNDATION, Decision 4).
const TRIMMED_LINE = "Messages above this line are no longer sent to the model";

export default function ChatScreen({
  chat,
  loadingTitle,
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
  sentAt = null,
  arrived = null,
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
  mode,
  modeOpen,
  onToggleMode,
  onModeChange,
  onBack,
  onSend,
  onSkillChange,
  onStop,
  onRetry,
  onAnswerAgain,
  onVersion,
  onNewChat,
  onContinue,
  focusReply,
  onReplyFocused,
}) {
  // Which message is being edited, and the token that puts its sentence in the box (Madde 195).
  // Held here rather than in App: it is a state of this screen, and it ends the moment the sentence
  // is sent.
  const [editing, setEditing] = useState(null);
  // The label answers "when was this asked for", and the record says: the question being answered
  // is the open line's last message -- the sentence on its way, or the one written before the turn
  // began (Madde 462). So a reload in the middle of a turn shows when it was asked, not the reload.
  // A draft draws no bubble before the door answers, so there it is when the sentence left.
  const last = thinking ? chat?.messages.at(-1) : null;
  const askedAt = last?.role === "user" ? last.at : thinking ? sentAt : null;

  // The box, for the card's Try again: a refused reply is sent again by the box that holds it.
  const box = useRef(null);

  // Search chats' Enter hands the chat it opens the focus (Madde 365). App asks only once this
  // chat's record is on screen -- the box is shut and born again while it is read -- and hearing it
  // done lets the ask go, so the next render does not take the focus back.
  useEffect(() => {
    if (!focusReply) return;
    box.current.focus();
    onReplyFocused();
  }, [focusReply]);

  const scroll = useRef(null);
  const toBottom = () => {
    const list = scroll.current;
    if (list) list.scrollTop = list.scrollHeight;
  };

  // Whether the reader was at the foot when they last scrolled. Taken then rather than once the foot
  // has grown: a card taller than STICK_WITHIN -- a permission card printing a whole file -- would
  // otherwise make a reader at the foot look like one who had scrolled away.
  const following = useRef(true);
  const onScroll = () => {
    const list = scroll.current;
    following.current = list.scrollHeight - list.scrollTop - list.clientHeight <= STICK_WITHIN;
  };

  // A message the user just sent is theirs to see, so the list always jumps.
  useEffect(toBottom, [chat?.messages.length]);

  // Whatever else lands at the foot follows the reader rather than the other way round: the wait as
  // its steps and its line grow -- no words pull the list down since Madde 440 -- and the cards a
  // running turn puts there (Madde 380). Counts rather than lists: an absent list is a fresh [] on
  // every render.
  useEffect(() => {
    if (following.current) toBottom();
  }, [
    streamingCalls.length,
    progress,
    creatingFile,
    createdFiles.length,
    permission,
    refused,
    error,
  ]);

  // A chat the server says is not there: the way back, over the line saying so. A chat still being
  // read draws its own frame below instead (design item 194).
  if (missing) {
    return (
      <div className="screen">
        <div className="screen__column">
          <button type="button" className="back" onClick={onBack}>
            ← back
          </button>
          <p className="screen__missing">That chat does not exist.</p>
        </div>
      </div>
    );
  }

  // A message remembers what it produced and is never rewritten -- that sentence was true when it
  // was said. The card claims something else, that the file exists and is called this, so it is
  // drawn from the crossing of the two: once the file is deleted it simply stops having a card.
  const onDisk = new Set(files.map((file) => file.name));

  /* Read off the record like everything else on this screen: the same number the stamp under the
     last answer shows, and nothing counts it a second time. A record written before Madde 92
     carries none, and then there is no circle. The box and a full chat's notice both carry it. */
  const gauge = <ContextGauge sent={chat?.context?.sent} ceiling={chat?.context?.ceiling} />;

  return (
    /* A narrow shell hides the conversation while a file is open, and CSS cannot look at a later
       sibling to find that out. The screen knows already, so it says so. */
    <div className={reading?.name ? "chat-layout chat-layout--reading" : "chat-layout"}>
      <div className="chat">
        {/* The chat's name alone: the project's name and the way out of it are the bar's (the
            design's items 152 and 168). */}
        <header className="chat__header">
          {/* Before the record comes, the chat is called what its sidebar row calls it: the list
              was read first and says the same (design item 194). */}
          <span className="chat__title">{chat ? chat.title : loadingTitle}</span>
        </header>

        <div className="chat__scroll" ref={scroll} onScroll={onScroll}>
          <div className="chat__column">
            {/* While the record is read only the spinner stands here -- not even a turn still
                running into this chat: there is no transcript yet to draw it on. */}
            {chat ? (
              <>
                {chat.messages.map((message, index) => {
                  // The model failed technically on all five tries (Madde 440): the answer is the
                  // failure card, the failure's own words under it. Refused on all five (Madde
                  // 445), it is plain answer text -- the refusal message -- and only the card is
                  // this kind's. Both carry msg--failed because the design marks every failed
                  // answer with it; what the class styles is the card, so on a refusal it draws
                  // nothing.
                  const technical = message.failed === "technical";
                  return (
                    <Fragment key={`${message.at}-${index}`}>
                      {/* Before the first message still sent. Zero is a chat nobody trimmed, and
                          a record from before Madde 345 carries no number, which equals no
                          index. */}
                      {index > 0 && index === chat.trimmed ? (
                        <p className="trimmed">{TRIMMED_LINE}</p>
                      ) : null}
                      <div
                        className={
                          message.role === "user"
                            ? "msg msg--user"
                            : /* The answer the turn just ended on fades its words in, once
                                 (design item 214). */
                              `msg msg--ai${message.failed ? " msg--failed" : ""}${
                                index === arrived ? " msg--arrived" : ""
                              }`
                        }
                      >
                        {/* Only an answer has steps; a question is what was typed and nothing
                            else. */}
                        {message.role === "ai" ? <ToolCalls calls={message.calls} /> : null}
                        {/* What the user typed stays what they typed -- `**test**` keeps its
                            asterisks. Correcting it happens here rather than in the composer
                            (Madde 197): the sentence is on the message, so the field that changes
                            it is too. Only a question can be gone back to -- an answer is a whole
                            turn with its own calls, and stepping into the middle of one would mean
                            nothing on disk. */}
                        {message.role === "user" ? (
                          editing?.index === index ? (
                            <EditMessage
                              text={editing.text}
                              onConfirm={(text) => {
                                setEditing(null);
                                // Refused, the sentence comes back to the field it was typed in
                                // (FOUNDATION, principle 1); the card says why.
                                Promise.resolve(onSend?.(text, index)).catch(() =>
                                  setEditing({ index, text }),
                                );
                              }}
                              onCancel={() => setEditing(null)}
                            />
                          ) : (
                            <div className="msg__bubble">{message.text}</div>
                          )
                        ) : technical ? (
                          /* Try again only while it is the open line's last message and no turn
                             runs: a chat that has moved on keeps the card as a record, and a second
                             press before the record is read again would start a second turn. It
                             answers the question again and never sends the composer. */
                          <FailureCard
                            words={message.text}
                            onRetry={
                              index === chat.messages.length - 1 && !thinking ? onAnswerAgain : null
                            }
                          />
                        ) : /* Only when there is something to draw: a stopped answer has no
                               words. */
                        message.text ? (
                          <div className="msg__text">
                            <Markdown text={message.text} />
                          </div>
                        ) : null}
                        {/* One turn can produce more than one file, so the card is not a single
                            slot. */}
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
                        {/* Where the turn stopped: under what it made and just above its stamp
                            (design item 215) -- the files stay, and this is the turn's end. Nobody
                            but the user can stop an answer, so the word says what happened and
                            invents no cause. */}
                        {message.stopped ? <div className="msg__stopped">Stopped</div> : null}
                        {/* Closes the turn. Only an answer carries a count: spending is what an
                            answer does, and a number under the question would read as its price.
                            The server sends the user's own message a usage of zeros, so this
                            would hold without the check -- but a rule that leans on someone else's
                            zeros breaks the day they change. A stopped turn and a refused one have
                            no finished answer for the counts to describe, so their stamp is the
                            time alone (design items 215 and 221), and the failure card has no time
                            of its own, so it has no stamp. */}
                        {technical ? null : (
                          <Stamp
                            at={message.at}
                            usage={
                              message.role === "ai" && !message.stopped && !message.failed
                                ? message.usage
                                : null
                            }
                          >
                            {/* The pencil is handed over only where there is something to correct:
                                a question, and not one already open for correction -- a second
                                door onto an open field is one whose meaning nobody can state.
                                Named for the message rather than Edit alone, which the mode picker
                                already wears. */}
                            <MessageFoot
                              standing={message.variants}
                              onVersion={onVersion}
                              onEdit={
                                message.role === "user" && editing?.index !== index
                                  ? () => setEditing({ index, text: message.text })
                                  : null
                              }
                            />
                          </Stamp>
                        )}
                      </div>
                    </Fragment>
                  );
                })}

                {thinking ? (
                  // The wait stands until the turn ends (design item 214): the words come whole,
                  // with the record, and the design refuses a fake partial answer. Since Madde 194
                  // it carries where the turn is after the time, and is the time alone until the
                  // first frame says so -- round 0/16 would claim a measurement nobody took.
                  <div className="msg msg--ai msg--waiting" data-testid="thinking">
                    <ToolCalls calls={streamingCalls} running />
                    <div className="dots">
                      <span className="dots__dot" />
                      <span className="dots__dot" />
                      <span className="dots__dot" />
                    </div>
                    {creatingFile ? <CreatingFile /> : null}
                    {progress ? <LiveStrip at={askedAt} {...progress} /> : <Stamp at={askedAt} />}
                  </div>
                ) : null}

                {/* Born during this answer, so they are drawn from the stream. Once the server's
                    record arrives it carries the same names and these are dropped. */}
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

                {/* Where the turn stopped: the answer's text is still above it, or the dots are,
                    and the question stands underneath them. */}
                {permission ? (
                  <PermissionCard
                    tool={permission.tool}
                    args={permission.args}
                    onAllow={onAllow}
                    onDeny={onDeny}
                  />
                ) : null}

                {/* A message the server refused and an answer that never came are one card
                    (design item 193): either way no answer came, and Try again asks for one again
                    -- what it sends is the hook's to know, and a refused reply is the
                    composer's. */}
                {[refused, error].filter(Boolean).map((words, index) => (
                  <FailureCard
                    key={index}
                    words={words}
                    onRetry={onRetry ? () => onRetry(() => box.current.submit()) : null}
                  />
                ))}
              </>
            ) : (
              <div className="chat__spinner">
                <Spinner />
              </div>
            )}
          </div>
        </div>

        <div className="chat__composer">
          {chat?.full ? (
            <FullNotice gauge={gauge} onNewChat={onNewChat} onContinue={onContinue} />
          ) : null}
          {/* Shut until the record comes, and born afresh with it: kept across the opening, a
              sentence left in one chat's box would be offered to the next. */}
          <Composer
            key={chat ? "read" : "loading"}
            ref={box}
            disabled={!chat}
            /* Hidden rather than taken away while the notice stands: a reply typed as the last
               answer filled the chat is the user's work, and Continue here hands the box back with
               it. Standing, the box also keeps a refused reply's Try again able to send it. */
            hidden={chat?.full}
            rows={2}
            placeholder="Reply..."
            action="Send"
            gauge={gauge}
            /* karar 1's order, with Madde 91's mode in front of it: Mode · Skills · Send. What the
               model may do at all comes before which job it is doing. No model is named here since
               Madde 358: there is one, and the server says which. Both selections are handed in
               rather than read off the chat: they are the session's, and the session is App's.
               Which picker is open is App's too, because only one may stand open and Escape closes
               it in a fixed order with the rest. */
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
                  disabled={!chat}
                  onToggle={onToggleMode}
                  onChange={onModeChange}
                />
                <SkillPicker
                  skill={skill}
                  open={skillsOpen}
                  disabled={!chat}
                  onToggle={onToggleSkills}
                  onChange={onSkillChange}
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
