# Madde 342 — Açık dosyanın başlığı · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `bbc8ab1b`'nin kırmızı testlerini yeşile getiren başlık: çubukta çerçeveli `←`, yazılı
`Refresh` ve `Copy`, altta ad; Download ve yalnız onun kullandığı her şey gider.

**Architecture:** `FilePanel.jsx` başlığı iki satıra çevirir; `useFile.js` `download`'ı bırakır;
iki çağıran `onDownload`'ı bırakır; `workspace.css` başlığın kurallarını tasarımın `kit.css`'inden
alır.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m342-dosya-basligi-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- UI metni İngilizce: `Refresh`, `Copy`, `Copied`, `Could not copy`.
- `npm run build` koşulmaz, `dist` commit'lenmez — koordinatör birleştirirken derler.
- `workspace.css`'te yalnız okuyucunun kuralları ve `.back--inline` değişir; ötekilerin sırası ve
  biçimi olduğu gibi.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Başlık, Download'sız

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/FilePanel.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/useFile.js`
- Modify: `queen-agent/frontend/src/features/workspace/FileRail.jsx` (`onDownload` satırı)
- Modify: `queen-agent/frontend/src/features/workspace/ProjectScreen.jsx` (`onDownload` satırı)
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css`

**Interfaces:**
- Consumes: `bbc8ab1b`'deki testler.
- Produces: `FilePanel({ name, file, missing, error, back, onClose, onRefresh })`;
  `useFile(projectId)` → `{ name, file, missing, error, open, close, reload }`.

- [ ] **Step 1: `CopyButton` yazıyla konuşur**

```jsx
    <button
      type="button"
      className="ghost reader__copy"
      disabled={!text}
      data-said={said === "Copied" ? "yes" : said ? "no" : undefined}
      onClick={copy}
    >
      {said ?? "Copy"}
    </button>
```

Download'ı anan yorumlar düzelir: "Download's waiting is a different waiting…" cümlesi gider;
"This is why the panel's own copy is what goes -- Download can read again, and this cannot." →
"This is why the panel's own copy is what goes: reading again first would lose the gesture."

- [ ] **Step 2: `FilePanel`'in başlığı**

`useState`'in `preparing`/`failed`'ı, `download`'ı, `onDownload` parametresi ve
`{failed ? … : null}` satırı gider. Başlık:

```jsx
      <header className="reader__head">
        <div className="reader__bar">
          {back ? (
            <button type="button" className="back back--inline" onClick={onClose}>
              ←
            </button>
          ) : (
            <button type="button" className="reader__close" title="Close" onClick={onClose}>
              ×
            </button>
          )}
          <div className="reader__tools">
            <button type="button" className="ghost reader__refresh" onClick={onRefresh}>
              Refresh
            </button>
            <CopyButton text={file?.text ?? ""} />
          </div>
        </div>
        <span className="reader__name">{file ? file.name : name}</span>
      </header>
```

- [ ] **Step 3: `useFile.js`** — `save` ve `download` gider, dönen nesneden `download` çıkar.

- [ ] **Step 4: `FileRail.jsx` ve `ProjectScreen.jsx`** — `onDownload={reading.download}` satırları
gider.

- [ ] **Step 5: `workspace.css`**

`.back--inline { margin-bottom: 0; }` →

```css
/* Two classes, so it wins over .back's 18 wherever it is written: with one, source order let .back
   win, and the arrow stood 9 above the middle of its row (APP-BUGS 48). */
.back.back--inline {
  margin-bottom: 0;
}
```

Okuyucunun başlığı:

```css
/* Two rows: the framed buttons above, the name under them on a row of its own, so the name never
   gives up room to the buttons. */
.reader__head {
  flex: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 18px 28px;
  border-bottom: 1px solid var(--line);
}

/* The way back at one edge, Refresh and Copy at the other. */
.reader__bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.reader__tools {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Framed like Refresh and Copy beside it; colour, face and hover stay .back's. Only here: the chat
   header's way back carries back--inline too, and its look is not this header's to change. */
.reader__bar > .back {
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: var(--radius-control);
  padding: 5px 11px;
}

/* One line height for all three, so the arrow's 12px and the words' 12.5px make one height. */
.reader__bar > button,
.reader__tools > button {
  flex: none;
  line-height: 20px;
}

.reader__name {
  min-width: 0;
  font-size: 14px;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

`.reader__download` kuralı gider. `.file-list__refresh, .reader__refresh, .reader__copy` ve onun
`:hover`'ı yalnız `.file-list__refresh`'i seçer. `.reader__copy:disabled`'in önüne:

```css
/* Wide enough for Could not copy, so the answer takes Copy's place and the head does not move. */
.reader__copy {
  min-width: 116px;
}
```

ve Madde 193'ün yorumunda "icon" → "button".

- [ ] **Step 6: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: QueenAgent ön ucu 662/662, arka ucu 933; queen-editor ön ucu 749, arka ucu 1158 + 377'nin
iki kırmızısı.

- [ ] **Step 7: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/FilePanel.jsx queen-agent/frontend/src/features/workspace/useFile.js queen-agent/frontend/src/features/workspace/FileRail.jsx queen-agent/frontend/src/features/workspace/ProjectScreen.jsx queen-agent/frontend/src/features/workspace/workspace.css docs/specs/2026-09-29-queenagent-m342-dosya-basligi-uygulama-design.md docs/plans/2026-09-29-queenagent-m342-dosya-basligi-uygulama-plan.md docs/specs/2026-09-29-queenagent-m342-dosya-basligi-testler-design.md
git commit -m @'
feat: Madde 342 -- the open file's head is a framed back, Refresh and Copy above the name, and Download is gone

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
