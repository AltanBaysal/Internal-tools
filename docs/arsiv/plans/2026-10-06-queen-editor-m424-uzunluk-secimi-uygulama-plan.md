# Madde 424 — Uzunluk seçimi, uygulama turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test turunun 24 kırmızısını, testlerin tarif ettiği koddan fazlasını yazmadan yeşile çevirmek.

**Architecture:** `shared/api.js`'e kapının iki fonksiyonu; `useVideoLength` kancası H3'ü, okumayı,
belleği ve yazmayı tek yerde tutar; `LayerPanel` ve `PhotoDetail` yalnız onun `seconds`'ına bakar.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [m424 uygulama turu](../specs/2026-10-06-queen-editor-m424-uzunluk-secimi-uygulama-design.md),
[m424 test turu](../specs/2026-10-06-queen-editor-m424-uzunluk-secimi-testler-design.md)

## Global Constraints

- Kod ve yorumlar İngilizce; ekrandaki sözler Türkçe, tasarımdaki gibi.
- Sayıyla birimi arasında ` `.
- Test dosyalarına dokunulmaz. `dist` kurulmaz. Sunucuya dokunulmaz.
- Commit mesajında çift tırnak yok; amend yok.

---

### Görev 1: `shared/api.js` — kapının iki fonksiyonu

**Files:** Modify: `queen-editor/frontend/src/shared/api.js` (`saveReferenceSettings`'in altına).

**Interfaces:** Produces — `getVideoLength(project) → Promise<number>`,
`saveVideoLength(project, seconds) → Promise<null>`.

- [ ] **Adım 1**

```js
// How long the project's H3 videos run (madde 422, 424): 4, 8 or 12 seconds. With nothing saved the
// server answers 8 -- the default is its to say, not the screen's.
export async function getVideoLength(project) {
  const body = await request(`/api/projects/${encodeURIComponent(project)}/video-length`);
  return body.seconds;
}

// 204 with no body: the screen already shows what it sent.
export async function saveVideoLength(project, seconds) {
  return request(`/api/projects/${encodeURIComponent(project)}/video-length`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seconds }),
  });
}
```

### Görev 2: `useVideoLength.js` — yeni kanca

**Files:** Create: `queen-editor/frontend/src/features/photo_generation/useVideoLength.js`.

**Interfaces:** Consumes — Görev 1. Produces — `useVideoLength(project, videoRow) → { seconds:
number | null, choose(seconds) → Promise }`; `choose` yazılamazsa geri döner ve hatayı fırlatır.

- [ ] **Adım 1**

```js
import { useEffect, useRef, useState } from "react";

import { getVideoLength, saveVideoLength } from "../../shared/api.js";

// The length the server last confirmed, per project, for the length of a visit. The video panel is
// built afresh on every opening and every step in and out of a frame; without this its length block
// would come in a beat after the panel each time and push everything under it down. Asked again on
// every mount all the same: the record on disk is the answer.
const CONFIRMED = new Map();

/** The project's H3 video length (madde 424): the number to show and say, and how to choose one.
 *
 * `videoRow` is the producers' video row. Only an H3 session has a length to choose -- WAN's is fixed
 * in its graph -- and the server says which session this is: `reads_references` is written from the
 * same setting that puts a length on every H3 job. No row means the model is not read yet, and then
 * nobody can say. `seconds` is null there, and while the length is not known: nothing drawn and
 * nothing promised, rather than a number that may be wrong.
 */
export function useVideoLength(project, videoRow) {
  const h3 = videoRow?.reads_references === true;
  const [known, setKnown] = useState(() => CONFIRMED.get(project) ?? null);
  // A press made while the read was on its way is newer than what the read will answer.
  const pressed = useRef(false);

  useEffect(() => {
    if (!h3) return undefined;
    let alive = true;
    getVideoLength(project)
      .then((seconds) => {
        if (pressed.current) return;
        CONFIRMED.set(project, seconds);
        if (alive) setKnown(seconds);
      })
      // Unread, the length stays unknown: the block stays out and no sentence promises one. A dead
      // server is already said by the gallery's own poll, in the panel's card.
      .catch(() => {});
    return () => { alive = false; };
  }, [project, h3]);

  // Shown at once, the design's way, then written. A write that fails takes the screen back to what
  // the project holds: a length shown as chosen that the queue will not use would be a lie.
  function choose(seconds) {
    pressed.current = true;
    setKnown(seconds);
    return saveVideoLength(project, seconds)
      .then(() => { CONFIRMED.set(project, seconds); })
      .catch((err) => {
        setKnown(CONFIRMED.get(project) ?? null);
        throw err;
      });
  }

  return { seconds: h3 ? known : null, choose };
}
```

### Görev 3: `LayerPanel.jsx` — blok, basış, cümleler

**Files:** Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`.

**Interfaces:** Consumes — Görev 2.

- [ ] **Adım 1: İçe aktarma ve uzunluklar**

```js
import { useVideoLength } from "./useVideoLength.js";

// The lengths an H3 video can be made at, in seconds (madde 422). The server refuses any other, so
// this is only what the segment offers.
const LENGTHS = [4, 8, 12];
```

- [ ] **Adım 2: Bileşenin başındaki yorum** — *"the length is fixed, so the only questions left are which
  frames, and how many of each"* yerine: *"so the questions left are which frames, how many of each,
  and -- for an H3 video -- how long"*.

- [ ] **Adım 3: Kanca, cümlenin sonu, basış**

```js
  // The project's setting, not this panel's: it is read and written through the project, and only a
  // video has one -- the sound panel is handed no video row (madde 424).
  const { seconds: length, choose: chooseLength } =
    useVideoLength(project, layer === "video" ? producer : null);
  // What a video will be, said once at the end of whichever sentence is on show. The space is
  // unbreakable so the number never ends a line with its unit alone on the next.
  const lengthSaid = length === null ? "" : ` ${length} sn.`;

  // A press of its own, so its answer takes the slot under the button: nothing when it is written,
  // the sentence that came back when it is not -- where the panel says its other failures.
  function handleLength(seconds) {
    setRefused(null);
    chooseLength(seconds).catch((err) => {
      setAdded(null);
      clearTimeout(fade.current);
      setRefused(err.message);
    });
  }
```

- [ ] **Adım 4: Blok, Model kutusunun hemen altında**

```jsx
      {length !== null && (
        /* Under the Model box and above everything a tab has of its own, so changing tab leaves it
           where it is (madde 424). Not drawn until there is a length to show: under WAN, while the
           model or the length is not read yet, nothing stands in for it. */
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Mono size={11} data-label style={LABEL}>Video uzunluğu</Mono>
          <div className="wf-segment" style={{ display: "flex" }}>
            {LENGTHS.map((one) => (
              <button key={one} type="button" aria-label={`${one} saniye`}
                      className={length === one ? "is-on" : ""} style={{ flex: 1 }}
                      onClick={() => handleLength(one)}>
                {`${one} sn`}
              </button>
            ))}
          </div>
        </div>
      )}
```

- [ ] **Adım 5: Cümleler** — Referanstan: `` `${listed} prompt × ${n} varyant = ${listed * n} kart.` +
  lengthSaid ``; Kareden: `{… said.tail}{lengthSaid}`.

### Görev 4: `PhotoDetail.jsx` — iki not

**Files:** Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`.

**Interfaces:** Consumes — Görev 2, `useProducers()` (`features/producers/useProducers.js`).

- [ ] **Adım 1: Model ve uzunluk**

```js
import { useProducers } from "../producers/useProducers.js";
import { useVideoLength } from "./useVideoLength.js";

  // Which video model the session has, for the one thing this page says about it: the length a new
  // video gets (madde 424). The answer is remembered for the visit, so stepping in costs nothing.
  const { producers } = useProducers();
  const { seconds: length } =
    useVideoLength(project, (producers || []).find((row) => row.id === "video"));
  // The panel's own ending: unbreakable, so the number keeps its unit on its line.
  const lengthSaid = length === null ? "" : ` ${length} sn.`;
```

- [ ] **Adım 2: Yeniden üret'in notu** — `… {nounOf(picked, "video")}.{lengthSaid}`.

- [ ] **Adım 3: Tekrar dene'nin notu, düğmenin hemen altında**

```jsx
              {openState === "failed" && open === "video" && length !== null && (
                /* The red video is made again at the project's length now, and this is the one
                   place a retry can say so (madde 424). */
                <Note size={12} style={{ color: "var(--ink-3)", textAlign: "center" }}>
                  Aynı kare yeniden denenir.{lengthSaid}
                </Note>
              )}
```

### Görev 5: Yeşili gör ve commit'le

- [ ] **Adım 1: Dört satır, paralel, yazıldığı gibi** — beklenen: dördü de yeşil.
- [ ] **Adım 2: Commit**

```
git add docs/specs/2026-10-06-queen-editor-m424-uzunluk-secimi-uygulama-design.md docs/plans/2026-10-06-queen-editor-m424-uzunluk-secimi-uygulama-plan.md queen-editor/frontend/src/shared/api.js queen-editor/frontend/src/features/photo_generation/useVideoLength.js queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx
git commit -m "feat(queen-editor): 424 -- …" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
