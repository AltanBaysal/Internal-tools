import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Sidebar from "./Sidebar.jsx";

const msg = (content) => ({ role: "user", content });

const chats = [
  { id: 1, messages: [msg("kanlı dövüş sahnesi")], draft: "" },
  { id: 2, messages: [], draft: "" },
];

function show(extra = {}) {
  const props = {
    chats,
    activeId: 1,
    onSelect: vi.fn(),
    onNew: vi.fn(),
    onDelete: vi.fn(),
    apiKey: "xai-123",
    onApiKey: vi.fn(),
    model: "grok-4.3",
    onModel: vi.fn(),
    ...extra,
  };
  render(<Sidebar {...props} />);
  return props;
}

describe("the chat list", () => {
  it("draws the chats with their titles", () => {
    show();
    expect(screen.getByText("kanlı dövüş sahnesi")).toBeTruthy();
    expect(screen.getByText("Yeni sohbet")).toBeTruthy();
  });

  it("reports the id when a chat is clicked", () => {
    const props = show();
    fireEvent.click(screen.getByText("Yeni sohbet"));
    expect(props.onSelect).toHaveBeenCalledWith(2);
  });

  it("reports a click on the new-chat button", () => {
    const props = show();
    fireEvent.click(screen.getByRole("button", { name: /Yeni sohbet ekle/ }));
    expect(props.onNew).toHaveBeenCalled();
  });
});

describe("deleting", () => {
  // Every row has its own delete button, so the label has to name the chat -- a bare
  // /sohbetini sil/ would match both rows and the query would throw.
  const deleteFirst = () =>
    screen.getByRole("button", { name: "kanlı dövüş sahnesi sohbetini sil" });

  it("deletes when confirmed", () => {
    vi.stubGlobal("confirm", vi.fn(() => true));
    const props = show();
    fireEvent.click(deleteFirst());
    expect(props.onDelete).toHaveBeenCalledWith(1);
  });

  it("does not delete when cancelled", () => {
    vi.stubGlobal("confirm", vi.fn(() => false));
    const props = show();
    fireEvent.click(deleteFirst());
    expect(props.onDelete).not.toHaveBeenCalled();
  });

  it("asks before deleting", () => {
    const ask = vi.fn(() => false);
    vi.stubGlobal("confirm", ask);
    show();
    fireEvent.click(deleteFirst());
    expect(ask).toHaveBeenCalled();
  });
});

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
