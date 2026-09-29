# Madde 348 — Mesajın altındaki notlar tek satırda · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mesajın notları tek `msg__stamp` satırında, saat önde; süren cevabın satırı saatle başlar.
Test turunun kırmızıları yeşile döner.

**Architecture:** `Stamp` sözlerini kendi `span`'ına koyar ve ardından çocuklarını çizer; ChatScreen
sorunun `MessageFoot`'unu onun içine koyar, `MessageFoot` kendi satırını bırakır; `LiveStrip` `at` alır.
`.msg__stamp` flex bir satır olur, `.msg__foot` kalkar.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m348-mesaj-alti-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Testlere dokunulmaz: kırmızı commit'teki testleri kod karşılar.
- Kod ve yorum İngilizce; yorum nedeni söyler ve yalnız bugün doğru olanı.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Tek satır

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/Stamp.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/MessageFoot.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx` — yalnız mesajın bloğu ve iki `LiveStrip`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — `.msg__edit`'in yorumu, `.msg__foot`, `.msg__stamp`, `.msg__stamp--live`

**Interfaces:**
- Consumes: `clockTime(iso)` (`shared/time.js`).
- Produces: `Stamp({ at, usage, children })`, `LiveStrip({ at, round, of, tokens })`,
  `MessageFoot({ standing, onVersion, onEdit })` (fragment).

- [ ] **Step 1: `Stamp`**

```jsx
export default function Stamp({ at, usage, children }) {
  if (!at) return null;
  const spent = (usage?.sent ?? 0) + (usage?.answered ?? 0);
  const when = clockTime(at);
  return (
    <div className="msg__stamp">
      {/* An element of their own, so the row's gap parts the words from the arrows and the pencil
          and never a word from a glyph. */}
      <span>{spent ? `${when} · ${shorten(spent)} tokens` : when}</span>
      {children}
    </div>
  );
}
```

Üstündeki yorum: satır bir tane, saat önde, ardından mesajın verdiği notlar (Madde 348, tasarımın 139'u).

- [ ] **Step 2: `LiveStrip`**

```jsx
export function LiveStrip({ at, round, of, tokens }) {
  // ...
  const when = at ? `${clockTime(at)} · ` : "";
  // <span>{`${when}round ${round}/${of} · ${shorten(tokens)} tokens · `}</span>
}
```

Yorum: saat, kaydın saatinin duracağı yerde önde; beklemenin ilk çiziminde damga henüz yok, o zaman
satır `round`'la başlar.

- [ ] **Step 3: `MessageFoot` fragment olur**

```jsx
export default function MessageFoot({ standing, onVersion, onEdit }) {
  return (
    <>
      <Versions standing={standing} onVersion={onVersion} />
      {onEdit ? (
        <button type="button" className="msg__edit" aria-label="Edit message" title="Edit message" onClick={onEdit}>
          ✎
        </button>
      ) : null}
    </>
  );
}
```

Boş-satır bekçisi kalkar: satır `Stamp`'in, ve boş bir fragment hiçbir şey çizmez.

- [ ] **Step 4: ChatScreen**

Metnin altındaki `<MessageFoot …/>` bloğu kalkar; mesajın `Stamp`'i:

```jsx
<Stamp at={message.at} usage={message.role === "ai" ? message.usage : null}>
  {/* kalemin yorumu */}
  <MessageFoot standing={message.variants} onVersion={onVersion} onEdit={…bugünkü gibi…} />
</Stamp>
```

İki canlı satır: `{progress ? <LiveStrip at={askedAt} {...progress} /> : <Stamp at={askedAt} />}`.

- [ ] **Step 5: CSS**

```css
.msg__stamp {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--muted);
}

.msg__stamp--live {
  gap: 7px;
}
```

`.msg__foot` kuralı ve yorumu kalkar; `.msg__edit`'in yorumu kalemin artık satırda durduğunu söyler.

- [ ] **Step 6: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; queen-agent ön ucu 699.

- [ ] **Step 7: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/Stamp.jsx queen-agent/frontend/src/features/workspace/MessageFoot.jsx queen-agent/frontend/src/features/workspace/ChatScreen.jsx queen-agent/frontend/src/features/workspace/workspace.css docs/superpowers/specs/2026-09-29-queenagent-m348-mesaj-alti-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m348-mesaj-alti-uygulama-plan.md
git commit -m @'
feat: Madde 348 -- a message's notes stand on one row, the time first, and the live row starts with the time

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
