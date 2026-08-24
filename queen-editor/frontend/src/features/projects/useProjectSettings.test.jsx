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

  it("opens ready the second time the same project is looked at", async () => {
    getSettings.mockResolvedValue({ prompts: "İLK", negative: "", variants: 2 });

    const first = renderHook(() => useProjectSettings("hatirlanan"));
    await settle();
    first.unmount();

    // Opening a frame tears this hook down and building it again is the whole of coming back.
    // There is nothing to wait for: the answer is in hand.
    const { result } = renderHook(() => useProjectSettings("hatirlanan"));
    expect(result.current.status).toBe("ready");
    expect(result.current.settings.prompts).toBe("İLK");
  });

  it("still waits for a project nothing has answered for", async () => {
    getSettings.mockResolvedValue({ prompts: "İLK", negative: "", variants: 2 });

    const first = renderHook(() => useProjectSettings("dolduran"));
    await settle();
    first.unmount();

    // What is remembered is one project's own answer, never another's.
    const { result } = renderHook(() => useProjectSettings("bos"));
    expect(result.current.status).toBe("loading");
  });

  it("refreshes what it remembered, without a wait on screen", async () => {
    getSettings.mockResolvedValue({ prompts: "ESKİ", negative: "", variants: 2 });

    const first = renderHook(() => useProjectSettings("tazelenen"));
    await settle();
    first.unmount();

    getSettings.mockResolvedValue({ prompts: "YENİ", negative: "", variants: 2 });
    const { result } = renderHook(() => useProjectSettings("tazelenen"));
    // Remembering is not believing forever: the record is asked for again, and the screen simply
    // does not go blank while the answer is on its way.
    expect(result.current.settings.prompts).toBe("ESKİ");
    await settle();

    expect(result.current.settings.prompts).toBe("YENİ");
    expect(result.current.status).toBe("ready");
  });

  it("keeps what it remembered when the refresh cannot be read", async () => {
    getSettings.mockResolvedValue({ prompts: "DURAN", negative: "", variants: 2 });

    const first = renderHook(() => useProjectSettings("duran"));
    await settle();
    first.unmount();

    getSettings.mockRejectedValue(new Error("Sunucuya ulaşılamadı."));
    const { result } = renderHook(() => useProjectSettings("duran"));
    await settle();

    // A refresh that fell over costs the user nothing, and emptying the screen over it would be
    // the opposite of quiet. The dead tunnel is the status poll's to report, and it does.
    expect(result.current.status).toBe("ready");
    expect(result.current.settings.prompts).toBe("DURAN");
  });
});
