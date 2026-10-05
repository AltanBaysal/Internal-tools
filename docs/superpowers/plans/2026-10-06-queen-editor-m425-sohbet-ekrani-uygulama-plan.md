# Madde 425 — Agent'ın sohbeti ekranda, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır, madde 425'in kendi dalında. Kod yazılır, dört satır koşulur,
> suit yeşile döner, ve commit'lenir.

**Hedef:** Test turunun commit'lediği testleri yeşile çeviren ekran: `api.js`'te altı kapı,
`features/agent/`'ta sohbetin hook'u ve paneli, `SidePanel`'in bağlaması, `app.css`'te tasarımın sohbet
sınıfları.

**Yapı:** `useAgentChat(project)` sunucuyla konuşur, yoklamayı yürütür ve proje başına ekran hafızasını
tutar; `AgentPanel` çizer, kaydırmayı ve odağı tutar. `SidePanel` başlığını agent paneline verir.

**Araçlar:** React 18 (`useState`, `useEffect`, `useLayoutEffect`, `useRef`); yeni bağımlılık yok.

**Spec:** [m425 uygulama turu](../specs/2026-10-06-queen-editor-m425-sohbet-ekrani-uygulama-design.md),
[m425 test turu](../specs/2026-10-06-queen-editor-m425-sohbet-ekrani-testler-design.md)

## Her yere geçerli kurallar

- Kod ve yorum İngilizce; ekranda görünen her söz Türkçe.
- Sunucuya, `dist`'e ve yol haritasına dokunulmaz.
- Testlere dokunulmaz: commit'lenen testlerin söylediği yazılır, fazlası değil.
- Yorum *neden*i söyler, ve yalnız bugün doğru olanı.
- `vendor/` elle değişmez; tasarımın `qe-chat` sınıfları `shared/app.css`'e girer.

---

## Görev 1: `shared/api.js` — altı kapı

**Dosya:** Değiştir: `queen-editor/frontend/src/shared/api.js` — `getExportSummary`'nin üstüne.

- [ ] **Adım 1:**

```js
// The agent's chats (madde 417, 420): a chat is named by its number inside the project. The empty
// chat waiting comes back rather than a new one -- the server never makes a second.
export async function newChat(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats`, { method: "POST" });
}

// Only the chats with a question, the newest last question first, each first question whole.
export async function listChats(project) {
  const body = await request(`/api/projects/${encodeURIComponent(project)}/chats`);
  return body.chats;
}

export async function openChat(project, chat) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats/${chat}`);
}

// Answers at once with the chat, the question last and no outcome yet: the agent goes on on the
// server.
export async function askQuestion(project, chat, text) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats/${chat}/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

export async function stopAgent(project, chat) {
  return request(`/api/projects/${encodeURIComponent(project)}/chats/${chat}/stop`,
                 { method: "POST" });
}

// Which chats' agents work now. It lives in the server's memory, not in the chats' record, so it is
// a door of its own.
export async function workingChats(project) {
  const body = await request(`/api/projects/${encodeURIComponent(project)}/chats/working`);
  return body.working;
}
```

## Görev 2: `features/agent/useAgentChat.js` — sohbetin verisi ve yoklama

**Dosya:** Oluştur: `queen-editor/frontend/src/features/agent/useAgentChat.js`

- [ ] **Adım 1: Dosyanın tamamı.**

```js
import { useEffect, useState } from "react";

import {
  askQuestion,
  listChats,
  newChat,
  openChat,
  stopAgent,
  workingChats,
} from "../../shared/api.js";

// How often the server is asked while an agent works. A step is a round with the model, seconds
// long, so once a second keeps the live line live; while nothing works nothing is asked.
const POLL_MS = 1000;

// What a visit remembers per project: which chat is open, whether the list is, and each chat's
// draft. Memory only, like the rest of the screen's memory (SidePanel's open panel, the gallery's
// list): a reload opens the newest chat, and a draft not sent goes with it.
const KEPT = new Map();

function kept(project) {
  if (!KEPT.has(project)) KEPT.set(project, { open: null, list: false, drafts: {} });
  return KEPT.get(project);
}

// The agent's chats in one project: the open one as the server last told it, which chats' agents
// work, the list, the box, and the presses. The agent runs on the server (madde 420), so the screen
// only asks -- and asks again only while something works.
export function useAgentChat(project) {
  const memory = kept(project);
  const [chat, setChat] = useState(null);
  const [working, setWorking] = useState([]);
  const [list, setList] = useState(memory.list);
  const [rows, setRows] = useState(null);
  const [draft, setDraft] = useState("");
  // The question on its way: drawn at once, before the server has it.
  const [pending, setPending] = useState(null);
  // { text, question, poll }: the request's own words, the question it carried if it was one, and
  // whether it was a look at the server -- which the next good look takes back.
  const [failure, setFailure] = useState(null);
  const id = chat ? chat.id : null;
  const busy = id !== null && (working.includes(id) || pending !== null);

  const fail = (err, question = null) => setFailure({ text: err.message, question });

  // The chat the server sent is the open one now, with its own draft.
  function take(fresh) {
    memory.open = fresh.id;
    memory.list = false;
    setList(false);
    setChat(fresh);
    setDraft(memory.drafts[fresh.id] || "");
    setFailure(null);
  }

  // Who works is asked before the chat is read: the server writes an answer and takes the chat off
  // the working list in one hold, so a chat read after "not working" carries its outcome.
  async function show(chatId) {
    try {
      const ids = await workingChats(project);
      const fresh = await openChat(project, chatId);
      setWorking(ids);
      take(fresh);
    } catch (err) {
      fail(err);
    }
  }

  // Nothing remembered: the newest chat, or the empty one waiting when nothing has been asked.
  async function first() {
    try {
      const found = await listChats(project);
      if (found.length) await show(found[0].id);
      else take(await newChat(project));
    } catch (err) {
      fail(err);
    }
  }

  const reopen = () => (memory.open === null ? first() : show(memory.open));

  async function openList() {
    memory.list = true;
    setList(true);
    setRows(null);
    setFailure(null);
    try {
      setRows(await listChats(project));
    } catch (err) {
      fail(err);
    }
  }

  useEffect(() => {
    if (memory.list) openList();
    else reopen();
  }, [project]);

  // While an agent works the server is looked at again: who works, then -- while the conversation is
  // on screen and its chat works or has just stopped -- the chat itself. Each new working list arms
  // the next look, so the loop runs for as long as the list is not empty.
  useEffect(() => {
    if (!working.length) return undefined;
    let gone = false;
    const timer = setTimeout(async () => {
      try {
        const ids = await workingChats(project);
        const read = !list && id !== null && (working.includes(id) || ids.includes(id));
        const fresh = read ? await openChat(project, id) : null;
        if (gone) return;
        if (fresh) setChat(fresh);
        setWorking(ids);
        setFailure((shown) => (shown && shown.poll ? null : shown));
      } catch (err) {
        if (gone) return;
        setFailure({ text: err.message, poll: true });
        // One look that did not arrive must not end the loop: the same list, new, arms the next.
        setWorking((ids) => [...ids]);
      }
    }, POLL_MS);
    // A look still in the air when the chat or the view changes is dropped: it would bring back a
    // chat that is no longer the open one.
    return () => {
      gone = true;
      clearTimeout(timer);
    };
  }, [project, working, list, id]);

  function write(text) {
    memory.drafts[id] = text;
    setDraft(text);
  }

  async function send() {
    const text = draft.trim();
    if (!text) return;
    const asked = id;
    write("");
    setPending(text);
    setFailure(null);
    try {
      const fresh = await askQuestion(project, asked, text);
      setWorking((ids) => (ids.includes(asked) ? ids : [...ids, asked]));
      setChat(fresh);
    } catch (err) {
      // The server never took it: the question stays on screen over the card.
      fail(err, text);
    } finally {
      setPending(null);
    }
  }

  // Nothing to stop while the question is on its way: no agent has started.
  async function stop() {
    if (pending !== null) return;
    const stopped = id;
    try {
      const fresh = await stopAgent(project, stopped);
      setWorking((ids) => ids.filter((one) => one !== stopped));
      setChat(fresh);
      setFailure(null);
    } catch (err) {
      fail(err);
    }
  }

  async function startNew() {
    try {
      take(await newChat(project));
    } catch (err) {
      fail(err);
    }
  }

  // Closing the list reads the open chat again: its agent may have finished meanwhile.
  const toggleList = () => (list ? reopen() : openList());

  return { chat, working, list, rows, open: memory.open, draft, pending, failure, busy,
           write, send, stop, startNew, toggleList, show };
}
```

## Görev 3: `features/agent/AgentPanel.jsx` — çizim, kaydırma, odak

**Dosya:** Oluştur: `queen-editor/frontend/src/features/agent/AgentPanel.jsx`

- [ ] **Adım 1: Dosyanın tamamı.**

```jsx
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
```

## Görev 4: `SidePanel.jsx` — başlık agent paneline

**Dosyalar:** Değiştir: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`;
Sil: `queen-editor/frontend/src/features/photo_generation/AgentPanel.jsx` (`git rm`).

- [ ] **Adım 1: Import.** `import AgentPanel from "./AgentPanel.jsx";` →
  `import AgentPanel from "../agent/AgentPanel.jsx";`
- [ ] **Adım 2: Başlık bir değişkende,** `const current = …`'in altında:

```jsx
  // A real heading: the open panel's name is also the only thing on screen that says which of the
  // three you are looking at.
  const heading = current && (
    <h2 style={{ margin: 0 }}>
      <Mono size={11} style={LABEL}>{current.heading || current.title}</Mono>
    </h2>
  );
```

- [ ] **Adım 3: Panelin içinde** eski `<h2>…</h2>` ve yorumunun yerine:

```jsx
        {/* The agent's chat puts its two buttons in the heading's row, so it draws the heading
            itself (madde 425). */}
        {open !== "agent" && heading}
```

  ve `{open === "agent" && <AgentPanel />}` → `{open === "agent" && <AgentPanel project={project}
  heading={heading} />}`.
- [ ] **Adım 4: Bileşenin yorumu:** *"and the agent that has not been designed yet"* → *"and the
  agent"*.

## Görev 5: `shared/app.css` — tasarımın sohbet sınıfları

**Dosya:** Değiştir: `queen-editor/frontend/src/shared/app.css` — sona.

- [ ] **Adım 1:** `kit.css`'in 447 – 625. satırları (`.qe-chat` … `.qe-chat-row-date`), değerleri
  olduğu gibi; yorumlar uygulamanın diliyle *(madde 425; uzun cevabın adımlarının konuşmanın başından
  ölçülmesi; kutunun içindeki düğmenin 10px'i; ilk sorunun burada tek satıra kesilmesi)*.
  `.qe-dot`, `.qe-dot--alive` ve `.qe-thin-scroll` zaten bu dosyada.

## Görev 6: Koşu — yeşil, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil — QueenAgent pytest 989, QueenAgent vitest 838, Queen Editor pytest 1441,
Queen Editor vitest 837 (öncekiler 799, `AgentPanel.test.jsx`'in 38'i).

- [ ] **Adım 2: Commit** — kod, uygulama spec'i ve bu plan; `dist` yok:

```powershell
git add docs/superpowers/specs/2026-10-06-queen-editor-m425-sohbet-ekrani-uygulama-design.md docs/superpowers/plans/2026-10-06-queen-editor-m425-sohbet-ekrani-uygulama-plan.md queen-editor/frontend/src/shared/api.js queen-editor/frontend/src/shared/app.css queen-editor/frontend/src/features/agent/useAgentChat.js queen-editor/frontend/src/features/agent/AgentPanel.jsx queen-editor/frontend/src/features/photo_generation/SidePanel.jsx
git commit -m @'
feat(queen-editor): 425 -- the AI agent panel is the designed chat: Yeni sohbet and Sohbetler beside the heading; the newest chat opens, read from the server; the question a bubble, its steps under it in the server's words with the one going on last and live, the answer whole, a failure a card in its own words, Durduruldu after a stop; one button inside the box, the arrow off while the box is empty and the square while the agent works; Enter sends, Shift+Enter breaks the line; the list in the conversation's place with a live dot on a working chat; the open chat, the list and each chat's draft remembered for the visit; the server looked at once a second only while an agent works, who works first and then the open chat; a reader scrolled up stays where they are; six chat doors in api.js, the qe-chat classes in app.css

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
