# Madde 341 — Yanıp sönen kare kalkar · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Süren cevap karesiz çizilir, ve kareye ait kod, özellik ve CSS kalmaz.

**Architecture:** `ChatScreen` `caret` göndermeyi bırakır; `Markdown` onu almayı ve `Caret`'i
çizmeyi bırakır; `.caret` kuralı silinir.

**Tech Stack:** React 18, vitest.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m341-kare-kalkar-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- `ChatScreen.jsx`'teki değişiklik tek satır (344 aynı dosyayı bölüyor).
- `workspace.css`'te yalnız `.caret` kuralı ve yorumu silinir; öteki kurallara dokunulmaz.
- `dist` derlenmez ve commit'lenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Kare kalkar

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx:495`
- Modify: `queen-agent/frontend/src/features/workspace/Markdown.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css:567-577`
- Test: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` (red turda yazıldı)

**Interfaces:**
- Produces: `Markdown({ text })` — tek özellik.

- [ ] **Step 1: ChatScreen artık kare istemez**

```jsx
                  <Markdown text={streamingText} />
```

- [ ] **Step 2: Markdown kareyi bilmez**

Başın yorumu yalnız ilk paragrafı tutar; `Caret` silinir. Kalanlar:

```jsx
import { parseBlocks } from "../../shared/markdown.js";

// Tokens become React elements here and nowhere else. The wrapper carries no size of its own: the
// container it sits in picks the scale, so one parser serves both the bubble and the file panel.

function blockList(nodes) {
  return nodes.map((node, key) => block(node, key));
}

function block(node, key) {
  switch (node.type) {
    case "heading": {
      const Heading = `h${node.level}`;
      return <Heading key={key}>{inline(node.inline)}</Heading>;
    }
    case "code":
      return (
        <pre key={key}>
          <code>{node.text}</code>
        </pre>
      );
    case "rule":
      return <hr key={key} />;
    case "quote":
      return <blockquote key={key}>{blockList(node.blocks)}</blockquote>;
    case "list": {
      const List = node.ordered ? "ol" : "ul";
      return (
        <List key={key}>
          {node.items.map((item, index) => (
            <li key={index}>
              {inline(item.inline)}
              {item.blocks ? blockList(item.blocks) : null}
            </li>
          ))}
        </List>
      );
    }
    case "table":
      // Its own scroller: the page never scrolls sideways, so a wide table scrolls inside itself.
      return (
        <div key={key} className="md__table-scroll">
          <table>…bugünkü thead ve tbody, değişmeden…</table>
        </div>
      );
    default:
      return <p key={key}>{inline(node.inline)}</p>;
  }
}

export default function Markdown({ text }) {
  return <div className="md">{blockList(parseBlocks(text))}</div>;
}
```

`inline` değişmez.

- [ ] **Step 3: `.caret` kuralını sil**

`workspace.css`'te `/* Where the answer has got to. … */` yorumu ve `.caret { … }` kuralı, arkasındaki
boş satırla.

- [ ] **Step 4: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent'ın arka ucu 933, ön ucu 643 yeşil; queen-editor'ün arka ucu 1158 + 377'nin
bilinen iki kırmızısı; ön ucu 749.

- [ ] **Step 5: Commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ChatScreen.jsx queen-agent/frontend/src/features/workspace/Markdown.jsx queen-agent/frontend/src/features/workspace/workspace.css docs/superpowers/specs/2026-09-29-queenagent-m341-kare-kalkar-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m341-kare-kalkar-uygulama-plan.md
git commit -m @'
feat: Madde 341 -- an answer still arriving ends with its text, and no square blinks after it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
