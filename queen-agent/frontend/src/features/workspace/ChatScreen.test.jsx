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

// A narrow shell hides the conversation while a file is open, and CSS cannot look at a later
// sibling to find out. The screen already knows, so it says so.
test("the layout says when something is being read", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} reading={{ name: "a.md" }} />);
  expect(container.querySelector(".chat-layout--reading")).toBeTruthy();
});

test("with nothing open the layout says nothing", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(container.querySelector(".chat-layout--reading")).toBeNull();
});

// --- the calls a turn made (Madde 66) ------------------------------------------------------------

const ANSWERED = {
  ...CHAT,
  messages: [
    CHAT.messages[0],
    {
      ...CHAT.messages[1],
      calls: [
        { tool: "list_files", target: "", outcome: "No files" },
        { tool: "read_file", target: "aylin.json", outcome: "45 lines" },
      ],
    },
  ],
};

// --- one door in front of them (Madde 84) --------------------------------------------------------
//
// Madde 66 put the calls on the screen and into the record, and 78 settled what a call reads as.
// Both stand. What changed is that a call is a card now, and the cards live behind one handle: shut,
// a running turn says which step it is on and a finished one says how many there were.

test("a stored answer keeps the calls it made, behind one card", () => {
  // The half the item is really about: someone reading the chat a week later sees that the answer
  // looked before it spoke. It is behind a door now rather than spread over the answer, and the
  // door says how many steps it hides.
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  expect(container.querySelectorAll(".tool-call")).toHaveLength(0);
  expect(screen.getByRole("button", { name: /2 steps/ })).toBeTruthy();
});

test("opening the card lists every call the turn made", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(container.querySelectorAll(".tool-call")).toHaveLength(2);
});

test("pressing it again puts them away", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(container.querySelectorAll(".tool-call")).toHaveLength(0);
});

// --- the shape of the line (Madde 78) ------------------------------------------------------------
//
// The shape asked for is the one Claude Code uses: a marker, the tool with its subject in brackets,
// and how it went. What 84 took away is the ⎿ under it -- the card boundary says that now.

test("a call is drawn as its tool with the file in brackets", () => {
  // Asked for by its text: a missing line then names what was looked for, rather than failing
  // later on a null nobody can read.
  render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(screen.getByText("⏺ read_file(aylin.json)").className).toBe("tool-call__head");
});

test("a call about no file in particular is drawn without empty brackets", () => {
  // Listing a directory really is about no file, and a pair of empty brackets would announce
  // something that is not there.
  render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(screen.getByText("⏺ list_files").className).toBe("tool-call__head");
});

test("how the call went sits on the same card, not under it", () => {
  // The mark used to say "the result of the thing above". The card says it now: everything inside
  // one card belongs to one call.
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  const said = [...container.querySelectorAll(".tool-call__outcome")].map(
    (line) => line.textContent,
  );
  expect(said).toEqual(["No files", "45 lines"]);
});

test("a call with nothing to say leaves that side of the card empty", () => {
  // What a chat recorded before Madde 78 looks like. A blank half would claim a result that was
  // never written down.
  const older = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], calls: [{ tool: "list_files" }] }],
  };
  const { container } = render(<ChatScreen project={PROJECT} chat={older} />);
  fireEvent.click(screen.getByRole("button", { name: /1 step/ }));
  expect(screen.getByText("⏺ list_files")).toBeTruthy();
  expect(container.querySelector(".tool-call__outcome")).toBeNull();
});

// --- what the handle says while the answer runs (Madde 84) ---------------------------------------

const RUNNING = [
  { tool: "list_files", target: "", outcome: "No files" },
  { tool: "read_file", target: "aylin.json" },
];

test("while the answer runs the closed card says what it is doing now", () => {
  // The one thing a reader wants while they wait: not how many steps there have been, but which one
  // is happening. A call still in flight has no outcome yet, and that is the live half.
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking streamingCalls={RUNNING} />);
  expect(screen.getByRole("button", { name: /read_file\(aylin\.json\)/ })).toBeTruthy();
  expect(screen.queryByText(/2 steps/)).toBeNull();
});

test("opening a running turn switches the handle to the count", () => {
  // Open, the last call is on a card of its own right below -- so the handle stops repeating it and
  // says what it is a door to.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking streamingCalls={RUNNING} />,
  );
  fireEvent.click(screen.getByRole("button", { name: /read_file\(aylin\.json\)/ }));
  expect(screen.getByRole("button", { name: /2 steps/ })).toBeTruthy();
  expect(container.querySelectorAll(".tool-call")).toHaveLength(2);
});

test("a call card is a record rather than a door", () => {
  // The handle is pressable because it opens something. A step that already happened opens nothing,
  // so it is not a button -- Madde 78's rule, kept while the drawing changes around it.
  const { container } = render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  expect(container.querySelector(".tool-call").tagName).toBe("DIV");
});

test("the handle says whether it is open", () => {
  render(<ChatScreen project={PROJECT} chat={ANSWERED} />);
  const handle = screen.getByRole("button", { name: /2 steps/ });
  expect(handle.getAttribute("aria-expanded")).toBe("false");
  fireEvent.click(handle);
  expect(handle.getAttribute("aria-expanded")).toBe("true");
});

test("one call is one step rather than one steps", () => {
  // An interface that writes "1 steps" looks like it never read the number.
  const once = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], calls: [{ tool: "list_files" }] }],
  };
  render(<ChatScreen project={PROJECT} chat={once} />);
  expect(screen.getByText("⏺ 1 step")).toBeTruthy();
});

test("an answer that called nothing draws no list at all", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(container.querySelector(".tool-calls")).toBeNull();
});

// --- stopping a running answer (Madde 67) --------------------------------------------------------

test("an answer that is running can be stopped", () => {
  const onStop = vi.fn();
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking onStop={onStop} />);
  fireEvent.click(screen.getByRole("button", { name: "Stop" }));
  expect(onStop).toHaveBeenCalled();
});

test("with nothing running there is nothing to stop", () => {
  // No dead control beside an idle composer.
  render(<ChatScreen project={PROJECT} chat={CHAT} onStop={vi.fn()} />);
  expect(screen.queryByRole("button", { name: "Stop" })).toBeNull();
});

test("a stopped answer is drawn as one", () => {
  // Half a sentence with no mark reads as a model that finished on one.
  const stopped = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], text: "Half a", stopped: true }],
  };
  const { container } = render(<ChatScreen project={PROJECT} chat={stopped} />);
  expect(container.querySelector(".msg--stopped")).toBeTruthy();
});

test("a stopped answer says so in words", () => {
  // The grey rule down the side means something to whoever put it there. The word means the same
  // thing to everybody.
  const stopped = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], text: "Half a", stopped: true }],
  };
  render(<ChatScreen project={PROJECT} chat={stopped} />);
  expect(screen.getByText("Stopped")).toBeTruthy();
});

test("an answer that ran to the end says nothing", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.queryByText("Stopped")).toBeNull();
});

test("a stop before the first word is still a message on screen", () => {
  // Madde 81's own case. Nothing was said, so there is no text block to draw -- an empty one would
  // put the grey rule beside nothing at all.
  const stopped = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], text: "", stopped: true }],
  };
  const { container } = render(<ChatScreen project={PROJECT} chat={stopped} />);
  expect(screen.getByText("Stopped")).toBeTruthy();
  expect(container.querySelector(".msg__text")).toBeNull();
});

test("a call seen while the answer is still running is drawn as it arrives", () => {
  // Same road the file cards take: what the stream reports is drawn before any record exists.
  render(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      streamingCalls={[{ tool: "read_file", target: "plan.md" }]}
    />,
  );
  // One string rather than neighbouring fragments since Madde 78: the brackets are part of the
  // line's text, not an element beside it. Since 84 it reaches the screen on the shut handle rather
  // than on a card of its own -- what this claims is that it reaches the screen at all, and which
  // element carries it is the neighbouring test's business.
  expect(screen.getByText("⏺ read_file(plan.md)")).toBeTruthy();
});

test("the rail's rows can be deleted from the chat", () => {
  // Same road as the project screen: the screen only hands the way to ask further along.
  const remove = vi.fn();
  const files = [{ name: "notes.md", ext: "md", modifiedAt: NOW }];
  render(<ChatScreen project={PROJECT} chat={CHAT} files={files} deleting={{ remove }} />);
  fireEvent.click(screen.getByRole("button", { name: "Delete notes.md" }));
  expect(remove).toHaveBeenCalledWith("notes.md");
});

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

// --- the stamp under a message (Madde 83) --------------------------------------------------------
//
// One note under the message rather than two at its two ends, and no name in it: the sidebar carries
// the name, and which side a message sits on says who wrote it.

test("a user message is stamped with the time and nothing else", () => {
  // The design draws the person's own name there but never says where it comes from, and there is
  // no such setting. Who wrote it is already clear from the bubble sitting on the right.
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("11:04").className).toBe("msg__stamp");
  expect(screen.queryByText(/You/)).toBeNull();
});

test("an answer is stamped with the time and nothing else either", () => {
  // The name used to sit above every answer and it said nothing new: the sidebar carries it, and an
  // answer sitting on the left already says whose turn this was.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("11:05").className).toBe("msg__stamp");
  // Asked of the conversation rather than of the screen: the rail's empty state names QueenAgent
  // too, and that sentence is not the repetition this is about.
  expect(container.querySelector(".chat__column").textContent).not.toContain("QueenAgent");
});

test("the stamp closes a message rather than opening it", () => {
  // A note belongs under the thing it is about. Above, it is read before there is anything to read
  // it against -- and it was two notes at two ends, which is the same note said twice.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  const messages = [...container.querySelectorAll(".msg")];
  expect(messages).toHaveLength(2);
  expect(messages.map((msg) => msg.lastElementChild.className)).toEqual([
    "msg__stamp",
    "msg__stamp",
  ]);
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

test("no failure card ever offers a settings screen", () => {
  // Madde 62. The old props are passed on purpose: the claim is "whatever the caller sends", and
  // the only way to prove the old branch is gone is to feed it exactly what used to trigger it.
  // The card is left with the server's own sentence, which is what the repo asks for anyway.
  render(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      error="No API key is set."
      missingKey
      onSettings={vi.fn()}
    />,
  );
  expect(screen.getByText("No API key is set.")).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Settings/ })).toBeNull();
});

test("no failure, no card at all", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.queryByText("Couldn't get a response.")).toBeNull();
});

test("a message that was never sent is not told as an answer that never came", () => {
  // Two different failures: one has a request to retry, the other has a sentence to write again.
  render(<ChatScreen project={PROJECT} chat={CHAT} refused="a message needs text" />);
  expect(screen.getByText("a message needs text")).toBeTruthy();
  expect(screen.queryByText("Couldn't get a response.")).toBeNull();
  expect(screen.queryByRole("button", { name: "Try again" })).toBeNull();
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

test("the waiting stamp carries the time the wait began", () => {
  // Today the clock only appears once the answer has been saved; the design wants the stamp and the
  // dots on screen together, time and all.
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 7, 9, 14, 32));
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  expect(screen.getByText("14:32").className).toBe("msg__stamp");
  vi.useRealTimers();
});

test("that time does not move while the answer arrives", () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 7, 9, 14, 32));
  const { rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  vi.setSystemTime(new Date(2026, 7, 9, 14, 35));
  rerender(<ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here" />);
  // It answers "when was this asked for", and that answer stopped being new at 14:32.
  expect(screen.getByText("14:32")).toBeTruthy();
  expect(screen.queryByText("14:35")).toBeNull();
  vi.useRealTimers();
});

test("the file being written waits inside the block that is waiting", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking creatingFile />);
  expect(container.querySelector("[data-testid=thinking] .creating")).toBeTruthy();
  // The skeleton of the card about to be born: an empty badge slot where the chip will go.
  expect(container.querySelector(".creating .creating__chip")).toBeTruthy();
});

test("a file born mid-answer waits under the text instead", () => {
  // The design never met this one -- in its own flow the file is born at the end of the stream. The
  // rule that covers both: the box belongs to whichever block is still pending.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Saving" creatingFile />,
  );
  expect(container.querySelector("[data-testid=streaming] .creating")).toBeTruthy();
  expect(container.querySelectorAll(".creating").length).toBe(1);
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

// The card is the primary way into a file: the design turns it from a receipt into a door.
function withCard(files = ["outline.md"]) {
  return { ...CHAT, messages: [CHAT.messages[0], { ...CHAT.messages[1], files }] };
}

test("the card is a door, and says so", () => {
  const open = vi.fn();
  const { container } = render(
    <ChatScreen
      project={PROJECT}
      chat={withCard()}
      files={withFiles("outline.md")}
      reading={{ open }}
    />,
  );
  // The rail's row is a real button now too, so the card is asked for by what it is.
  const card = container.querySelector(".file-card");
  expect(card.textContent).toContain("Open ›");
  fireEvent.click(card);
  expect(open).toHaveBeenCalledWith("outline.md");
});

test("the card of the file being read says open rather than offering to", () => {
  const { container } = render(
    <ChatScreen
      project={PROJECT}
      chat={withCard()}
      files={withFiles("outline.md")}
      reading={{ name: "outline.md", open: vi.fn() }}
    />,
  );
  // The rail's row is a real button now too, so the card is asked for by what it is.
  const card = container.querySelector(".file-card");
  expect(card.className).toContain("file-card--selected");
  // Telling someone to open what is already open would be the wrong sentence, and there is nowhere
  // left to go, so the arrow drops with it.
  expect(card.textContent).toContain("open");
  expect(card.textContent).not.toContain("Open ›");
});

test("the other cards are not marked", () => {
  const { container } = render(
    <ChatScreen
      project={PROJECT}
      chat={withCard(["outline.md", "sources.txt"])}
      files={withFiles("outline.md", "sources.txt")}
      reading={{ name: "outline.md", open: vi.fn() }}
    />,
  );
  const cards = [...container.querySelectorAll(".file-card")];
  const other = cards.find((card) => card.textContent.includes("sources.txt"));
  expect(other.className).not.toContain("selected");
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

function withText(role, text) {
  return { ...CHAT, messages: [{ role, at: CHAT.messages[0].at, text }] };
}

test("an answer is drawn as Markdown", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={withText("ai", "**Done.**")} />);
  expect(container.querySelector(".msg--ai strong").textContent).toBe("Done.");
});

test("what the user typed stays exactly as they typed it", () => {
  // The design asks for this one by name: writing `**test**` shows the asterisks.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={withText("user", "**test**")} />,
  );
  expect(container.querySelector(".msg__bubble").textContent).toBe("**test**");
  expect(container.querySelector(".msg__bubble strong")).toBeNull();
});

test("text that is still arriving is drawn as Markdown too", () => {
  // Raw first and formatted afterwards would be a flicker, not a stream.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="# Title" />,
  );
  expect(container.querySelector("[data-testid=streaming] h1").textContent).toBe("Title");
});

test("only the text still arriving carries a caret", () => {
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here it" />,
  );
  expect(container.querySelector("[data-testid=streaming] .caret")).toBeTruthy();
  expect(container.querySelector(".msg--ai:not([data-testid=streaming]) .caret")).toBeNull();
});

// jsdom lays nothing out, so the sizes are declared and what is under test is the decision: does
// the list follow the answer down, or does it leave the reader where they are?
function scrollable(container, { at }) {
  const scroll = container.querySelector(".chat__scroll");
  Object.defineProperty(scroll, "scrollHeight", { configurable: true, value: 1000 });
  Object.defineProperty(scroll, "clientHeight", { configurable: true, value: 300 });
  scroll.scrollTop = at;
  return scroll;
}

test("a new message takes the list to the bottom", () => {
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  const scroll = scrollable(container, { at: 0 });
  const said = { ...CHAT, messages: [...CHAT.messages, { role: "user", at: NOW, text: "More" }] };
  rerender(<ChatScreen project={PROJECT} chat={said} />);
  expect(scroll.scrollTop).toBe(1000);
});

test("a reader who has scrolled up is never dragged back down", () => {
  const { container, rerender } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here" />,
  );
  // 700px from the bottom: reading, not watching.
  const scroll = scrollable(container, { at: 0 });
  rerender(<ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here it is" />);
  expect(scroll.scrollTop).toBe(0);
});

test("a reader who is watching the end stays stuck to it", () => {
  const { container, rerender } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here" />,
  );
  // 100px from the bottom, inside the design's 220.
  const scroll = scrollable(container, { at: 600 });
  rerender(<ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here it is" />);
  expect(scroll.scrollTop).toBe(1000);
});

test("the rail lists the project's files beside the conversation", () => {
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  render(<ChatScreen project={PROJECT} chat={CHAT} files={files} />);
  expect(screen.getByTestId("file-rail").textContent).toContain("outline.md");
});

test("the rail is drawn at the width the app is holding, and reports a drag back to it", () => {
  // The width outlives this screen -- it crosses chats -- so the screen only carries it through.
  const onResizeRail = vi.fn();
  render(
    <ChatScreen project={PROJECT} chat={CHAT} railWidth={380} onResizeRail={onResizeRail} />,
  );
  expect(screen.getByTestId("file-rail").style.width).toBe("380px");
  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 400 });
  fireEvent.mouseMove(window, { clientX: 340 });
  expect(onResizeRail).toHaveBeenCalledWith(440);
});

test("the composer says which model answers, without offering a choice", () => {
  // Madde 82: one model, and nothing on a chat says which. The name is there to be read.
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("Grok Build")).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Grok Build/ })).toBeNull();
});

test("the foot carries Skills, the model and Send, in that order", () => {
  // karar 1's order, complete at last.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  const foot = container.querySelector(".composer__foot");
  // karar 1's order stands; the middle one stopped being a control in Madde 82.
  expect(foot.textContent).toBe("Skills⌄Grok Build↑");
  const buttons = [...foot.querySelectorAll("button")];
  expect(buttons.length).toBe(2);
  // Madde 80 took the word off the button; the name it answers to is asked for separately now.
  expect(buttons[1].getAttribute("aria-label")).toBe("Send");
});

test("while an answer runs the row ends in Stop, and there is no fourth button", () => {
  // Madde 79, in one sentence. Madde 67 put Stop beside Send; the two are one control now, because
  // an answer that is running is exactly when there is nothing to send.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking onStop={vi.fn()} />,
  );
  const foot = container.querySelector(".composer__foot");
  expect(foot.textContent).toBe("Skills⌄Grok Build⏹");
  const buttons = [...foot.querySelectorAll("button")];
  expect(buttons.length).toBe(2);
  expect(buttons[1].getAttribute("aria-label")).toBe("Stop");
});

test("a chat with a skill selected says which one", () => {
  render(<ChatScreen project={PROJECT} chat={{ ...CHAT, skill: "verify-prompts" }} />);
  expect(screen.getByRole("button", { name: /Verify prompts/ })).toBeTruthy();
});

test("picking a skill is passed up rather than kept here", () => {
  const onSkillChange = vi.fn();
  render(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      skillsOpen
      onSkillChange={onSkillChange}
    />,
  );
  fireEvent.click(screen.getByText("Split into frames"));
  expect(onSkillChange).toHaveBeenCalledWith("split-into-frames");
});

// --- what the answer spent (Madde 68) ------------------------------------------------------------
//
// The number is 68's; where it is drawn is 83's. It rides in the stamp under the answer now, after
// the time and one separator, rather than on a line of its own.

const withUsage = (usage) => ({
  ...CHAT,
  messages: [CHAT.messages[0], { ...CHAT.messages[1], usage }],
});

test("an answer says what it spent, beside when it was said", () => {
  // One number rather than the breakdown: the owner asked for a plain total under each answer, and
  // what it is made of stays on disk for the context work rather than being drawn here.
  render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 12400, cached: 9100, answered: 842 })} />,
  );
  // Asked for by its text rather than by its class: a missing element then names what was looked
  // for, instead of failing later on a null nobody can read.
  expect(screen.getByText("11:05 · 13.2k tokens").className).toBe("msg__stamp");
});

test("a small answer is not dressed up as a big one", () => {
  render(<ChatScreen project={PROJECT} chat={withUsage({ sent: 300, cached: 0, answered: 42 })} />);
  expect(screen.getByText("11:05 · 342 tokens").className).toBe("msg__stamp");
});

test("an answer nobody measured still says when it was said", () => {
  // Zero is what an answer from before this existed reads back as, and a count under it would claim
  // a measurement nobody took. The time is not a measurement -- it was said at a time either way.
  render(<ChatScreen project={PROJECT} chat={withUsage({ sent: 0, cached: 0, answered: 0 })} />);
  expect(screen.getByText("11:05").className).toBe("msg__stamp");
  expect(screen.queryByText(/tokens/)).toBeNull();
});

test("the user's own message never carries a count", () => {
  // Spending is what an answer does. A number under the question would read as its price.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 300, cached: 0, answered: 42 })} />,
  );
  expect(screen.getByText("11:04").className).toBe("msg__stamp");
  expect(container.querySelector(".msg--user").textContent).not.toContain("tokens");
});
