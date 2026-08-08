import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import FileView from "./FileView.jsx";

const DOSYA = { id: 1, projectId: 1, name: "plan.md", content: "ilk satır" };

describe("FileView", () => {
  it("shows the name and the raw content", () => {
    render(<FileView file={DOSYA} onChange={() => {}} onClose={() => {}} />);
    expect(screen.getByText("plan.md")).toBeTruthy();
    expect(screen.getByRole("textbox").value).toBe("ilk satır");
  });

  it("reports every keystroke, because there is no save button", () => {
    const onChange = vi.fn();
    render(<FileView file={DOSYA} onChange={onChange} onClose={() => {}} />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "yeni" } });
    expect(onChange).toHaveBeenCalledWith("yeni");
  });

  it("offers the file as a download link named after it", () => {
    render(<FileView file={DOSYA} onChange={() => {}} onClose={() => {}} />);
    const link = screen.getByText("İndir").closest("a");
    expect(link.getAttribute("download")).toBe("plan.md");
    expect(decodeURIComponent(link.getAttribute("href"))).toContain("ilk satır");
  });

  it("closes on the × without touching the content", () => {
    const onClose = vi.fn();
    const onChange = vi.fn();
    render(<FileView file={DOSYA} onChange={onChange} onClose={onClose} />);
    fireEvent.click(screen.getByRole("button", { name: "Dosyayı kapat" }));
    expect(onClose).toHaveBeenCalled();
    expect(onChange).not.toHaveBeenCalled();
  });

  it("copies the whole content", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    render(<FileView file={DOSYA} onChange={() => {}} onClose={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: /Kopyala/ }));
    expect(await screen.findByRole("button", { name: "Kopyalandı" })).toBeTruthy();
    expect(writeText).toHaveBeenCalledWith("ilk satır");
  });
});
