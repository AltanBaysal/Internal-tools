import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { waitForQueue } from "../../shared/api.js";
import { useQueueWatch } from "../../shared/queue_watch.js";
import { useEndedNotification } from "./useEndedNotification.js";

vi.mock("../../shared/api.js", () => ({ waitForQueue: vi.fn() }));

// How the queue last ended, as the server keeps it: the worker's published state.
const DONE = { status: "done", project: "düğün", done: 2, failed: 0, total: 2 };
const ERROR = { status: "error", project: "düğün",
                error: "ComfyUI 3 denemede cevap vermedi.\nConnectionError: refused" };
const WAITING = { status: "waiting", project: "düğün" };

// The server's answer: how many times the queue ended, and how it last did. The start count stays
// where it is unless a test moves it: the notification is about endings.
const said = (ended, last = DONE, started = 9) => ({ started, ended, last: ended ? last : null });

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
  waitForQueue.mockReset();
  waitForQueue.mockImplementation((seen) => new Promise((resolve, reject) => {
    asks.push({ seen, resolve, reject });
  }));
});

// Opened as App opens it -- the watch and its listener -- and the first ask, answered at once, has
// said where the counts stand.
async function open(count = 4) {
  const view = renderHook(() => {
    useQueueWatch();
    useEndedNotification();
  });
  await settle();
  await answer(said(count));
  return view;
}

const bodies = () => shown.map((one) => one.body);

describe("useEndedNotification — the notification (madde 509)", () => {
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

  it("does not ring when the queue starts (madde 518)", async () => {
    await open();

    await answer(said(4, DONE, 10));

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

    await answer(said(0, DONE, 0));
    expect(shown).toEqual([]);

    await answer(said(1, DONE, 0));
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

  it("stops ringing once it is gone", async () => {
    const { unmount } = await open();

    unmount();
    await answer(said(5));

    expect(shown).toEqual([]);
  });
});
