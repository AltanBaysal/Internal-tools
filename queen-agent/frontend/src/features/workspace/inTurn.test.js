import { expect, test } from "vitest";

import { inTurn } from "./inTurn.js";

// Madde 450: the project list's reads and writes reach the server one at a time, in the order asked.

const held = () => {
  let release;
  const promise = new Promise((resolve) => {
    release = resolve;
  });
  return { promise, release };
};

test("a task starts only once the one before it has settled, and each caller gets its own result", async () => {
  const queued = inTurn();
  const first = held();
  const started = [];
  const one = queued(() => {
    started.push("one");
    return first.promise;
  });
  const two = queued(() => {
    started.push("two");
    return "second";
  });
  await Promise.resolve();
  expect(started).toEqual(["one"]);
  first.release("first");
  expect(await one).toBe("first");
  expect(await two).toBe("second");
  expect(started).toEqual(["one", "two"]);
});

test("a task that rejects hands its caller the rejection, and the next one still runs", async () => {
  const queued = inTurn();
  const failing = queued(() => Promise.reject(new Error("refused")));
  const next = queued(() => "ran");
  await expect(failing).rejects.toThrow("refused");
  expect(await next).toBe("ran");
});

test("a task that throws does not stop the next one either", async () => {
  const queued = inTurn();
  const failing = queued(() => {
    throw new Error("broke");
  });
  const next = queued(() => "ran");
  await expect(failing).rejects.toThrow("broke");
  expect(await next).toBe("ran");
});
