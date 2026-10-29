import { beforeEach, describe, expect, it, vi } from "vitest";

import { askPermission, notify } from "./notification.js";

// The browser's Notification, faked: what was shown, and whether permission was asked.
let shown;
class FakeNotification {
  static permission = "default";
  static requestPermission = vi.fn(() => Promise.resolve("granted"));
  constructor(title, options) {
    this.title = title;
    this.options = options;
    this.close = vi.fn();
    shown.push(this);
  }
}

beforeEach(() => {
  shown = [];
  FakeNotification.permission = "default";
  FakeNotification.requestPermission.mockClear();
  vi.stubGlobal("Notification", FakeNotification);
});

describe("askPermission — the first Kuyruğa ekle asks (madde 498, 509)", () => {
  it("asks while the browser has no answer yet", () => {
    askPermission();

    expect(FakeNotification.requestPermission).toHaveBeenCalledTimes(1);
  });

  it.each(["granted", "denied"])("does not ask again once the answer is %s", (answer) => {
    FakeNotification.permission = answer;

    askPermission();

    expect(FakeNotification.requestPermission).not.toHaveBeenCalled();
  });

  it("does nothing where the browser has no notifications", () => {
    vi.stubGlobal("Notification", undefined);

    expect(() => askPermission()).not.toThrow();
  });

  it("lets a refused request go without a word", async () => {
    FakeNotification.requestPermission.mockReturnValueOnce(Promise.reject(new Error("kapalı")));

    askPermission();
    // An unhandled rejection would fail the run here.
    await Promise.resolve();
  });
});

describe("notify", () => {
  it("shows the news under the app's name, one tag replacing the last and still ringing", () => {
    FakeNotification.permission = "granted";

    notify("Sıra boş.");

    expect(shown).toHaveLength(1);
    expect(shown[0].title).toBe("Queen Editor");
    expect(shown[0].options).toEqual({ body: "Sıra boş.", tag: "queen-editor-queue",
                                       renotify: true });
  });

  it("brings the tab forward and closes itself when clicked", () => {
    FakeNotification.permission = "granted";
    const focus = vi.spyOn(window, "focus").mockImplementation(() => {});

    notify("Sıra boş.");
    shown[0].onclick();

    expect(focus).toHaveBeenCalled();
    expect(shown[0].close).toHaveBeenCalled();
  });

  it.each(["default", "denied"])("shows nothing while permission is %s", (answer) => {
    FakeNotification.permission = answer;

    notify("Sıra boş.");

    expect(shown).toEqual([]);
  });

  it("does nothing where the browser has no notifications", () => {
    vi.stubGlobal("Notification", undefined);

    expect(() => notify("Sıra boş.")).not.toThrow();
  });

  it("keeps a constructor that throws to itself", () => {
    // Chrome on Android allows a notification only through a service worker.
    class Refusing {
      static permission = "granted";
      constructor() { throw new TypeError("Illegal constructor"); }
    }
    vi.stubGlobal("Notification", Refusing);

    expect(() => notify("Sıra boş.")).not.toThrow();
  });
});
