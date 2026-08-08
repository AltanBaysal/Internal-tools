import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Sidebar from "./Sidebar.jsx";

// The lists themselves are covered in ProjectList.test.jsx and ChatList.test.jsx; what is left here
// is what the sidebar itself owns — the settings panel and which of the two lists is showing.
function show(extra = {}) {
  const props = {
    projects: [
      { id: 1, name: "Genel" },
      { id: 2, name: "Kampanya" },
    ],
    files: [],
    chats: [{ id: 1, projectId: 1, messages: [], draft: "" }],
    active: { projectId: 1, chatId: 1 },
    on: {
      openProject: vi.fn(), newProject: vi.fn(), deleteProject: vi.fn(),
      openChat: vi.fn(), newChat: vi.fn(), deleteChat: vi.fn(),
    },
    apiKey: "xai-123",
    onApiKey: vi.fn(),
    model: "grok-4.3",
    onModel: vi.fn(),
    ...extra,
  };
  render(<Sidebar {...props} />);
  return props;
}

describe("the settings panel", () => {
  it("starts closed when a key is stored", () => {
    show();
    expect(screen.queryByPlaceholderText("xAI API anahtarı")).toBeNull();
  });

  it("starts open when there is no key", () => {
    show({ apiKey: "" });
    expect(screen.getByPlaceholderText("xAI API anahtarı")).toBeTruthy();
  });

  it("toggles open and shut", () => {
    show();
    fireEvent.click(screen.getByRole("button", { name: /Ayarlar/ }));
    expect(screen.getByPlaceholderText("xAI API anahtarı")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: /Ayarlar/ }));
    expect(screen.queryByPlaceholderText("xAI API anahtarı")).toBeNull();
  });

  it("reports a typed key", () => {
    const props = show({ apiKey: "" });
    fireEvent.change(screen.getByPlaceholderText("xAI API anahtarı"), {
      target: { value: "xai-yeni" },
    });
    expect(props.onApiKey).toHaveBeenCalledWith("xai-yeni");
  });

  it("reports a typed model name", () => {
    const props = show({ apiKey: "" });
    fireEvent.change(screen.getByPlaceholderText("model"), { target: { value: "grok-5" } });
    expect(props.onModel).toHaveBeenCalledWith("grok-5");
  });

  it("keeps the key unreadable on screen", () => {
    show({ apiKey: "" });
    expect(screen.getByPlaceholderText("xAI API anahtarı").type).toBe("password");
  });
});

describe("the two lists", () => {
  it("starts on the open project's chats, under its name", () => {
    show();
    expect(screen.getByRole("button", { name: "‹ Genel" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "+ Yeni sohbet" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "+ Yeni proje" })).toBeNull();
  });

  it("swaps to the project list when the name is clicked", () => {
    show();
    fireEvent.click(screen.getByRole("button", { name: "‹ Genel" }));
    expect(screen.getByRole("button", { name: "+ Yeni proje" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "+ Yeni sohbet" })).toBeNull();
  });

  it("comes back to the chats once a project is picked", () => {
    const props = show();
    fireEvent.click(screen.getByRole("button", { name: "‹ Genel" }));
    fireEvent.click(screen.getByText("Kampanya"));
    expect(props.on.openProject).toHaveBeenCalledWith(2);
    expect(screen.getByRole("button", { name: "+ Yeni sohbet" })).toBeTruthy();
  });

  it("comes back to the chats after adding a project", () => {
    const props = show();
    fireEvent.click(screen.getByRole("button", { name: "‹ Genel" }));
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni proje" }));
    expect(props.on.newProject).toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "+ Yeni sohbet" })).toBeTruthy();
  });

  it("stays on the project list after a delete, so more can follow", () => {
    const props = show();
    fireEvent.click(screen.getByRole("button", { name: "‹ Genel" }));
    fireEvent.click(screen.getByRole("button", { name: "Kampanya projesini sil" }));
    expect(props.on.deleteProject).toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "+ Yeni proje" })).toBeTruthy();
  });
});
