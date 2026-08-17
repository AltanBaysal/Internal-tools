import { render } from "@testing-library/react";
import { expect, test } from "vitest";

import Markdown from "./Markdown.jsx";

const draw = (text) => render(<Markdown text={text} />).container;

test("headings are headings", () => {
  const container = draw("# One\n\n## Two\n\n### Three\n\n#### Four");
  expect(container.querySelector("h1").textContent).toBe("One");
  expect(container.querySelector("h2").textContent).toBe("Two");
  expect(container.querySelector("h3").textContent).toBe("Three");
  expect(container.querySelector("h4").textContent).toBe("Four");
});

test("the three emphases each get their own element", () => {
  const container = draw("**b** *i* ~~s~~");
  expect(container.querySelector("strong").textContent).toBe("b");
  expect(container.querySelector("em").textContent).toBe("i");
  expect(container.querySelector("del").textContent).toBe("s");
});

test("inline code and a code block are both code", () => {
  expect(draw("`x`").querySelector("code").textContent).toBe("x");
  const block = draw("```js\nx = 1\n```");
  expect(block.querySelector("pre code").textContent).toBe("x = 1");
});

test("both list kinds are lists", () => {
  expect(draw("- one\n- two").querySelectorAll("ul li").length).toBe(2);
  expect(draw("1. one\n2. two").querySelectorAll("ol li").length).toBe(2);
});

test("a table is a table with a head", () => {
  const container = draw("| a | b |\n| --- | --- |\n| 1 | 2 |");
  expect(container.querySelectorAll("thead th").length).toBe(2);
  expect(container.querySelectorAll("tbody td").length).toBe(2);
});

test("a quote and a rule draw as themselves", () => {
  expect(draw("> quoted").querySelector("blockquote").textContent).toContain("quoted");
  expect(draw("---").querySelector("hr")).toBeTruthy();
});

test("a link opens away from the app", () => {
  // The app is a local page; a document's link belongs in a new tab, and never carries a referrer.
  const link = draw("[docs](https://example.com)").querySelector("a");
  expect(link.getAttribute("href")).toBe("https://example.com");
  expect(link.getAttribute("target")).toBe("_blank");
  expect(link.getAttribute("rel")).toContain("noreferrer");
});

test("a target that is not a link is not drawn as one", () => {
  const container = draw("[x](javascript:alert(1))");
  expect(container.querySelector("a")).toBeNull();
  expect(container.textContent).toContain("javascript:");
});

test("the wrapper is the one hook the scales hang on", () => {
  // The component never picks a size: the container it sits in does, through this class.
  expect(draw("text").querySelector(".md")).toBeTruthy();
});

test("nothing empty draws an empty wrapper rather than crashing", () => {
  expect(draw("").querySelector(".md").textContent).toBe("");
});
