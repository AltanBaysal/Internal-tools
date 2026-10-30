import { act, renderHook } from "@testing-library/react";
import { StrictMode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { waitForQueue } from "./api.js";
import { onQueueMoved, useQueueWatch } from "./queue_watch.js";

vi.mock("./api.js", () => ({ waitForQueue: vi.fn() }));

const DONE = { status: "done", project: "düğün" };

// The server's answer: how many times the queue started and ended, and how it last ended.
const said = (started, ended) => ({ started, ended, last: ended ? DONE : null });

// The held asks, as the server holds them: each waits until the test answers it.
let asks;
// What the listener was told, as [said, before] pairs.
let told;
let stopListening;

const settle = () => act(async () => {});

async function answer(answered) {
  asks.at(-1).resolve(answered);
  await settle();
}

beforeEach(() => {
  vi.useFakeTimers();
  asks = [];
  told = [];
  waitForQueue.mockReset();
  waitForQueue.mockImplementation((seen) => new Promise((resolve, reject) => {
    asks.push({ seen, resolve, reject });
  }));
  stopListening?.();
  stopListening = onQueueMoved((now, before) => told.push([now, before]));
});

// Opened, and the first ask -- with no counts, answered at once -- has said where they stand.
async function open(started = 3, ended = 3) {
  const view = renderHook(() => useQueueWatch());
  await settle();
  await answer(said(started, ended));
  return view;
}

const seenOf = (ask) => (ask.seen ? [ask.seen.started, ask.seen.ended] : null);

describe("useQueueWatch — listening (madde 509, 518)", () => {
  it("asks with no counts on opening, then holds one ask from the counts that brought", async () => {
    await open();

    expect(asks.map(seenOf)).toEqual([null, [3, 3]]);
  });

  it("asks again from each answer's counts, one ask at a time", async () => {
    await open();

    await answer(said(3, 3));
    await answer(said(4, 3));

    expect(asks.map(seenOf)).toEqual([null, [3, 3], [3, 3], [4, 3]]);
  });

  it("asks again ten seconds after an ask that did not arrive, from the same counts", async () => {
    await open();

    asks.at(-1).reject(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    await settle();
    expect(asks).toHaveLength(2);

    await act(() => vi.advanceTimersByTimeAsync(9_999));
    expect(asks).toHaveLength(2);
    await act(() => vi.advanceTimersByTimeAsync(1));
    expect(asks.map(seenOf)).toEqual([null, [3, 3], [3, 3]]);
  });

  it("holds one ask after being taken down and put up again at once", async () => {
    // StrictMode does this to every effect: the first run's ask, with no counts, is answered at
    // once and must not open a second held ask when it lands.
    renderHook(() => useQueueWatch(), { wrapper: StrictMode });
    await settle();
    asks.forEach((one) => one.resolve(said(3, 3)));
    await settle();

    expect(asks.filter((one) => one.seen !== null)).toHaveLength(1);
  });

  it("stops listening once it is gone", async () => {
    const { unmount } = await open();

    unmount();
    await answer(said(4, 3));

    expect(asks).toHaveLength(2);
    expect(told).toEqual([]);
  });
});

describe("useQueueWatch — what the listeners are told", () => {
  it("tells nobody where the counts stand when it opens", async () => {
    await open();

    expect(told).toEqual([]);
  });

  it("tells nobody of an ask that ran out with the same counts", async () => {
    await open();

    await answer(said(3, 3));

    expect(told).toEqual([]);
  });

  it("tells a start, with the counts heard before it", async () => {
    await open();

    await answer(said(4, 3));

    expect(told).toEqual([[said(4, 3), said(3, 3)]]);
  });

  it("tells an ending", async () => {
    await open();

    await answer(said(3, 4));

    expect(told).toEqual([[said(3, 4), said(3, 3)]]);
  });

  it("does not miss a start after a server that came up again with the same start count", async () => {
    // The tab heard one start and one ending; the server restarts and counts from nought, and the
    // queue starts once: started is 1 again, and only the ending count says anything moved.
    await open(1, 1);

    await answer(said(1, 0));

    expect(told).toEqual([[said(1, 0), said(1, 1)]]);
  });

  it("tells a listener nothing once it has stopped listening", async () => {
    await open();

    stopListening();
    await answer(said(4, 3));

    expect(told).toEqual([]);
  });
});
