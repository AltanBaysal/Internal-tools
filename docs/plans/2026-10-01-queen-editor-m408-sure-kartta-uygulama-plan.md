# Madde 408 — Süre kartta, uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Commit'lenmiş kırmızı testleri yeşile çevirmek: durum raporu modelin başladığı anı söyler,
karenin sayfası açık sekmenin süresini, galeri canlı süreyi gösterir.

**Architecture:** Döngü `now()`'ı üreticiden hemen önce `startedAt` olarak raporlar. Ekranda
`frame_status.jsx` `clock` ve kendi kendini çizen `LiveClock`'u verir; galeri etiketi ve karenin sayfası
onları kullanır.

**Tech Stack:** Python (Flask'sız domain), React 18, vitest.

**Spec:** [m408 uygulama turu](../specs/2026-10-01-queen-editor-m408-sure-kartta-uygulama-design.md)

## Global Constraints

- Durum alanı `startedAt`, kancanın ve galerinin adı da `startedAt`; etiket bileşeninin prop'u `since`.
- Süre `m:ss`, aşağı yuvarlanır, sıfırın altına inmez.
- UI metni Türkçe (`Üretim süresi`, `henüz başlamadı`); kod ve yorumlar İngilizce, yorum NEDEN der.
- Dist kurulmaz. Testlere dokunulmaz.

---

### Task 1: Döngü anı raporlar

**Files:** Modify `queen-editor/backend/features/photo_generation/domain/run_loop.py` — `runner.report`
çağrısı ve `started = clock()` satırı.

- [ ] İlerleme raporu bir değişkende, anı sıfırlayarak:

```python
            progress = {**queue.counts(jobs, slots),
                        "current": None if writing else current,
                        "pending": [photo_file(j["id"])
                                    for j in (owed if writing else owed[1:])],
                        "startedAt": None}
            runner.report(progress)
```

- [ ] Üretim kolunda, `started = clock()`'tan hemen önce:

```python
                    runner.report({**progress, "startedAt": now()})
                    started = clock()
```

### Task 2: `clock`, `LiveClock`, iki satırlı etiket

**Files:** Modify `queen-editor/frontend/src/features/photo_generation/frame_status.jsx`.

```jsx
import { useEffect, useState } from "react";

export function clock(seconds) {
  const whole = Math.max(0, Math.floor(seconds || 0));
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
}

export function LiveClock({ since }) {
  const [, tick] = useState(0);
  useEffect(() => {
    if (!since) return undefined;
    const timer = setInterval(() => tick((count) => count + 1), 1000);
    return () => clearInterval(timer);
  }, [since]);
  return clock(since ? (Date.now() - Date.parse(since)) / 1000 : 0);
}
```

`Pill({ color, alive, below, children })`: `below` varken dış span `flexDirection: "column"`,
`alignItems: "flex-start"`, `gap: 2`, `whiteSpace: "nowrap"`; içinde nokta+kelimeler bir satır, altında
`below`. `StatusPill({ layer, state, since })`: `below={shown.alive && since ? <LiveClock since={since} />
: null}`. `StatusPills` `since`'i geçirir.

### Task 3: Kanca ve galeri

- `useGeneration.js`: `const startedAt = current ? job.startedAt || null : null;` döndür.
- `Gallery.jsx`: prop `startedAt`; `statusOf(frame, rendering, flowing, startedAt)` →
  `[{ layer: rendering, state: "running", since: startedAt }]`.
- `ProjectScreen.jsx`: kancadan `startedAt`, `<Gallery … startedAt={startedAt} />`.

### Task 4: Karenin sayfası

**Files:** Modify `PhotoDetail.jsx`.

```jsx
function productionTime(state, seconds, since) {
  if (state === "running") {
    return (
      <span data-time style={{ display: "flex", alignItems: "center", gap: 5,
                               color: "var(--accent)" }}>
        <span aria-hidden="true" className="qe-dot qe-dot--alive"
              style={{ background: "currentColor", width: 5, height: 5 }} />
        <LiveClock since={since} />
      </span>
    );
  }
  if (state === "pending") {
    return <span data-time style={{ color: "var(--ink-3)" }}>henüz başlamadı</span>;
  }
  if (state === "done" && typeof seconds === "number") return <span data-time>{clock(seconds)}</span>;
  return null;
}
```

Bileşende: `const timeShown = productionTime(openState, (frame?.renderSeconds || {})[open], startedAt);`
ve `info` grubunda *Sıra*'dan sonra `{timeShown && <Field label="Üretim süresi" value={timeShown} />}`.

### Task 5: Yeşil koş, commit'le

- [ ] Dört satır, aynen, paralel; hepsi yeşil.
- [ ] Uygulama spec'i, plan ve kod tek commit: `feat(queen-editor): 408 -- ...`
