# Madde 100 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m100-hatirlama-testler-design.md](../specs/2026-08-28-queenagent-m100-hatirlama-testler-design.md)
**Tur:** ikiden birincisi — **yalnız testler**. Kod yazılmıyor, kırmızı commit'leniyor.
**Komut:** `npm test --prefix queen-agent/frontend`

---

## 1 · `src/test-setup.js` — depolama da temizleniyor

```js
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
```

## 2 · `src/shared/useRemembered.test.jsx` — yeni dosya

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { useRemembered } from "./remembered.js";

// What the browser keeps for itself. Not the server: since Madde 86 nothing there reads a
// selection back, and what is kept here is this browser's preference rather than the chat's record.

afterEach(() => {
  vi.unstubAllGlobals();
});

function Host({ fallback = "none" }) {
  const [value, setValue] = useRemembered("skill", fallback);
  return (
    <div>
      <span data-testid="value">{value}</span>
      <button type="button" onClick={() => setValue("picked")}>
        pick
      </button>
      <button type="button" onClick={() => setValue("")}>
        let go
      </button>
    </div>
  );
}

test("with nothing kept the answer is the fallback", () => {
  render(<Host />);
  expect(screen.getByTestId("value").textContent).toBe("none");
});

test("what was kept comes back on the next mount", () => {
  const first = render(<Host />);
  fireEvent.click(screen.getByText("pick"));
  first.unmount();

  render(<Host />);
  expect(screen.getByTestId("value").textContent).toBe("picked");
});

test("letting a value go is kept as itself, not as nothing", () => {
  // The trap this exists for: an empty selection and no selection are different things, and a read
  // that folds them together undoes the user's "drop this" on every reload.
  const first = render(<Host />);
  fireEvent.click(screen.getByText("pick"));
  fireEvent.click(screen.getByText("let go"));
  first.unmount();

  render(<Host />);
  expect(screen.getByTestId("value").textContent).toBe("");
});

test("a browser that refuses to be read hands back the fallback", () => {
  // A private window, or storage switched off. Both throw on the read rather than answering null.
  vi.stubGlobal("localStorage", {
    getItem: () => {
      throw new Error("denied");
    },
    setItem: () => {},
  });
  render(<Host />);
  expect(screen.getByTestId("value").textContent).toBe("none");
});

test("a browser that refuses to be written to still works", () => {
  // The memory is lost and nothing else is: the selection still holds for this session.
  vi.stubGlobal("localStorage", {
    getItem: () => null,
    setItem: () => {
      throw new Error("full");
    },
  });
  render(<Host />);
  fireEvent.click(screen.getByText("pick"));
  expect(screen.getByTestId("value").textContent).toBe("picked");
});
```

## 3 · `src/App.test.jsx` — seçim

Dosyanın sonuna:

```jsx
// --- the selection the browser keeps (Madde 100) -------------------------------------------------

async function reborn() {
  /* The app mounted a second time over the same browser. A reload is what this stands for -- React
     state is gone and only what was written down survives. */
  cleanup();
  render(<App />);
  return waitFor(() => expect(screen.getByRole("button", { name: /Skills|Generate/ })).toBeTruthy());
}

test("a skill picked survives the app being mounted again", async () => {
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Generate prompts+", { selector: ".menu__item-name" }));
  await waitFor(() => expect(screen.getByRole("button", { name: /Generate prompts/ })).toBeTruthy());

  await reborn();
  expect(screen.getByRole("button", { name: /Generate prompts/ })).toBeTruthy();
});

test("the message sent after a reload carries the remembered skill", async () => {
  // The point of the item: mid-flow, a turn that goes without its instruction is a turn nobody
  // asked for, and nothing on screen would have said so.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Generate prompts+", { selector: ".menu__item-name" }));
  await waitFor(() => expect(screen.getByRole("button", { name: /Generate prompts/ })).toBeTruthy());

  const fetch = withChat();
  await reborn();
  const box = screen.getByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "carry on" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(JSON.parse(sent[1].body).skill).toBe("generate-prompts-plus");
  });
});

// Letting the skill go is not asked about here. On this screen an empty selection and no selection
// draw the same button, so the claim cannot fail whatever the code does -- and a test that cannot
// fail is noise. It is asked where the two are told apart: the hook's own test, with a fallback
// that is not the empty string.
```

`cleanup` `@testing-library/react`'ten import ediliyor — dosyanın import satırına ekleniyor.

## 4 · Koş

```
npm test --prefix queen-agent/frontend
python -m pytest queen-agent -q
```

Beklenen: ön yüzde **yedi kırmızı** — `useRemembered.test.jsx`'ten 5 *(olmayan bir modülü import
ediyor, yani toplanamıyor)*, `App.test.jsx`'ten 2. Arka yüzde değişen yok.

## 5 · Commit

```
test(queen-agent): red for a selection the browser keeps
```
