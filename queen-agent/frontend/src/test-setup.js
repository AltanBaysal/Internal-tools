import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

// Testing Library only auto-cleans when vitest runs with globals; we keep globals off, so unmount
// between tests by hand -- otherwise every render stacks up in the same jsdom document.
afterEach(cleanup);

// And the browser's own memory, since Madde 100. One jsdom serves a whole file, so a test that
// picks a skill would otherwise hand it to every test after it -- and those tests were written in
// a world where nothing was remembered.
afterEach(() => {
  try {
    window.localStorage.clear();
  } catch {
    // A jsdom without storage is a browser without storage: nothing to clear, nothing to say.
  }
});

// And the spies, for the reason the two above exist: one jsdom and one window serve a whole file.
// A spy was always meant to belong to the test that made it, and nothing here was taking it down --
// vitest 3 hid that, because spying an already-spied method handed back a fresh wrapper. Vitest 4
// hands back the *same* mock, so the second test to spy on window.history.pushState inherited every
// call made since the first one did, its own setup lines included. Restoring puts the real method
// back, and that is what makes the next spyOn a new spy rather than an old one.
afterEach(() => {
  vi.restoreAllMocks();
});
