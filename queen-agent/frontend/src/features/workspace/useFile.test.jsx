import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { useFile } from "./useFile.js";

const FILE = { name: "plan.md", ext: "md", size: 8, text: "the body", modifiedAt: "2026-08-09" };

beforeEach(() => {
  // jsdom has no object URLs, and the saving step is the browser's job rather than ours to test.
  URL.createObjectURL = vi.fn().mockReturnValue("blob:x");
  URL.revokeObjectURL = vi.fn();
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

function Host({ projectId = "p1" }) {
  const reading = useFile(projectId);
  return (
    <div>
      <button type="button" onClick={() => reading.open("plan.md")}>
        open
      </button>
      <button type="button" onClick={() => reading.open("plan.md", "p2")}>
        open elsewhere
      </button>
      <button type="button" onClick={() => reading.download()}>
        save
      </button>
      <button type="button" onClick={() => reading.reload()}>
        refresh
      </button>
      <button type="button" onClick={reading.close}>
        close
      </button>
      <span data-testid="name">{reading.name ?? ""}</span>
      <span data-testid="text">{reading.file?.text ?? ""}</span>
      <span data-testid="missing">{reading.missing ? "gone" : ""}</span>
    </div>
  );
}

function stub(response) {
  const fetch = vi.fn().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

test("opening a file reads it", async () => {
  stub({ ok: true, status: 200, json: async () => FILE });
  render(<Host />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("text").textContent).toBe("the body"));
});

test("a file that is not there is marked gone rather than shouting", async () => {
  stub({ ok: false, status: 404, text: async () => JSON.stringify({ error: "file not found" }) });
  render(<Host />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("missing").textContent).toBe("gone"));
});

test("closing forgets which file was open", async () => {
  stub({ ok: true, status: 200, json: async () => FILE });
  render(<Host />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("name").textContent).toBe("plan.md"));
  fireEvent.click(screen.getByText("close"));
  expect(screen.getByTestId("name").textContent).toBe("");
});

test("a different project closes what was open", async () => {
  stub({ ok: true, status: 200, json: async () => FILE });
  const { rerender } = render(<Host projectId="p1" />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("name").textContent).toBe("plan.md"));
  rerender(<Host projectId="p2" />);
  // The file belongs to the project that was left behind.
  await waitFor(() => expect(screen.getByTestId("name").textContent).toBe(""));
});

test("coming back to the project finds the panel closed", async () => {
  stub({ ok: true, status: 200, json: async () => FILE });
  const { rerender } = render(<Host projectId="p1" />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("name").textContent).toBe("plan.md"));

  rerender(<Host projectId="p2" />);
  await waitFor(() => expect(screen.getByTestId("name").textContent).toBe(""));
  rerender(<Host projectId="p1" />);
  // Leaving the project closed it. Reopening itself would be the panel deciding for the user.
  expect(screen.getByTestId("name").textContent).toBe("");
});

test("a file opened in the same breath as going to its project survives the trip", async () => {
  stub({ ok: true, status: 200, json: async () => FILE });
  const { rerender } = render(<Host projectId="p1" />);
  fireEvent.click(screen.getByText("open elsewhere"));
  // Not on screen yet: it belongs to the project being navigated to.
  expect(screen.getByTestId("name").textContent).toBe("");

  rerender(<Host projectId="p2" />);
  await waitFor(() => expect(screen.getByTestId("name").textContent).toBe("plan.md"));
});

test("saving reads the file again rather than keeping the copy on screen", async () => {
  const fetch = stub({ ok: true, status: 200, json: async () => FILE });
  render(<Host />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("text").textContent).toBe("the body"));
  const reads = fetch.mock.calls.length;

  fireEvent.click(screen.getByText("save"));
  // The panel may have been open for a while; what lands on disk is what the server holds now.
  await waitFor(() => expect(fetch.mock.calls.length).toBe(reads + 1));
  await waitFor(() => expect(URL.createObjectURL).toHaveBeenCalled());
});

// Madde 192. The panel used to read its file once and never again: the effect hangs off the path,
// and the path answers *which* file is open rather than what is in it. A turn that rewrote the open
// file left the screen showing the copy it was opened with.

test("refreshing reads the open file again", async () => {
  let onDisk = FILE;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(async () => ({ ok: true, status: 200, json: async () => onDisk })),
  );
  render(<Host />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("text").textContent).toBe("the body"));

  onDisk = { ...FILE, text: "the body, rewritten" };
  fireEvent.click(screen.getByText("refresh"));
  await waitFor(() => expect(screen.getByTestId("text").textContent).toBe("the body, rewritten"));
});

test("the text stays on screen while the fresh copy is on its way", async () => {
  // The first read starts from nothing, so it may draw nothing. A refresh has a page under the
  // reader's eyes, and blanking it for a frame is the panel blinking at them.
  let hand;
  const fetch = vi
    .fn()
    .mockResolvedValueOnce({ ok: true, status: 200, json: async () => FILE })
    .mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          hand = resolve;
        }),
    );
  vi.stubGlobal("fetch", fetch);
  render(<Host />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("text").textContent).toBe("the body"));

  fireEvent.click(screen.getByText("refresh"));
  await waitFor(() => expect(fetch.mock.calls.length).toBe(2));
  expect(screen.getByTestId("text").textContent).toBe("the body");

  hand({ ok: true, status: 200, json: async () => ({ ...FILE, text: "later" }) });
  await waitFor(() => expect(screen.getByTestId("text").textContent).toBe("later"));
});

test("with nothing open there is nothing to refresh", async () => {
  const fetch = stub({ ok: true, status: 200, json: async () => FILE });
  render(<Host />);
  fireEvent.click(screen.getByText("refresh"));
  // Two turns of the microtask queue: long enough for a read that was going to happen to have
  // started. A reload that asked for the path whatever it was would knock at files/null.
  await Promise.resolve();
  await Promise.resolve();
  expect(fetch).not.toHaveBeenCalled();
});

test("a file deleted while it was open is marked gone by the next refresh", async () => {
  let gone = false;
  const fetch = vi.fn().mockImplementation(async () =>
    gone
      ? { ok: false, status: 404, text: async () => JSON.stringify({ error: "file not found" }) }
      : { ok: true, status: 200, json: async () => FILE },
  );
  vi.stubGlobal("fetch", fetch);
  render(<Host />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("text").textContent).toBe("the body"));

  gone = true;
  fireEvent.click(screen.getByText("refresh"));
  await waitFor(() => expect(screen.getByTestId("missing").textContent).toBe("gone"));
  // And the body goes with it: a page under a line saying the file is gone is the older of the two
  // lies, not the gentler one.
  expect(screen.getByTestId("text").textContent).toBe("");
});

test("the saved file keeps the name it has in the project", async () => {
  stub({ ok: true, status: 200, json: async () => FILE });
  render(<Host />);
  fireEvent.click(screen.getByText("open"));
  await waitFor(() => expect(screen.getByTestId("text").textContent).toBe("the body"));
  fireEvent.click(screen.getByText("save"));
  await waitFor(() => expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:x"));
});
