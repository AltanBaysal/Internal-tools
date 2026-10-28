import { act, fireEvent, render, screen } from "@testing-library/react";
import { StrictMode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { sayHere, waitForIdle } from "../../shared/api.js";
import IdleWatch from "./IdleWatch.jsx";

vi.mock("../../shared/api.js", () => ({ sayHere: vi.fn(), waitForIdle: vi.fn() }));

const SENTENCE = "Sıra 10 dakikadır boş. Colab açık kaldıkça A100 boşa para yiyor.";

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

const box = () => screen.queryByText("Orada mısın?");
const here = () => fireEvent.click(screen.getByRole("button", { name: "Buradayım" }));
const settle = () => act(async () => {});

// The ask held now is answered with `said`, and its answer is taken.
async function answer(said) {
  asks.at(-1).resolve(said);
  await settle();
}

beforeEach(() => {
  vi.useFakeTimers();
  shown = [];
  asks = [];
  FakeNotification.permission = "granted";
  vi.stubGlobal("Notification", FakeNotification);
  sayHere.mockReset();
  sayHere.mockResolvedValue({ version: 4, asking: false });
  waitForIdle.mockReset();
  waitForIdle.mockImplementation((after) => new Promise((resolve, reject) => {
    asks.push({ after, resolve, reject });
  }));
});

async function open() {
  const view = render(<IdleWatch />);
  await settle();
  return view;
}

describe("IdleWatch — listening (madde 498)", () => {
  it("says it is here on opening, then holds one ask from the version that brought", async () => {
    await open();

    expect(sayHere).toHaveBeenCalledTimes(1);
    expect(asks.map((one) => one.after)).toEqual([4]);
    expect(box()).toBeNull();
  });

  it("asks at once when Buradayım did not arrive", async () => {
    sayHere.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));

    await open();

    expect(asks.map((one) => one.after)).toEqual([null]);
  });

  it("asks again from each answer's version, one ask at a time", async () => {
    await open();

    await answer({ version: 4, asking: false });
    await answer({ version: 5, asking: true });

    expect(asks.map((one) => one.after)).toEqual([4, 4, 5]);
  });

  it("asks again ten seconds after an ask that did not arrive, from the same version", async () => {
    await open();

    asks.at(-1).reject(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    await settle();
    expect(asks).toHaveLength(1);

    await act(() => vi.advanceTimersByTimeAsync(9_999));
    expect(asks).toHaveLength(1);
    await act(() => vi.advanceTimersByTimeAsync(1));
    expect(asks.map((one) => one.after)).toEqual([4, 4]);
  });

  it("holds one ask after being taken down and put up again at once", async () => {
    // StrictMode does this to every effect: the first run's Buradayım is still on its way when the
    // second run starts, and must not open a second ask when it lands.
    render(<StrictMode><IdleWatch /></StrictMode>);
    await settle();

    expect(sayHere).toHaveBeenCalledTimes(2);
    expect(asks).toHaveLength(1);
  });

  it("stops listening once it is gone", async () => {
    const { unmount } = await open();

    unmount();
    await answer({ version: 5, asking: true });

    expect(asks).toHaveLength(1);
    expect(shown).toEqual([]);
  });
});

describe("IdleWatch — the question", () => {
  it("shows the box and rings when the server asks", async () => {
    await open();

    await answer({ version: 5, asking: true });

    expect(box()).toBeTruthy();
    expect(screen.getByText(SENTENCE)).toBeTruthy();
    expect(shown).toEqual([{ title: "Queen Editor — orada mısın?", body: SENTENCE,
                             tag: "queen-editor-idle", renotify: true }]);
  });

  it("rings again for the question asked ten minutes later, the box staying up", async () => {
    await open();
    await answer({ version: 5, asking: true });

    await answer({ version: 6, asking: true });

    expect(shown).toHaveLength(2);
    expect(box()).toBeTruthy();
  });

  it("does not ring twice for one question", async () => {
    await open();
    await answer({ version: 5, asking: true });

    await answer({ version: 5, asking: true });

    expect(shown).toHaveLength(1);
  });

  it("takes the box down without a sound when work starts", async () => {
    await open();
    await answer({ version: 5, asking: true });

    await answer({ version: 6, asking: false });

    expect(box()).toBeNull();
    expect(shown).toHaveLength(1);
  });

  it("closes on Buradayım at once and tells the server", async () => {
    await open();
    await answer({ version: 5, asking: true });
    sayHere.mockResolvedValue({ version: 6, asking: false });

    here();
    expect(box()).toBeNull();
    await settle();

    expect(sayHere).toHaveBeenCalledTimes(2);
  });

  it("asks on screen alone without permission for notifications", async () => {
    FakeNotification.permission = "denied";
    await open();

    await answer({ version: 5, asking: true });

    expect(box()).toBeTruthy();
    expect(shown).toEqual([]);
  });

  it("asks on screen alone where the browser has no notifications", async () => {
    vi.stubGlobal("Notification", undefined);
    await open();

    await answer({ version: 5, asking: true });

    expect(box()).toBeTruthy();
  });
});
