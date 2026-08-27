import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

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
