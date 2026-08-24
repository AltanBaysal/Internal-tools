import { describe, expect, it } from "vitest";

import { createQueue, imageQueue } from "./image_queue.js";

// Every test reads one list: who was granted, in the order it happened. A queue that hands slots
// out in the wrong order or loses one shows up as a different list, not as a different count.
describe("image queue", () => {
  it("grants the first askers up to the limit", () => {
    const queue = createQueue(2);
    const granted = [];

    queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));

    expect(granted).toEqual(["a", "b"]);
  });

  it("makes an asker past the limit wait", () => {
    const queue = createQueue(2);
    const granted = [];

    queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));
    queue.ask(() => granted.push("c"));

    expect(granted).toEqual(["a", "b"]);
  });

  it("hands a freed slot to the asker that has waited longest", () => {
    const queue = createQueue(2);
    const granted = [];
    const first = queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));
    queue.ask(() => granted.push("c"));
    queue.ask(() => granted.push("d"));

    first.done();

    // c asked before d, so the slot is c's. Without an order, a gallery that is scrolled through
    // leaves its oldest waiters at the back for as long as new ones keep arriving.
    expect(granted).toEqual(["a", "b", "c"]);
  });

  it("skips an asker that gave up and grants the one behind it", () => {
    const queue = createQueue(2);
    const granted = [];
    const first = queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));
    const leaving = queue.ask(() => granted.push("c"));
    queue.ask(() => granted.push("d"));

    leaving.done();
    first.done();

    // Two things at once: the one that left is never drawn, and its place does not swallow the
    // slot. Only the second half says the queue goes on -- one tile scrolled past must not stall
    // every tile behind it.
    expect(granted).toEqual(["a", "b", "d"]);
  });

  it("frees one slot however many times done is called", () => {
    const queue = createQueue(2);
    const granted = [];
    const first = queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));
    queue.ask(() => granted.push("c"));
    queue.ask(() => granted.push("d"));

    first.done();
    first.done();

    // A tile that loads and is then taken off the screen releases twice. The second release must
    // not hand out a slot the queue never got back.
    expect(granted).toEqual(["a", "b", "c"]);
  });

  it("keeps a freed slot for the next asker when no one is waiting", () => {
    const queue = createQueue(1);
    const granted = [];
    const first = queue.ask(() => granted.push("a"));

    first.done();
    queue.ask(() => granted.push("b"));

    expect(granted).toEqual(["a", "b"]);
  });

  it("shares one queue of a single slot for the gallery", () => {
    const granted = [];

    imageQueue.ask(() => granted.push("a"));
    imageQueue.ask(() => granted.push("b"));
    imageQueue.ask(() => granted.push("c"));

    // One at a time: the picture downloads, and only when it is in does the next request leave.
    // Tested on the shared instance because that is the one the gallery uses -- createQueue could
    // be right while the app shipped a different ceiling. Nothing is released here on purpose:
    // this test is last, and no other test reads this queue.
    expect(granted).toEqual(["a"]);
  });
});
