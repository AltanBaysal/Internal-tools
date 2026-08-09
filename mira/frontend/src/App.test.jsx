import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import App from "./App.jsx";

afterEach(() => {
  vi.unstubAllGlobals();
  // jsdom shares one document across tests, so a pushed address has to be put back.
  window.history.pushState(null, "", "/");
});

function stubProjects(projects) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => projects }),
  );
}

test("the shell renders", () => {
  stubProjects([]);
  render(<App />);
  expect(screen.getByTestId("app-shell")).toBeTruthy();
});

test("loaded projects reach both the sidebar and the cards", async () => {
  stubProjects([{ id: "p1", name: "Thesis", desc: "Summaries.", hue: 45, chats: 0, files: 0 }]);
  render(<App />);
  await waitFor(() => expect(screen.getAllByText("Thesis").length).toBe(2));
});

test("a project address does not draw home", async () => {
  stubProjects([]);
  window.history.pushState(null, "", "/p/pabc");
  render(<App />);
  await waitFor(() => expect(screen.queryByRole("heading", { level: 1 })).toBeNull());
});
