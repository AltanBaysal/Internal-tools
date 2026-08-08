import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import GeneratePanel from "./GeneratePanel.jsx";

const SETTINGS = { prompts: '["ilk prompt"]', negative: "", variants: 4 };
const PROMPT_BOX = '["ilk prompt", "ikinci prompt"]';
const RUNNING = { status: "running", project: "düğün", done: 7, failed: 0, total: 48 };

function renderPanel(props) {
  return render(
    <GeneratePanel
      job={{ status: "idle" }}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      onGenerate={() => Promise.resolve({ added: 4 })}
      onClearError={() => {}}
      {...props}
    />,
  );
}

const promptBox = () => screen.getByPlaceholderText(PROMPT_BOX);
const variantBox = () => screen.getByRole("spinbutton");

describe("GeneratePanel — the button", () => {
  it("adds to the queue instead of starting a run", () => {
    renderPanel();

    expect(screen.getByText("Üretime ekle")).toBeTruthy();
    expect(screen.queryByText("Üret")).toBeNull();
  });

  it("stays open while the queue flows", () => {
    renderPanel({ job: RUNNING });

    expect(promptBox().disabled).toBe(false);
    expect(variantBox().disabled).toBe(false);
    expect(screen.getByText("Üretime ekle").closest("button").disabled).toBe(false);
  });

  it("is disabled on an empty list", () => {
    renderPanel({ settings: { ...SETTINGS, prompts: "   " } });

    expect(screen.getByText("Üretime ekle").closest("button").disabled).toBe(true);
  });

  it("is disabled while another project holds the worker", () => {
    renderPanel({ job: { status: "running", project: "balo" }, busyElsewhere: true });

    expect(screen.getByText("Üretime ekle").closest("button").disabled).toBe(true);
    expect(screen.getByText("Üretim sürüyor: balo — bitmesini bekle.")).toBeTruthy();
  });

  it("holds only the button while the request is in flight, never the fields", async () => {
    let release;
    renderPanel({ onGenerate: () => new Promise((resolve) => { release = resolve; }) });

    fireEvent.click(screen.getByText("Üretime ekle"));

    expect(screen.getByText("Ekleniyor…").closest("button").disabled).toBe(true);
    expect(promptBox().disabled).toBe(false);

    await act(async () => { release({ added: 4 }); });
  });

  it("never shows the prompt times variant preview", () => {
    renderPanel({ settings: { ...SETTINGS, prompts: '["a", "b"]', variants: 3 } });

    expect(screen.queryByText(/varyant =/)).toBeNull();
  });
});

describe("GeneratePanel — the confirmation", () => {
  beforeEach(() => vi.useFakeTimers({ shouldAdvanceTime: true }));
  afterEach(() => vi.useRealTimers());

  it("quotes the number of frames the server took, then clears itself", async () => {
    renderPanel({ onGenerate: () => Promise.resolve({ added: 48 }) });

    fireEvent.click(screen.getByText("Üretime ekle"));

    await waitFor(() => expect(screen.getByText("✓ 48 kare kuyruğa eklendi")).toBeTruthy());

    await act(async () => { vi.advanceTimersByTime(4000); });

    expect(screen.queryByText("✓ 48 kare kuyruğa eklendi")).toBeNull();
  });

  it("says one line when the queue would not take the frames", async () => {
    renderPanel({ onGenerate: () => Promise.resolve(null) });

    fireEvent.click(screen.getByText("Üretime ekle"));

    await waitFor(() => expect(screen.getByText("Kuyruğa eklenemedi")).toBeTruthy());
    expect(screen.queryByText(/kuyruğa eklendi/)).toBeNull();
  });
});

describe("GeneratePanel — the variant box", () => {
  it("refuses a value outside 1-26", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "27" } });
    expect(variantBox().value).toBe("4");

    fireEvent.change(variantBox(), { target: { value: "0" } });
    expect(variantBox().value).toBe("4");

    fireEvent.change(variantBox(), { target: { value: "26" } });
    expect(variantBox().value).toBe("26");
  });

  it("snaps an emptied box back to 1 when it loses focus", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "" } });
    expect(variantBox().value).toBe("");        // clearing has to be possible while typing

    fireEvent.blur(variantBox());
    expect(variantBox().value).toBe("1");
  });

  it("has no error state of its own", () => {
    renderPanel({ error: "Varyant sayısı 1-26 arası bir tam sayı olmalı.", errorField: "variants" });

    expect(variantBox().style.borderColor).toBe("");
    expect(screen.queryByText("Varyant sayısı 1-26 arası bir tam sayı olmalı.")).toBeNull();
  });
});

describe("GeneratePanel — a format error", () => {
  it("reddens the prompt box and writes the server's one line underneath", () => {
    renderPanel({ error: "Format hatası — liste okunamadı", errorField: "prompts" });

    expect(screen.getByText("Format hatası — liste okunamadı")).toBeTruthy();
    expect(promptBox().style.borderColor).toBe("var(--danger)");
  });

  it("clears the error once typing starts", () => {
    const onClearError = vi.fn();
    renderPanel({ error: "Format hatası — liste okunamadı", errorField: "prompts", onClearError });

    fireEvent.change(promptBox(), { target: { value: '["a"]' } });

    expect(onClearError).toHaveBeenCalled();
  });
});
