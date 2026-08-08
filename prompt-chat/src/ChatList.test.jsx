import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ChatList from "./ChatList.jsx";

const CHATS = [
  { id: 1, projectId: 1, messages: [{ role: "user", content: "kar manzarası" }], draft: "" },
  { id: 2, projectId: 1, messages: [], draft: "" },
  { id: 3, projectId: 2, messages: [{ role: "user", content: "başka proje" }], draft: "" },
];

function draw() {
  const on = { openChat: vi.fn(), newChat: vi.fn(), deleteChat: vi.fn() };
  render(<ChatList chats={CHATS} projectId={1} activeId={1} on={on} />);
  return on;
}

describe("ChatList", () => {
  it("shows only the open project's chats", () => {
    draw();
    expect(screen.getByText("kar manzarası")).toBeTruthy();
    expect(screen.queryByText("başka proje")).toBeNull();
  });

  it("titles a chat that has no messages yet", () => {
    draw();
    expect(screen.getByText("Yeni sohbet")).toBeTruthy();
  });

  it("marks the open one", () => {
    draw();
    expect(screen.getByText("kar manzarası").closest(".row").className).toContain("active");
  });

  it("opens a chat by its title", () => {
    const on = draw();
    fireEvent.click(screen.getByText("kar manzarası"));
    expect(on.openChat).toHaveBeenCalledWith(1);
  });

  it("names the chat a delete would take", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "kar manzarası sohbetini sil" }));
    expect(on.deleteChat).toHaveBeenCalledWith(1);
  });

  it("offers a way to add one", () => {
    const on = draw();
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni sohbet" }));
    expect(on.newChat).toHaveBeenCalled();
  });
});
