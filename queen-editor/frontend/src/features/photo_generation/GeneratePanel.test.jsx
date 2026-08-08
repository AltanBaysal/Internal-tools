import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import GeneratePanel from "./GeneratePanel.jsx";

const SETTINGS = { prompts: '["ilk prompt"]', negative: "", variants: 4 };
const PROMPT_BOX = '["ilk prompt", "ikinci prompt"]';

function renderPanel(props) {
  return render(
    <GeneratePanel
      job={{ status: "idle" }}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      onGenerate={() => Promise.resolve()}
      onClearError={() => {}}
      {...props}
    />,
  );
}

describe("GeneratePanel — the form", () => {
  it("offers the generate button with the fields", () => {
    renderPanel();

    expect(screen.getByText("Üret")).toBeTruthy();
    expect(screen.getByPlaceholderText(PROMPT_BOX)).toBeTruthy();
  });

  it("previews how many photos the list would make", () => {
    renderPanel({ settings: { ...SETTINGS, prompts: '["a", "b"]', variants: 3 } });

    expect(screen.getByText(/2 prompt × 3 varyant/)).toBeTruthy();
  });

  it("keeps the run's own status out of the form", () => {
    renderPanel({ job: { status: "running", project: "düğün", done: 7, total: 48 } });

    expect(screen.queryByText("7 / 48")).toBeNull();
    expect(screen.queryByText("Durdur")).toBeNull();
  });

  it("says whose run is blocking when another project holds the worker", () => {
    renderPanel({ job: { status: "running", project: "balo" }, busyElsewhere: true });

    expect(screen.getByText("Üretim sürüyor: balo — bitmesini bekle.")).toBeTruthy();
    expect(screen.getByText("Üret").closest("button").disabled).toBe(true);
  });
});

describe("GeneratePanel — a field error", () => {
  it("reddens the field the server named and writes its text underneath", () => {
    renderPanel({ error: "Prompt listesi boş.", errorField: "prompts" });

    expect(screen.getByText("Prompt listesi boş.")).toBeTruthy();
    expect(screen.getByPlaceholderText(PROMPT_BOX).style.borderColor).toBe("var(--danger)");
  });

  it("clears the error once typing starts", () => {
    const onClearError = vi.fn();
    renderPanel({ error: "Prompt listesi boş.", errorField: "prompts", onClearError });

    fireEvent.change(screen.getByPlaceholderText(PROMPT_BOX), { target: { value: '["a"]' } });

    expect(onClearError).toHaveBeenCalled();
  });
});
