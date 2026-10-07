# Madde 102 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m102-ekran-uygulama-design.md](../specs/2026-08-28-queenagent-m102-ekran-uygulama-design.md)
**Tur 1:** on üç kırmızı commit'lendi *(`5732e38`)*. Bu turda test yazılmaz.
**Komut:** `npm test --prefix queen-agent/frontend`

---

## 1 · `features/workspace/PermissionCard.jsx` — yeni dosya

```jsx
import { useState } from "react";

// The question Madde 99 raises, seen. It stands in the transcript while the turn is paused, and the
// two buttons are the only way past it apart from Stop -- which is the send button, already there.
//
// The reason lives here rather than in App: it is the box's momentary state, the way the composer's
// draft is, and only the finished sentence leaves.
export default function PermissionCard({ tool, args, onAllow, onDeny }) {
  const [reason, setReason] = useState("");

  return (
    <div className="permission" data-testid="permission">
      <span className="permission__line">QueenAgent wants to run {tool}</span>
      {/* Raw and unparsed. run_tool is the one reader of these and a second one here would drift
          from it on the first change to either -- while approving a write nobody can see is
          approving nothing at all. */}
      <pre className="permission__args">{args}</pre>
      <div className="permission__row">
        {/* Called rather than handed over: onClick={onAllow} would send a click event up, and an
            approval has nothing to carry. */}
        <button type="button" className="permission__allow" onClick={() => onAllow?.()}>
          Allow
        </button>
        <button type="button" className="permission__deny" onClick={() => onDeny?.(reason.trim())}>
          Deny
        </button>
        {/* Beside Deny because that is the button that needs it: an approval has nothing to add,
            and a refusal with nothing written on it is a wall the model walks into again. */}
        <input
          type="text"
          className="permission__reason"
          placeholder="Why not? (optional)"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
        />
      </div>
    </div>
  );
}
```

## 2 · `features/workspace/modes.js`

```js
// Two names for two reasons: the mode an approval arrives in, and the mode the app starts in. The
// same value today, and nothing says they have to stay the same one.
export const EDIT = "edit";
export const DEFAULT_MODE = EDIT;
```

Ask'ın satırı:

```js
  { id: "ask", name: "Ask", detail: "Read and answer. A write stops and asks." },
```

## 3 · `features/workspace/useChat.js`

Alan, `streamingCalls`'ın altına:

```js
  // The question a paused turn is waiting on: {tool, args}, or null. The frame says `arguments`
  // and this says `args` -- the word is a language rule, not a rename: `arguments` cannot be
  // destructured as a prop inside a module.
  const [permission, setPermission] = useState(null);
```

Kare, `file` dalının ardına:

```js
            else if (frame.event === "permission")
              setPermission({ tool: frame.data.tool, args: frame.data.arguments });
```

`finally`'ye, `setStreamingCalls([])`'in yanına:

```js
        // However the turn ended. A question left standing would hang over the next turn offering
        // to allow something nobody is waiting on any more.
        setPermission(null);
```

`stop`'un yanına:

```js
  const answer = useCallback(
    async (allowed, reason) => {
      // The card goes first: the turn carries on down the stream that is already open, and waiting
      // for the door to answer would leave the question on screen after it was settled.
      setPermission(null);
      // The chat the stream went into rather than the address: a chat born by this very message
      // has no address yet, and the question would knock at chats/null.
      const landed = streamingInto.current ?? chatId;
      await postJson(
        `/api/projects/${projectId}/chats/${landed}/permission`,
        allowed ? { allowed: true } : { allowed: false, reason },
      ).catch(() => {});
    },
    [projectId, chatId],
  );
```

Dönen nesneye `permission` ve `answer` ekleniyor.

## 4 · `features/workspace/ChatScreen.jsx`

Import: `import PermissionCard from "./PermissionCard.jsx";`

Props: `createdFiles`'ın yanına `permission`, `onStop`'un yanına `onAllow` ve `onDeny`.

Doğan dosya kartlarının ardına:

```jsx
            {/* Where the turn stopped: the text is still above it, or the dots are, and the
                question stands underneath. */}
            {permission ? (
              <PermissionCard
                tool={permission.tool}
                args={permission.args}
                onAllow={onAllow}
                onDeny={onDeny}
              />
            ) : null}
```

## 5 · `App.jsx`

Import: `import { DEFAULT_MODE, EDIT } from "./features/workspace/modes.js";` — bugünkü satır
yalnız `DEFAULT_MODE` alıyor.

`ChatScreen`'e, `onStop`'un yanına:

```jsx
            permission={chat.permission}
            onAllow={() => {
              chat.answer(true, "");
              /* The answer settles this one call; the picker settles the next turn. Left on ask,
                 the very next message would raise the same question again. */
              setLastMode(EDIT);
            }}
            onDeny={(reason) => chat.answer(false, reason)}
```

## 6 · `features/workspace/workspace.css`

`.failure`'ın ardına:

```css
/* The question a paused turn is waiting on. Its own tone rather than the failure's: nothing has
   gone wrong here, somebody is being asked. */
.permission {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-card);
  padding: 14px 16px;
}

.permission__line {
  font-size: 14px;
  color: var(--ink);
}

.permission__args {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--muted);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.permission__row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.permission__allow,
.permission__deny {
  flex: none;
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: var(--radius-control);
  padding: 6px 13px;
  font-family: inherit;
  font-size: 12.5px;
  color: var(--ink);
  cursor: pointer;
}

.permission__allow:hover,
.permission__deny:hover {
  border-color: var(--muted);
}

/* Takes what is left of the row: the reason is the long thing here, and the buttons are fixed. */
.permission__reason {
  flex: 1;
  min-width: 0;
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: var(--radius-control);
  padding: 6px 10px;
  font-family: inherit;
  font-size: 12.5px;
  color: var(--ink);
}
```

Değişken adları dosyanın kendi adlarıdır; yoksa `.failure`'ın yaptığı gibi düz değer yazılır.

## 7 · Koş

```
npm test --prefix queen-agent/frontend
python -m pytest queen-agent -q
```

On üç kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 8 · `dist`

```
npm run build --prefix queen-agent/frontend
```

Aynı commit'te. Defter bu depoyu klonluyor ve hiç derlemiyor.

## 9 · Commit

```
feat(queen-agent): the screen asks before a tool runs
```
