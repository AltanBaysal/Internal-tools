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
      <button type="button" onClick={deleting.undo}>
        undo
      </button>
      <span data-testid="names">{files.map((file) => file.name).join(",")}</span>
      <span data-testid="deleted">{deleting.deleted?.trashed ?? ""}</span>
      <span data-testid="error">{deleting.error ?? ""}</span>
    </div>
  );
}

function server({ onDisk = [], trashed = "plan.md", refuse = false }) {
  const state = { files: [...onDisk] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "DELETE") {
      state.files = [];
      return Promise.resolve({ ok: true, status: 200, json: async () => ({ trashed }) });
    }
    if (path.includes("/trash/")) {
      if (refuse) {
        return Promise.resolve({ ok: false, status: 409, json: async () => ({}) });
      }
      state.files = [...onDisk];
      return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => state.files });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const PLAN = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };

test("removing a file takes it out of the list and offers an undo", async () => {
  server({ onDisk: [PLAN] });
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe("plan.md"));

  fireEvent.click(screen.getByText("remove"));
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe(""));
  expect(screen.getByTestId("deleted").textContent).toBe("plan.md");
});

test("undo asks for the name the file had, not the one the trash gave it", async () => {
  const fetch = server({ onDisk: [PLAN], trashed: "plan-2.md" });
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe("plan.md"));
  fireEvent.click(screen.getByText("remove"));
  await waitFor(() => expect(screen.getByTestId("deleted").textContent).toBe("plan-2.md"));

  fireEvent.click(screen.getByText("undo"));
  await waitFor(() => expect(screen.getByTestId("deleted").textContent).toBe(""));
  const restore = fetch.mock.calls.find(([path]) => path.includes("/trash/"));
  expect(restore[0]).toContain("plan-2.md");
  expect(JSON.parse(restore[1].body)).toEqual({ name: "plan.md" });
});

test("an undo the server refuses keeps the offer and says why", async () => {
  server({ onDisk: [PLAN], refuse: true });
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe("plan.md"));
  fireEvent.click(screen.getByText("remove"));
  await waitFor(() => expect(screen.getByTestId("deleted").textContent).toBe("plan.md"));

  fireEvent.click(screen.getByText("undo"));
  await waitFor(() => expect(screen.getByTestId("error").textContent).toContain("409"));
  // The file is still in the trash, so the offer is still real.
  expect(screen.getByTestId("deleted").textContent).toBe("plan.md");
});

test("leaving the project takes the offer with it", async () => {
  server({ onDisk: [PLAN] });
  const { rerender } = render(<Host projectId="p1" />);
  await waitFor(() => expect(screen.getByTestId("names").textContent).toBe("plan.md"));
  fireEvent.click(screen.getByText("remove"));
  await waitFor(() => expect(screen.getByTestId("deleted").textContent).toBe("plan.md"));

  rerender(<Host projectId="p2" />);
  await waitFor(() => expect(screen.getByTestId("deleted").textContent).toBe(""));
});
