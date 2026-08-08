import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import MentionPicker from "./MentionPicker.jsx";

const SKILLS = [
  { name: "netlestirme", description: "Soruları çıkarır." },
  { name: "plan-yazma", description: "Adımlara böler." },
];

describe("MentionPicker", () => {
  it("shows each item behind the prefix it is called with", () => {
    render(<MentionPicker prefix="/" items={SKILLS} onPick={() => {}} />);
    expect(screen.getByText("/plan-yazma")).toBeTruthy();
    expect(screen.getByText("Adımlara böler.")).toBeTruthy();
  });

  it("uses the same body for file mentions", () => {
    render(<MentionPicker prefix="@" items={[{ name: "plan.md" }]} onPick={() => {}} />);
    expect(screen.getByText("@plan.md")).toBeTruthy();
  });

  it("leaves out the description line when an item has none", () => {
    const { container } = render(
      <MentionPicker prefix="@" items={[{ name: "plan.md" }]} onPick={() => {}} />
    );
    expect(container.querySelector(".mention-desc")).toBeNull();
  });

  it("draws nothing at all for an empty list", () => {
    const { container } = render(<MentionPicker prefix="/" items={[]} onPick={() => {}} />);
    expect(container.firstChild).toBeNull();
  });

  it("hands the bare name to onPick, without the prefix", () => {
    const onPick = vi.fn();
    render(<MentionPicker prefix="@" items={[{ name: "plan.md" }]} onPick={onPick} />);
    fireEvent.click(screen.getByText("@plan.md"));
    expect(onPick).toHaveBeenCalledWith("plan.md");
  });
});
