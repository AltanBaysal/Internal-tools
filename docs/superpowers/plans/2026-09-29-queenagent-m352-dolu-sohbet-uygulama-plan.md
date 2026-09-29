# Madde 352 — Dolan sohbette *burada devam et* · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `5a9779c1`'in kırmızı testlerini yeşile getirmek: kayıt `full` taşır, dolu sohbette kutunun
yerinde bildirim durur, `Continue here` kırpar.

**Architecture:** Sunucuda tek satır. Ön uçta yeni `FullNotice.jsx`; `ChatScreen` onu `chat.full`'da
çizer ve kutuyu gizler; `useChat.trim` kapıyı çağırıp kaydı yeniden okur; `App` iki düğmeyi bağlar;
`workspace.css` şeklini verir.

**Tech Stack:** Flask; React 18, vitest.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m352-dolu-sohbet-uygulama-design.md)

## Global Constraints

- Arayüz metni İngilizce: `This chat is full.`, `Continue here sends only the latest messages to the
  model; the older ones stay on screen.`, `New chat`, `Continue here`.
- Yorum NEDEN'i söyler; test dosyalarına dokunulmaz; `dist` derlenmez.
- Dört satır, yazıldığı gibi, paralel. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Kayıt `full` taşır

**Files:** Modify `queen-agent/backend/features/workspace/presentation/routes.py` — `_chat_json`

- [ ] **Step 1:** `"trimmed": sent_from(chat),`'ın arkasına:

```python
        # Whether the chat takes another turn (Madde 352). The screen stands its notice on this
        # alone rather than counting against the ceiling itself -- the rule has one home.
        "full": is_full(chat),
```

### Task 2: Bildirim

**Files:**
- Create: `queen-agent/frontend/src/features/workspace/FullNotice.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/Composer.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css`

**Interfaces:**
- Produces: `FullNotice({ gauge, onNewChat, onContinue })`; `ChatScreen`'in `onNewChat`, `onContinue`
  özellikleri.

- [ ] **Step 1: `FullNotice.jsx`**

```jsx
// A full chat takes no more messages, and says so in the box's place the moment its record does
// (Madde 352; design items 140 and 182). The two ways on are both ghost: nothing is destroyed,
// somebody is being asked.
export default function FullNotice({ gauge, onNewChat, onContinue }) {
  return (
    <div className="full">
      <div className="full__text">
        <p className="full__line">This chat is full.</p>
        <p className="full__detail">
          Continue here sends only the latest messages to the model; the older ones stay on screen.
        </p>
      </div>
      <div className="full__actions">
        <div className="composer__gauge">{gauge}</div>
        <button type="button" className="ghost full__new" onClick={onNewChat}>
          New chat
        </button>
        <button type="button" className="ghost full__continue" onClick={onContinue}>
          Continue here
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: `ChatScreen.jsx`** — `FullNotice` içeri alınır; `onNewChat`, `onContinue` özellikleri;
  `.chat__composer`:

```jsx
        <div className="chat__composer">
          {chat.full ? (
            <FullNotice gauge={gauge} onNewChat={onNewChat} onContinue={onContinue} />
          ) : null}
          <Composer
            ref={box}
            /* Hidden rather than taken away while the notice stands: a reply typed as the last
               answer filled the chat is the user's work, and Continue here hands the box back with
               it. Standing, the box also keeps a refused reply's Try again able to send it. */
            hidden={chat.full}
            ...
            gauge={gauge}
            ...
          />
        </div>
```

`Composer.jsx`: özelliklere `hidden` eklenir, ve kök `<div className="composer" hidden={hidden}>`.

`gauge` erken dönüşten sonra bir kez kurulur:

```jsx
  const gauge = <ContextGauge sent={chat.context?.sent} ceiling={chat.context?.ceiling} />;
```

- [ ] **Step 3: `workspace.css`** — `.composer`'ın kuralının arkasına:

```css
/* The full chat's notice (Madde 352): in the box's place and in the box's shape, at the width the
   box has in a chat. Not red -- nothing is destroyed, somebody is being asked. */
.full {
  max-width: 720px;
  margin: 0 auto;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 14px 16px 10px;
  box-shadow: 0 1px 2px rgba(60, 50, 40, 0.04);
}

.full__line {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--ink);
}

/* Not --muted: a sentence to read, and --muted holds only 3.7:1 on the surface. */
.full__detail {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #6b6259;
}

/* The gauge's own margin-right: auto holds it at the left of the two buttons. */
.full__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 6px;
}
```

### Task 3: Kırpma, ve bağlanması

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/useChat.js` — `version`'ın arkasına `trim`,
  dönüşte `trim`
- Modify: `queen-agent/frontend/src/App.jsx` — `ChatScreen`'e iki özellik

- [ ] **Step 1: `useChat.trim`**

```js
  // Continue here (Madde 352): the server trims, and the record is read back the way a version is.
  // A refusal met while the chat was full said it was full, which stops being true here; an answer
  // that never came is still owed, so its card and its Try again stay.
  const trim = useCallback(async () => {
    try {
      await postJson(`/api/projects/${projectId}/chats/${chatId}/trim`);
      setChat(await getJson(`/api/projects/${projectId}/chats/${chatId}`));
      setRefused(null);
    } catch (failure) {
      setError(failure.message);
    }
  }, [projectId, chatId]);
```

- [ ] **Step 2: `App.jsx`** — `onVersion={chat.version}`'ın yanına:

```jsx
              /* The notice's New chat is the sidebar's own. */
              onNewChat={openDraft}
              onContinue={chat.trim}
```

### Task 4: Yeşil ve commit

- [ ] **Step 1:** Dört satır paralel; dördü yeşil.
- [ ] **Step 2:** Commit:

```powershell
git add queen-agent/backend/features/workspace/presentation/routes.py queen-agent/frontend/src/features/workspace/FullNotice.jsx queen-agent/frontend/src/features/workspace/ChatScreen.jsx queen-agent/frontend/src/features/workspace/Composer.jsx queen-agent/frontend/src/features/workspace/workspace.css queen-agent/frontend/src/features/workspace/useChat.js queen-agent/frontend/src/App.jsx docs/superpowers/specs/2026-09-29-queenagent-m352-dolu-sohbet-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m352-dolu-sohbet-uygulama-plan.md
git commit -m @'
feat: Madde 352 -- a full chat stands its notice in the box's place, and Continue here trims it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
