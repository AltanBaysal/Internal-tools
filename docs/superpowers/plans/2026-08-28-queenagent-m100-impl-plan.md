# Madde 100 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m100-hatirlama-uygulama-design.md](../specs/2026-08-28-queenagent-m100-hatirlama-uygulama-design.md)
**Tur 1:** yedi kırmızı commit'lendi *(`527b378`)*. Bu turda test yazılmaz.
**Komut:** `npm test --prefix queen-agent/frontend`

---

## 1 · `src/shared/remembered.js` — yeni dosya

```js
import { useEffect, useState } from "react";

// A value this browser keeps across a reload. Not the server: since Madde 86 nothing there reads a
// selection back, and what is kept here is a preference of this browser rather than the chat's own
// record. Madde 86's worry does not come back either -- there is still one value, and this is only
// where it is born.
//
// Every touch of storage is wrapped. A browser with it switched off, or a private window, throws on
// the read as well as the write, and what is lost is the memory: the selection still holds for the
// session it was made in.
const PREFIX = "queenagent.";

function kept(name) {
  try {
    return window.localStorage.getItem(PREFIX + name);
  } catch {
    return null;
  }
}

function keep(name, value) {
  try {
    window.localStorage.setItem(PREFIX + name, value);
  } catch {
    // Nothing to do and nothing to say.
  }
}

export function useRemembered(name, fallback) {
  // Read in the initialiser, so it happens once on the first render rather than on every one --
  // and what a later read would find is what this already wrote.
  const [value, setValue] = useState(() => {
    const written = kept(name);
    // null is "never chosen" and "" is "chosen and then let go". Folding the two together would
    // undo the user's dropping of a skill on every reload.
    return written === null ? fallback : written;
  });

  // The first render writes back what it just read, which changes nothing. A flag to skip that one
  // pass would be its own thing to get wrong, for no gain.
  useEffect(() => {
    keep(name, value);
  }, [name, value]);

  return [value, setValue];
}
```

## 2 · `src/App.jsx`

Import satırlarına:

```js
import { useRemembered } from "./shared/remembered.js";
```

`lastSkill`:

```js
  // The last skill picked, and what the next chat is born with. Remembered by the browser since
  // Madde 100: a five-step flow that loses its skill on a reload sends the next turn with no
  // instruction, and nothing on screen says so.
  const [lastSkill, setLastSkill] = useRemembered("skill", "");
```

`lastMode` **değişmiyor**. Yenilemeden sonra edit'e dönüyor, yani izin verilen kipe; unutulmasının
bir bedeli yok.

## 3 · Koş

```
npm test --prefix queen-agent/frontend
python -m pytest queen-agent -q
```

Yedi kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 4 · `dist`

```
npm run build --prefix queen-agent/frontend
```

Aynı commit'te.

## 5 · Commit

```
feat(queen-agent): the browser keeps the skill that was picked
```
