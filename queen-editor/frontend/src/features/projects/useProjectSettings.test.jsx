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
  it("ayarlar gelince hazır duruma geçer", async () => {
    getSettings.mockResolvedValue({ prompts: '["a"]', negative: "kötü", variants: 4 });

    const { result } = renderHook(() => useProjectSettings("düğün"));
    expect(result.current.status).toBe("loading");

    await settle();

    expect(result.current.status).toBe("ready");
    expect(result.current.settings.negative).toBe("kötü");
  });

  it("hata durumunda sunucunun metnini taşır", async () => {
    getSettings.mockRejectedValue(new Error("Proje bulunamadı: düğün"));

    const { result } = renderHook(() => useProjectSettings("düğün"));
    await settle();

    expect(result.current.status).toBe("error");
    expect(result.current.error).toBe("Proje bulunamadı: düğün");
  });

  it("proje hızlı değişirse eski projenin geç gelen cevabını yutar", async () => {
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
