import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { useFiles } from "./useFiles.js";

afterEach(() => {
  vi.unstubAllGlobals();
});

function Host({ projectId = "p1" }) {
  const { files, deleting } = useFiles(projectId);
  return (
    <div>
      <button type="button" onClick={() => deleting.remove("plan.md")}>
        remove
      </button>
      <span data-testid="names">{files.map((file) => file.name).join(",")}</span>
      <span data-testid="error">{deleting.error ?? ""}</span>
      <span data-testid="keys">{Object.keys(deleting).sort().join(",")}</span>
    </div>
  );
}

function server({ onDisk = [], refuse = false }) {
  const state = { files: [...onDisk] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "DELETE") {
      if (refuse) return Promise.resolve({ ok: false, status: 409, text: async () => "" });
      state.files = [];
      return Promise.resolve({ ok: true, status: 200, json: async () => ({ trashed: "plan.md" }) });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => state.files });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const PLAN = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };

test("removing a file takes it out of the list", async () => {
  server({ onDisk: [PLAN] });
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe("plan.md"));
  fireEvent.click(screen.getByText("remove"));
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe(""));
});

test("nothing is kept in order to offer it back", async () => {
  // The trash name was held only for as long as the undo offer stood; karar 16 took the offer, so
  // there is nothing left to remember.
  server({ onDisk: [PLAN] });
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe("plan.md"));
  expect(screen.getByTestId("keys").textContent).toBe("error,remove");
});

test("a refused delete says what the server said", async () => {
  // The strip that used to carry this line is gone; the line is not.
  server({ onDisk: [PLAN], refuse: true });
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe("plan.md"));
  fireEvent.click(screen.getByText("remove"));
  await waitFor(() => expect(screen.getByTestId("error").textContent).toContain("409"));
  // Refused means still there.
  expect(screen.getByTestId("names").textContent).toBe("plan.md");
});

test("leaving the project clears the last failure", async () => {
  server({ onDisk: [PLAN], refuse: true });
  const { rerender } = render(<Host projectId="p1" />);
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe("plan.md"));
  fireEvent.click(screen.getByText("remove"));
  await waitFor(() => expect(screen.getByTestId("error").textContent).toContain("409"));

  rerender(<Host projectId="p2" />);
  await waitFor(() => expect(screen.getByTestId("error").textContent).toBe(""));
});
