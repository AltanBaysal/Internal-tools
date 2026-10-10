import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { useChat } from "./useChat.js";

// The hook draws what the server says the chat is doing (Madde 462): its record, its status and
// its running turn, read once and then listened to.

afterEach(() => vi.unstubAllGlobals());

const AT = "2026-10-10T10:00:00.000Z";
const QUESTION = { role: "user", at: AT, text: "write it", calls: [], files: [] };
const ANSWER = { role: "ai", at: AT, text: "Done.", calls: [], files: [] };

function turn(fields = {}) {
  return {
    id: "t1",
    status: "running",
    calls: [],
    files: [],
    creating: false,
    progress: null,
    permission: null,
    ...fields,
  };
}

function record(id, messages, live = null) {
  return {
    id,
    title: id,
    messages,
    status: live ? live.status : "answered",
    turn: live,
  };
}

const ok = (body, status = 200) => Promise.resolve({ ok: true, status, json: async () => body });
const no = (status, body) =>
  Promise.resolve({ ok: false, status, text: async () => JSON.stringify(body) });

// A server by hand: `reads` answers each GET of a chat in turn (the last one again once it runs
// out), `answer` the POSTs, and `events` a GET of the events door asked by hand.
function server({ reads = {}, answer = () => ok({}), events = () => ok({}) } = {}) {
  const left = Object.fromEntries(Object.entries(reads).map(([id, list]) => [id, [...list]]));
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "POST") return answer(path, JSON.parse(options.body ?? "{}"));
    if (path.endsWith("/events")) return events(path);
    const id = path.match(/\/chats\/(\w+)$/)?.[1];
    const list = left[id];
    if (!list) return no(404, { error: "chat not found" });
    return list.length > 1 ? list.shift() : list[0];
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const posts = (fetch) =>
  fetch.mock.calls
    .filter(([, options]) => options?.method === "POST")
    .map(([path, options]) => [path, JSON.parse(options.body ?? "{}")]);

const streams = () => globalThis.EventSource.opened;
const lastStream = () => streams().at(-1);
const say = (stream, data) => act(() => stream.emit(data));

function opened(chatId, handlers = {}) {
  return renderHook(
    ({ id }) => useChat("p1", id, handlers.onFile, handlers.onBorn, handlers.onEnd),
    { initialProps: { id: chatId } },
  );
}

test("a reload during a running turn draws the turn and listens to it", async () => {
  const running = turn({ calls: [{ tool: "read_file", target: "plan.md", outcome: "1 line" }] });
  server({
    reads: {
      c1: [ok(record("c1", [QUESTION], running)), ok(record("c1", [QUESTION, ANSWER]))],
    },
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.thinking).toBe(true));
  expect(result.current.streamingCalls).toEqual(running.calls);
  expect(streams().map((stream) => stream.url)).toEqual(["/api/projects/p1/chats/c1/events"]);

  say(lastStream(), { turn: turn({ ...running, progress: { round: 2, of: 32, tokens: 140 } }) });
  expect(result.current.progress).toEqual({ round: 2, of: 32, tokens: 140 });

  // The end: the stream closes and the record the turn wrote is read, its answer fading in.
  say(lastStream(), { turn: null });
  expect(lastStream().readyState).toBe(globalThis.EventSource.CLOSED);
  await waitFor(() => expect(result.current.chat.messages).toHaveLength(2));
  expect(result.current.thinking).toBe(false);
  expect(result.current.arrived).toBe(1);
});

test("a reload during a waiting question draws its card, and the answer names turn and question", async () => {
  const waiting = turn({
    status: "waiting",
    permission: { wait: 4, tool: "create_file", arguments: '{"name":"a.md"}' },
  });
  const fetch = server({ reads: { c1: [ok(record("c1", [QUESTION], waiting))] } });
  const { result } = opened("c1");
  await waitFor(() =>
    expect(result.current.permission).toEqual({ tool: "create_file", args: '{"name":"a.md"}' }),
  );
  expect(result.current.thinking).toBe(true);

  await act(() => result.current.answer(true, ""));
  expect(posts(fetch)).toEqual([
    ["/api/projects/p1/chats/c1/permission", { turn: "t1", wait: 4, allowed: true }],
  ]);
  // Taken down at once, before the server's frame says so.
  expect(result.current.permission).toBeNull();
});

test("an answer the server never got puts the card back", async () => {
  const waiting = turn({ status: "waiting", permission: { wait: 4, tool: "edit_file", arguments: "{}" } });
  server({
    reads: { c1: [ok(record("c1", [QUESTION], waiting))] },
    answer: () => Promise.reject(new TypeError("Failed to fetch")),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.permission).not.toBeNull());
  await act(() => result.current.answer(true, ""));
  expect(result.current.permission).toEqual({ tool: "edit_file", args: "{}" });
});

test("a deny carries its reason, and Stop names the turn it was pressed for", async () => {
  const waiting = turn({ status: "waiting", permission: { wait: 2, tool: "edit_file", arguments: "{}" } });
  const fetch = server({ reads: { c1: [ok(record("c1", [QUESTION], waiting))] } });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.permission).not.toBeNull());
  await act(() => result.current.answer(false, "not that one"));
  await act(() => result.current.stop());
  expect(posts(fetch)).toEqual([
    [
      "/api/projects/p1/chats/c1/permission",
      { turn: "t1", wait: 2, allowed: false, reason: "not that one" },
    ],
    ["/api/projects/p1/chats/c1/stop", { turn: "t1" }],
  ]);
});

test("a dropped connection is mended by the browser, with no card", async () => {
  server({ reads: { c1: [ok(record("c1", [QUESTION], turn()))] } });
  const { result } = opened("c1");
  await waitFor(() => expect(streams()).toHaveLength(1));
  act(() => lastStream().drop());
  // EventSource reconnects by itself, and the first frame is the turn as it stands.
  say(lastStream(), { turn: turn({ files: ["a.md"] }) });
  expect(result.current.createdFiles).toEqual(["a.md"]);
  expect(result.current.error).toBeNull();
  expect(streams()).toHaveLength(1);
});

test("a stream refused before it said anything has its door asked, and the card says what it said", async () => {
  // The tunnel's 502 on the first connect: EventSource passes on nothing of it, so the door is asked
  // once by hand. Left alone, the dots and Stop stood for ever with nothing to press.
  const fetch = server({
    reads: { c1: [ok(record("c1", [QUESTION], turn()))] },
    events: () => Promise.resolve({ ok: false, status: 502, text: async () => "Bad Gateway" }),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(streams()).toHaveLength(1));
  act(() => lastStream().refuse());
  await waitFor(() => expect(result.current.error).toBe("HTTP 502: Bad Gateway"));
  expect(streams()).toHaveLength(1);
  expect(fetch.mock.calls.filter(([path]) => path.endsWith("/events"))).toHaveLength(1);
  // The card takes the wait's place, as the failure card does: nothing frozen above it.
  expect([result.current.thinking, result.current.progress, result.current.creatingFile]).toEqual([
    false,
    null,
    false,
  ]);
});

test("the refused stream's Try again brings the live view back", async () => {
  server({
    reads: { c1: [ok(record("c1", [QUESTION], turn({ creating: true })))] },
    events: () => Promise.resolve({ ok: false, status: 524, text: async () => "A timeout occurred" }),
    answer: () => ok(record("c1", [QUESTION], turn()), 200),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(streams()).toHaveLength(1));
  act(() => lastStream().refuse());
  await waitFor(() => expect(result.current.error).toBe("HTTP 524: A timeout occurred"));
  expect(result.current.thinking).toBe(false);
  await act(() => result.current.answerAgain("edit"));
  expect(result.current.error).toBeNull();
  expect(result.current.thinking).toBe(true);
  expect(lastStream().readyState).not.toBe(globalThis.EventSource.CLOSED);
});

test("a door that answers the hand is listened to once more, and not asked a second time", async () => {
  const fetch = server({ reads: { c1: [ok(record("c1", [QUESTION], turn()))] } });
  const { result } = opened("c1");
  await waitFor(() => expect(streams()).toHaveLength(1));
  act(() => lastStream().refuse());
  await waitFor(() => expect(streams()).toHaveLength(2));
  // Refused again before a word: no third stream and no second ask, but a card to press.
  act(() => lastStream().refuse());
  await waitFor(() => expect(result.current.error).toBe("the browser closed this answer's stream"));
  expect(result.current.thinking).toBe(false);
  expect(streams()).toHaveLength(2);
  expect(fetch.mock.calls.filter(([path]) => path.endsWith("/events"))).toHaveLength(1);
});

test("a stream that had worked is opened again as it was, without a read", async () => {
  const fetch = server({ reads: { c1: [ok(record("c1", [QUESTION], turn()))] } });
  opened("c1");
  await waitFor(() => expect(streams()).toHaveLength(1));
  say(lastStream(), { turn: turn() });
  act(() => lastStream().refuse());
  expect(streams()).toHaveLength(2);
  expect(fetch.mock.calls.filter(([path]) => path.endsWith("/chats/c1"))).toHaveLength(1);
});

test("a stream refused before a word whose turn has ended draws the record and asks nothing", async () => {
  const fetch = server({
    reads: { c1: [ok(record("c1", [QUESTION], turn())), ok(record("c1", [QUESTION, ANSWER]))] },
  });
  const { result } = opened("c1");
  await waitFor(() => expect(streams()).toHaveLength(1));
  act(() => lastStream().refuse());
  await waitFor(() => expect(result.current.chat.messages).toHaveLength(2));
  expect(result.current.thinking).toBe(false);
  expect(fetch.mock.calls.filter(([path]) => path.endsWith("/events"))).toHaveLength(0);
});

test("when the read after a refused stream fails, the card says what the read said", async () => {
  server({
    reads: { c1: [ok(record("c1", [QUESTION], turn())), no(502, { error: "HTTP 502: Bad Gateway" })] },
  });
  const { result } = opened("c1");
  await waitFor(() => expect(streams()).toHaveLength(1));
  act(() => lastStream().refuse());
  await waitFor(() => expect(result.current.error).toBe("HTTP 502: Bad Gateway"));
});

test("a sentence is drawn at once and handed over to the server's record", async () => {
  let reply;
  const fetch = server({
    reads: { c1: [ok(record("c1", [QUESTION, ANSWER]))] },
    answer: () => new Promise((resolve) => (reply = resolve)),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  let sent;
  act(() => {
    sent = result.current.send("more", "verify", "edit");
  });
  expect(result.current.chat.messages.map((message) => message.text)).toEqual([
    "write it",
    "Done.",
    "more",
  ]);
  // The wait, and its Stop, stand from the moment the sentence leaves.
  expect(result.current.thinking).toBe(true);
  const asked = { ...QUESTION, text: "more", at: "2026-10-10T10:01:00.000Z" };
  await act(async () => {
    reply({ ok: true, status: 202, json: async () => record("c1", [QUESTION, ANSWER, asked], turn()) });
    await sent;
  });
  expect(result.current.chat.messages.at(-1).at).toBe("2026-10-10T10:01:00.000Z");
  expect(result.current.thinking).toBe(true);
  expect(posts(fetch)).toEqual([
    ["/api/projects/p1/messages", { chat: "c1", text: "more", skill: "verify", mode: "edit" }],
  ]);
  expect(lastStream().url).toBe("/api/projects/p1/chats/c1/events");
});

test("a Stop pressed before the door answers is sent with the turn the door names", async () => {
  let reply;
  const fetch = server({
    reads: { c1: [ok(record("c1", [QUESTION, ANSWER]))] },
    answer: (path) =>
      path.endsWith("/messages") ? new Promise((resolve) => (reply = resolve)) : ok({ turn: null }),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  let sent;
  act(() => {
    sent = result.current.send("more", "", "edit");
  });
  await act(() => result.current.stop());
  expect(posts(fetch)).toHaveLength(1);
  await act(async () => {
    reply({ ok: true, status: 202, json: async () => record("c1", [QUESTION], turn({ id: "t5" })) });
    await sent;
  });
  expect(posts(fetch).at(-1)).toEqual(["/api/projects/p1/chats/c1/stop", { turn: "t5" }]);
});

test("a Stop pressed for a send the server refused goes nowhere", async () => {
  let refuse;
  const fetch = server({
    reads: { c1: [ok(record("c1", [QUESTION, ANSWER]))] },
    answer: () => new Promise((resolve) => (refuse = resolve)),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  let sent;
  act(() => {
    sent = result.current.send("more", "", "edit").catch(() => {});
  });
  await act(() => result.current.stop());
  await act(async () => {
    refuse({ ok: false, status: 400, text: async () => JSON.stringify({ error: "no" }) });
    await sent;
  });
  expect(posts(fetch).map(([path]) => path)).toEqual(["/api/projects/p1/messages"]);
});

test("a draft's first answer names the chat it was born as", async () => {
  const onBorn = vi.fn();
  server({ answer: () => ok(record("c9", [QUESTION], turn()), 202) });
  const { result } = opened(null, { onBorn });
  await act(() => result.current.send("write it", "", "edit"));
  expect(onBorn).toHaveBeenCalledWith("c9");
  expect(lastStream().url).toBe("/api/projects/p1/chats/c9/events");
});

// --- the chat's mode (Madde 463) -------------------------------------------------------------------

function deferred() {
  let settle;
  const promise = new Promise((resolve) => {
    settle = resolve;
  });
  return { promise, settle };
}

test("a draft's first message carries the mode it was picked in, and a chat's message carries none", async () => {
  const fetch = server({ answer: () => ok(record("c9", [QUESTION]), 202) });
  const draft = opened(null);
  await act(() => draft.result.current.send("write it", "", "plan"));
  const chat = opened("c1");
  await act(() => chat.result.current.send("more", "", ""));
  expect(posts(fetch).map(([, body]) => body.mode)).toEqual(["plan", undefined]);
});

test("a pick is drawn at once, sent to the chat's own door, and becomes the chat's mode", async () => {
  const answered = deferred();
  const fetch = server({
    reads: { c1: [ok({ ...record("c1", [QUESTION, ANSWER]), mode: "edit" })] },
    answer: () => answered.promise,
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat?.mode).toBe("edit"));
  let picking;
  act(() => {
    picking = result.current.pickMode("ask");
  });
  // Before the server has said a word: the picker answers the click.
  expect(result.current.chat.mode).toBe("ask");
  await waitFor(() =>
    expect(posts(fetch)).toEqual([["/api/projects/p1/chats/c1/mode", { mode: "ask" }]]),
  );
  await act(async () => {
    answered.settle({ ok: true, status: 200, json: async () => ({ mode: "ask" }) });
    await picking;
  });
  expect(result.current.chat.mode).toBe("ask");
  expect(result.current.error).toBeNull();
});

// Each pick answered by hand, in whatever order the test settles them.
function picksAnsweredByHand(mode = "edit") {
  const asked = [];
  const fetch = server({
    reads: { c1: [ok({ ...record("c1", [QUESTION, ANSWER]), mode })] },
    answer: () => {
      const answered = deferred();
      asked.push(answered);
      return answered.promise;
    },
  });
  const said = (body) => ({ ok: true, status: 200, json: async () => body });
  return { fetch, asked, said };
}

test("a second pick waits for the first one's answer, so the server takes them in click order", async () => {
  // Sent side by side, two picks can reach the server either way round: Edit, then a quick
  // correction to Ask, could end with the server in Edit and the screen in Ask.
  const { fetch, asked, said } = picksAnsweredByHand();
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat?.mode).toBe("edit"));
  let second;
  act(() => {
    result.current.pickMode("plan");
    second = result.current.pickMode("ask");
  });
  expect(result.current.chat.mode).toBe("ask");
  await waitFor(() => expect(asked).toHaveLength(1));
  expect(posts(fetch)).toEqual([["/api/projects/p1/chats/c1/mode", { mode: "plan" }]]);
  await act(async () => asked[0].settle(said({ mode: "plan" })));
  await waitFor(() => expect(posts(fetch)).toHaveLength(2));
  expect(posts(fetch)[1]).toEqual(["/api/projects/p1/chats/c1/mode", { mode: "ask" }]);
  // The first answer does not draw over the pick still on its way.
  expect(result.current.chat.mode).toBe("ask");
  await act(async () => {
    asked[1].settle(said({ mode: "ask" }));
    await second;
  });
  expect(result.current.chat.mode).toBe("ask");
});

test("an earlier pick the server took stands when the later one is refused", async () => {
  // The answers come in click order, so each says where the server is: the one it took is drawn.
  const { asked, said } = picksAnsweredByHand();
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat?.mode).toBe("edit"));
  let second;
  act(() => {
    result.current.pickMode("plan");
    second = result.current.pickMode("ask");
  });
  await waitFor(() => expect(asked).toHaveLength(1));
  await act(async () => asked[0].settle(said({ mode: "plan" })));
  await waitFor(() => expect(asked).toHaveLength(2));
  await act(async () => {
    asked[1].settle({
      ok: false,
      status: 500,
      text: async () => JSON.stringify({ error: "projects.json is busy" }),
    });
    await second;
  });
  expect(result.current.chat.mode).toBe("plan");
  expect(result.current.error).toBe("projects.json is busy");
});

test("picking the mode already shown asks the server nothing", async () => {
  const { fetch } = picksAnsweredByHand("ask");
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat?.mode).toBe("ask"));
  await act(() => result.current.pickMode("ask"));
  expect(posts(fetch)).toEqual([]);
});

test("a refused pick goes back to the chat's mode, and the card says what the server said", async () => {
  server({
    reads: { c1: [ok({ ...record("c1", [QUESTION, ANSWER]), mode: "plan" })] },
    answer: () => no(400, { error: "mode must be plan, ask or edit" }),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat?.mode).toBe("plan"));
  await act(() => result.current.pickMode("ask"));
  expect(result.current.chat.mode).toBe("plan");
  expect(result.current.error).toBe("mode must be plan, ask or edit");
});

test("an answer to a question draws the mode the server says the chat is in", async () => {
  // The switch to Edit after an Allow is the server's rule: the screen draws what it is told.
  const waiting = turn({ status: "waiting", permission: { wait: 4, tool: "create_file", arguments: "{}" } });
  server({
    reads: { c1: [ok({ ...record("c1", [QUESTION], waiting), mode: "ask" })] },
    answer: () => ok({ turn: turn(), mode: "edit" }),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.permission).not.toBeNull());
  await act(() => result.current.answer(true, ""));
  expect(result.current.chat.mode).toBe("edit");
});

test("an edit refused while a turn runs leaves the transcript whole and follows that turn", async () => {
  // 461's QA: the transcript went blank until a reload, and the refusal was thrown uncaught.
  const live = turn({ id: "t7" });
  server({
    reads: { c1: [ok(record("c1", [QUESTION, ANSWER]))] },
    answer: () =>
      no(409, { error: "this chat is still answering", ...record("c1", [QUESTION, ANSWER], live) }),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  let refusal;
  await act(async () => {
    refusal = await result.current.send("write it better", "", "edit", 0).catch((failure) => failure);
  });
  // Thrown on, so the field that held the sentence takes it back.
  expect(refusal.message).toBe("this chat is still answering");
  expect(result.current.chat.messages.map((message) => message.text)).toEqual(["write it", "Done."]);
  expect(result.current.refused).toBe("this chat is still answering");
  expect(result.current.thinking).toBe(true);
});

test("a send refused into another tab's turn draws the chat as that turn holds it", async () => {
  // QA of 462: the tab was out of date, and the wait stood under its old record -- without the other
  // tab's question, and with no time.
  const theirs = { ...QUESTION, text: "the other tab's question", at: "2026-10-10T10:05:00.000Z" };
  server({
    reads: { c1: [ok(record("c1", [QUESTION, ANSWER]))] },
    answer: () =>
      no(409, { error: "this chat is still answering", ...record("c1", [QUESTION, ANSWER, theirs], turn()) }),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  await act(async () => {
    await result.current.send("mine", "", "edit").catch(() => {});
  });
  expect(result.current.chat.messages.map((message) => message.text)).toEqual([
    "write it",
    "Done.",
    "the other tab's question",
  ]);
  expect(result.current.chat.error).toBeUndefined();
  expect(result.current.refused).toBe("this chat is still answering");
  expect(result.current.thinking).toBe(true);
  await waitFor(() => expect(lastStream()?.url).toBe("/api/projects/p1/chats/c1/events"));
});

test("a turn this hook started is heard to its end off screen, and draws nothing there", async () => {
  const onEnd = vi.fn();
  server({
    reads: {
      c1: [ok(record("c1", [QUESTION, ANSWER]))],
      c2: [ok(record("c2", [QUESTION, ANSWER]))],
    },
    answer: () => ok(record("c1", [QUESTION, ANSWER, QUESTION], turn()), 202),
  });
  const { result, rerender } = opened("c1", { onEnd });
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  await act(() => result.current.send("again", "", "edit"));
  const own = lastStream();

  rerender({ id: "c2" });
  await waitFor(() => expect(result.current.chat?.id).toBe("c2"));
  // Kept open: 452's list is read once the turn is over, wherever the user is.
  expect(own.readyState).not.toBe(globalThis.EventSource.CLOSED);
  say(own, { turn: turn({ files: ["a.md"] }) });
  expect(result.current.createdFiles).toEqual([]);
  say(own, { turn: null });
  expect(onEnd).toHaveBeenCalledTimes(1);
  expect(own.readyState).toBe(globalThis.EventSource.CLOSED);
  expect(result.current.chat.id).toBe("c2");
});

test("a stream the screen opened closes when the screen leaves the chat", async () => {
  server({
    reads: {
      c1: [ok(record("c1", [QUESTION], turn()))],
      c2: [ok(record("c2", [QUESTION, ANSWER]))],
    },
  });
  const { rerender } = opened("c1");
  await waitFor(() => expect(streams()).toHaveLength(1));
  rerender({ id: "c2" });
  expect(streams()[0].readyState).toBe(globalThis.EventSource.CLOSED);
});

test("a file born mid-turn is announced once", async () => {
  const onFile = vi.fn();
  server({ reads: { c1: [ok(record("c1", [QUESTION], turn()))] } });
  opened("c1", { onFile });
  await waitFor(() => expect(streams()).toHaveLength(1));
  say(lastStream(), { turn: turn({ files: ["a.md"] }) });
  say(lastStream(), { turn: turn({ files: ["a.md"], progress: { round: 2, of: 32, tokens: 9 } }) });
  expect(onFile).toHaveBeenCalledTimes(1);
});

test("a turn whose own code broke ends on its words over the unanswered question", async () => {
  server({
    reads: { c1: [ok(record("c1", [QUESTION], turn())), ok({ ...record("c1", [QUESTION]), status: "unanswered" })] },
  });
  const { result } = opened("c1");
  await waitFor(() => expect(streams()).toHaveLength(1));
  say(lastStream(), { turn: null, error: "the disk went away" });
  await waitFor(() => expect(result.current.error).toBe("the disk went away"));
  expect(result.current.thinking).toBe(false);
});

test("an unanswered question is drawn as it is, with nothing asked and no card", async () => {
  const fetch = server({ reads: { c1: [ok({ ...record("c1", [QUESTION]), status: "unanswered" })] } });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  expect([result.current.error, result.current.refused, result.current.thinking]).toEqual([
    null,
    null,
    false,
  ]);
  expect(posts(fetch)).toEqual([]);
  expect(streams()).toHaveLength(0);
});

test("Try again asks its own door, and draws what it answers", async () => {
  const failed = { ...ANSWER, text: "HTTP 502", failed: "technical" };
  const fetch = server({
    reads: { c1: [ok({ ...record("c1", [QUESTION, failed]), status: "failed" })] },
    answer: () => ok(record("c1", [QUESTION], turn()), 202),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  await act(() => result.current.answerAgain());
  // No mode: the chat holds its own (Madde 463).
  expect(posts(fetch)).toEqual([["/api/projects/p1/chats/c1/retry", {}]]);
  // The failed answer is gone the moment the door answers: it is the server's record now.
  expect(result.current.chat.messages).toHaveLength(1);
  expect(result.current.thinking).toBe(true);
});

async function startedThenLeft(onEnd) {
  server({
    reads: {
      c1: [ok(record("c1", [QUESTION, ANSWER]))],
      c2: [ok(record("c2", [QUESTION, ANSWER]))],
    },
    answer: () => ok(record("c1", [QUESTION, ANSWER, QUESTION], turn()), 202),
  });
  const view = opened("c1", { onEnd });
  await waitFor(() => expect(view.result.current.chat).not.toBeNull());
  await act(() => view.result.current.send("again", "", "edit"));
  const own = lastStream();
  view.rerender({ id: "c2" });
  await waitFor(() => expect(view.result.current.chat?.id).toBe("c2"));
  return own;
}

test("an own stream that had worked and gives up off screen is opened again, and its end still heard", async () => {
  const onEnd = vi.fn();
  const own = await startedThenLeft(onEnd);
  say(own, { turn: turn() });
  act(() => own.refuse());
  expect(streams()).toHaveLength(2);
  say(lastStream(), { turn: null });
  expect(onEnd).toHaveBeenCalledTimes(1);
});

test("an own stream that never worked and gives up off screen ends its turn's upkeep once", async () => {
  const onEnd = vi.fn();
  const own = await startedThenLeft(onEnd);
  act(() => own.refuse());
  expect(onEnd).toHaveBeenCalledTimes(1);
  expect(streams()).toHaveLength(1);
});

test("a tab-return read that lands after a send's answer does not draw over it", async () => {
  // The look left before the send; what it brings back is older than what the door answered.
  let look;
  const more = { ...QUESTION, text: "more" };
  server({
    reads: {
      c1: [ok(record("c1", [QUESTION, ANSWER])), new Promise((resolve) => (look = resolve))],
    },
    answer: () => ok(record("c1", [QUESTION, ANSWER, more], turn()), 202),
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  await act(async () => window.dispatchEvent(new Event("focus")));
  await act(() => result.current.send("more", "", "edit"));
  await act(async () => look({ ok: true, status: 200, json: async () => record("c1", [QUESTION, ANSWER]) }));
  expect(result.current.chat.messages).toHaveLength(3);
  expect(result.current.thinking).toBe(true);
});

test("coming back to the tab reads the chat once, and a turn another tab started is listened to", async () => {
  // The item's "iki sekme aynı şeyi görür", for a tab that sat idle in the chat.
  const fetch = server({
    reads: { c1: [ok(record("c1", [QUESTION, ANSWER])), ok(record("c1", [QUESTION, ANSWER, QUESTION], turn()))] },
  });
  const { result } = opened("c1");
  await waitFor(() => expect(result.current.chat).not.toBeNull());
  expect(streams()).toHaveLength(0);
  await act(async () => window.dispatchEvent(new Event("focus")));
  await waitFor(() => expect(result.current.thinking).toBe(true));
  expect(lastStream().url).toBe("/api/projects/p1/chats/c1/events");
  // Already followed: coming back again reads nothing.
  await act(async () => document.dispatchEvent(new Event("visibilitychange")));
  expect(fetch.mock.calls.filter(([path]) => path.endsWith("/chats/c1"))).toHaveLength(2);
});
