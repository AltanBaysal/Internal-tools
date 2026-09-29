# Madde 347 — Sohbet başlığında yalnız sohbetin adı · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sohbet başlığında yalnız sohbetin adı; test turunun iki kırmızısı yeşil.

**Architecture:** `ChatScreen`'in başlığından `←` düğmesi ve `/` kalkar, `project` özelliği de onunla;
`App` onu artık vermez. `.chat__slash` kuralı kalkar, `.reader__bar > .back`'in yorumu bugüne uyar.

**Tech Stack:** React 18, vitest.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m347-sohbet-basligi-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; yorum yalnız nedeni ve bugün doğru olanı söyler.
- `onBack` ve yüklenirken duran `← back` yerinde kalır (v9-2l'nin).
- `dist` derlenmez; commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Başlıkta yalnız ad, yeşil

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx` — özellik listesi, `chat__header`
- Modify: `queen-agent/frontend/src/App.jsx` — `<ChatScreen project={project}`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — `.chat__slash`, `.reader__bar > .back`'in yorumu

**Interfaces:**
- Consumes: test turunun iki testi (`ChatScreen.test.jsx`).
- Produces: `ChatScreen` artık `project` almıyor.

- [ ] **Step 1: Başlık**

`ChatScreen.jsx`'te özellik listesinden `project,` satırı silinir, ve başlık:

```jsx
        <header className="chat__header">
          <span className="chat__title">{chat.title}</span>
        </header>
```

- [ ] **Step 2: App**

`App.jsx`'te `<ChatScreen`'in altındaki `project={project}` satırı silinir.

- [ ] **Step 3: CSS**

`workspace.css`'ten silinir:

```css
.chat__slash {
  color: #cfc7bc;
}
```

`.reader__bar > .back`'in yorumu şu olur:

```css
/* Framed like Refresh and Copy beside it; colour, face and hover stay .back's. */
```

- [ ] **Step 4: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü yeşil; queen-agent'ın ön ucu 695 test.

- [ ] **Step 5: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/ChatScreen.jsx queen-agent/frontend/src/App.jsx queen-agent/frontend/src/features/workspace/workspace.css docs/superpowers/specs/2026-09-29-queenagent-m347-sohbet-basligi-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m347-sohbet-basligi-uygulama-plan.md
git commit -m @'
feat: Madde 347 -- the chat header holds the chat name alone; the project name is the bar's

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
