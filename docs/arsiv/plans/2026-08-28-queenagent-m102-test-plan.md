# Madde 102 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m102-ekran-testler-design.md](../specs/2026-08-28-queenagent-m102-ekran-testler-design.md)
**Tur:** ikiden birincisi — **yalnız testler**. Kod yazılmıyor, kırmızı commit'leniyor.
**Komut:** `npm test --prefix queen-agent/frontend`

---

## Tur 2'nin ayrıca dokunacağı yer

`dist` aynı commit'te derlenecek — ön yüz değişikliği bunsuz bitmiş sayılmıyor. Bu turda
derlenmiyor: bu turda çalışan bir ön yüz yok, kırmızı testler var.

---

## 1 · `queen-agent/frontend/src/features/workspace/PermissionCard.test.jsx` — yeni dosya

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import PermissionCard from "./PermissionCard.jsx";

// Madde 99 asked the question; this is where it is seen. The card stands in the transcript while
// the turn is paused, and the two buttons are the only way past it apart from Stop.

const ARGS = '{"name": "plan.md", "content": "# Plan"}';

test("it names the tool that wants to run", () => {
  render(<PermissionCard tool="create_file" args={ARGS} />);
  expect(screen.getByText("QueenAgent wants to run create_file")).toBeTruthy();
});

test("it shows the arguments as they came", () => {
  // Raw, unparsed. Approving a write without seeing what is being written is approving nothing,
  // and a second parser beside run_tool's would drift from it on the first change to either.
  render(<PermissionCard tool="create_file" args={ARGS} />);
  expect(screen.getByText(ARGS)).toBeTruthy();
});

test("allowing hands nothing up but the yes", () => {
  const onAllow = vi.fn();
  render(<PermissionCard tool="create_file" args={ARGS} onAllow={onAllow} />);
  fireEvent.click(screen.getByText("Allow"));
  expect(onAllow).toHaveBeenCalledWith();
});

test("denying carries what is in the box", () => {
  // A refusal with nothing written on it is a wall the model walks into again, so the box is next
  // to the button that needs it.
  const onDeny = vi.fn();
  render(<PermissionCard tool="create_file" args={ARGS} onDeny={onDeny} />);
  fireEvent.change(screen.getByPlaceholderText("Why not? (optional)"), {
    target: { value: "that file is mine" },
  });
  fireEvent.click(screen.getByText("Deny"));
  expect(onDeny).toHaveBeenCalledWith("that file is mine");
});

test("an empty box still denies", () => {
  // Optional means optional: a button that did nothing until a sentence was typed would be a
  // second question nobody asked.
  const onDeny = vi.fn();
  render(<PermissionCard tool="create_file" args={ARGS} onDeny={onDeny} />);
  fireEvent.click(screen.getByText("Deny"));
  expect(onDeny).toHaveBeenCalledWith("");
});
```

## 2 · `queen-agent/frontend/src/features/workspace/ModePicker.test.jsx` — Ask'ın satırı

Dosyanın sonuna:

```jsx
test("ask mode no longer claims nothing is written", () => {
  // It was true until Madde 99 and is not now: a write in this mode stops and asks. A line that
  // says otherwise sends the user looking for a bug that is a feature.
  render(<ModePicker mode="ask" open />);
  const said = screen.getByText("Ask", { selector: ".menu__item-name" }).closest(".menu__item")
    .textContent;
  expect(said).not.toContain("Nothing is written");
  expect(said).toContain("asks");
});
```

## 3 · `queen-agent/frontend/src/App.test.jsx` — akan turun içinde

Dosyanın sonuna:

```jsx
// --- the question the screen asks (Madde 102) ----------------------------------------------------

const ASKING =
  'event: chat\ndata: {"chat":"c1"}\n\n' +
  'event: permission\ndata: {"tool":"create_file","arguments":"{\\"name\\": \\"plan.md\\"}"}\n\n';

function paused(onAnswer) {
  /* A chat mid-answer, stopped on a question. The gate is released by whatever answers the door,
     so the turn only finishes once the test has pressed something -- the same shape the stop test
     uses, and nothing in it depends on timing. */
  const owed = { id: "c1", title: "hello", messages: [] };
  const { response, release } = gatedSse(ASKING, `event: done\ndata: ${JSON.stringify(owed)}\n\n`);
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") return Promise.resolve(response);
    if (path.endsWith("/permission") && options?.method === "POST") {
      onAnswer?.(path, JSON.parse(options.body));
      release();
      return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
    }
    if (path.endsWith("/chats/c1"))
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");
  return { fetch, release };
}

async function asked() {
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  /* Sent in ask mode, which is the mode the question exists for -- and it is also what makes the
     picker's move afterwards something to see: the app starts in edit, where nothing is asked. */
  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  fireEvent.click(screen.getByText("Ask", { selector: ".menu__item-name" }));
  fireEvent.change(box, { target: { value: "write the plan" } });
  fireEvent.keyDown(box, { key: "Enter" });
  return screen.findByText("QueenAgent wants to run create_file");
}

test("a permission frame puts the card up while the answer is still running", async () => {
  const { release } = paused();
  await asked();
  expect(screen.getByText('{"name": "plan.md"}')).toBeTruthy();
  release();
});

test("allowing sends the yes to the chat's own door", async () => {
  let sent = null;
  const { release } = paused((path, body) => {
    sent = { path, body };
  });
  await asked();
  fireEvent.click(screen.getByText("Allow"));
  await waitFor(() => expect(sent).toBeTruthy());
  expect(sent.path).toContain("/api/projects/p1/chats/c1/permission");
  expect(sent.body).toEqual({ allowed: true });
  release();
});

test("allowing moves the mode picker to edit", async () => {
  // The answer settles this one call; the picker is what settles the next turn. Left on Ask, the
  // very next message would raise the same question again.
  paused();
  await asked();
  expect(screen.getByText("Ask", { selector: ".picker__name" })).toBeTruthy();
  fireEvent.click(screen.getByText("Allow"));
  await waitFor(() =>
    expect(screen.getByText("Edit", { selector: ".picker__name" })).toBeTruthy(),
  );
});

test("denying carries the reason the user typed", async () => {
  let sent = null;
  paused((path, body) => {
    sent = body;
  });
  await asked();
  fireEvent.change(screen.getByPlaceholderText("Why not? (optional)"), {
    target: { value: "not that file" },
  });
  fireEvent.click(screen.getByText("Deny"));
  await waitFor(() => expect(sent).toBeTruthy());
  expect(sent).toEqual({ allowed: false, reason: "not that file" });
});

test("answering takes the card down", async () => {
  paused();
  await asked();
  fireEvent.click(screen.getByText("Allow"));
  await waitFor(() =>
    expect(screen.queryByText("QueenAgent wants to run create_file")).toBeNull(),
  );
});

test("the send button is still a stop while the card stands", async () => {
  // The wait has no end and no timeout, so the way out is the button that was already there.
  const { release } = paused();
  await asked();
  expect(screen.getByTitle("Stop")).toBeTruthy();
  release();
});

test("a turn that ends unanswered takes the card with it", async () => {
  // A stop, or a stream that died. Left standing, the card would hang over the next turn offering
  // to allow something nobody is waiting on any more.
  const owed = { id: "c1", title: "hello", messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(sseResponse(ASKING + `event: done\ndata: ${JSON.stringify(owed)}\n\n`));
    }
    if (path.endsWith("/chats/c1"))
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "write the plan" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() =>
    expect(screen.queryByText("QueenAgent wants to run create_file")).toBeNull(),
  );
  expect(fetch.mock.calls.some(([path]) => String(path).endsWith("/permission"))).toBe(false);
});
```

## 4 · Koş

```
npm test --prefix queen-agent/frontend
python -m pytest queen-agent -q
```

Beklenen: ön yüzde **on üç kırmızı** — `PermissionCard.test.jsx`'ten 5, `ModePicker.test.jsx`'ten 1,
`App.test.jsx`'ten 7. Arka yüzde değişen yok; oradaki iki kırmızı `test_notebook`'un.

`PermissionCard.test.jsx` olmayan bir modülü **dosyanın başında** import ediyor, ve o dosyanın
toplanması patlıyor. Sorun değil: patlayan yalnız o dosya, ve içindeki beş test zaten bu turun
kırmızıları. Ötekiler var olan dosyalarda ve tek tek düşüyorlar.

## 5 · Commit

```
test(queen-agent): red for the screen that asks
```
