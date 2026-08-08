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

describe("sohbet listesi", () => {
  it("sohbetleri adlarıyla çizer", () => {
    show();
    expect(screen.getByText("kanlı dövüş sahnesi")).toBeTruthy();
    expect(screen.getByText("Yeni sohbet")).toBeTruthy();
  });

  it("bir sohbete tıklayınca id'siyle haber verir", () => {
    const props = show();
    fireEvent.click(screen.getByText("Yeni sohbet"));
    expect(props.onSelect).toHaveBeenCalledWith(2);
  });

  it("Yeni sohbet düğmesi haber verir", () => {
    const props = show();
    fireEvent.click(screen.getByRole("button", { name: /Yeni sohbet ekle/ }));
    expect(props.onNew).toHaveBeenCalled();
  });
});

describe("silme", () => {
  // Every row has its own delete button, so the label has to name the chat -- a bare
  // /sohbetini sil/ would match both rows and the query would throw.
  const deleteFirst = () =>
    screen.getByRole("button", { name: "kanlı dövüş sahnesi sohbetini sil" });

  it("onaylanırsa siler", () => {
    vi.stubGlobal("confirm", vi.fn(() => true));
    const props = show();
    fireEvent.click(deleteFirst());
    expect(props.onDelete).toHaveBeenCalledWith(1);
  });

  it("iptal edilirse silmez", () => {
    vi.stubGlobal("confirm", vi.fn(() => false));
    const props = show();
    fireEvent.click(deleteFirst());
    expect(props.onDelete).not.toHaveBeenCalled();
  });

  it("silmeden önce sorar", () => {
    const ask = vi.fn(() => false);
    vi.stubGlobal("confirm", ask);
    show();
    fireEvent.click(deleteFirst());
    expect(ask).toHaveBeenCalled();
  });
});

describe("ayarlar", () => {
  it("anahtar kayıtlıysa kapalı gelir", () => {
    show();
    expect(screen.queryByPlaceholderText("xAI API anahtarı")).toBeNull();
  });

  it("anahtar yoksa açık gelir", () => {
    show({ apiKey: "" });
    expect(screen.getByPlaceholderText("xAI API anahtarı")).toBeTruthy();
  });

  it("düğme açıp kapatır", () => {
    show();
    fireEvent.click(screen.getByRole("button", { name: /Ayarlar/ }));
    expect(screen.getByPlaceholderText("xAI API anahtarı")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: /Ayarlar/ }));
    expect(screen.queryByPlaceholderText("xAI API anahtarı")).toBeNull();
  });

  it("anahtar yazılınca haber verir", () => {
    const props = show({ apiKey: "" });
    fireEvent.change(screen.getByPlaceholderText("xAI API anahtarı"), {
      target: { value: "xai-yeni" },
    });
    expect(props.onApiKey).toHaveBeenCalledWith("xai-yeni");
  });

  it("model yazılınca haber verir", () => {
    const props = show({ apiKey: "" });
    fireEvent.change(screen.getByPlaceholderText("model"), { target: { value: "grok-5" } });
    expect(props.onModel).toHaveBeenCalledWith("grok-5");
  });

  it("anahtar ekranda okunmaz", () => {
    show({ apiKey: "" });
    expect(screen.getByPlaceholderText("xAI API anahtarı").type).toBe("password");
  });
});
