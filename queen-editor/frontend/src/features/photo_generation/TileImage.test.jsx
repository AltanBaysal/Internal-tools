import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { fileUrl } from "../../shared/api.js";
import { shownPictures } from "../../shared/shown_pictures.js";
import { TileImage } from "./TileImage.jsx";

// The queue's own rules are tested next door. What is tested here is the protocol -- ask, draw
// when granted, release when finished -- so the queue is a fake the test holds the grant of.
// vi.hoisted because vi.mock is lifted above the imports and cannot see an ordinary const.
const queue = vi.hoisted(() => {
  const waiting = [];
  return {
    waiting,
    ask(grant) {
      const ticket = { grant, released: 0, done: () => { ticket.released += 1; } };
      waiting.push(ticket);
      return ticket;
    },
    forget: () => { waiting.length = 0; },
  };
});

vi.mock("../../shared/image_queue.js", () => ({ imageQueue: queue }));

// How long the tile waits before it lets the queue move on. Written out rather than imported: a
// test that reads the number from the code cannot say the number is wrong.
const PATIENCE = 30000;

// Found by its alt rather than its role: a picture that has not arrived is hidden, and testing
// library leaves a hidden element out of the accessibility tree altogether.
const picture = () => screen.getByAltText("1_a.png");
const sourceOf = () => picture().getAttribute("src");
const seen = () => picture().style.display !== "none";
const holder = () => document.querySelector(".wf-img");
const turning = () => document.querySelector(".wf-spinner");
// Optional call on purpose: a tile that never asks must leave the assertion to do the failing
// rather than throw on an empty queue.
const grant = () => act(() => queue.waiting[0]?.grant());
const releases = () => queue.waiting.map((ticket) => ticket.released);

beforeEach(() => {
  queue.forget();
  // A picture that has been on screen once is remembered for the session, so a suite whose tests
  // all name the same file has to start each of them from nothing.
  shownPictures.clear();
});
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("TileImage — asking", () => {
  it("asks for the picture as soon as the tile is built", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    // Nothing was scrolled and nothing came into view: the tile asks because it exists. That is
    // what makes the gallery fill in frame order instead of in the order the page was scrolled.
    expect(queue.waiting).toHaveLength(1);
  });

  it("asks even where the browser could tell it is out of sight", () => {
    // The gate this task removes only exists where there is an observer to run it, and jsdom has
    // none -- so an observer is put here for the tile to ignore. Without this test the removal
    // could not be seen from a test at all.
    vi.stubGlobal("IntersectionObserver", class {
      observe() {}
      disconnect() {}
    });

    render(<TileImage project="düğün" file="1_a.png" />);

    expect(queue.waiting).toHaveLength(1);
  });

  it("draws no picture until the queue grants a slot", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    // The ceiling is only a ceiling if being in the queue is not enough to be drawn.
    expect(sourceOf()).toBeNull();
  });

  it("draws the picture once the queue grants a slot", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    grant();

    expect(sourceOf()).toBe(fileUrl("düğün", "1_a.png"));
  });

  it("skips the queue for a picture it has already shown", () => {
    const first = render(<TileImage project="düğün" file="1_a.png" />);
    grant();
    fireEvent.load(picture());
    first.unmount();

    render(<TileImage project="düğün" file="1_a.png" />);

    // No second wait, and no second ticket: the bytes are in the browser's cache, so what waiting
    // again would cost is the picture blinking off the screen (İstek 1.2). Not even a holder for
    // an instant -- a holder is what the blink looks like.
    expect(queue.waiting).toHaveLength(1);
    expect(sourceOf()).toBe(fileUrl("düğün", "1_a.png"));
    expect(seen()).toBe(true);
    expect(holder()).toBeNull();
  });

  it("does not remember a picture that never arrived", () => {
    const first = render(<TileImage project="düğün" file="1_a.png" />);
    grant();
    fireEvent.error(picture());
    first.unmount();

    render(<TileImage project="düğün" file="1_a.png" />);

    expect(sourceOf()).toBeNull();
  });
});

describe("TileImage — what the tile shows", () => {
  it("shows a plain holder while it waits its turn", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    // Every tile is in the queue from the moment it is built, so a ring on each of them would be
    // ninety rings turning at once. That is not information.
    expect(holder()).toBeTruthy();
    expect(turning()).toBeNull();
  });

  it("shows a turning holder while the picture is coming", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    grant();

    // With a ceiling of one there is exactly one of these on the screen: the gallery's answer to
    // what is downloading right now.
    expect(turning()).toBeTruthy();
  });

  it("keeps the picture out of sight until it arrives", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    grant();

    // The complaint this started from: an img with nothing to draw writes its alt text on the
    // screen, and the alt text is the file name.
    expect(seen()).toBe(false);
  });

  it("shows the picture and drops the holder once it arrives", () => {
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    fireEvent.load(picture());

    expect(seen()).toBe(true);
    expect(holder()).toBeNull();
  });

  it("leaves a quiet holder where a picture never arrived", () => {
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    fireEvent.error(picture());

    // A broken image icon and a file name is what this replaces. The ring goes with it: nothing
    // is coming any more, and a ring that turns forever says the opposite.
    expect(holder()).toBeTruthy();
    expect(turning()).toBeNull();
    expect(seen()).toBe(false);
  });
});

describe("TileImage — giving the slot back", () => {
  it("frees its slot once the picture has loaded", () => {
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    fireEvent.load(picture());

    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the picture fails", () => {
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    fireEvent.error(picture());

    // Loaded and failed are the same answer: the slot is what is being returned, not a verdict on
    // the file. One broken photo must not take a permanent bite out of the ceiling.
    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the tile is taken off the screen", () => {
    const { unmount } = render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    unmount();

    // Opening a frame's page, deleting it, dragging it elsewhere: the tile stops being, and the
    // queue must not go on holding a slot for it.
    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the picture takes too long", () => {
    vi.useFakeTimers();
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    act(() => vi.advanceTimersByTime(PATIENCE));

    // An img download has no timeout of its own -- the ten second abort in api.js belongs to
    // fetch. A request that hangs answers neither load nor error, and with a ceiling of one a
    // ticket held forever is the whole gallery stopped behind it.
    expect(releases()).toEqual([1]);
  });

  it("draws a picture that arrives after its slot was given up", () => {
    vi.useFakeTimers();
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();
    act(() => vi.advanceTimersByTime(PATIENCE));

    fireEvent.load(picture());

    // Letting the queue move on is not cancelling the download. The bytes were already on their
    // way, and a picture is what the tile is for.
    expect(seen()).toBe(true);
    expect(shownPictures.has(fileUrl("düğün", "1_a.png"))).toBe(true);
  });
});
