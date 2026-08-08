import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App.jsx";

// skillSource.js reads the real files in the repo. Letting the tests depend on them would mean
// editing a skill's wording breaks the suite, so the list is fixed here. Vitest hoists vi.mock to
// the top of the file and the factory cannot see outer variables, hence the values written inline.
vi.mock("./skillSource.js", () => ({
  skills: [
    { name: "netlestirme", description: "Soruları çıkarır.", body: "SORU TALİMATI" },
    { name: "plan-yazma", description: "Adımlara böler.", body: "PLAN TALİMATI" },
  ],
  errors: [],
}));

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
// The exact label, not a regex: a chat with no messages is titled "Yeni sohbet" too, so a loose
// match would find its row as well as this button.
const newChatButton = () => screen.getByRole("button", { name: "+ Yeni sohbet" });

// A file's name is in the list and, when it is open, in the file view header — never both, but the
// pane is the thing the assertion means either way.
const inFiles = () => within(document.querySelector(".file-pane"));

// Projects live behind the header button now, so a test that touches them opens that list first.
function browseProjects() {
  fireEvent.click(screen.getByRole("button", { name: /^‹/ }));
}

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

  it("keeps the chat when the confirmation is cancelled", async () => {
    withKey();
    vi.stubGlobal("confirm", vi.fn(() => false));
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("kalsın");
    fireEvent.click(sendButton());
    await screen.findByText("merhaba");

    fireEvent.click(screen.getByRole("button", { name: /kalsın sohbetini sil/ }));
    expect(screen.getByRole("button", { name: /kalsın sohbetini sil/ })).toBeTruthy();
  });

  it("does not leave the screen empty when the open chat is deleted", () => {
    withKey();
    vi.stubGlobal("confirm", vi.fn(() => true));
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Yeni sohbet sohbetini sil/ }));
    expect(composer()).toBeTruthy();
  });
});

describe("calling a skill", () => {
  it("changes nothing at all when no skill is called", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("cevap"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByText("cevap")).toBeTruthy();
    expect(screen.queryByText("/plan-yazma")).toBeNull();
    // messages[0] is the system message, so the user's own turn is at 1.
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.messages[1]).toEqual({ role: "user", content: "selam" });
  });

  it("opens the list when the draft is a bare slash", () => {
    withKey();
    render(<App />);
    write("/");
    expect(screen.getByText("/plan-yazma")).toBeTruthy();
    expect(screen.getByText("/netlestirme")).toBeTruthy();
  });

  it("closes the list once a space is typed", () => {
    withKey();
    render(<App />);
    write("/plan-yazma bir şey");
    expect(screen.queryByText("Adımlara böler.")).toBeNull();
  });

  it("puts the picked name into the draft, ready for the question", () => {
    withKey();
    render(<App />);
    write("/pl");
    fireEvent.click(screen.getByText("/plan-yazma"));
    expect(composer().value).toBe("/plan-yazma ");
  });

  it("stores the name, shows the tag, and sends the instruction", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("1. kutu bul"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("/plan-yazma taşınacağım");
    fireEvent.click(sendButton());

    expect(await screen.findByText("1. kutu bul")).toBeTruthy();
    expect(inChat().getByText("/plan-yazma")).toBeTruthy();
    expect(inChat().getByText("taşınacağım")).toBeTruthy();
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.messages[1].content).toBe("PLAN TALİMATI\n\ntaşınacağım");
  });

  it("refuses an unknown name and never reaches the network", () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("olmamalı"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("/yok-boyle bir şey");
    fireEvent.click(sendButton());

    expect(screen.getByText(/"\/yok-boyle" bulunamadı/)).toBeTruthy();
    expect(screen.getByText(/\/plan-yazma/)).toBeTruthy();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("clears the complaint once a valid call replaces it", async () => {
    withKey();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("tamam")));
    render(<App />);

    write("/yok-boyle bir şey");
    fireEvent.click(sendButton());
    expect(screen.getByText(/bulunamadı/)).toBeTruthy();

    write("/plan-yazma bir şey");
    fireEvent.click(sendButton());

    expect(await screen.findByText("tamam")).toBeTruthy();
    expect(screen.queryByText(/bulunamadı/)).toBeNull();
  });

  it("sends nothing when only the name was typed", () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("olmamalı"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("/plan-yazma");
    fireEvent.click(sendButton());

    expect(fetchMock).not.toHaveBeenCalled();
  });
});

const newFileButton = () => screen.getByRole("button", { name: "+ Yeni dosya" });
const editor = () => document.querySelector(".file-view textarea");

describe("the workspace", () => {
  it("creates a file, names it, and opens it on the right", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    expect(inFiles().getByText("plan.md")).toBeTruthy();
    expect(editor()).toBeTruthy();
  });

  it("keeps what is typed into a file", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    fireEvent.change(editor(), { target: { value: "birinci madde" } });
    expect(editor().value).toBe("birinci madde");
  });

  it("refuses a second file with the same name and says why", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    // Creating a file opens it, and the open file takes the column, so the way back to the list is
    // through the arrow.
    fireEvent.click(screen.getByRole("button", { name: "Dosya listesine dön" }));
    fireEvent.click(newFileButton());
    expect(screen.getByText(/zaten var/)).toBeTruthy();
  });

  it("opens the file list on @ and writes the choice into the draft", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());

    write("bak şu @");
    fireEvent.click(screen.getByText("@plan.md"));
    expect(composer().value).toBe("bak şu @plan.md ");
  });

  it("sends the file content with the message", async () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    const fetchMock = vi.fn().mockResolvedValue(ok("okudum"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    fireEvent.click(newFileButton());
    fireEvent.change(editor(), { target: { value: "birinci madde" } });

    write("@plan.md ne yazıyor");
    fireEvent.click(sendButton());

    expect(await screen.findByText("okudum")).toBeTruthy();
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.messages[1].content).toContain("birinci madde");
  });

  it("treats an @ that matches no file as ordinary text", async () => {
    withKey();
    const fetchMock = vi.fn().mockResolvedValue(ok("tamam"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("@herkes bakabilir");
    fireEvent.click(sendButton());

    expect(await screen.findByText("tamam")).toBeTruthy();
    const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(sent.messages[1]).toEqual({ role: "user", content: "@herkes bakabilir" });
  });

  it("keeps the open file open across a chat switch, because it belongs to the project", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    fireEvent.change(editor(), { target: { value: "birinci madde" } });

    fireEvent.click(newChatButton());

    expect(editor()).toBeTruthy();
    expect(editor().value).toBe("birinci madde");
  });

  it("keeps one project's files away from another and closes the open file on the way", () => {
    withKey();
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());
    expect(editor()).toBeTruthy();

    vi.stubGlobal("prompt", vi.fn(() => "İkinci proje"));
    browseProjects();
    fireEvent.click(screen.getByRole("button", { name: "+ Yeni proje" }));

    expect(inFiles().queryByText("plan.md")).toBeNull();
    expect(editor()).toBeNull();
  });

  it("says what deleting a project would cost before doing it", () => {
    withKey();
    const confirmMock = vi.fn(() => false);
    vi.stubGlobal("confirm", confirmMock);
    vi.stubGlobal("prompt", vi.fn(() => "plan"));
    render(<App />);
    fireEvent.click(newFileButton());

    browseProjects();
    fireEvent.click(screen.getByRole("button", { name: "Genel projesini sil" }));
    expect(confirmMock.mock.calls[0][0]).toMatch(/1 dosya/);
    expect(screen.getByText("Genel")).toBeTruthy();
  });
});
