import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App.jsx";

// A chat's first user message is also its sidebar title, so an unscoped getByText would match twice.
// Scoping says the thing we actually mean: the message is in the conversation.
const inChat = () => within(document.querySelector(".chat"));

const ok = (content) => ({
  ok: true,
  status: 200,
  text: async () => JSON.stringify({ choices: [{ message: { content } }] }),
});

const composer = () => screen.getByPlaceholderText(/Mesaj yaz/);
const sendButton = () => screen.getByRole("button", { name: /Gönder|…/ });
const newChatButton = () => screen.getByRole("button", { name: /Yeni sohbet ekle/ });

function write(text) {
  fireEvent.change(composer(), { target: { value: text } });
}

// A stored key keeps the settings panel closed, which is the everyday state; tests that need the
// fields open leave it unset.
function withKey() {
  localStorage.setItem("xai_key", "xai-kayitli");
}

describe("startup", () => {
  it("opens with an empty chat when none are stored", () => {
    render(<App />);
    expect(composer().value).toBe("");
    expect(screen.getByText("Yeni sohbet")).toBeTruthy();
  });

  it("opens the settings panel when there is no key", () => {
    render(<App />);
    expect(screen.getByPlaceholderText("xAI API anahtarı")).toBeTruthy();
  });

  it("leaves the settings panel closed when a key is stored", () => {
    withKey();
    render(<App />);
    expect(screen.queryByPlaceholderText("xAI API anahtarı")).toBeNull();
  });

  it("does not go blank on a corrupt stored list", () => {
    localStorage.setItem("chats", "{yarim");
    render(<App />);
    expect(composer()).toBeTruthy();
  });

  it("brings stored chats back", () => {
    localStorage.setItem(
      "chats",
      JSON.stringify([{ id: 1, messages: [{ role: "user", content: "eski mesaj" }], draft: "" }])
    );
    localStorage.setItem("active_chat", "1");
    render(<App />);
    expect(inChat().getByText("eski mesaj")).toBeTruthy();
  });
});

describe("sending", () => {
  it("writes the message into the open chat and lands the reply", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByText("merhaba")).toBeTruthy();
    expect(inChat().getByText("selam")).toBeTruthy();
  });

  it("shows an error in the service's own words", async () => {
    withKey();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 401, text: async () => "kim bu" })
    );
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByText("HTTP 401 — kim bu")).toBeTruthy();
  });

  it("disables sending while a reply is pending", async () => {
    withKey();
    let release;
    const held = new Promise((resolve) => {
      release = resolve;
    });
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(held));
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByRole("button", { name: "…" })).toBeTruthy();
    expect(sendButton().disabled).toBe(true);

    release(ok("merhaba"));
    await screen.findByText("merhaba");
    expect(sendButton().disabled).toBe(false);
  });

  it("does not send an empty message", () => {
    withKey();
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    write("   ");
    fireEvent.click(sendButton());
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("sends on Enter but not on Shift+Enter", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("merhaba"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("selam");
    fireEvent.keyDown(composer(), { key: "Enter", shiftKey: true });
    expect(fetchMock).not.toHaveBeenCalled();

    fireEvent.keyDown(composer(), { key: "Enter" });
    await screen.findByText("merhaba");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("keeps working after an error", async () => {
    withKey();
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({ ok: false, status: 500, text: async () => "patladı" })
        .mockResolvedValueOnce(ok("yine buradayım"))
    );
    render(<App />);

    write("bir");
    fireEvent.click(sendButton());
    await screen.findByText("HTTP 500 — patladı");

    write("iki");
    fireEvent.click(sendButton());
    expect(await screen.findByText("yine buradayım")).toBeTruthy();
  });

  it("sends the stored key with the request", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("merhaba"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    await screen.findByText("merhaba");
    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer xai-kayitli");
  });
});

describe("moving between chats", () => {
  it("opens a new chat empty and keeps the old one listed", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("kanlı dövüş");
    fireEvent.click(sendButton());
    await screen.findByText("merhaba");

    fireEvent.click(newChatButton());
    expect(screen.queryByText("merhaba")).toBeNull();
    expect(screen.getByText("kanlı dövüş")).toBeTruthy(); // listedeki başlık
  });

  it("brings the messages back when returning to a chat", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("kanlı dövüş");
    fireEvent.click(sendButton());
    await screen.findByText("merhaba");

    fireEvent.click(newChatButton());
    fireEvent.click(screen.getByText("kanlı dövüş"));
    expect(screen.getByText("merhaba")).toBeTruthy();
  });

  it("gives every chat its own draft", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);

    // The title comes from the messages, not from the draft. Without a sent message both rows would
    // read "Yeni sohbet" and there would be no way to click back to this one.
    write("ilk sohbet");
    fireEvent.click(sendButton());
    await screen.findByText("merhaba");

    write("yarım kalan metin");
    fireEvent.click(newChatButton());
    expect(composer().value).toBe("");

    fireEvent.click(screen.getByText("ilk sohbet"));
    expect(composer().value).toBe("yarım kalan metin");
  });

  it("clears that chat's draft on send", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    await screen.findByText("merhaba");
    expect(composer().value).toBe("");
  });

  it("lands the reply in the chat that asked, even after switching away", async () => {
    withKey();
    let release;
    const held = new Promise((resolve) => {
      release = resolve;
    });
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(held));
    render(<App />);
    write("ilk sohbetin sorusu");
    fireEvent.click(sendButton());

    fireEvent.click(newChatButton());
    release(ok("ilk sohbete ait cevap"));

    // Ekranda duran yeni sohbete bulaşmadı...
    await screen.findByRole("button", { name: "Gönder" });
    expect(screen.queryByText("ilk sohbete ait cevap")).toBeNull();

    // ...isteyen sohbete yazıldı.
    fireEvent.click(screen.getByText("ilk sohbetin sorusu"));
    expect(screen.getByText("ilk sohbete ait cevap")).toBeTruthy();
  });
});

describe("deleting", () => {
  it("removes a deleted chat from the list", async () => {
    withKey();
    vi.stubGlobal("confirm", vi.fn(() => true));
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("silinecek");
    fireEvent.click(sendButton());
    await screen.findByText("merhaba");

    fireEvent.click(newChatButton());
    fireEvent.click(screen.getByRole("button", { name: /silinecek sohbetini sil/ }));
    expect(screen.queryByText("silinecek")).toBeNull();
  });

  it("does not leave the screen empty when the open chat is deleted", () => {
    withKey();
    vi.stubGlobal("confirm", vi.fn(() => true));
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Yeni sohbet sohbetini sil/ }));
    expect(composer()).toBeTruthy();
  });
});
