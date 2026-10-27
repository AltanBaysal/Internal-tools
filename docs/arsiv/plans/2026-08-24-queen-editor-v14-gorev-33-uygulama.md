# v14 Görev 33 — Ekran bilmediğini söylemez: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Önceki commit'in üç kırmızı testini yeşile döndürmek.

**Architecture:** Var olan bir bayrağı üç dosyadan geçirmek, ve panele bir erken çıkış eklemek.

**Tech Stack:** React 18, Vite, Vitest + jsdom.

**Spec:** [Görev 33 uygulama spec'i](../specs/2026-08-24-queen-editor-v14-gorev-33-uygulama-design.md)

## Global Constraints

- **Test dosyalarının iddiaları değişmiyor.** Bir istisna çıktı ve kaydı burada:
  `SidePanel.test.jsx`'in `column` yardımcısı bayrağı vermiyordu, dolayısıyla kuyruk panelini açan üç
  mevcut test panelin sustuğu hâli görüyordu. `QueuePanel.test.jsx`'in yardımcısına aynı satır test
  döngüsünde eklenmişti; bunun eşi atlanmış. Üç testin **cümleleri ve iddiaları aynı** — hepsi
  panelin *bildiğinde* ne dediğini sınıyor, ve yardımcı artık onlara bunu söylüyor.
- **Prop adı `known`** — `useGeneration`'ın bugün döndürdüğü ad.
- **Varsayılan yok.**
- **Erken çıkış hook'tan sonra durur.** React hook'ları koşulsuz koşar.
- Dil: kod ve yorumlar **İngilizce**; commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test: `npm test --prefix queen-editor/frontend` · Derleme:
  `npm run build --prefix queen-editor/frontend` · **`dist` aynı commit'e girer.**

## File Structure

| Dosya | İşlem |
|---|---|
| `.../photo_generation/QueuePanel.jsx` | `known` alır, bilmiyorsa halka gösterip çıkar |
| `.../photo_generation/SidePanel.jsx` | `known` alır ve geçirir |
| `.../photo_generation/ProjectScreen.jsx` | `known`'ı hook'tan okur ve geçirir |

---

### Task 1: Panel bilmeden susar

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx`

**Interfaces:**
- Produces: `QueuePanel` `known` alır. `false` iken yalnız `.wf-spinner` çizer.

- [ ] **Step 1: Bekleyişin ölçüsünü yaz**

`const FRAMES = ...` benzeri sabitlerin yanına — `CARD_TONE`'un altına:

```jsx
// The panel's own waiting, in its own column: the same shape the photo panel takes while the
// project record is in flight (madde 31).
const WAITING = { flex: 1, display: "flex", alignItems: "center", justifyContent: "center" };
```

- [ ] **Step 2: İmzaya bayrağı ekle**

Bugünkü hâli:

```jsx
export default function QueuePanel({ job, error, errorField, busyElsewhere, project, stopping,
                                     queue, failures, producers, onStop, onResume, onCancel,
                                     onRetryAll, onInstall }) {
```

Yerine:

```jsx
export default function QueuePanel({ job, known, error, errorField, busyElsewhere, project,
                                     stopping, queue, failures, producers, onStop, onResume,
                                     onCancel, onRetryAll, onInstall }) {
```

- [ ] **Step 3: Erken çıkışı hook'un altına koy**

Bugünkü ilk satır:

```jsx
  const [clearing, setClearing] = useState(false);

  // Another project's finished batch must not talk into this panel (state leaks across projects
```

Yerine:

```jsx
  const [clearing, setClearing] = useState(false);

  // idle is a placeholder, not an answer: before the server has reported anything there is no true
  // sentence to write about the queue, and this panel used to write the loudest wrong one -- that
  // the queue is empty, over a run that may well be flowing (madde 33). Below the hook rather than
  // above it, because hooks run unconditionally.
  if (!known) return <div style={WAITING}><span className="wf-spinner" /></div>;

  // Another project's finished batch must not talk into this panel (state leaks across projects
```

- [ ] **Step 4: Panelin testinin yeşile döndüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `QueuePanel.test.jsx` **48 tests, 0 failed**. `SidePanel` ve `ProjectScreen` hâlâ 1'er
failed.

---

### Task 2: Sütun ve ekran bayrağı taşır

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`

**Interfaces:**
- Consumes: Task 1'in `known` prop'u.
- Produces: kablonun tamamı — `useGeneration` → `ProjectScreen` → `SidePanel` → `QueuePanel`.

- [ ] **Step 1: `SidePanel` imzasına ekle**

Bugünkü hâli:

```jsx
export default function SidePanel({ job, error, errorField, busyElsewhere, settings, settingsError,
                                    project, stopping, queue, failures, models, modelsError,
                                    producers, frames, selected, onQueueLayer,
                                    onGenerate, onStop, onResume, onCancel, onClearError,
                                    onRetryAll, onRetrySettings }) {
```

Yerine:

```jsx
export default function SidePanel({ job, known, error, errorField, busyElsewhere, settings,
                                    settingsError, project, stopping, queue, failures, models,
                                    modelsError, producers, frames, selected, onQueueLayer,
                                    onGenerate, onStop, onResume, onCancel, onClearError,
                                    onRetryAll, onRetrySettings }) {
```

- [ ] **Step 2: `SidePanel` bayrağı panele versin**

Bugünkü hâli:

```jsx
        {open === "queue" && (
          <QueuePanel job={job} error={error} errorField={errorField}
```

Yerine:

```jsx
        {open === "queue" && (
          <QueuePanel job={job} known={known} error={error} errorField={errorField}
```

- [ ] **Step 3: `ProjectScreen` bayrağı hook'tan okusun**

Bugünkü hâli:

```jsx
  const { job, frames, error, errorField, stopping, queue, failures, current, currentLayer,
          retryAll, queueLayer,
```

Yerine:

```jsx
  const { job, known, frames, error, errorField, stopping, queue, failures, current, currentLayer,
          retryAll, queueLayer,
```

- [ ] **Step 4: `ProjectScreen` bayrağı sütuna versin**

Bugünkü hâli:

```jsx
        <SidePanel job={job} error={saveError || error} errorField={errorField}
```

Yerine:

```jsx
        <SidePanel job={job} known={known} error={saveError || error} errorField={errorField}
```

- [ ] **Step 5: Takımın tamamen yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **0 failed**, 571 tests.

---

### Task 3: Derle, doğrula, commit'le

- [ ] **Step 1: Ön yüzü derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Değişen her şeyi gör**

Run: `git status --short`

Expected: üç kaynak dosya, `dist/` altındakiler ve `docs/superpowers`. **Test dosyaları bu listede
olmamalı.**

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the queue panel stops guessing before the first answer

Until the server had reported anything, the panel said the queue was empty and
told the user to send frames from the photo panel -- over a run that may well
have been flowing. idle is a placeholder, not an answer.

Nothing new was needed. useGeneration has kept a flag for whether the server has
spoken on this mount since the day the placeholder was named, and its comment
says what this item says: a screen that acts on the placeholder decides on a
state nobody reported. The flag was computed and returned and never read. What
was missing was the wire, from the hook through the screen and the column to the
panel.

Not knowing now looks the way not knowing looks everywhere else in this app: the
panel waits in its own column and writes nothing. The flag takes no default --
a forgotten wire is exactly what this was, and a default would let the next one
pass unnoticed.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** Panelin sessizliği → Task 1. Kablo → Task 2. Derlenmiş çıktı → Task 3.

**Ad tutarlılığı:** Dört dosyada tek ad, `known`, ve `useGeneration` onu zaten böyle döndürüyor.

**Bilerek dışarıda:** `PhotoDetail` bayrağı almıyor. O da `useGeneration` kullanıyor ama kuyruk
paneli yok; okuyacağı bir yer olmadan geçirmek, kullanılmayan ikinci bir kablo olurdu — bu maddenin
düzelttiği şeyin aynısı.
