import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Which chat is open, whether the list is, and the drafts are remembered for the length of a visit,
// and that memory lives in the module. So each test gets the module fresh, and starts the way a
// reloaded page does. Nothing is mocked in this file, so resetModules really does rebuild it.
let AgentPanel;

beforeEach(async () => {
  vi.resetModules();
  ({ default: AgentPanel } = await import("./AgentPanel.jsx"));
  vi.useFakeTimers();
});

afterEach(() => {
  vi.restoreAllMocks();
});

const PROJECT = "düğün";
const POLL_MS = 1000;
const ASKED = "2026-10-06T10:00:00+00:00";
const REFUSED = "Model hata döndü, farklı şekilde dene.";
const UNREACHED = "Sunucuya ulaşılamadı — bağlantıyı kontrol et.";
const BUSY = "Bu sohbette agent hâlâ çalışıyor.";

// Each step carries both of the server's sentences: the one while it goes on, the one when done.
const LOOKING = ["Projeye bakıyor…", "Projeye baktı"];
const READING_2 = ["2 numaralı kareyi okuyor…", "2 numaralı kareyi okudu"];
const READING_3 = ["3 numaralı kareyi okuyor…", "3 numaralı kareyi okudu"];

const step = ([running, done], finished = true) => ({ running, done, finished });
const question = (text, askedAt, steps = [], outcome = null) => ({ text, askedAt, steps, outcome });
const answered = (text) => ({ kind: "answer", text });

// Built in local time, so the date the row shows does not depend on the machine's zone.
const FIRST = { id: 1, questions: [question(
  "Hangi kareler hata verdi?", new Date(2026, 9, 4, 18, 5).toISOString(),
  [step(LOOKING)], answered("7 numaralı karenin fotoğrafı üretilemedi."))] };
const SECOND = { id: 2, questions: [question(
  "Kaç karede video var?", new Date(2026, 9, 5, 15, 48).toISOString(),
  [step(LOOKING), step(READING_2)], answered("Videosu olan 4 kare var."))] };
// A chat whose agent is reading frame 3, when the server says it works; cut off when it does not.
const WORKING = { id: 1, questions: [question(
  "12 numaralı karenin prompt'u ne?", ASKED, [step(LOOKING), step(READING_3, false)])] };

// A server that keeps the project's chats and answers the six doors of 417 and 420 in their shape.
// A test changes what it holds -- a step written, an answer given, the network gone, a question
// held on its way -- and moves the clock: what the screen then shows came through its own requests.
function fakeServer({ chats = [], working = [] } = {}) {
  const server = {
    chats: structuredClone(chats),
    working: [...working],
    calls: [],          // "METHOD path", the project's name as it was before encoding
    bodies: [],         // every JSON body sent
    down: false,        // no request reaches it
    refusal: null,      // { status, error } every question gets
    hold: false,        // a question stays on its way until release()
    release: null,
  };
  const find = (id) => server.chats.find((chat) => chat.id === id);
  const last = (id) => find(id).questions.at(-1);
  const finishLast = (steps) => { if (steps.length) steps.at(-1).finished = true; };

  // The agent starts a step: the one before it is finished (420's loop).
  server.step = (id, words) => {
    finishLast(last(id).steps);
    last(id).steps.push(step(words, false));
  };
  // An answer or a failure finishes the last step, and the chat no longer works (420's record).
  server.end = (id, outcome) => {
    finishLast(last(id).steps);
    last(id).outcome = outcome;
    server.working = server.working.filter((one) => one !== id);
  };

  // The body is written out at once: what the screen holds is never the server's own object.
  function reply(status, body) {
    const text = JSON.stringify(body);
    return Promise.resolve({ ok: status < 400, status, statusText: "", text: async () => text });
  }

  function ask(id, text) {
    find(id).questions.push(question(text, ASKED));
    server.working.push(id);
    return reply(200, find(id));
  }

  server.fetch = vi.fn((url, options = {}) => {
    const method = options.method || "GET";
    const path = decodeURIComponent(url);
    server.calls.push(`${method} ${path}`);
    if (options.body) server.bodies.push(JSON.parse(options.body));
    if (server.down) return Promise.reject(new TypeError("Failed to fetch"));
    const [, rest] = path.match(/^\/api\/projects\/[^/]+\/chats(.*)$/);
    if (rest === "" && method === "GET") {
      const rows = server.chats.filter((chat) => chat.questions.length)
        .map((chat) => ({ id: chat.id, firstQuestion: chat.questions[0].text,
                          lastAskedAt: chat.questions.at(-1).askedAt }))
        .sort((a, b) => (a.lastAskedAt < b.lastAskedAt ? 1 : -1));
      return reply(200, { chats: rows });
    }
    if (rest === "" && method === "POST") {
      let chat = server.chats.find((one) => !one.questions.length);
      if (!chat) {
        chat = { id: Math.max(0, ...server.chats.map((one) => one.id)) + 1, questions: [] };
        server.chats.push(chat);
      }
      return reply(200, chat);
    }
    if (rest === "/working") {
      return reply(200, { working: [...server.working].sort((a, b) => a - b) });
    }
    const [, number, door] = rest.match(/^\/(\d+)(?:\/(\w+))?$/);
    const id = Number(number);
    if (!find(id)) return reply(404, { error: `Sohbet yok: ${id}` });
    if (!door) return reply(200, find(id));
    if (door === "questions") {
      if (server.refusal) return reply(server.refusal.status, { error: server.refusal.error });
      const { text } = JSON.parse(options.body);
      if (!server.hold) return ask(id, text);
      return new Promise((resolve) => { server.release = () => resolve(ask(id, text)); });
    }
    // The stop door: the finished steps stay, the one going on is dropped (420's record). A chat
    // that does not work is left as it is.
    if (server.working.includes(id)) {
      last(id).steps = last(id).steps.filter((one) => one.finished);
      last(id).outcome = { kind: "stopped" };
      server.working = server.working.filter((one) => one !== id);
    }
    return reply(200, find(id));
  });
  vi.stubGlobal("fetch", server.fetch);
  return server;
}

// Testing Library's waitFor does not understand vitest's fake clock: the clock is moved inside
// act(), which runs the timers and the promises they unblock.
async function settle(ms = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
}

async function open(project = PROJECT) {
  const view = render(<AgentPanel project={project} heading={<h2>AI agent</h2>} />);
  await settle();
  return view;
}

const box = () => screen.getByLabelText("Soru");
const send = () => screen.getByRole("button", { name: "Gönder" });
const stop = () => screen.getByRole("button", { name: "Durdur" });
const list = () => screen.getByRole("button", { name: "Sohbetler" });
const newChat = () => screen.getByRole("button", { name: "Yeni sohbet" });
const lines = () => [...document.querySelectorAll(".qe-chat-step")].map((line) => line.textContent);
const liveLines = () => [...document.querySelectorAll(".qe-chat-step.is-live")]
  .map((line) => line.textContent);
const chatsUrl = (rest = "") => `/api/projects/${PROJECT}/chats${rest}`;

function type(text) {
  fireEvent.change(box(), { target: { value: text } });
}

async function enter(options = {}) {
  const notPrevented = fireEvent.keyDown(box(), { key: "Enter", ...options });
  await settle();
  return notPrevented;
}

describe("AgentPanel — opening", () => {
  it("opens the newest chat with its question, its finished steps and its answer", async () => {
    const server = fakeServer({ chats: [FIRST, SECOND] });

    await open();

    expect(screen.getByText("Kaç karede video var?").className).toContain("qe-chat-q");
    expect(lines()).toEqual(["Projeye baktı", "2 numaralı kareyi okudu"]);
    expect(screen.getByText("Videosu olan 4 kare var.").className).toContain("qe-chat-a");
    expect(screen.queryByText("Hangi kareler hata verdi?")).toBeNull();
    expect(document.querySelector(".qe-dot--alive")).toBeNull();
    expect(send().disabled).toBe(true);
    // Who works is asked before the chat is read (spec, rule 27), and no new chat is made.
    expect(server.calls).toEqual(
      [`GET ${chatsUrl()}`, `GET ${chatsUrl("/working")}`, `GET ${chatsUrl("/2")}`]);
  });

  it("opens the empty chat waiting when nothing has been asked yet", async () => {
    const server = fakeServer();

    await open();

    expect(server.calls).toContain(`POST ${chatsUrl()}`);
    expect(screen.getByText("Projeyle ilgili bir şey sor.")).toBeTruthy();
    expect(box().placeholder).toBe("Sorunu yaz…");
    expect(send().disabled).toBe(true);
  });

  it("comes back after a reload on the newest chat with its agent still at work", async () => {
    fakeServer({ chats: [WORKING], working: [1] });

    await open();

    expect(lines()).toEqual(["Projeye baktı", "3 numaralı kareyi okuyor…"]);
    expect(liveLines()).toEqual(["3 numaralı kareyi okuyor…"]);
    expect(document.querySelector(".qe-chat-step.is-live .qe-dot--alive")).toBeTruthy();
    expect(stop().disabled).toBe(false);
  });

  it("draws a question cut off by a restart without an answer, its open step not live", async () => {
    // No outcome, and the server says nobody works on it: the run died with the process (420).
    const server = fakeServer({ chats: [WORKING] });

    await open();

    expect(lines()).toEqual(["Projeye baktı", "3 numaralı kareyi okuyor…"]);
    expect(document.querySelector(".qe-dot--alive")).toBeNull();
    expect(screen.queryByText("Durduruldu")).toBeNull();
    expect(screen.queryByText("Çalışıyor…")).toBeNull();
    expect(send()).toBeTruthy();
    const asked = server.calls.length;
    await settle(5 * POLL_MS);
    expect(server.calls).toHaveLength(asked);
  });

  it("says so when the chat cannot be read", async () => {
    const server = fakeServer({ chats: [FIRST] });
    server.down = true;

    await open();

    expect(screen.getByText(UNREACHED).className).toContain("qe-chat-err");
    expect(screen.queryByLabelText("Soru")).toBeNull();
  });

  it("puts the heading and the chat's two buttons in one row", async () => {
    fakeServer();

    await open();

    const row = screen.getByRole("heading", { name: "AI agent" }).parentElement;
    expect(row.className).toContain("qe-chat-head");
    expect(row.contains(newChat())).toBe(true);
    expect(row.contains(list())).toBe(true);
  });
});

describe("AgentPanel — asking", () => {
  it("sends on Enter: the box empties, the question is a bubble and the agent works", async () => {
    const server = fakeServer();
    await open();

    type("Kaç kare var?");
    await enter();

    expect(server.calls).toContain(`POST ${chatsUrl("/1/questions")}`);
    expect(server.bodies).toEqual([{ text: "Kaç kare var?" }]);
    expect(box().value).toBe("");
    expect(screen.getByText("Kaç kare var?").className).toContain("qe-chat-q");
    // The server has written no step yet: the wait line says the agent is at it.
    expect(liveLines()).toEqual(["Çalışıyor…"]);
    expect(stop()).toBeTruthy();
  });

  it("does not send on Shift+Enter, and leaves the key to the box", async () => {
    const server = fakeServer();
    await open();

    type("Kaç kare var?");
    const notPrevented = await enter({ shiftKey: true });

    // The line break is the browser's own: the key is not taken from it.
    expect(notPrevented).toBe(true);
    expect(server.bodies).toEqual([]);
  });

  it.each(["", "   ", "\n"])("keeps the arrow off while the box holds %j", async (text) => {
    fakeServer();
    await open();

    type(text);
    expect(send().disabled).toBe(true);

    type("a");
    expect(send().disabled).toBe(false);
  });

  it("sends on the arrow without the spaces around the words, and gives the focus back to the box",
     async () => {
       const server = fakeServer();
       await open();

       type("  Kaç kare var?\n");
       fireEvent.click(send());
       await settle();

       expect(server.bodies).toEqual([{ text: "Kaç kare var?" }]);
       expect(document.activeElement).toBe(box());
     });

  it("shows a question on its way with Çalışıyor…, and ■ does nothing before it arrives",
     async () => {
       const server = fakeServer();
       server.hold = true;
       await open();

       type("Kaç kare var?");
       await enter();

       expect(screen.getByText("Kaç kare var?").className).toContain("qe-chat-q");
       expect(liveLines()).toEqual(["Çalışıyor…"]);
       // No agent has started yet, so there is nothing to stop.
       fireEvent.click(stop());
       await settle();
       expect(server.calls.filter((call) => call.endsWith("/stop"))).toEqual([]);

       server.release();
       await settle();

       // The server's chat takes the question's place: it is drawn once.
       expect(screen.getAllByText("Kaç kare var?")).toHaveLength(1);
       expect(liveLines()).toEqual(["Çalışıyor…"]);
       expect(stop()).toBeTruthy();
     });

  it("puts the steps under the question as they come, the one going on last and live",
     async () => {
       const server = fakeServer();
       await open();
       type("Kaç kare var?");
       await enter();

       server.step(1, LOOKING);
       await settle(POLL_MS);
       expect(liveLines()).toEqual(["Projeye bakıyor…"]);

       server.step(1, READING_2);
       await settle(POLL_MS);
       expect(lines()).toEqual(["Projeye baktı", "2 numaralı kareyi okuyor…"]);
       expect(liveLines()).toEqual(["2 numaralı kareyi okuyor…"]);
     });

  it("puts the answer under its steps at once, turns the button back and stops asking",
     async () => {
       const server = fakeServer({ chats: [WORKING], working: [1] });
       await open();

       server.end(1, answered("12 numaralı karenin prompt'u: ürün kumsalda."));
       await settle(POLL_MS);

       expect(lines()).toEqual(["Projeye baktı", "3 numaralı kareyi okudu"]);
       expect(screen.getByText("12 numaralı karenin prompt'u: ürün kumsalda.").className)
         .toContain("qe-chat-a");
       expect(document.querySelector(".qe-dot--alive")).toBeNull();
       expect(send()).toBeTruthy();
       const asked = server.calls.length;
       await settle(5 * POLL_MS);
       expect(server.calls).toHaveLength(asked);
     });

  it.each([REFUSED, "DeepSeek HTTP 500: Internal Server Error"])(
    "puts a failure in the answer's place as a card in the server's words: %s", async (text) => {
      const server = fakeServer({ chats: [WORKING], working: [1] });
      await open();

      server.end(1, { kind: "failure", text });
      await settle(POLL_MS);

      expect(screen.getByText(text).className).toContain("qe-chat-err");
      expect(lines()).toEqual(["Projeye baktı", "3 numaralı kareyi okudu"]);
      // No way to ask again from the card: the user writes the question again.
      expect(screen.queryByRole("button", { name: /dene/i })).toBeNull();
      expect(send()).toBeTruthy();
    });

  it.each([
    ["the network is gone", (server) => { server.down = true; }, UNREACHED],
    ["the server refuses it", (server) => { server.refusal = { status: 409, error: BUSY }; }, BUSY],
  ])("keeps a question the server did not take as a bubble over a card when %s",
     async (_, cut, said) => {
       const server = fakeServer();
       await open();

       type("Kaç kare var?");
       cut(server);
       await enter();

       expect(screen.getByText("Kaç kare var?").className).toContain("qe-chat-q");
       expect(screen.getByText(said).className).toContain("qe-chat-err");
       // The request never reached an agent, so there is nothing it did.
       expect(lines()).toEqual([]);
       expect(send()).toBeTruthy();
     });

  it("lets a question be typed while the agent works, and Enter does not send it", async () => {
    const server = fakeServer({ chats: [WORKING], working: [1] });
    await open();

    type("ikinci soru");
    await enter();

    expect(box().value).toBe("ikinci soru");
    expect(server.bodies).toEqual([]);
    expect(stop()).toBeTruthy();
  });
});

describe("AgentPanel — stopping", () => {
  it("stops the agent on ■: the finished step stays, the one going on goes, Durduruldu is added",
     async () => {
       const server = fakeServer({ chats: [WORKING], working: [1] });
       await open();

       // Pressable with an empty box: it has to stop the agent.
       expect(stop().disabled).toBe(false);
       fireEvent.click(stop());
       await settle();

       expect(server.calls).toContain(`POST ${chatsUrl("/1/stop")}`);
       expect(lines()).toEqual(["Projeye baktı"]);
       expect(screen.getByText("Durduruldu").className).toContain("qe-chat-stopped");
       expect(document.querySelector(".qe-chat-a")).toBeNull();
       expect(send()).toBeTruthy();
       expect(document.activeElement).toBe(box());
     });

  it("keeps what was typed while the agent worked, and the arrow can send it", async () => {
    fakeServer({ chats: [WORKING], working: [1] });
    await open();

    type("ikinci soru");
    fireEvent.click(stop());
    await settle();

    expect(box().value).toBe("ikinci soru");
    expect(send().disabled).toBe(false);
  });
});

describe("AgentPanel — coming back", () => {
  it("opens where the agent got to while the panel was closed, with the draft still in the box",
     async () => {
       const server = fakeServer({ chats: [WORKING], working: [1] });
       const first = await open();
       type("yarım kalan");

       first.unmount();
       const asked = server.calls.length;
       await settle(5 * POLL_MS);
       // A closed panel asks the server nothing.
       expect(server.calls).toHaveLength(asked);

       server.end(1, answered("Cevap burada."));
       await open();

       // The chat it had open, read again: not the list.
       expect(server.calls.slice(asked)).toEqual(
         [`GET ${chatsUrl("/working")}`, `GET ${chatsUrl("/1")}`]);
       expect(screen.getByText("Cevap burada.")).toBeTruthy();
       expect(box().value).toBe("yarım kalan");
     });

  it("opens another project on its own chats", async () => {
    const server = fakeServer({ chats: [FIRST, SECOND] });
    const first = await open("düğün");
    first.unmount();
    const asked = server.calls.length;

    await open("kına");

    expect(server.calls[asked]).toBe("GET /api/projects/kına/chats");
  });

  it("does not read the open chat again while it is idle and another chat works", async () => {
    const server = fakeServer({ chats: [WORKING], working: [1] });
    await open();
    fireEvent.click(newChat());
    await settle();
    const asked = server.calls.length;

    await settle(3 * POLL_MS);

    const later = server.calls.slice(asked);
    expect(later.length).toBeGreaterThan(0);
    expect(later.every((call) => call === `GET ${chatsUrl("/working")}`)).toBe(true);
  });

  it("says so when a look at the server does not reach it, and takes it back once it does",
     async () => {
       const server = fakeServer({ chats: [WORKING], working: [1] });
       await open();

       server.down = true;
       await settle(POLL_MS);
       expect(screen.getByText(UNREACHED).className).toContain("qe-chat-err");

       server.down = false;
       server.step(1, READING_2);
       await settle(POLL_MS);
       expect(screen.queryByText(UNREACHED)).toBeNull();
       expect(liveLines()).toEqual(["2 numaralı kareyi okuyor…"]);
     });
});

describe("AgentPanel — the list", () => {
  it("opens in the conversation's place: newest first, first question and last date, open marked",
     async () => {
       fakeServer({ chats: [FIRST, SECOND, { id: 3, questions: [] }] });
       await open();

       fireEvent.click(list());
       await settle();

       const rows = [...document.querySelectorAll(".qe-chat-row")];
       // The empty chat has no row.
       expect(rows.map((row) => row.querySelector(".qe-chat-row-q").textContent))
         .toEqual(["Kaç karede video var?", "Hangi kareler hata verdi?"]);
       expect(rows[0].querySelector(".qe-chat-row-date").textContent).toBe("5 Eki 2026 · 15:48");
       expect(rows[0].className).toContain("is-on");
       expect(rows[1].className).not.toContain("is-on");
       expect(list().getAttribute("aria-pressed")).toBe("true");
       expect(list().className).toContain("is-on");
       expect(screen.queryByLabelText("Soru")).toBeNull();
     });

  it("marks a chat whose agent works with a live dot, which leaves when the agent is done",
     async () => {
       const server = fakeServer({ chats: [WORKING], working: [1] });
       await open();
       fireEvent.click(list());
       await settle();

       expect(screen.getByRole("img", { name: "Agent çalışıyor" })).toBeTruthy();

       server.end(1, answered("Bitti."));
       await settle(POLL_MS);
       expect(screen.queryByRole("img", { name: "Agent çalışıyor" })).toBeNull();
     });

  it("says Henüz sohbet yok. when no chat has a question", async () => {
    fakeServer();
    await open();

    fireEvent.click(list());
    await settle();

    expect(screen.getByText("Henüz sohbet yok.")).toBeTruthy();
  });

  it("opens a row's chat where it left off, and the list closes", async () => {
    fakeServer({ chats: [FIRST, SECOND] });
    await open();
    fireEvent.click(list());
    await settle();

    fireEvent.click(screen.getByText("Hangi kareler hata verdi?"));
    await settle();

    expect(screen.getByText("Hangi kareler hata verdi?").className).toContain("qe-chat-q");
    expect(screen.getByText("7 numaralı karenin fotoğrafı üretilemedi.")).toBeTruthy();
    expect(list().getAttribute("aria-pressed")).toBe("false");
  });

  it("brings the open chat back, read again, when Sohbetler is pressed again", async () => {
    const server = fakeServer({ chats: [WORKING], working: [1] });
    await open();
    fireEvent.click(list());
    await settle();

    // The answer lands while the list is open.
    server.end(1, answered("Liste açıkken geldi."));
    await settle(POLL_MS);
    fireEvent.click(list());
    await settle();

    expect(screen.getByText("Liste açıkken geldi.")).toBeTruthy();
    expect(send()).toBeTruthy();
  });

  it("opens on the list when the panel was closed with the list open", async () => {
    fakeServer({ chats: [FIRST, SECOND] });
    const first = await open();
    fireEvent.click(list());
    await settle();
    first.unmount();

    await open();

    expect(list().getAttribute("aria-pressed")).toBe("true");
    expect(document.querySelectorAll(".qe-chat-row")).toHaveLength(2);
  });

  it("opens the empty chat on Yeni sohbet with the cursor in the box, from the list too",
     async () => {
       const server = fakeServer({ chats: [FIRST, SECOND] });
       await open();
       fireEvent.click(list());
       await settle();

       fireEvent.click(newChat());
       await settle();

       expect(server.calls).toContain(`POST ${chatsUrl()}`);
       expect(screen.getByText("Projeyle ilgili bir şey sor.")).toBeTruthy();
       expect(list().getAttribute("aria-pressed")).toBe("false");
       expect(document.activeElement).toBe(box());
     });

  it("lets a new chat ask while the first one still works: two chats at once", async () => {
    const server = fakeServer({ chats: [WORKING], working: [1] });
    await open();
    fireEvent.click(newChat());
    await settle();

    type("İkinci sohbetin sorusu");
    await enter();

    expect(server.calls).toContain(`POST ${chatsUrl("/2/questions")}`);
    expect(stop()).toBeTruthy();
    fireEvent.click(list());
    await settle();
    expect(screen.getAllByRole("img", { name: "Agent çalışıyor" })).toHaveLength(2);
  });

  it("keeps each chat's draft with its chat", async () => {
    fakeServer({ chats: [FIRST, SECOND] });
    await open();
    type("ikinciye yarım");

    fireEvent.click(newChat());
    await settle();
    expect(box().value).toBe("");

    fireEvent.click(list());
    await settle();
    fireEvent.click(screen.getByText("Kaç karede video var?"));
    await settle();
    expect(box().value).toBe("ikinciye yarım");
  });
});

describe("AgentPanel — scrolling", () => {
  // jsdom lays nothing out: the conversation's sizes are given here, and scrollTop keeps whatever it
  // is set to.
  function sized(height, view = 300) {
    const log = document.querySelector(".qe-chat-log");
    const size = { height };
    Object.defineProperty(log, "scrollHeight", { configurable: true, get: () => size.height });
    Object.defineProperty(log, "clientHeight", { configurable: true, get: () => view });
    return { log, size };
  }

  it("does not pull a reader who scrolled up down to a new step", async () => {
    const server = fakeServer({ chats: [WORKING], working: [1] });
    await open();
    const { log, size } = sized(1000);
    log.scrollTop = 100;
    fireEvent.scroll(log);

    size.height = 1100;
    server.step(1, READING_2);
    await settle(POLL_MS);

    expect(log.scrollTop).toBe(100);
  });

  it("follows a new step when the conversation is at the bottom", async () => {
    const server = fakeServer({ chats: [WORKING], working: [1] });
    await open();
    const { log, size } = sized(1000);
    log.scrollTop = 700;
    fireEvent.scroll(log);

    size.height = 1100;
    server.step(1, READING_2);
    await settle(POLL_MS);

    expect(log.scrollTop).toBe(1100);
  });

  it("shows an answer taller than the conversation from the start of its steps", async () => {
    const server = fakeServer({ chats: [WORKING], working: [1] });
    await open();
    const { log } = sized(2000);
    vi.spyOn(HTMLElement.prototype, "offsetHeight", "get").mockImplementation(function height() {
      return this.classList.contains("qe-chat-a") ? 900 : 20;
    });
    vi.spyOn(HTMLElement.prototype, "offsetTop", "get").mockImplementation(function top() {
      return this.classList.contains("qe-chat-steps") ? 240 : 0;
    });

    server.end(1, answered("Uzun bir cevap."));
    await settle(POLL_MS);

    expect(log.scrollTop).toBe(240);
  });
});
