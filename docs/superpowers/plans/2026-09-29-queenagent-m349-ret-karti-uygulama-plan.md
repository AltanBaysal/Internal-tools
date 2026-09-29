# Madde 349 — Sunucunun reddi de hata kartı · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ret de kahverengi kartı çizer, ve kartın Try again'i reddedilen gönderişi aynen yeniden
gönderir.

**Architecture:** `ChatScreen` `refused` ile `error`'u aynı kartla çizer. `.refused` CSS kuralı
gider. Task 1 reddedilen gönderişin argümanlarını hook'ta tutuyordu; Task 2 (ikinci geçiş) bunun
yerine cümlenin tek sahibini kutu yapar: reddedilen bir cevabın Try again'i kutunun gönderişidir.

**Tech Stack:** React 18, vitest, Testing Library.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m349-ret-karti-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; yorum neden'i söyler, yalnız bugün doğru olanı.
- `App.jsx` değişmez; `dist` derlenmez; `workspace.css`'te yalnız `.refused` kuralı gider.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Ret kartı, yeşil

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/useChat.js` — `refused`'ın yorumu, yükleme
  etkisi, `send`'in `catch`'i, `retry`
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx` — ret satırı ve hata kartı
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — `.refused`

**Interfaces:**
- Consumes: kırmızı turun testleri (`ChatScreen.test.jsx`, `App.test.jsx`).
- Produces: `useChat(...).retry()` — `refused` doluyken reddedilen `send` argümanlarıyla, değilse
  `send(null)`; hiç fırlatmaz.

- [ ] **Step 1: `useChat` ret'i hatırlasın**

`refused`'ın yorumu ve yanına ref:

```js
  // Kept apart from `error` on purpose, though both draw the same card (Madde 349): a message that
  // was never sent and an answer that never came are asked for again differently, and only this
  // hook knows which road the message came down.
  const [refused, setRefused] = useState(null);
  // What the refused send carried, so Try again sends it again as it was.
  const refusedSend = useRef(null);
```

Yükleme etkisinin iki dalında `setError(null);`'un yanına `setRefused(null);` — ilkinin üstüne:

```js
    // A refusal belongs to the chat it was said in: its Try again, pressed here, would write the
    // sentence into this one.
```

`catch`'te `setRefused`'ın arkasına:

```js
        refusedSend.current = [text, skill, mode, model, from];
```

ve fırlatmanın yorumu:

```js
        // Thrown on rather than swallowed, but only when there was a sentence: the composer is
        // holding the only copy of it and has to know to keep it.
```

`retry`:

```js
    // Try again sends again what got no answer: the refused send as it was, or -- after a failed
    // answer -- the same road with no sentence on it. A second refusal is on the card already and
    // the sentence back in the box since the first, so there is nobody left to tell.
    retry: () => (refused ? send(...refusedSend.current) : send(null)).catch(() => {}),
```

- [ ] **Step 2: `ChatScreen` iki hâli tek kartla çizsin**

`{refused ? <p className="refused">…}` satırı ve yorumu, ve `{error ? (<div className="failure">…)}`
yerine:

```jsx
            {/* A message the server refused and an answer that never came are one card (design
                item 193): either way no answer came, and Try again asks for one again -- what it
                sends is the hook's to know. */}
            {[refused, error].filter(Boolean).map((words, index) => (
              <div key={index} className="failure">
                <div className="failure__body">
                  <span className="failure__line">Couldn&apos;t get a response.</span>
                  <span className="failure__detail">{words}</span>
                </div>
                {onRetry ? (
                  <button type="button" className="failure__retry" onClick={onRetry}>
                    Try again
                  </button>
                ) : null}
              </div>
            ))}
```

Kartın içindeki iki yorum (tahmin edilen sebep yok; ayarlar ekranı yok) olduğu gibi kalır.

- [ ] **Step 3: `.refused` kuralını sil**

`workspace.css`'te `/* One line, no card: … */` yorumu ve `.refused { … }` kuralı.

- [ ] **Step 4: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü yeşil; queen-agent'ın ön ucu 697.

- [ ] **Step 5: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/useChat.js queen-agent/frontend/src/features/workspace/ChatScreen.jsx queen-agent/frontend/src/features/workspace/workspace.css docs/superpowers/specs/2026-09-29-queenagent-m349-ret-karti-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m349-ret-karti-uygulama-plan.md
git commit -m @'
feat: Madde 349 -- a refused message draws the failure card, and Try again sends it again

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```

---

### Task 2: İkinci geçiş — Try again kutunun gönderişi, kart sohbetinde kalır; yeşil

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/Composer.jsx` — `forwardRef`,
  `useImperativeHandle`
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx` — kutunun ref'i, kartın
  `onClick`'i
- Modify: `queen-agent/frontend/src/features/workspace/useChat.js` — `refusedSend` yerine
  `refusedReply`, `retry(sendBox)`, yükleme etkisindeki iki `setRefused(null)`

**Interfaces:**
- Consumes: ikinci kırmızı commit'in üç testi.
- Produces: `Composer`'ın ref'i `{ submit() }`; `useChat(...).retry(sendBox)` — ret bir cevabınsa
  `sendBox()`, değilse `send(null)`.

- [ ] **Step 1: Composer kendi `submit`'ini versin**

```js
import { forwardRef, useImperativeHandle, useState } from "react";
...
export default forwardRef(function Composer(
  { rows, placeholder, action, gauge, foot, running, onStop, onSubmit },
  ref,
) {
  ...
  // Try again after a refused reply is this box sending (Madde 349): the sentence came back here,
  // and with one owner it cannot be sent twice.
  useImperativeHandle(ref, () => ({ submit }));
  ...
});
```

- [ ] **Step 2: ChatScreen kartın Try again'ine kutuyu versin**

```jsx
  // The box, for the card's Try again: a refused reply is sent again by the box that holds it.
  const box = useRef(null);
  ...
  <button type="button" className="failure__retry" onClick={() => onRetry(() => box.current.submit())}>
  ...
  <Composer ref={box} ... />
```

- [ ] **Step 3: useChat yalnız retin cevap olup olmadığını tutsun**

```js
  // Whether the refused send was a reply: its sentence went back to the box then, and the box is
  // what sends it again -- one owner, so it cannot go twice (Madde 349).
  const refusedReply = useRef(false);
  ...
        refusedReply.current = text !== null && from === null;
  ...
    // Try again sends again what got no answer. A refused reply is the box's to send: its sentence
    // went back there. Anything else -- a failed answer, a refused Try again, or a refused edit,
    // whose sentence nothing holds any more -- asks with no sentence on it.
    retry: (sendBox) => (refused && refusedReply.current ? sendBox() : send(null)),
```

Yükleme etkisinin iki dalına `setRefused(null);` ve ilkinin üstüne:

```js
    // A refusal belongs to the chat it was said in: its Try again sends the box, which pressed
    // here would write the sentence into this chat.
```

- [ ] **Step 4: Dört satırı paralel koş, yeşili gör**

Beklenen: dördü yeşil; queen-agent'ın ön ucu 700.

- [ ] **Step 5: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/Composer.jsx queen-agent/frontend/src/features/workspace/ChatScreen.jsx queen-agent/frontend/src/features/workspace/useChat.js docs/superpowers/specs/2026-09-29-queenagent-m349-ret-karti-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m349-ret-karti-uygulama-plan.md
git commit -m @'
feat: Madde 349 -- Try again after a refused reply is the box sending it, and a refusal stays in its chat

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
