import { expect, test } from "vitest";

import { parseBlocks, parseInline } from "./markdown.js";

const only = (text) => {
  const blocks = parseBlocks(text);
  expect(blocks.length).toBe(1);
  return blocks[0];
};

// The text of a token tree, with the markers gone -- enough to say what survived the parse.
const flatten = (tokens) =>
  tokens.map((token) => (token.tokens ? flatten(token.tokens) : (token.text ?? ""))).join("");

test("four heading levels are headings", () => {
  for (const level of [1, 2, 3, 4]) {
    const block = only(`${"#".repeat(level)} Title`);
    expect(block.type).toBe("heading");
    expect(block.level).toBe(level);
    expect(flatten(block.inline)).toBe("Title");
  }
});

test("a fifth level is not a heading", () => {
  // The design names four. What it does not name stays as it was typed.
  const block = only("##### Title");
  expect(block.type).toBe("paragraph");
  expect(flatten(block.inline)).toBe("##### Title");
});

test("a fence keeps its text exactly and remembers the language", () => {
  const block = only("```python\nx = 1\n\ny = 2\n```");
  expect(block.type).toBe("code");
  expect(block.lang).toBe("python");
  expect(block.text).toBe("x = 1\n\ny = 2");
});

test("a fence with no language still parses", () => {
  expect(only("```\nplain\n```").lang).toBe(null);
});

test("a fence that never closes ends with the text", () => {
  // Streaming safety, and it comes free: an unfinished block must not swallow the layout.
  const block = only("```js\nhalf(");
  expect(block.type).toBe("code");
  expect(block.text).toBe("half(");
});

test("markers inside a fence are not markers", () => {
  expect(only("```\n**bold**\n```").text).toBe("**bold**");
});

test("both list markers make a list", () => {
  for (const marker of ["-", "*", "+"]) {
    const block = only(`${marker} one\n${marker} two`);
    expect(block.type).toBe("list");
    expect(block.ordered).toBe(false);
    expect(block.items.map((item) => flatten(item.inline))).toEqual(["one", "two"]);
  }
});

test("a numbered list is ordered", () => {
  const block = only("1. one\n2. two");
  expect(block.type).toBe("list");
  expect(block.ordered).toBe(true);
  expect(block.items.length).toBe(2);
});

test("an indented item belongs to the one above it", () => {
  // Drawn flat, a nested bullet reads as literal text inside its parent -- broken, not missing.
  const block = only("- one\n  - deeper\n- two");
  expect(block.items.length).toBe(2);
  const nested = block.items[0].blocks;
  expect(nested.length).toBe(1);
  expect(nested[0].type).toBe("list");
  expect(flatten(nested[0].items[0].inline)).toBe("deeper");
});

test("a table needs its separator row", () => {
  const block = only("| a | b |\n| --- | --- |\n| 1 | 2 |");
  expect(block.type).toBe("table");
  expect(block.head.map(flatten)).toEqual(["a", "b"]);
  expect(block.rows.map((row) => row.map(flatten))).toEqual([["1", "2"]]);
});

test("a row of pipes with no separator is just text", () => {
  expect(only("| a | b |").type).toBe("paragraph");
});

test("alignment marks a table without moving anything", () => {
  // The colons say "this is a table"; the design never asks for a right-aligned column.
  const block = only("| a |\n| :---: |\n| 1 |");
  expect(block.type).toBe("table");
});

test("a quote holds blocks of its own", () => {
  const block = only("> # Inside\n> text");
  expect(block.type).toBe("quote");
  expect(block.blocks[0].type).toBe("heading");
  expect(block.blocks[1].type).toBe("paragraph");
});

test("three dashes are a rule", () => {
  expect(only("---").type).toBe("rule");
  expect(only("***").type).toBe("rule");
});

test("a blank line separates two paragraphs", () => {
  const blocks = parseBlocks("one\n\ntwo");
  expect(blocks.length).toBe(2);
  expect(blocks.every((block) => block.type === "paragraph")).toBe(true);
});

test("a single newline inside a paragraph is a line break", () => {
  // Markdown's own rule turns it into a space; in a chat that glues a list of lines into one wall.
  const block = only("one\ntwo");
  expect(block.inline.some((token) => token.type === "break")).toBe(true);
});

test("the four inline markers are read", () => {
  expect(parseInline("**b**")[0].type).toBe("strong");
  expect(parseInline("*i*")[0].type).toBe("em");
  expect(parseInline("_i_")[0].type).toBe("em");
  expect(parseInline("~~s~~")[0].type).toBe("del");
  expect(parseInline("`c`")[0].type).toBe("code");
});

test("emphasis nests", () => {
  const [strong] = parseInline("**bold *and italic***");
  expect(strong.type).toBe("strong");
  expect(strong.tokens.some((token) => token.type === "em")).toBe(true);
});

test("code wins over every other marker", () => {
  const [code] = parseInline("`**not bold**`");
  expect(code.type).toBe("code");
  expect(code.text).toBe("**not bold**");
});

test("a link keeps its text and its target", () => {
  const [link] = parseInline("[docs](https://example.com)");
  expect(link.type).toBe("link");
  expect(link.href).toBe("https://example.com");
  expect(flatten([link])).toBe("docs");
});

test("mail is a target too", () => {
  expect(parseInline("[a](mailto:a@b.c)")[0].type).toBe("link");
});

test("a script target is not a link", () => {
  // The one place a rendered answer could reach out and touch the app.
  const tokens = parseInline("[x](javascript:alert(1))");
  expect(tokens.every((token) => token.type !== "link")).toBe(true);
  expect(flatten(tokens)).toContain("javascript:");
});

test("an unmatched marker stays as it was typed", () => {
  expect(flatten(parseInline("2 * 3 * 4"))).toBe("2 * 3 * 4");
  expect(parseInline("2 * 3 * 4").every((token) => token.type === "text")).toBe(true);
});

test("empty text is no blocks at all", () => {
  expect(parseBlocks("")).toEqual([]);
  expect(parseBlocks("   \n\n ")).toEqual([]);
});
