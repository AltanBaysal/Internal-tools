import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { act, fireEvent, render, screen, within } from "@testing-library/react";
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

// Madde 344: the screen is the screen, and what draws one message lives in files of its own. A lock
// rather than a behaviour -- every test below still draws the screen and looks at what it does.
// Read off disk, like workspace.css.test.js: vitest hands back neither import.meta.url nor `?raw`.
test("the message's parts are drawn from their own files", () => {
  const source = readFileSync(resolve(process.cwd(), "src/features/workspace/ChatScreen.jsx"), "utf8");
  const parts = [
    "ToolCalls",
    "Stamp",
    "LiveStrip",
    "EditMessage",
    "Versions",
    "MessageFoot",
    "CreatingFile",
    "FileCard",
    "FailureCard",
  ];
  expect(parts.filter((part) => source.includes(`function ${part}(`))).toEqual([]);
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

test("a stopped answer has no cost under it, only Stopped and the time", () => {
  // Design item 215: the request it dropped never came, so there are no counts to describe. The
  // record still keeps what the finished rounds spent.
  const stopped = {
    ...CHAT,
    messages: [
      CHAT.messages[0],
      {
        ...CHAT.messages[1],
        text: "",
        stopped: true,
        usage: { sent: 12400, cached: 9100, answered: 842 },
      },
    ],
  };
  const { container } = render(<ChatScreen project={PROJECT} chat={stopped} />);
  expect(container.querySelector(".msg--ai .msg__stamp").textContent).toBe("11:05");
  expect(screen.getByText("Stopped")).toBeTruthy();
  // No rule down the side: the design took the stopped answer's line away.
  expect(container.querySelector(".msg--stopped")).toBeNull();
});

test("a stopped answer draws its file cards, then Stopped, then the time", () => {
  // Design item 215 (shell.js, message): the files the turn wrote stay, and Stopped closes the
  // turn just above its stamp.
  const stopped = {
    ...CHAT,
    messages: [
      CHAT.messages[0],
      { ...CHAT.messages[1], text: "", stopped: true, files: ["plan.md"] },
    ],
  };
  const files = [{ name: "plan.md", ext: "md", modifiedAt: NOW }];
  const { container } = render(<ChatScreen project={PROJECT} chat={stopped} files={files} />);
  const parts = [...container.querySelector(".msg--ai").children].map((part) => part.className);
  expect(parts).toEqual(["file-cards", "msg__stopped", "msg__stamp"]);
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
  // The screen only hands the way to ask further along: the question itself is App's.
  const remove = vi.fn();
  const files = [{ name: "notes.md", ext: "md", modifiedAt: NOW }];
  render(<ChatScreen project={PROJECT} chat={CHAT} files={files} deleting={{ remove }} />);
  fireEvent.click(screen.getByRole("button", { name: "Delete notes.md" }));
  expect(remove).toHaveBeenCalledWith("notes.md");
});

test("the chat's header holds its name and nothing else", () => {
  // Design items 152 and 168: the project's name lives in the bar alone, so the header is no longer
  // a breadcrumb.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(container.querySelector(".chat__header").textContent).toBe("Write the intro");
});

test("the header offers no way back, and the project's name is nowhere on the screen", () => {
  // Leaving the project is the bar's Exit project; the sidebar already opens the project's other
  // chats.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} onBack={vi.fn()} />);
  expect(container.querySelector(".chat__header button")).toBeNull();
  expect(screen.queryByText(/Thesis research/)).toBeNull();
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
  expect(screen.getByText("11:04").parentElement.className).toBe("msg__stamp");
  expect(screen.queryByText(/You/)).toBeNull();
});

test("an answer is stamped with the time and nothing else either", () => {
  // The name used to sit above every answer and it said nothing new: the sidebar carries it, and an
  // answer sitting on the left already says whose turn this was.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("11:05").parentElement.className).toBe("msg__stamp");
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

// --- the running turn, live (Madde 194) ----------------------------------------------------------
//
// The stamp fell at the end of a turn, so a turn that took a minute showed three blinking dots for a
// minute. What matters is not looking frozen: the number can sit still for thirty seconds, and the
// spinner is what says the screen is alive.

const RUNNING_AT = { round: 4, of: 16, tokens: 12300 };

test("the running turn says where it is, on one line, where the stamp sits", () => {
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking progress={RUNNING_AT} />,
  );
  const strip = screen.getByTestId("live-strip");
  // The same class the finished stamp wears: when the turn ends the two swap places, and two
  // different-looking things trading places is a jump on the page.
  expect(strip.className).toContain("msg__stamp");
  expect(strip.textContent).toContain("round 4/16");
  expect(strip.textContent).toContain("12.3k tokens");
  // English, like the rest of QueenAgent's UI and like the stamp it turns into.
  expect(strip.textContent).not.toContain("jeton");
  expect(container.querySelector(".msg--waiting").lastElementChild).toBe(strip);
});

test("the strip carries a word that says nothing about the work", () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 7, 9, 14, 32));
  try {
    render(<ChatScreen project={PROJECT} chat={CHAT} thinking progress={RUNNING_AT} />);
    // A gerund and an ellipsis. Deriving it from the tool name was asked against: the two pieces
    // beside it already carry every fact there is. The whole line is pinned here -- one row, in
    // this order, with nothing dividing it into columns.
    //
    // The two facts lead and the moving part trails (user, 7 September). The spinner's job is to
    // move, and where it sits does not change whether it does. Madde 348: the time the wait began
    // stands before them, where the record's time will stand.
    expect(screen.getByTestId("live-strip").textContent).toMatch(
      /^14:32 · round 4\/16 · 12\.3k tokens · [A-Z][a-z]+ing…$/,
    );
  } finally {
    vi.useRealTimers();
  }
});

test("the spinner sits behind the numbers, in front of the word", () => {
  // The text alone is no proof of an arrangement: the same letters can come out of any markup. The
  // spinner draws nothing of its own, so where it stands is only sayable of its neighbours.
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking progress={RUNNING_AT} />);
  const spinner = screen.getByTestId("live-strip").querySelector(".msg__spinner");
  expect(spinner.previousElementSibling.textContent).toContain("12.3k tokens");
  expect(spinner.nextElementSibling.textContent).toMatch(/^[A-Z][a-z]+ing…$/);
});

test("the word changes on its own", () => {
  vi.useFakeTimers();
  try {
    render(<ChatScreen project={PROJECT} chat={CHAT} thinking progress={RUNNING_AT} />);
    const first = screen.getByTestId("live-strip").textContent;
    act(() => vi.advanceTimersByTime(10_000));
    expect(screen.getByTestId("live-strip").textContent).not.toBe(first);
  } finally {
    vi.useRealTimers();
  }
});

test("the spinner does not wait for a timer", () => {
  // The one thing that must never stall. A turn that has React busy has its intervals waiting
  // too, and that is exactly the moment the screen has to look alive -- so the spinning is the
  // stylesheet's, not JavaScript's.
  vi.useFakeTimers();
  try {
    const { container } = render(
      <ChatScreen project={PROJECT} chat={CHAT} thinking progress={RUNNING_AT} />,
    );
    // Not .strip__spinner: workspace.css.test.js guards the deleted undo strip by forbidding the
    // string ".strip" anywhere in the stylesheet, and that guard is worth more than the name.
    expect(container.querySelector(".msg__spinner")).toBeTruthy();
  } finally {
    vi.useRealTimers();
  }
});

test("a turn that has not reported yet gets the dots and no strip", () => {
  // round 0/16 would be the screen claiming a measurement nobody took.
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  expect(screen.queryByTestId("live-strip")).toBeNull();
  expect(screen.getByTestId("thinking")).toBeTruthy();
});

test("the strip rides in the wait for as long as the turn runs", () => {
  // Design item 214: the words come and are not drawn, so the dots, the steps and the strip stand
  // until the turn ends.
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking progress={RUNNING_AT} />);
  expect(screen.getByTestId("thinking").textContent).toContain("round 4/16");
});

test("both messages are drawn", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getByText("Here it is.")).toBeTruthy();
});

test("a chat that does not exist says so, under the way back", () => {
  // The design keeps ← back over the missing line (item 194 takes it only from a chat opening).
  render(<ChatScreen project={PROJECT} chat={null} missing />);
  expect(screen.getByText("That chat does not exist.")).toBeTruthy();
  expect(screen.getByRole("button", { name: "← back" })).toBeTruthy();
  expect(screen.queryByTestId("spinner")).toBeNull();
});

// --- a chat while it opens (Madde 355) -----------------------------------------------------------
//
// Design item 194: until the record comes the chat's own frame stands -- its title, a shut box and
// the rail -- and only where the messages will be does the spinner turn.

const RAIL = [{ name: "outline.md", ext: "md", modifiedAt: NOW }];

test("a chat still on its way stands in its own frame", () => {
  const { container } = render(
    <ChatScreen project={PROJECT} chat={null} loadingTitle="Write the intro" files={RAIL} />,
  );
  // The sidebar row's own name: the list was read before the record, and says the same.
  expect(container.querySelector(".chat__header").textContent).toBe("Write the intro");
  expect(screen.getByTestId("file-rail").textContent).toContain("outline.md");
  expect(screen.getByPlaceholderText("Reply...")).toBeTruthy();
});

test("where the messages will be, the spinner turns and nothing else", () => {
  // Not even a turn still running into this chat: opening draws no turn (design item 194).
  const { container } = render(<ChatScreen project={PROJECT} chat={null} thinking />);
  const column = container.querySelector(".chat__column");
  expect(column.children).toHaveLength(1);
  expect(column.firstElementChild.className).toBe("chat__spinner");
  expect(column.firstElementChild.firstElementChild).toBe(screen.getByTestId("spinner"));
});

test("nothing in the box can be written or picked yet", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={null} />);
  expect(screen.getByPlaceholderText("Reply...").disabled).toBe(true);
  const pickers = [...container.querySelectorAll(".composer__foot .picker")];
  expect(pickers.map((picker) => picker.disabled)).toEqual([true, true]);
});

test("no way back stands alone while it opens", () => {
  render(<ChatScreen project={PROJECT} chat={null} onBack={vi.fn()} />);
  expect(screen.queryByRole("button", { name: "← back" })).toBeNull();
});

test("a chat whose row has not come either opens with a blank title", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={null} />);
  expect(container.querySelector(".chat__title").textContent).toBe("");
});

test("a sentence left in one chat's box does not follow into the next", () => {
  // The box is born afresh with each chat, as it was when opening took the box away: what was typed
  // in one chat is never offered to another.
  const { rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  fireEvent.change(screen.getByPlaceholderText("Reply..."), { target: { value: "for the first" } });
  rerender(<ChatScreen project={PROJECT} chat={null} />);
  rerender(<ChatScreen project={PROJECT} chat={{ ...CHAT, id: "c2", title: "Other" }} />);
  expect(screen.getByPlaceholderText("Reply...").value).toBe("");
});

test("waiting for an answer draws three dots and no fake text", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  expect(screen.getByTestId("thinking")).toBeTruthy();
});

test("nothing blinks when nothing is pending", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.queryByTestId("thinking")).toBeNull();
});

test("a running turn draws no words, only the wait", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  expect(container.querySelector("[data-testid=thinking] .msg__text")).toBeNull();
  expect(screen.queryByTestId("streaming")).toBeNull();
});

test("the answer that has just arrived whole fades its words in", () => {
  // Design item 214, msg--arrived: the record's message takes the wait's place and its words fade
  // in over 200ms. Only that one: the rest of the chat was already there.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} arrived={1} />);
  const [question, answer] = container.querySelectorAll(".msg");
  expect(answer.classList.contains("msg--arrived")).toBe(true);
  expect(question.classList.contains("msg--arrived")).toBe(false);
});

test("a chat opened from disk has nothing arriving", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(container.querySelector(".msg--arrived")).toBeNull();
});

// --- the failed answer (Madde 440; design items 216 and 221) -------------------------------------

const READ = { tool: "read_file", target: "aylin.json", outcome: "45 lines" };
const FAILED = {
  ...CHAT,
  messages: [
    CHAT.messages[0],
    { ...CHAT.messages[1], text: "HTTP 502", failed: "technical", calls: [READ] },
  ],
};

test("a failed answer is the failure card, with the failure's own words", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={FAILED} />);
  const answer = container.querySelector(".msg--ai");
  expect(answer.classList.contains("msg--failed")).toBe(true);
  expect(answer.querySelector(".failure__line").textContent).toBe("Couldn't get a response.");
  expect(answer.querySelector(".failure__detail").textContent).toBe("HTTP 502");
  // Its words are the card's, never an answer's text.
  expect(answer.querySelector(".msg__text")).toBeNull();
});

test("a failed answer keeps the steps its turn took", () => {
  render(<ChatScreen project={PROJECT} chat={FAILED} />);
  expect(screen.getByRole("button", { name: /1 step/ })).toBeTruthy();
});

test("a failed answer's card has no time", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={FAILED} />);
  expect(container.querySelector(".msg--ai .msg__stamp")).toBeNull();
  expect(screen.queryByText("11:05")).toBeNull();
});

test("the failed answer's Try again answers the question again, not through the composer", () => {
  // Its own door: the transient cards' Try again may send the composer, this one never does.
  const onRetry = vi.fn();
  const onAnswerAgain = vi.fn();
  render(
    <ChatScreen project={PROJECT} chat={FAILED} onRetry={onRetry} onAnswerAgain={onAnswerAgain} />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(onAnswerAgain).toHaveBeenCalled();
  expect(onRetry).not.toHaveBeenCalled();
});

test("while a turn runs, the failed answer's card has no Try again", () => {
  // Between the press and the record read again, a second press would start a second turn.
  const onAnswerAgain = vi.fn();
  const { container } = render(
    <ChatScreen project={PROJECT} chat={FAILED} thinking onAnswerAgain={onAnswerAgain} />,
  );
  expect(container.querySelector(".msg--failed .failure")).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Try again" })).toBeNull();
});

test("once the chat has moved on, the failed answer's card has no Try again", () => {
  const onAnswerAgain = vi.fn();
  const movedOn = {
    ...FAILED,
    messages: [...FAILED.messages, { role: "user", at: NOW, text: "never mind" }],
  };
  const { container } = render(
    <ChatScreen project={PROJECT} chat={movedOn} onAnswerAgain={onAnswerAgain} />,
  );
  expect(container.querySelector(".msg--failed .failure")).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Try again" })).toBeNull();
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

test("a refused message draws the failure card with the server's words", () => {
  // Design item 193: a message the server refused and an answer that never came are one card --
  // the same sentence, the server's own words under it, and Try again.
  const onRetry = vi.fn();
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} refused="a message needs text" onRetry={onRetry} />,
  );
  expect(screen.getByText("Couldn't get a response.")).toBeTruthy();
  expect(container.querySelector(".failure__detail").textContent).toBe("a message needs text");
  expect(container.querySelector(".refused")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(onRetry).toHaveBeenCalled();
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
  expect(screen.getByText("14:32").parentElement.className).toBe("msg__stamp");
  vi.useRealTimers();
});

test("that time does not move while the answer arrives", () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 7, 9, 14, 32));
  const { rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  vi.setSystemTime(new Date(2026, 7, 9, 14, 35));
  rerender(<ChatScreen project={PROJECT} chat={CHAT} thinking progress={RUNNING_AT} />);
  // It answers "when was this asked for", and that answer stopped being new at 14:32.
  expect(screen.getByTestId("live-strip").textContent).toMatch(/^14:32 · /);
  expect(screen.queryByText(/14:35/)).toBeNull();
  vi.useRealTimers();
});

test("the file being written waits inside the block that is waiting", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking creatingFile />);
  expect(container.querySelector("[data-testid=thinking] .creating")).toBeTruthy();
  // The skeleton of the card about to be born: an empty badge slot where the chip will go.
  expect(container.querySelector(".creating .creating__chip")).toBeTruthy();
});

test("nothing dashed is drawn when no file is being written", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  expect(screen.queryByText("creating file…")).toBeNull();
});

test("a file that lands mid-answer becomes a card straight away", () => {
  render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking createdFiles={["outline.md"]} />,
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

// jsdom lays nothing out, so the sizes are declared and what is under test is the decision: does
// the list follow the answer down, or does it leave the reader where they are? The reader is put
// there by a scroll, the way a real reader gets there.
function scrollable(container, { at }) {
  const scroll = container.querySelector(".chat__scroll");
  Object.defineProperty(scroll, "scrollHeight", { configurable: true, value: 1000 });
  Object.defineProperty(scroll, "clientHeight", { configurable: true, value: 300 });
  scroll.scrollTop = at;
  fireEvent.scroll(scroll);
  return scroll;
}

// Something new at the foot, as the list sees it: it is taller.
function grow(scroll, height) {
  Object.defineProperty(scroll, "scrollHeight", { configurable: true, value: height });
}

test("a new message takes the list to the bottom", () => {
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  const scroll = scrollable(container, { at: 0 });
  const said = { ...CHAT, messages: [...CHAT.messages, { role: "user", at: NOW, text: "More" }] };
  rerender(<ChatScreen project={PROJECT} chat={said} />);
  expect(scroll.scrollTop).toBe(1000);
});

// --- a card at the chat's foot is seen (Madde 380) ------------------------------------------------
// Found in the browser: after a failed answer the list stopped 98px short of its foot, the card half
// under the box. Each card below is one that appears at the foot of the chat.

test("a reader at the foot sees a failure card whole", () => {
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  const scroll = scrollable(container, { at: 700 });
  grow(scroll, 1100);
  rerender(<ChatScreen project={PROJECT} chat={CHAT} error="HTTP 401" />);
  expect(scroll.scrollTop).toBe(1100);
});

test("a reader at the foot sees a refused message's card whole", () => {
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  const scroll = scrollable(container, { at: 700 });
  grow(scroll, 1100);
  rerender(<ChatScreen project={PROJECT} chat={CHAT} refused="A message cannot be empty." />);
  expect(scroll.scrollTop).toBe(1100);
});

test("a reader at the foot is taken down to a permission card taller than the follow distance", () => {
  // The card prints the call's arguments raw -- a write_file's whole content -- so it can be far
  // taller than 220. Measured once it has arrived, the reader who was at the foot would look like
  // one who had scrolled away.
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  const scroll = scrollable(container, { at: 700 });
  grow(scroll, 1600);
  rerender(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      permission={{ tool: "write_file", args: '{"name": "intro.md", "content": "..."}' }}
    />,
  );
  expect(scroll.scrollTop).toBe(1600);
});

test("a reader at the foot sees a file card the answer just made", () => {
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  const scroll = scrollable(container, { at: 700 });
  grow(scroll, 1100);
  rerender(<ChatScreen project={PROJECT} chat={CHAT} thinking createdFiles={["intro.md"]} />);
  expect(scroll.scrollTop).toBe(1100);
});

test("a reader at the foot keeps the wait in view as its steps and its line grow", () => {
  // No words pull the list down any more (Madde 440): the wait itself is what grows at the foot.
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  const scroll = scrollable(container, { at: 700 });
  grow(scroll, 1100);
  rerender(<ChatScreen project={PROJECT} chat={CHAT} thinking streamingCalls={RUNNING} />);
  expect(scroll.scrollTop).toBe(1100);
  grow(scroll, 1200);
  rerender(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      streamingCalls={RUNNING}
      progress={RUNNING_AT}
    />,
  );
  expect(scroll.scrollTop).toBe(1200);
});

test("a reader up the page is not pulled down by the wait growing", () => {
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  const scroll = scrollable(container, { at: 0 });
  grow(scroll, 1600);
  rerender(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      streamingCalls={RUNNING}
      progress={RUNNING_AT}
    />,
  );
  expect(scroll.scrollTop).toBe(0);
});

test("a reader up the page stays where they are when cards arrive at the foot", () => {
  // The same rule the answer keeps: the list follows the reader, not the other way round.
  const { container, rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} thinking />);
  const scroll = scrollable(container, { at: 0 });
  grow(scroll, 1600);
  rerender(
    <ChatScreen
      project={PROJECT}
      chat={CHAT}
      thinking
      error="HTTP 401"
      refused="A message cannot be empty."
      permission={{ tool: "write_file", args: "{}" }}
      createdFiles={["intro.md"]}
    />,
  );
  expect(scroll.scrollTop).toBe(0);
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

test("a model an older message was sent with is not drawn", () => {
  // Madde 146 to 357 wrote it onto the message. It stays on disk as a record and is shown nowhere.
  const old = { ...CHAT, messages: [{ ...CHAT.messages[0], model: "deepseek-v4-pro" }] };
  render(<ChatScreen project={PROJECT} chat={old} />);
  expect(screen.queryByText(/deepseek-v4-pro/)).toBeNull();
});

test("the foot carries the mode, Skills and Send, in that order", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  const foot = container.querySelector(".composer__foot");
  // karar 1's order stands; Madde 91 put the mode in front of the row -- what the model may do at
  // all comes before which job it is doing. No model is shown anywhere since Madde 358, so the row
  // is two pickers and Send.
  expect(foot.textContent).toBe("Edit⌄Skills⌄↑");
  const buttons = [...foot.querySelectorAll("button")];
  expect(buttons.length).toBe(3);
  // Madde 80 took the word off the button; the name it answers to is asked for separately now.
  expect(buttons[2].getAttribute("aria-label")).toBe("Send");
});

test("while an answer runs the row ends in Stop, and nothing is added beside it", () => {
  // Madde 79, in one sentence. Madde 67 put Stop beside Send; the two are one control now, because
  // an answer that is running is exactly when there is nothing to send.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking onStop={vi.fn()} />,
  );
  const foot = container.querySelector(".composer__foot");
  expect(foot.textContent).toBe("Edit⌄Skills⌄⏹");
  const buttons = [...foot.querySelectorAll("button")];
  expect(buttons.length).toBe(3);
  expect(buttons[2].getAttribute("aria-label")).toBe("Stop");
});

test("the picker shows the skill it is handed, not the chat's", () => {
  // Madde 86: the selection is the session's, and the session is App's. This screen is handed one.
  // A skill sitting in an old record is history, not a selection.
  // The two values are the record's and none: since Madde 94 the menu holds one name, so the
  // disagreement is shown the other way round -- a stored skill against a session that picked
  // nothing.
  render(
    <ChatScreen project={PROJECT} chat={{ ...CHAT, skill: "edit-prompts" }} skill="" />,
  );
  expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Edit prompts/ })).toBeNull();
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
  fireEvent.click(screen.getByText("Edit prompts"));
  expect(onSkillChange).toHaveBeenCalledWith("edit-prompts");
});

// --- what the answer spent (Madde 68, Madde 354) -------------------------------------------------
//
// The number is 68's; where it is drawn is 83's and 348's. Madde 354 (design items 189, 192) split
// it: what came from the cache and what missed it, and nothing for what the model wrote.

const withUsage = (usage) => ({
  ...CHAT,
  messages: [CHAT.messages[0], { ...CHAT.messages[1], usage }],
});
const answerWords = (container) =>
  container.querySelector(".msg--ai .msg__stamp").firstElementChild.textContent;

test("an answer says what came from the cache and what missed it, beside when it was said", () => {
  const { container } = render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 12400, cached: 9100, answered: 842 })} />,
  );
  expect(answerWords(container)).toBe("11:05 · 9.1k cached · 3.3k missed");
});

test("a small answer is not dressed up as a big one", () => {
  const { container } = render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 300, cached: 0, answered: 42 })} />,
  );
  expect(answerWords(container)).toBe("11:05 · 0 cached · 300 missed");
});

test("an answer nobody measured still says when it was said", () => {
  // Zero is what an answer from before this existed reads back as, and a count under it would claim
  // a measurement nobody took. The time is not a measurement -- it was said at a time either way.
  render(<ChatScreen project={PROJECT} chat={withUsage({ sent: 0, cached: 0, answered: 0 })} />);
  expect(screen.getByText("11:05").parentElement.className).toBe("msg__stamp");
  expect(screen.queryByText(/cached|missed/)).toBeNull();
});

test("the user's own message never carries a count", () => {
  // Spending is what an answer does. A number under the question would read as its price.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 300, cached: 0, answered: 42 })} />,
  );
  expect(screen.getByText("11:04").parentElement.className).toBe("msg__stamp");
  const question = container.querySelector(".msg--user").textContent;
  expect(question).not.toContain("cached");
  expect(question).not.toContain("missed");
});

// --- the context gauge (Madde 92) ----------------------------------------------------------------

test("the chat screen draws the gauge from the record it read", () => {
  // The same measurement the stamp under the answer shows, read from the one place the record's
  // shape is built. Nothing here counts anything a second time.
  render(<ChatScreen project={PROJECT} chat={{ ...CHAT, context: { sent: 41000, ceiling: 50000 } }} />);
  expect(screen.getByRole("img").style.getPropertyValue("--filled")).toBe("0.82");
});

// --- the mode a turn is sent in (Madde 91) -------------------------------------------------------

// --- editing a message, and the versions it leaves behind (Madde 195) ----------------------------

const ALONE = { index: 0, of: 1, versions: [""] };
const BRANCHED = {
  ...CHAT,
  messages: [
    { ...CHAT.messages[0], variants: { index: 1, of: 2, versions: ["", "l2"] } },
    { ...CHAT.messages[1], variants: ALONE },
  ],
};

test("a question can be edited and an answer cannot", () => {
  // The point a turn starts from is the user's own message. An answer is not one sentence but a
  // whole turn with its own calls, and there is nothing on disk that going back into it would mean.
  //
  // Named for the message rather than Edit alone: the mode picker in the foot already wears that
  // word, and two controls with one name is a screen nobody can be told how to use.
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.getAllByRole("button", { name: "Edit message" })).toHaveLength(1);
});

// Madde 197: the sentence is corrected where it stands. What follows replaces the tests that
// watched it travel to the composer -- the road itself is gone, not only its shape.

function _editing(chat = CHAT, props = {}) {
  const rendered = render(<ChatScreen project={PROJECT} chat={chat} {...props} />);
  fireEvent.click(screen.getByRole("button", { name: "Edit message" }));
  return { ...rendered, field: rendered.container.querySelector(".msg__editing-input") };
}

test("pressing edit turns the message itself into something writable", () => {
  const { container, field } = _editing();
  expect(field.value).toBe("Write the intro");
  // And the bubble is not sitting under it: one sentence is drawn once, either as text or as the
  // field that is correcting it.
  expect(container.querySelectorAll(".msg__bubble")).toHaveLength(0);
});

test("nothing lands in the composer", () => {
  // The whole madde in one line. The sentence being corrected is on the message, and the box below
  // is for the next thing the user says.
  const { container } = _editing();
  expect(container.querySelector(".composer__input").value).toBe("");
});

test("the tick sends the corrected sentence and says which message it starts from", () => {
  // Without the index the server has no way to tell an edit from an ordinary reply, and the
  // sentence would land on the end of the line instead of opening one.
  const onSend = vi.fn();
  const { field } = _editing(CHAT, { onSend });
  fireEvent.change(field, { target: { value: "Write a shorter intro" } });
  fireEvent.click(screen.getByRole("button", { name: "Confirm edit" }));
  expect(onSend).toHaveBeenCalledWith("Write a shorter intro", 0);
});

test("the cross sends nothing and gives the message back", () => {
  const onSend = vi.fn();
  const { container, field } = _editing(CHAT, { onSend });
  fireEvent.change(field, { target: { value: "something else" } });
  fireEvent.click(screen.getByRole("button", { name: "Cancel edit" }));
  expect(onSend).not.toHaveBeenCalled();
  expect(container.querySelector(".msg__editing-input")).toBeNull();
  // Asked of the bubble rather than of the page: the chat is named after this same sentence, so
  // the text alone is on screen twice and proves nothing about the message.
  expect(container.querySelector(".msg__bubble").textContent).toBe("Write the intro");
});

test("enter confirms and shift-enter does not", () => {
  // The composer's own rule, so one habit works in both places. Two writable areas asking for two
  // different keys is how both of them get used wrongly.
  const onSend = vi.fn();
  const { field } = _editing(CHAT, { onSend });
  fireEvent.change(field, { target: { value: "Write a shorter intro" } });
  fireEvent.keyDown(field, { key: "Enter", shiftKey: true });
  expect(onSend).not.toHaveBeenCalled();
  fireEvent.keyDown(field, { key: "Enter" });
  expect(onSend).toHaveBeenCalledWith("Write a shorter intro", 0);
});

test("escape gives up, exactly as the cross does", () => {
  const onSend = vi.fn();
  const { container, field } = _editing(CHAT, { onSend });
  fireEvent.keyDown(field, { key: "Escape" });
  expect(onSend).not.toHaveBeenCalled();
  expect(container.querySelector(".msg__editing-input")).toBeNull();
});

test("while a message is being corrected there is no second way in", () => {
  // A pencil under an open field is a door whose meaning nobody can state: does pressing it throw
  // away what has been typed and start again? The field is closed by the tick or the cross.
  _editing();
  expect(screen.queryByRole("button", { name: "Edit message" })).toBeNull();
});

test("an ordinary reply starts from nothing", () => {
  const onSend = vi.fn();
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} onSend={onSend} />);
  const box = container.querySelector(".composer__input");
  fireEvent.change(box, { target: { value: "and the ending" } });
  fireEvent.keyDown(box, { key: "Enter" });
  expect(onSend).toHaveBeenCalledWith("and the ending", null);
});

test("a message that stands among versions says which one is showing", () => {
  render(<ChatScreen project={PROJECT} chat={BRANCHED} />);
  // The second of two: the first line's own sentence, and the edit standing where it stood.
  expect(screen.getByText("2/2")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Previous version" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Next version" })).toBeTruthy();
});

test("a message with nothing beside it draws no strip", () => {
  // Every message carries the field, so without this the arrows would sit under every sentence in
  // the chat offering to step through one thing.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(container.querySelector(".versions")).toBeNull();
});

test("the arrows ask for the version on either side", () => {
  const onVersion = vi.fn();
  render(<ChatScreen project={PROJECT} chat={BRANCHED} onVersion={onVersion} />);
  fireEvent.click(screen.getByRole("button", { name: "Previous version" }));
  expect(onVersion).toHaveBeenCalledWith("");
});

test("at the end of the row there is nothing further to step to", () => {
  const onVersion = vi.fn();
  render(<ChatScreen project={PROJECT} chat={BRANCHED} onVersion={onVersion} />);
  expect(screen.getByRole("button", { name: "Next version" }).disabled).toBe(true);
});

// --- the notes under a message, on one row (Madde 199, Madde 348) -------------------------------
//
// Madde 199 put the arrows and the pencil on a line of their own, and the time stayed on the line
// under it: two rows of notes under one sentence (user, 11 and 28 September). Design item 139 puts
// them all on the stamp's row, the time first.

const rowOf = (container, who) => container.querySelector(`.msg--${who} .msg__stamp`);
const partsOf = (row) => [...row.children].map((part) => part.className);

test("under an edited question the time, the arrows and the pencil stand on one row", () => {
  // Where the sentence stands, then the way to change it: the other order would move the pencil
  // according to whether a strip is there at all, and one button would sit in two places.
  const { container } = render(<ChatScreen project={PROJECT} chat={BRANCHED} />);
  const row = rowOf(container, "user");
  expect(partsOf(row)).toEqual(["", "versions", "msg__edit"]);
  expect(row.firstElementChild.textContent).toBe("11:04");
  expect(container.querySelector(".msg__foot")).toBeNull();
});

test("a question with nothing beside it keeps its pencil after the time", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(partsOf(rowOf(container, "user"))).toEqual(["", "msg__edit"]);
});

test("an answer's row holds its words and nothing else", () => {
  // Neither a pencil nor arrows: an answer is a whole turn, and there is nothing to go back into.
  const { container } = render(<ChatScreen project={PROJECT} chat={BRANCHED} />);
  const row = rowOf(container, "ai");
  expect(partsOf(row)).toEqual([""]);
  expect(row.textContent).toBe("11:05");
});

test("while a message is being corrected the row is the time and the strip", () => {
  // Madde 197's rule stands: the pencil withdraws. The strip does not -- which version is being
  // corrected has to stay readable while it is corrected.
  const { container } = _editing(BRANCHED);
  expect(partsOf(rowOf(container, "user"))).toEqual(["", "versions"]);
});

test("the foot puts the mode before the skill", () => {
  // Mode · Skills · Send. What the model may do at all is a question that comes before which job it
  // is doing, so the row reads outermost first.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} mode="plan" />);
  const names = [...container.querySelectorAll(".composer__foot .picker__name")];
  expect(names.map((name) => name.textContent)).toEqual(["Plan", "Skills"]);
});

// --- the full chat's notice (Madde 352) ----------------------------------------------------------

const FULL = { ...CHAT, full: true, context: { sent: 50000, ceiling: 50000 } };

test("a full chat stands a notice where the box was", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={FULL} />);
  const notice = container.querySelector(".chat__composer .full");
  expect(notice.querySelector(".full__line").textContent).toBe("This chat is full.");
  expect(notice.querySelector(".full__detail").textContent).toBe(
    "Continue here sends only the latest messages to the model; the older ones stay on screen.",
  );
  // Nothing sends from a full chat: there is no box to type in and no button to press.
  expect(screen.queryByRole("textbox")).toBeNull();
  expect(screen.queryByRole("button", { name: "Send" })).toBeNull();
});

test("the notice's gauge stands at the left of its two buttons", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={FULL} />);
  const actions = container.querySelector(".full__actions");
  expect(actions.children).toHaveLength(3);
  const [gauge, fresh, carryOn] = actions.children;
  expect(gauge.className).toBe("composer__gauge");
  expect(within(gauge).getByRole("img").getAttribute("aria-label")).toBe("This chat is full");
  expect(fresh.textContent).toBe("New chat");
  expect(carryOn.textContent).toBe("Continue here");
  // Neither is the primary action: nothing is destroyed, somebody is being asked.
  expect(fresh.classList.contains("ghost")).toBe(true);
  expect(carryOn.classList.contains("ghost")).toBe(true);
});

test("the notice's buttons ask for a new chat and for this one to carry on", () => {
  const onNewChat = vi.fn();
  const onContinue = vi.fn();
  render(
    <ChatScreen project={PROJECT} chat={FULL} onNewChat={onNewChat} onContinue={onContinue} />,
  );
  fireEvent.click(screen.getByRole("button", { name: "New chat" }));
  expect(onNewChat).toHaveBeenCalled();
  expect(onContinue).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  expect(onContinue).toHaveBeenCalled();
});

test("a chat that is not full keeps its box and draws no notice", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={{ ...CHAT, full: false }} />);
  expect(container.querySelector(".full")).toBeNull();
  expect(screen.getByRole("textbox")).toBeTruthy();
});

test("a sentence typed as the chat fills is still in the box once it carries on", () => {
  // FOUNDATION's first principle: a reply typed while the last answer ran does not go with the box.
  const { rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  fireEvent.change(screen.getByRole("textbox"), { target: { value: "and then?" } });
  rerender(<ChatScreen project={PROJECT} chat={FULL} />);
  expect(screen.queryByRole("textbox")).toBeNull();
  rerender(<ChatScreen project={PROJECT} chat={{ ...CHAT, full: false }} />);
  expect(screen.getByRole("textbox").value).toBe("and then?");
});

// --- the trim's line (Madde 357) -----------------------------------------------------------------

const TRIMMED = {
  ...CHAT,
  trimmed: 2,
  messages: [
    ...CHAT.messages,
    { role: "user", at: new Date(2026, 7, 9, 11, 6).toISOString(), text: "Shorter" },
    { role: "ai", at: new Date(2026, 7, 9, 11, 7).toISOString(), text: "Shorter it is." },
  ],
};

test("a trimmed chat draws the line before the first message still sent", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={TRIMMED} />);
  const lines = container.querySelectorAll(".trimmed");
  expect(lines).toHaveLength(1);
  const [line] = lines;
  expect(line.tagName).toBe("P");
  expect(line.parentElement.className).toBe("chat__column");
  expect(line.textContent).toBe("Messages above this line are no longer sent to the model");
  // The record's number is where the model starts reading: the first turn above, the second below.
  expect(line.previousElementSibling.textContent).toContain("Here it is.");
  expect(line.nextElementSibling.querySelector(".msg__bubble").textContent).toBe("Shorter");
});

test("a chat nobody trimmed draws no line", () => {
  const { container, rerender } = render(
    <ChatScreen project={PROJECT} chat={{ ...TRIMMED, trimmed: 0 }} />,
  );
  expect(container.querySelector(".trimmed")).toBeNull();
  // A record from before Madde 345 carries no number at all.
  rerender(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(container.querySelector(".trimmed")).toBeNull();
});

// --- the reply box's focus (Madde 365) -----------------------------------------------------------

// Search chats' Enter opens a chat and hands its reply box the focus (design 151). The box is shut
// and born again while the record is read (Madde 355), so App asks once the record is here, and the
// screen says it has done it so the ask is not repeated.

test("asked to, the screen hands the focus to the reply box and says it has", () => {
  const done = vi.fn();
  render(<ChatScreen project={PROJECT} chat={CHAT} focusReply onReplyFocused={done} />);
  expect(document.activeElement).toBe(screen.getByPlaceholderText("Reply..."));
  expect(done).toHaveBeenCalledTimes(1);
});

test("unasked, the reply box is left alone", () => {
  const done = vi.fn();
  render(<ChatScreen project={PROJECT} chat={CHAT} onReplyFocused={done} />);
  expect(document.activeElement).not.toBe(screen.getByPlaceholderText("Reply..."));
  expect(done).not.toHaveBeenCalled();
});
