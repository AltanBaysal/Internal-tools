import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "vitest";

// A lock, not a behaviour test. jsdom neither loads this stylesheet nor evaluates media queries, so
// nothing here proves the sidebar narrows -- that is Madde 35's manual pass. What it does prove is
// that the four widths the design specifies are still the four widths the stylesheet carries.
//
// Read off disk rather than imported: vitest serves modules over its own protocol, so neither
// import.meta.url nor `?raw` hands back the file. The working directory is the frontend root.
const CSS = readFileSync(resolve(process.cwd(), "src/features/workspace/workspace.css"), "utf8");

// The `.sidebar { ... }` rule inside a given media block, or at the top level when none is named.
function sidebarRule(maxWidth) {
  const scope = maxWidth
    ? CSS.slice(CSS.indexOf(`@media (max-width: ${maxWidth}px)`))
    : CSS;
  const start = scope.indexOf(".sidebar {");
  expect(start).toBeGreaterThan(-1);
  return scope.slice(start, scope.indexOf("}", start));
}

test("the sidebar starts at its full width", () => {
  expect(sidebarRule()).toContain("width: 280px");
});

test("it narrows in three steps rather than one", () => {
  expect(sidebarRule(1000)).toContain("width: 226px");
  expect(sidebarRule(780)).toContain("width: 198px");
  expect(sidebarRule(640)).toContain("width: 172px");
});

test("only the narrowest step tightens the padding", () => {
  // Giving up width is not the same as giving up room to breathe: the padding holds until there is
  // no width left to hold it.
  expect(sidebarRule()).toContain("padding: 18px 14px");
  expect(sidebarRule(1000)).not.toContain("padding");
  expect(sidebarRule(780)).not.toContain("padding");
  expect(sidebarRule(640)).toContain("padding: 16px 10px");
});

test("the layout breakpoint no longer sets the sidebar width", () => {
  // Madde 33 brings the layout onto the same measurements; until then it keeps its own, and the
  // sidebar's four steps are the only thing that decides its width.
  const layout = CSS.slice(CSS.indexOf("@media (max-width: 1100px)"));
  expect(layout.slice(0, layout.indexOf("}", layout.indexOf(".chat-layout")))).not.toContain(
    ".sidebar",
  );
});
