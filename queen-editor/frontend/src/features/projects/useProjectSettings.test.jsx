import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getSettings } from "../../shared/api.js";
import { useProjectSettings } from "./useProjectSettings.js";

vi.mock("../../shared/api.js", () => ({
  getSettings: vi.fn(),
  saveSettings: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useProjectSettings", () => {
  it("becomes ready once the settings arrive", async () => {
    getSettings.mockResolvedValue({ prompts: '["a"]', negative: "kötü", variants: 4 });

    const { result } = renderHook(() => useProjectSettings("düğün"));
    expect(result.current.status).toBe("loading");

    await settle();

    expect(result.current.status).toBe("ready");
    expect(result.current.settings.negative).toBe("kötü");
  });

  it("carries the server's text on failure", async () => {
    getSettings.mockRejectedValue(new Error("Proje bulunamadı: düğün"));

    const { result } = renderHook(() => useProjectSettings("düğün"));
    await settle();

    expect(result.current.status).toBe("error");
    expect(result.current.error).toBe("Proje bulunamadı: düğün");
  });

  it("swallows a late answer for the previous project after a quick switch", async () => {
    let resolveFirst;
    getSettings
      .mockImplementationOnce(() => new Promise((resolve) => { resolveFirst = resolve; }))
      .mockImplementationOnce(() => Promise.resolve({ prompts: "İKİNCİ", negative: "", variants: 2 }));

    const { result, rerender } = renderHook(({ project }) => useProjectSettings(project), {
      initialProps: { project: "birinci" },
    });

    rerender({ project: "ikinci" });
    await settle();
    expect(result.current.settings.prompts).toBe("İKİNCİ");

    await act(async () => {
      resolveFirst({ prompts: "BİRİNCİ", negative: "", variants: 9 });
    });

    expect(result.current.settings.prompts).toBe("İKİNCİ");
  });
});
