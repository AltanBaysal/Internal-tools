import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ChatScreen from "./ChatScreen.jsx";

const PROJECT = { id: "p1", name: "Thesis research" };
const NOW = new Date().toISOString();
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

test("the way back to the project stays", () => {
  // The design asks for this one by name: a chat header is "← project name".
  const onBack = vi.fn();
  render(<ChatScreen project={PROJECT} chat={CHAT} onBack={onBack} />);
  fireEvent.click(screen.getByRole("button", { name: /Thesis research/ }));
  expect(onBack).toHaveBeenCalled();
});

test("nothing is written under the composer", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.queryByText("save the answer as a file")).toBeNull();
});

test("a user message is labelled You with its wall clock", () => {
  // The prototype took the name from a prop we never shipped; an unnamed user is "You".
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("You · 11:04")).toBeTruthy();
});

test("an answer is labelled QueenAgent", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("QueenAgent · 11:05")).toBeTruthy();
});

test("both messages are drawn", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("Here it is.")).toBeTruthy();
});

test("a chat that does not exist says so instead of crashing", () => {
  render(<ChatScreen project={PROJECT} chat={null} missing />);
  expect(screen.getByText("That chat does not exist.")).toBeTruthy();
  expect(screen.queryByTestId("skeleton")).toBeNull();
});

test("a chat still on its way draws blocks", () => {
  render(<ChatScreen project={PROJECT} chat={null} />);
  expect(screen.getByTestId("skeleton")).toBeTruthy();
});

test("waiting for an answer draws three dots and no fake text", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  expect(screen.getByTestId("thinking")).toBeTruthy();
});

test("nothing blinks when nothing is pending", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.queryByTestId("thinking")).toBeNull();
});

test("text that is still arriving is drawn as QueenAgent's turn", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here it" />);
  expect(screen.getByTestId("streaming").textContent).toContain("Here it");
  // The dots are only for the wait before the first piece.
  expect(screen.queryByTestId("thinking")).toBeNull();
});

test("a failure states what happened and repeats the server's words", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} error="POST failed with 500" />);
  expect(screen.getByText("Couldn't get a response.")).toBeTruthy();
  // No guessed cause: a bad key and a wrong model raise this same card.
  expect(screen.queryByText(/connection dropped/)).toBeNull();
  expect(screen.getByText(/failed with 500/)).toBeTruthy();
});

test("Try again asks again", () => {
  const onRetry = vi.fn();
  render(<ChatScreen project={PROJECT} chat={CHAT} error="boom" onRetry={onRetry} />);
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(onRetry).toHaveBeenCalled();
});

test("a file on its way shows a dashed card with no name on it", () => {
  // No name yet: the model's wish still has to be cleaned and a clash still has to be resolved.
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking creatingFile />);
  expect(screen.getByText("creating file…")).toBeTruthy();
});

test("nothing dashed is drawn when no file is being written", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  expect(screen.queryByText("creating file…")).toBeNull();
});

test("a file that lands mid-answer becomes a card straight away", () => {
  render(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      streamingText="Saved it."
      createdFiles={["outline.md"]}
    />,
  );
  expect(screen.getByText("outline.md")).toBeTruthy();
  expect(screen.getByText("✓ saved to project")).toBeTruthy();
});

function withFiles(...names) {
  return names.map((name) => ({ name, ext: name.split(".").pop(), modifiedAt: NOW }));
}

test("the file a stored reply produced is drawn under that reply", () => {
  const chat = {
    ...CHAT,
    messages: [
      CHAT.messages[0],
      { ...CHAT.messages[1], files: ["outline.md", "sources.txt"] },
    ],
  };
  render(
    <ChatScreen project={PROJECT} chat={chat} files={withFiles("outline.md", "sources.txt")} />,
  );
  // Two files can be born in one turn, so the card is not a single slot.
  expect(screen.getByText("outline.md", { selector: ".file-card__name" })).toBeTruthy();
  expect(screen.getByText("sources.txt", { selector: ".file-card__name" })).toBeTruthy();
});

test("the chip on a card comes from the name the reply remembers", () => {
  const chat = { ...CHAT, messages: [CHAT.messages[0], { ...CHAT.messages[1], files: ["a.txt"] }] };
  render(<ChatScreen project={PROJECT} chat={chat} files={withFiles("a.txt")} />);
  expect(screen.getByText("txt", { selector: ".file-card .file-chip" })).toBeTruthy();
});

test("a card is not drawn for a file the project no longer holds", () => {
  const chat = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], files: ["deleted-away.md"] }],
  };
  // The message remembers what it produced and is never rewritten; the card is that memory crossed
  // with what exists now, so a deleted file simply stops having one.
  render(<ChatScreen project={PROJECT} chat={chat} files={withFiles("outline.md")} />);
  expect(screen.queryByText("deleted-away.md")).toBeNull();
});

test("the rail lists the project's files beside the conversation", () => {
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  render(<ChatScreen project={PROJECT} chat={CHAT} files={files} />);
  expect(screen.getByTestId("file-rail").textContent).toContain("outline.md");
});
