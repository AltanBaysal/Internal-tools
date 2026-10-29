import { act, renderHook } from "@testing-library/react";
import { StrictMode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { waitForEnded } from "../../shared/api.js";
import { useEndedNotification } from "./useEndedNotification.js";

vi.mock("../../shared/api.js", () => ({ waitForEnded: vi.fn() }));

// How the queue last ended, as the server keeps it: the worker's published state.
const DONE = { status: "done", project: "düğün", done: 2, failed: 0, total: 2 };
const ERROR = { status: "error", project: "düğün",
                error: "ComfyUI 3 denemede cevap vermedi.\nConnectionError: refused" };
const WAITING = { status: "waiting", project: "düğün" };

// The server's answer: how many times the queue ended, and how it last did.
const said = (ended, last = DONE) => ({ ended, last: ended ? last : null });

// The browser's Notification, faked: every one shown is kept.
let shown;
class FakeNotification {
  static permission = "granted";
  constructor(title, options) {
    shown.push({ title, ...options });
  }
  close() {}
}

// The held asks, as the server holds them: each waits until the test answers it.
let asks;

const settle = () => act(async () => {});

// The ask held now is answered with `answer`, and its answer is taken.
async function answer(answered) {
  asks.at(-1).resolve(answered);
  await settle();
}

beforeEach(() => {
  vi.useFakeTimers();
  shown = [];
  asks = [];
  FakeNotification.permission = "granted";
  vi.stubGlobal("Notification", FakeNotification);
  waitForEnded.mockReset();
  waitForEnded.mockImplementation((after) => new Promise((resolve, reject) => {
    asks.push({ after, resolve, reject });
  }));
});

// Opened, and the first ask -- with no count, answered at once -- has said where the count stands.
async function open(count = 4) {
  const view = renderHook(() => useEndedNotification());
  await settle();
  await answer(said(count));
  return view;
}

const bodies = () => shown.map((one) => one.body);

describe("useEndedNotification — listening (madde 509)", () => {
  it("asks with no count on opening, then holds one ask from the count that brought", async () => {
    await open();

    expect(asks.map((one) => one.after)).toEqual([null, 4]);
    expect(shown).toEqual([]);
  });

  it("asks again from each answer's count, one ask at a time", async () => {
    await open();

    await answer(said(4));
    await answer(said(5));

    expect(asks.map((one) => one.after)).toEqual([null, 4, 4, 5]);
  });

  it("asks again ten seconds after an ask that did not arrive, from the same count", async () => {
    await open();

    asks.at(-1).reject(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    await settle();
    expect(asks).toHaveLength(2);

    await act(() => vi.advanceTimersByTimeAsync(9_999));
    expect(asks).toHaveLength(2);
    await act(() => vi.advanceTimersByTimeAsync(1));
    expect(asks.map((one) => one.after)).toEqual([null, 4, 4]);
  });

  it("holds one ask after being taken down and put up again at once", async () => {
    // StrictMode does this to every effect: the first run's ask, with no count, is answered at
    // once and must not open a second held ask when it lands.
    renderHook(() => useEndedNotification(), { wrapper: StrictMode });
    await settle();
    asks.forEach((one) => one.resolve(said(4)));
    await settle();

    expect(asks.filter((one) => one.after !== null)).toHaveLength(1);
  });

  it("stops listening once it is gone", async () => {
    const { unmount } = await open();

    unmount();
    await answer(said(5));

    expect(asks).toHaveLength(2);
    expect(shown).toEqual([]);
  });
});

describe("useEndedNotification — the notification", () => {
  it("rings once when the queue empties", async () => {
    await open();

    await answer(said(5, DONE));

    expect(shown).toEqual([{ title: "Queen Editor",
                             body: "Sıradaki bütün fotoğraf ve videolar bitti.",
                             tag: "queen-editor-queue", renotify: true }]);
  });

  it("rings with the server's own words when the queue stopped on an error", async () => {
    await open();

    await answer(said(5, ERROR));

    expect(bodies()).toEqual(
      ["Sıra durdu.\nComfyUI 3 denemede cevap vermedi.\nConnectionError: refused"]);
  });

  it.each([["photo", "fotoğraf"], ["video", "video"], ["audio", "ses"]])(
    "names the producer a queue stopped for: %s as %s",
    async (kind, word) => {
      await open();

      await answer(said(5, { ...WAITING, waitingFor: kind }));

      expect(bodies()).toEqual([`Sıra durdu: ${word} üreticisi kurulu değil.`]);
    },
  );

  it("does not ring for an ask that ran out with nothing new", async () => {
    await open();

    await answer(said(4));

    expect(shown).toEqual([]);
  });

  it("rings again for the next ending", async () => {
    await open();
    await answer(said(5));

    await answer(said(6));

    expect(shown).toHaveLength(2);
  });

  it("does not ring for a server that came up again and counts from nought", async () => {
    await open();

    await answer(said(0));
    expect(shown).toEqual([]);
    expect(asks.at(-1).after).toBe(0);

    await answer(said(1));
    expect(shown).toHaveLength(1);
  });

  it("does not ring for the count it opens on", async () => {
    await open(7);

    expect(shown).toEqual([]);
  });

  it("stays silent without permission for notifications", async () => {
    FakeNotification.permission = "denied";
    await open();

    await answer(said(5));

    expect(shown).toEqual([]);
  });
});
