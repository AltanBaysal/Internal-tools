import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Sidebar from "./Sidebar.jsx";

// The tree itself is covered in ProjectTree.test.jsx; what is left here is the settings panel,
// which is the only thing Sidebar still owns.
function show(extra = {}) {
  const props = {
    projects: [{ id: 1, name: "Genel" }],
    files: [],
    chats: [{ id: 1, projectId: 1, messages: [], draft: "" }],
    active: { projectId: 1, chatId: 1, fileId: null },
    on: {
      openProject: vi.fn(), newProject: vi.fn(), deleteProject: vi.fn(),
      openFile: vi.fn(), newFile: vi.fn(), deleteFile: vi.fn(),
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

describe("the tree", () => {
  it("is handed the workspace so the sidebar itself holds no list state", () => {
    show();
    expect(screen.getByText(/Genel/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "+ Yeni dosya" })).toBeTruthy();
  });
});
