import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import FilePane from "./FilePane.jsx";

const FILES = [{ id: 1, projectId: 1, name: "plan.md", content: "ilk satır" }];

function draw(file = null) {
  const on = { openFile: vi.fn(), newFile: vi.fn(), deleteFile: vi.fn(), closeFile: vi.fn() };
  render(<FilePane files={FILES} projectId={1} file={file} on={on} onChange={vi.fn()} />);
  return on;
}

describe("FilePane", () => {
  it("shows the list when no file is open", () => {
    draw();
    expect(screen.getByRole("button", { name: "+ Yeni dosya" })).toBeTruthy();
    expect(document.querySelector("textarea")).toBeNull();
  });

  it("shows the open file in place of the list", () => {
    draw(FILES[0]);
    expect(screen.getByRole("textbox").value).toBe("ilk satır");
    expect(screen.queryByRole("button", { name: "+ Yeni dosya" })).toBeNull();
  });

  it("hands the back arrow through", () => {
    const on = draw(FILES[0]);
    fireEvent.click(screen.getByRole("button", { name: "Dosya listesine dön" }));
    expect(on.closeFile).toHaveBeenCalled();
  });

  it("widens only while a file is open", () => {
    const { unmount } = render(
      <FilePane files={FILES} projectId={1} file={null} on={{}} onChange={vi.fn()} />
    );
    expect(document.querySelector(".file-pane").className).not.toContain("open");
    unmount();

    render(<FilePane files={FILES} projectId={1} file={FILES[0]} on={{}} onChange={vi.fn()} />);
    expect(document.querySelector(".file-pane").className).toContain("open");
  });
});
