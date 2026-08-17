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

// Motion is a fade of 140-220ms and the rail's width, and nothing else. A name that describes a
// movement is part of the drift, so only one animation name survives and it says what it does.
test("there is one fade and one blink, and nothing else", () => {
  expect(APP).toContain("@keyframes fadeIn");
  expect(APP).toContain("@keyframes blink");
  expect(APP).not.toContain("@keyframes riseIn");
  expect(APP).not.toContain("@keyframes slideIn");
  expect(APP).not.toContain("@keyframes spin");
});

test("no keyframe moves anything", () => {
  // Not sideways, not upwards: an element that has been laid out stays where it was put.
  const frames = APP.slice(APP.indexOf("@keyframes"));
  expect(frames).not.toContain("transform");
});

test("every animation stays inside the band", () => {
  const durations = [...WORKSPACE.matchAll(/animation: (\w+) ([\d.]+)s/g)];
  expect(durations.length).toBeGreaterThan(0);
  for (const [, name, seconds] of durations) {
    if (name === "blink") continue; // the design's own three dots, and they never settle
    expect(Number(seconds)).toBeLessThanOrEqual(0.22);
  }
  expect(WORKSPACE).not.toContain("animation: spin");
});

test("the rail's width transition is the one motion that is not a fade", () => {
  expect(WORKSPACE).toContain("transition: width 220ms ease");
});

// The page itself never scrolls -- only inner regions do. The shell is what holds that line.
test("the shell is the height of the visible window and no less", () => {
  // A 600px floor is exactly what makes a short window scroll the page.
  const shell = APP.slice(APP.indexOf("\n.app-shell {"));
  const rule = shell.slice(0, shell.indexOf("}"));
  expect(rule).toContain("height: 100dvh");
  expect(rule).not.toContain("min-height");
});

test("the only destructive control there is today reaches for the new red", () => {
  // The three surfaces the design names arrive with Madde 17, 18 and 19; the row's x is here now.
  expect(rule(WORKSPACE, ".row-x:hover")).toContain("var(--destructive)");
});
