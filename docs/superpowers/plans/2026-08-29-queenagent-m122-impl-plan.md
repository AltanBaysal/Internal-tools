# Madde 122 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-29-queenagent-m122-liste-uygulama-design.md](../specs/2026-08-29-queenagent-m122-liste-uygulama-design.md)
**Testler kırmızı commit'te**; bu tur yalnız `markdown.js`'in `listFrom`'una dokunur.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `listFrom` döngüsünün başına boş satır dalı

```js
    if (!lines[at].trim()) {
      // A blank line ends the list only when what follows is not more of it: models write a
      // blank between numbered items, and split into separate lists every <ol> counts from 1.
      let ahead = at;
      while (ahead < lines.length && !lines[ahead].trim()) ahead += 1;
      const beyond =
        ahead < lines.length ? (BULLET.exec(lines[ahead]) ?? NUMBER.exec(lines[ahead])) : null;
      if (!beyond || beyond[1].length < indent) break;
      if (beyond[1].length === indent && !BULLET.test(lines[ahead]) !== ordered) break;
      at = ahead;
      continue;
    }
```

## B. `dist` aynı commit'te: `npm run build --prefix queen-agent/frontend`

## Beklenen yeşil: frontend 568'in tamamı; backend olduğu gibi.

## Bilerek yapılmayanlar: `<ol start>` yok — gerekçesi tasarımda; `Markdown.jsx` değişmiyor.
