# Madde 323 — Prompt listesinin okunuşu, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Dört test satırını
> koordinatör koşar; commit onun.

**Hedef:** `ba83282f`'in altı kırmızı testi yeşile, gerisi yeşil kalarak.

**Spec:** [m323 uygulama turu](../specs/2026-09-24-queen-editor-m323-prompt-listesi-okunusu-uygulama-design.md)

## Her yere geçerli kurallar

- Yalnız `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx` değişiyor. Testlere,
  sunucuya ve dist'e dokunulmuyor.
- Yorum İngilizce ve yalnız bugün doğru olanı söylüyor.

---

## Görev 1: `promptCount` — `NO_PROMPTS`'un ve `promptsIn`'in yerine

`NO_VARIANTS`'ın altındaki `NO_PROMPTS` sabiti yorumuyla, ve `promptsIn` docstring'iyle gidiyor.
Yerine:

```js
// A list pasted out of a notebook cell may carry its name in front: prompt_list.py's own pattern.
const NAMED = /^[A-Za-z_]\w*\s*=\s*/;
// One quoted item and what follows it -- a comma, or the end of the list. Either quote; a backslash
// takes the next character with it, so an escaped quote does not end the item.
const ITEM = /^(["'])((?:\\.|(?!\1)[^\\])*)\1\s*(?:,\s*|$)/;

/** How many prompts a press would send, or 0 when the screen cannot tell.
 *
 * A preview for the line under the button, never a rule (FOUNDATION 4): the press goes whatever this
 * makes of the list, and the server's own reading (prompt_list.py) decides and says what is wrong.
 * It reads what that one reads as far as a count needs -- a JSON array or a Python list or tuple of
 * strings in either quote, with an optional `NAME =` in front, blank items left out. A JSON array of
 * strings is written the way a Python list is, so one loop reads both. The items are counted, never
 * decoded: a corner only Python reads, like a triple-quoted item, leaves the line empty and is still
 * sent.
 */
function promptCount(text) {
  const body = text.trim().replace(NAMED, "");
  const close = { "[": "]", "(": ")" }[body[0]];
  if (!close || !body.endsWith(close)) return 0;
  let rest = body.slice(1, -1).trim();
  let count = 0;
  while (rest) {
    const item = ITEM.exec(rest);
    if (!item) return 0;
    if (item[2].trim()) count += 1;
    rest = rest.slice(item[0].length);
  }
  return count;
}
```

## Görev 2: `refusalOf` artık listeye bakmıyor

```js
function refusalOf(words, can, scope, scoped, variants, fromPool) {
  if (variants === "") return NO_VARIANTS;
  // From the pool there are no frames to weigh, and the list is the server's to read
  // (prompt_list.py): what is wrong with it comes back in its own words.
  if (fromPool) return null;
```

`handleAdd`'deki çağrı son argümanı bırakıyor: `refusalOf(words, can, scope, scoped, shownVariants,
fromPool)`.

## Görev 3: Satır

`const written = promptsIn(prompts);` → `const listed = promptCount(prompts);`. Referanstan'ın dalı:

```jsx
        ) : fromPool ? (
          // Nothing is counted from the gallery here: a press makes a card per prompt per variant,
          // and the line says so in the user's own arithmetic. With nothing it can count it says
          // nothing -- what is wrong with a list is the server's to say, after the press.
          listed ? (
            <Note size={12} style={{ color: "var(--ink-3)", textAlign: "center" }}>
              {`${listed} prompt × ${Number(shownVariants) || 0} varyant = `
                + `${listed * (Number(shownVariants) || 0)} kart`}
            </Note>
          ) : null
        ) : owed ? (
```

## Görev 4: Denetim ve teslim

- [ ] `NO_PROMPTS`, `promptsIn` ve `written` dosyada kalmadı *(Grep)*.
- [ ] Koordinatöre dönüş: değişen dosyalar, spec'in dikte etmediği kararlar, emin olunmayanlar.
