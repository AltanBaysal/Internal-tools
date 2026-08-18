import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { useSettings } from "./useSettings.js";

afterEach(() => {
  vi.unstubAllGlobals();
});

function Host() {
  const { apiKey, save } = useSettings();
  return (
    <div>
      <span data-testid="key">{apiKey}</span>
      <button type="button" onClick={() => save("xai-new")}>
        save
      </button>
    </div>
  );
}

test("the saved key is read once, on the way in", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({ apiKey: "xai-abc" }) }),
  );
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("key").textContent).toBe("xai-abc"));
});

test("saving sends the key and keeps what came back", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ apiKey: "" }) })
    .mockResolvedValue({ ok: true, status: 200, json: async () => ({ apiKey: "xai-new" }) });
  vi.stubGlobal("fetch", fetch);
  render(<Host />);
  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));

  fireEvent.click(screen.getByText("save"));
  await waitFor(() => expect(screen.getByTestId("key").textContent).toBe("xai-new"));
  const [path, options] = fetch.mock.calls[1];
  expect(path).toBe("/api/settings");
  expect(options.method).toBe("PATCH");
  expect(JSON.parse(options.body)).toEqual({ apiKey: "xai-new" });
});

test("a key that could not be read leaves the screen empty rather than guessing", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500, text: async () => "" }));
  render(<Host />);
  await waitFor(() => expect(screen.getByTestId("key").textContent).toBe(""));
});
