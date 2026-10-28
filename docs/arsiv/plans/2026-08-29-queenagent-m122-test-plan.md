# Madde 122 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-29-queenagent-m122-liste-testler-design.md](../specs/2026-08-29-queenagent-m122-liste-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `queen-agent/frontend/src/shared/markdown.test.js` — liste testlerinin yanına

```js
test("numbered items separated by blank lines are one list", () => {
  // 28 Aug: a model writes a blank between its numbered items, and split into three <ol>s the
  // browser counted 1, 1, 1.
  const block = only("1. one\n\n2. two\n\n3. three");
  expect(block.type).toBe("list");
  expect(block.items.length).toBe(3);
});

test("bulleted items separated by blank lines are one list too", () => {
  const block = only("- one\n\n- two");
  expect(block.items.length).toBe(2);
});

test("a blank line still ends the list when what follows is no item", () => {
  const blocks = parseBlocks("1. one\n\nafter");
  expect(blocks.map((block) => block.type)).toEqual(["list", "paragraph"]);
});
```

## B. `queen-agent/frontend/src/features/workspace/Markdown.test.jsx` — liste testinin yanına

```jsx
test("blank-separated numbered items count on in one ol", () => {
  const container = draw("1. one\n\n2. two\n\n3. three");
  expect(container.querySelectorAll("ol").length).toBe(1);
  expect(container.querySelectorAll("ol li").length).toBe(3);
});
```

## Beklenen kırmızı: `markdown.test.js` 2, `Markdown.test.jsx` 1 *(paragraf testi korunan davranışı sabitliyor, bugün de yeşil)*.

## Bilerek yapılmayanlar: kaynak açılmaz; `dist` derlenmez.
