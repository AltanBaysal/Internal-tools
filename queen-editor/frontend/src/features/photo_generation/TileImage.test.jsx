import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { fileUrl } from "../../shared/api.js";
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

// jsdom has no layout and therefore no IntersectionObserver; the test supplies one and drives it
// by hand, the same way this suite supplies a clipboard and a video duration.
function stubObserver() {
  const made = [];
  vi.stubGlobal("IntersectionObserver", class {
    constructor(callback) { this.callback = callback; made.push(this); }
    observe() {}
    disconnect() {}
  });
  // Optional call for the same reason as grant below: a component that never observes leaves this
  // empty, and a helper that throws would hide the assertion the test is actually about.
  const fire = (isIntersecting) =>
    act(() => made[made.length - 1]?.callback([{ isIntersecting }]));
  return { near: () => fire(true), away: () => fire(false) };
}

const picture = () => screen.getByRole("img");
const sourceOf = () => picture().getAttribute("src");
// Optional call on purpose: while the skeleton never asks, this helper must leave the assertion to
// do the failing rather than throw on an empty queue.
const grant = () => act(() => queue.waiting[0]?.grant());
const releases = () => queue.waiting.map((ticket) => ticket.released);

beforeEach(() => queue.forget());
afterEach(() => vi.unstubAllGlobals());

describe("TileImage", () => {
  it("draws no picture before the tile comes near", () => {
    stubObserver();

    render(<TileImage project="düğün" file="1_a.png" />);

    expect(sourceOf()).toBeNull();
  });

  it("asks for the picture once the tile comes near", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);

    view.near();

    expect(queue.waiting).toHaveLength(1);
  });

  it("draws no picture until the queue grants a slot", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);

    view.near();

    // The ceiling is only a ceiling if being in the queue is not enough to be drawn.
    expect(sourceOf()).toBeNull();
  });

  it("draws the picture once the queue grants a slot", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);
    view.near();

    grant();

    expect(sourceOf()).toBe(fileUrl("düğün", "1_a.png"));
  });

  it("frees its slot once the picture has loaded", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);
    view.near();
    grant();

    fireEvent.load(picture());

    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the picture fails", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);
    view.near();
    grant();

    fireEvent.error(picture());

    // A file that cannot be drawn must not hold a slot: one broken photo would otherwise take a
    // permanent bite out of a ceiling of two.
    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the tile leaves before its turn", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);
    view.near();

    view.away();

    // Scrolled past while still waiting: it drops out of the queue, so what is on screen is not
    // stuck behind what no longer is.
    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the tile is taken off the screen", () => {
    const view = stubObserver();
    const { unmount } = render(<TileImage project="düğün" file="1_a.png" />);
    view.near();
    grant();

    unmount();

    expect(releases()).toEqual([1]);
  });

  it("draws the picture at once when the browser has no observer", () => {
    // Without this the gallery does not degrade, it dies: calling new on an absent constructor
    // throws where it stands. jsdom is one such browser, which is what keeps Gallery.test.jsx up.
    vi.stubGlobal("IntersectionObserver", undefined);

    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    expect(sourceOf()).toBe(fileUrl("düğün", "1_a.png"));
  });
});
