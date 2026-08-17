import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "vitest";

// A lock, not a behaviour test -- the same kind as workspace.css.test.js and for the same reason:
// jsdom loads no stylesheet. What it proves is that the palette the design specifies is the palette
// the app defines, and that every surface reaches for it by name.
const read = (path) => readFileSync(resolve(process.cwd(), path), "utf8");
const APP = read("src/shared/app.css");
const WORKSPACE = read("src/features/workspace/workspace.css");

// The `:root` block, where every colour is defined and nowhere else.
const ROOT = APP.slice(APP.indexOf(":root {"), APP.indexOf("}", APP.indexOf(":root {")));

function rule(css, selector) {
  const start = css.indexOf(`${selector} {`);
  expect(start).toBeGreaterThan(-1);
  return css.slice(start, css.indexOf("}", start));
}

test("the palette carries a destructive family of its own", () => {
  // The contract's colour table and its destructive section disagreed; #B23A2E won, so the app
  // gains a real red for the first time.
  expect(ROOT).toContain("--destructive: #b23a2e");
  expect(ROOT).toContain("--destructive-hover: #973026");
  expect(ROOT).toContain("--destructive-line: #ebcfc9");
  expect(ROOT).toContain("--destructive-soft: #fdf4f2");
});

test("a filled accent and accent-coloured text darken differently", () => {
  expect(ROOT).toContain("--accent-hover: #9e5232");
  expect(ROOT).toContain("--accent-link-hover: #8f4a2c");
});

test("the one variable that used to serve both is gone", () => {
  // Left under its old name, whichever of the two it became would be unreadable.
  expect(APP).not.toContain("--accent-strong");
  expect(WORKSPACE).not.toContain("--accent-strong");
});

test("filled accent surfaces take the filled hover", () => {
  expect(rule(WORKSPACE, ".sidebar__new-chat:hover")).toContain("var(--accent-hover)");
  expect(rule(WORKSPACE, ".empty__action:hover")).toContain("var(--accent-hover)");
  expect(rule(WORKSPACE, ".composer__send--ready:hover")).toContain("var(--accent-hover)");
});

test("accent-coloured text takes the text hover", () => {
  expect(rule(APP, "a:hover")).toContain("var(--accent-link-hover)");
  expect(rule(WORKSPACE, ".strip__undo:hover")).toContain("var(--accent-link-hover)");
});

test("the only destructive control there is today reaches for the new red", () => {
  // The three surfaces the design names arrive with Madde 17, 18 and 19; the row's x is here now.
  expect(rule(WORKSPACE, ".row-x:hover")).toContain("var(--destructive)");
});
