import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import ChatScreen from "./ChatScreen.jsx";

const PROJECT = { id: "p1", name: "Thesis research" };
const CHAT = {
  id: "c1",
  title: "Write the intro",
  messages: [
    { role: "user", at: new Date(2026, 7, 9, 11, 4).toISOString(), text: "Write the intro" },
    { role: "ai", at: new Date(2026, 7, 9, 11, 5).toISOString(), text: "Here it is." },
  ],
};

test("the breadcrumb names the project and the chat", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText(/Thesis research/)).toBeTruthy();
  expect(screen.getByText("Write the intro", { selector: ".chat__title" })).toBeTruthy();
});

test("a user message is labelled You with its wall clock", () => {
  // The prototype took the name from a prop we never shipped; an unnamed user is "You".
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("You · 11:04")).toBeTruthy();
});

test("an answer is labelled Mira", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("Mira · 11:05")).toBeTruthy();
});

test("both messages are drawn", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("Here it is.")).toBeTruthy();
});

test("a chat that does not exist says so instead of crashing", () => {
  render(<ChatScreen project={PROJECT} chat={null} missing />);
  expect(screen.getByText("That chat does not exist.")).toBeTruthy();
});

test("a failure is shown above the composer", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} error="POST failed with 500" />);
  expect(screen.getByText(/failed with 500/)).toBeTruthy();
});
