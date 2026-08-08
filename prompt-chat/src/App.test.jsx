import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App.jsx";

const keyBox = () => screen.getByPlaceholderText("xAI API anahtarı");
const modelBox = () => screen.getByPlaceholderText("model");

describe("anahtar ve model alanları", () => {
  it("model alanı varsayılanla açılır", () => {
    render(<App />);
    expect(modelBox().value).toBe("grok-4.3");
  });

  it("yazılan anahtar localStorage'a geçer", () => {
    render(<App />);
    fireEvent.change(keyBox(), { target: { value: "xai-123" } });
    expect(localStorage.getItem("xai_key")).toBe("xai-123");
  });

  it("kayıtlı anahtar açılışta geri gelir", () => {
    localStorage.setItem("xai_key", "xai-kayitli");
    render(<App />);
    expect(keyBox().value).toBe("xai-kayitli");
  });

  it("anahtar ekranda okunmaz", () => {
    render(<App />);
    expect(keyBox().type).toBe("password");
  });
});

const ok = (content) => ({
  ok: true,
  status: 200,
  text: async () => JSON.stringify({ choices: [{ message: { content } }] }),
});

const composer = () => screen.getByPlaceholderText(/Mesaj yaz/);
const sendButton = () => screen.getByRole("button", { name: /Gönder|…/ });

function write(text) {
  fireEvent.change(composer(), { target: { value: text } });
}

describe("sohbet", () => {
  it("gönderilen mesaj ve gelen cevap ekranda durur", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByText("merhaba")).toBeTruthy();
    expect(screen.getByText("selam")).toBeTruthy();
  });

  it("gönderince metin kutusu boşalır", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    await screen.findByText("merhaba");
    expect(composer().value).toBe("");
  });

  it("Enter gönderir, Shift+Enter göndermez", async () => {
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

  it("cevap beklenirken gönderme kapalıdır", async () => {
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

  it("boş mesaj gönderilmez", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    write("   ");
    fireEvent.click(sendButton());
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("hata, servisin kendi metniyle görünür", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 401, text: async () => "kim bu" })
    );
    render(<App />);
    write("selam");
    fireEvent.click(sendButton());

    expect(await screen.findByText("HTTP 401 — kim bu")).toBeTruthy();
  });

  it("hatadan sonra sohbet çalışmaya devam eder", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 500, text: async () => "patladı" })
      .mockResolvedValueOnce(ok("yine buradayım"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("bir");
    fireEvent.click(sendButton());
    await screen.findByText("HTTP 500 — patladı");

    write("iki");
    fireEvent.click(sendButton());
    expect(await screen.findByText("yine buradayım")).toBeTruthy();
  });

  it("hata satırı isteğe karışmaz", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 500, text: async () => "patladı" })
      .mockResolvedValueOnce(ok("tamam"));
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    write("bir");
    fireEvent.click(sendButton());
    await screen.findByText("HTTP 500 — patladı");

    write("iki");
    fireEvent.click(sendButton());
    await screen.findByText("tamam");

    const [, init] = fetchMock.mock.calls[1];
    expect(JSON.parse(init.body).messages).toEqual([
      { role: "user", content: "bir" },
      { role: "user", content: "iki" },
    ]);
  });

  it("kayıtlı anahtar isteğe gider", async () => {
    localStorage.setItem("xai_key", "xai-kayitli");
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
