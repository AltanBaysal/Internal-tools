import { useEffect, useLayoutEffect, useRef } from "react";

import { formatModified } from "../../shared/date.js";
import { useAgentChat } from "./useAgentChat.js";

// The wait before the server has said what the agent is doing: the question is on its way, or the
// agent has started and written no step yet (the designer's 211).
const WAITING = "Çalışıyor…";

// Drawn, not typed: ↑ and ■ come out at different sizes in different fonts (the design's sohbet.js).
const SEND_ICON = (
  <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2"
       strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M7 12V2M2.5 6.5 7 2l4.5 4.5" />
  </svg>
);
const STOP_ICON = (
  <svg viewBox="0 0 14 14" fill="currentColor" aria-hidden="true">
    <rect x="2" y="2" width="10" height="10" rx="2" />
  </svg>
);

// A question's steps, one line each, in the server's words: a finished step says what was done.
// While the agent works the last line is the live one -- its open step, or the wait when it has
// none. A step left open by a restart keeps its words and a still dot: it was going on, and is not.
function Steps({ steps, live }) {
  const lines = steps.map((one) => ({ text: one.finished ? one.done : one.running, live: false }));
  if (live) {
    if (steps.length && !steps.at(-1).finished) lines.at(-1).live = true;
    else lines.push({ text: WAITING, live: true });
  }
  if (!lines.length) return null;
  return (
    <div className="qe-chat-steps">
      {lines.map((line, index) => (
        <div key={index} className={line.live ? "qe-chat-step is-live" : "qe-chat-step"}>
          <span className={line.live ? "qe-dot qe-dot--alive" : "qe-dot"} aria-hidden="true" />
          <span>{line.text}</span>
        </div>
      ))}
    </div>
  );
}

// One question: its bubble, its steps and how it ended, as siblings in the conversation -- so the
// element just before a long answer is its steps.
function Question({ asked, live }) {
  const { outcome } = asked;
  return (
    <>
      <div className="qe-chat-q">{asked.text}</div>
      <Steps steps={asked.steps} live={live} />
      {outcome?.kind === "answer" && <div className="qe-chat-a">{outcome.text}</div>}
      {outcome?.kind === "failure" && <div className="qe-chat-err">{outcome.text}</div>}
      {outcome?.kind === "stopped" && <div className="qe-chat-stopped">Durduruldu</div>}
    </>
  );
}

function ChatList({ rows, open, working, failure, onOpen }) {
  return (
    <div className="qe-chat-list qe-thin-scroll">
      {rows && !rows.length && <span className="qe-chat-empty wf-note">Henüz sohbet yok.</span>}
      {(rows || []).map((row) => (
        <button key={row.id} type="button" onClick={() => onOpen(row.id)}
                className={row.id === open ? "qe-chat-row is-on" : "qe-chat-row"}>
          <span className="qe-chat-row-text">
            <span className="qe-chat-row-q">{row.firstQuestion}</span>
            <span className="qe-chat-row-date">
              {formatModified(Date.parse(row.lastAskedAt) / 1000)}
            </span>
          </span>
          {/* On a row the dot is the only thing that says the agent still works, so it is named. */}
          {working.includes(row.id) && (
            <span className="qe-dot qe-dot--alive" role="img" aria-label="Agent çalışıyor"
                  style={{ background: "var(--accent)" }} />
          )}
        </button>
      ))}
      {failure && <div className="qe-chat-err">{failure.text}</div>}
    </div>
  );
}

// The AI agent panel (madde 425, the designer's 207, 208, 210, 211, 212): the open project's chats
// with the agent, which runs on the server. The column hands over its heading, and the chat's two
// buttons stand beside it.
export default function AgentPanel({ project, heading }) {
  const agent = useAgentChat(project);
  const { chat, list, draft, pending, failure, busy } = agent;
  const log = useRef(null);
  const box = useRef(null);
  // Was the conversation at its bottom before this change? Measured as the user scrolls.
  const follow = useRef(true);
  const focusBox = useRef(false);

  // A chat opened, or the conversation drawn again after the list, starts at its bottom.
  useLayoutEffect(() => {
    follow.current = true;
  }, [chat?.id, list]);

  // An answer taller than the view is read from where its steps begin; anything else ends at the
  // bottom -- unless the user scrolled up to read, and a new step must not pull them down.
  useLayoutEffect(() => {
    const view = log.current;
    if (!view) return;
    const last = view.lastElementChild;
    if (last && last.classList.contains("qe-chat-a") && last.offsetHeight > view.clientHeight) {
      const before = last.previousElementSibling;
      view.scrollTop = (before && before.classList.contains("qe-chat-steps") ? before : last)
        .offsetTop;
    } else if (follow.current) {
      view.scrollTop = view.scrollHeight;
    }
  }, [chat, pending, failure, list]);

  // Yeni sohbet puts the cursor in the box once the new chat is drawn.
  useEffect(() => {
    if (focusBox.current && box.current) {
      box.current.focus();
      focusBox.current = false;
    }
  });

  function measure() {
    const view = log.current;
    follow.current = view.scrollHeight - view.scrollTop - view.clientHeight <= 4;
  }

  function ask() {
    follow.current = true;
    agent.send();
  }

  // One button, like Claude Code's: the arrow sends, the square stops. Either way the focus goes
  // back to the box, so the next question can be written at once.
  function press() {
    if (busy) agent.stop();
    else ask();
    box.current.focus();
  }

  // Enter sends and Shift+Enter breaks the line. While the agent works Enter sends nothing, and the
  // words stay in the box.
  function onKeyDown(event) {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    if (!busy) ask();
  }

  const asked = !chat ? []
    : pending === null ? chat.questions
      : [...chat.questions, { text: pending, steps: [], outcome: null }];
  const name = busy ? "Durdur" : "Gönder";

  return (
    <>
      <div className="qe-chat-head">
        {heading}
        <div className="qe-chat-tools">
          <button type="button" className="wf-btn wf-btn--sm"
                  onClick={() => { focusBox.current = true; agent.startNew(); }}>
            Yeni sohbet
          </button>
          <button type="button" aria-pressed={list} onClick={agent.toggleList}
                  className={list ? "wf-btn wf-btn--sm is-on" : "wf-btn wf-btn--sm"}>
            Sohbetler
          </button>
        </div>
      </div>
      <div className="qe-chat">
        {list ? (
          <ChatList rows={agent.rows} open={agent.open} working={agent.working}
                    failure={failure} onOpen={agent.show} />
        ) : chat ? (
          <>
            <div className="qe-chat-log qe-thin-scroll" ref={log} onScroll={measure}>
              {!asked.length && !failure && (
                <span className="qe-chat-empty wf-note">Projeyle ilgili bir şey sor.</span>
              )}
              {asked.map((one, index) => (
                <Question key={index} asked={one}
                          live={busy && index === asked.length - 1 && !one.outcome} />
              ))}
              {failure?.question && <div className="qe-chat-q">{failure.question}</div>}
              {failure && <div className="qe-chat-err">{failure.text}</div>}
            </div>
            <div className="qe-chat-compose">
              <textarea ref={box} className="wf-input" rows={3} aria-label="Soru"
                        placeholder="Sorunu yaz…" value={draft} onKeyDown={onKeyDown}
                        onChange={(event) => agent.write(event.target.value)} />
              <button type="button" aria-label={name} title={name} onClick={press}
                      disabled={!busy && !draft.trim()}
                      className={busy ? "wf-btn qe-chat-go wf-btn--primary"
                        : "wf-btn qe-chat-go wf-btn--hl"}>
                {busy ? STOP_ICON : SEND_ICON}
              </button>
            </div>
          </>
        ) : (
          failure && <div className="qe-chat-err">{failure.text}</div>
        )}
      </div>
    </>
  );
}
