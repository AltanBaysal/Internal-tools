# Madde 355 — Sohbet açılırken açılmış gibi görünür · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kaydı gelmemiş sohbet kendi çerçevesinde — satırın adıyla başlık, kapalı kutu, dosya paneli
— ve mesajların yerinde spinner'la çizilir; test turunun kırmızısı yeşile döner.

**Architecture:** `ChatScreen` tek ağaç çizer: `chat` yoksa sütunda yalnız `chat__spinner`, kutu ve
seçiciler `disabled`, kutunun `key`'i açılışla kaydı ayırır. `App` başlığı sohbet listesinden verir.
Stil sayfasına iki kural girer, bir kural çıkar.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m355-sohbet-acilisi-uygulama-design.md)

## Global Constraints

- Yalnız commit'li testlerin istediği; fazlası yok.
- Arayüz metni, kod ve yorum İngilizce; yorum NEDEN'i söyler.
- Testlere dokunulmaz; dört satır yazıldığı gibi, paralel.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Açılış çerçevesi

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/Composer.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/ModePicker.jsx`, `SkillPicker.jsx`, `ModelPicker.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx`
- Modify: `queen-agent/frontend/src/App.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css`

**Interfaces:**
- Consumes: `Spinner.jsx` (340) — `<span className="spinner" aria-hidden="true" data-testid="spinner" />`.
- Produces: `Composer`'da ve üç seçicide `disabled` prop'u; `ChatScreen`'de `loadingTitle`.

- [ ] **Step 1: `Composer.jsx`** — imzaya `disabled`, yazı alanına `disabled={disabled}`; üst yorumda
  bir cümle: kayıt gelene kadar kutu kapalıdır (Madde 355).

- [ ] **Step 2: Üç seçici** — imzaya `disabled`, düğmeye `disabled={disabled}`.

- [ ] **Step 3: `ChatScreen.jsx`**
  - `Skeleton` import'u yerine `Spinner` import'u; prop listesine `loadingTitle`.
  - Erken dönüş yalnız `missing` için:

```jsx
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
```

  - `onDisk` `files`'tan; başlık `{chat ? chat.title : loadingTitle}`, yorumu: kayıt gelmeden
    kenar çubuğundaki satırın adı.
  - Sütun: `{chat ? (<>…bugünkü içerik…</>) : (<div className="chat__spinner"><Spinner /></div>)}`,
    yorumu: açılış bir tur çizmez.
  - Kutu: `key={chat ? "read" : "loading"}`, `disabled={!chat}`, ölçü `chat?.context?.sent` ve
    `chat?.context?.ceiling`; üç seçiciye `disabled={!chat}`.

- [ ] **Step 4: `App.jsx`** — `<ChatScreen …>`'e:

```jsx
              /* Before the record comes, the chat is called what its sidebar row calls it. */
              loadingTitle={projectChats.find((row) => row.id === route.chatId)?.title}
```

- [ ] **Step 5: `workspace.css`**
  - `.skeleton--message .skeleton__block { height: 68px; }` kalkar.
  - `.file-list__spinner`'ın altına:

```css
/* Where the messages will be while a chat is read (design item 194): the header, the shut box and
   the rail stand around it. */
.chat__spinner {
  display: flex;
  justify-content: center;
  padding: 40px 12px;
}
```

  - `.picker` kurallarının yanına:

```css
/* Nothing can be written or picked until the chat's record has come (design item 194): faded the
   way the kit's other shut controls are. */
.composer__input:disabled,
.picker:disabled {
  cursor: default;
  opacity: 0.4;
}
```

- [ ] **Step 6: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

- [ ] **Step 7: Commit**

```powershell
git add queen-agent/frontend/src docs/specs/2026-09-29-queenagent-m355-sohbet-acilisi-uygulama-design.md docs/plans/2026-09-29-queenagent-m355-sohbet-acilisi-uygulama-plan.md
git commit -m @'
feat: Madde 355 -- a chat opening stands in its own frame: its row's name, the rail, a shut box, and the spinner where its messages will be

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
