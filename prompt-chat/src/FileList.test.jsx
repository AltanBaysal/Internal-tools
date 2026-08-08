import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import FileList from "./FileList.jsx";

const FILES = [
  { id: 1, projectId: 1, name: "plan.md", content: "" },
  { id: 2, projectId: 2, name: "baska.md", content: "" },
];

function draw() {
  const on = { openFile: vi.fn(), newFile: vi.fn(), deleteFile: vi.fn() };
  render(<FileList files={FILES} projectId={1} on={on} />);
  return on;
}

describe("FileList", () => {
  it("shows only the open project's files", () => {
    draw();
    expect(screen.getByText("plan.md")).toBeTruthy();
    expect(screen.queryByText("baska.md")).toBeNull();
  });

  it("opens a file by its name", () => {
    const on = draw();
    fireEvent.click(screen.getByText("plan.md"));
    expect(on.openFile).toHaveBeenCalledWith(1);
  });

  it("names the file a delete would take", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "plan.md dosyasını sil" }));
    expect(on.deleteFile).toHaveBeenCalledWith(1);
  });

  it("offers a way to add one", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni dosya" }));
    expect(on.newFile).toHaveBeenCalled();
  });
});
