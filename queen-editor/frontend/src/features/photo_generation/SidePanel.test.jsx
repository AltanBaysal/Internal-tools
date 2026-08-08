import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import SidePanel from "./SidePanel.jsx";

const SETTINGS = { prompts: '["ilk prompt"]', negative: "", variants: 4 };
const RUNNING = { status: "running", project: "düğün", done: 7, failed: 0, total: 48 };
const PROMPT_BOX = '["ilk prompt", "ikinci prompt"]';

function renderColumn(props) {
  return render(
    <SidePanel
      job={{ status: "idle" }}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      project="düğün"
      stopping={false}
      queue={{ pending: [], total: 0 }}
      onGenerate={() => Promise.resolve()}
      onStop={() => {}}
      onResume={() => {}}
      onCancel={() => {}}
      onClearError={() => {}}
      {...props}
    />,
  );
}

describe("SidePanel — the icon rail", () => {
  it("opens on the form panel", () => {
    renderColumn();

    expect(screen.getByPlaceholderText(PROMPT_BOX)).toBeTruthy();
    expect(screen.getByLabelText("Üretime ekle").getAttribute("aria-current")).toBe("page");
    expect(screen.getByLabelText("Kuyruğu takip et").getAttribute("aria-current")).toBeNull();
  });

  it("swaps the panel when another icon is pressed", () => {
    renderColumn({ job: RUNNING });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    expect(screen.queryByPlaceholderText(PROMPT_BOX)).toBeNull();
    expect(screen.getByText("7 / 48")).toBeTruthy();
    expect(screen.getByLabelText("Kuyruğu takip et").getAttribute("aria-current")).toBe("page");
  });

  it("keeps the run's own words out of the form panel", () => {
    renderColumn({ job: RUNNING });

    // The form panel is open: the progress card belongs to the queue panel, not here.
    expect(screen.queryByText("7 / 48")).toBeNull();
    expect(screen.queryByText("Durdur")).toBeNull();
  });

  it("opens the agent panel and leaves it deliberately empty", () => {
    renderColumn();

    fireEvent.click(screen.getByLabelText("AI agent"));

    expect(screen.getByText("Agent buradan çalışacak.")).toBeTruthy();
  });

  it("names the open panel above it", () => {
    renderColumn();

    expect(screen.getByText("Üretime ekle")).toBeTruthy();

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    expect(screen.getByText("Kuyruğu takip et")).toBeTruthy();
  });
});
