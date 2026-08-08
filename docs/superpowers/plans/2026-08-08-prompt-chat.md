# prompt-chat Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Grok ile düz sohbet eden, `localhost`'ta çalışan bir deney tezgâhı yapmak — WAN 2.2 T2V prompt'larının kalitesini denemek için.

**Architecture:** Backend yok. React uygulaması tarayıcıdan doğrudan `api.x.ai/v1/chat/completions`'a gider (xAI CORS'a izin veriyor, 2026-08-08'de doğrulandı). Üç katman: `chat.js` saf mantık (ağ yok, React yok), `api.js` tek `fetch` noktası, `App.jsx`/`Message.jsx` yalnız gösterim. Sohbet dizisi bellekte durur ve her istekte bütün olarak gönderilir — bağlamın tek taşıyıcısı odur.

**Tech Stack:** React 18.3 + Vite 5.4 + Vitest 3.2 + jsdom + Testing Library — Queen Editor'ın frontend'iyle **birebir aynı sürümler**, çünkü bu tezgâh işe yararsa kod oraya taşınacak.

**Spec:** [2026-08-08-prompt-chat-design.md](../specs/2026-08-08-prompt-chat-design.md)

## Global Constraints

- **Kendi klasörü, kendi `package.json`'ı:** `prompt-chat/`. Queen Editor'ın hiçbir dosyasını okumaz, ona hiçbir şey eklemez.
- **Backend yok.** Tek `fetch` `src/api.js`'tedir; başka hiçbir dosya ağa çıkmaz.
- **Anahtar kaynağa yazılmaz.** Sabit yok, `.env` yok (Vite `VITE_` değişkenlerini çıktıya gömer, yani saklamış olmayız). Anahtar yalnız ekrandaki alandan gelir, `localStorage`'da durur: `xai_key`, `xai_model` (varsayılan `grok-4.3`).
- **Hata metni ham geçer.** `HTTP <kod> — <gövde>` olduğu gibi basılır. Sebep uydurulmaz: 401 hem yanlış anahtar hem yanlış model id'si yüzünden gelebilir.
- **Dil ayrımı (repo kuralı):** kod yorumları ve commit mesajları **İngilizce**; ekranda görünen her metin **Türkçe**. Test adları da Türkçe (çıktıyı kullanıcı okuyor).
- **Cevap ham metindir.** JSX çocuğu olarak basılır (React kaçırır), `dangerouslySetInnerHTML` yok, markdown render yok. Satır sonlarını CSS'teki `white-space: pre-wrap` korur.
- **`temperature` / `max_tokens` gönderilmez.**
- **Testler tarayıcısız ve ağsız.** `fetch` `vi.stubGlobal` ile sahtelenir; hiçbir test gerçek saniye beklemez. `jest-dom` **kurulmaz** — Queen Editor'da da yok; `expect(btn.disabled).toBe(true)` gibi düz DOM iddiaları kullanılır.
- **`dist/` commit edilmez.** Queen Editor'ın "derlenmişi commit et" kuralı Colab yüzünden vardır; bu araç Colab'a gitmez. `prompt-chat/.gitignore` `dist/`i ve `node_modules/`ü kapsar.
- **Commit izni ayrıdır.** Aşağıdaki commit adımları **kendiliğinden yetki değildir** — kullanıcı deneyip "commit et" diyene kadar hiçbir şey commit edilmez.

---

### Task 1: Proje iskeleti, anahtar ve model alanları

Uygulama ayağa kalkar, koyu ve sade görünür; anahtar ile model alanları yazılanı hatırlar. `npm test` ilk yeşilini verir.

**Files:**
- Create: `prompt-chat/package.json`, `prompt-chat/vite.config.js`, `prompt-chat/.gitignore`, `prompt-chat/index.html`
- Create: `prompt-chat/src/main.jsx`, `prompt-chat/src/App.jsx`, `prompt-chat/src/app.css`, `prompt-chat/src/test-setup.js`
- Test: `prompt-chat/src/App.test.jsx`

**Interfaces:**
- Consumes: —
- Produces: `App` (default export, `src/App.jsx`); `localStorage` anahtarları `xai_key` ve `xai_model`; CSS sınıfları `.app`, `.msg`, `.role`, `.body`, `.copy`. Task 4 `App`'i genişletir, Task 5 `.copy`'yi kullanır.

- [ ] **Step 1: `prompt-chat/package.json`**

```json
{
  "name": "prompt-chat",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@testing-library/dom": "^10.4.1",
    "@testing-library/react": "^16.3.2",
    "@vitejs/plugin-react": "^4.3.1",
    "jsdom": "^29.1.1",
    "vite": "^5.4.0",
    "vitest": "^3.2.7"
  }
}
```

- [ ] **Step 2: `prompt-chat/vite.config.js`**

```js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vitest reuses this config, so tests get the same JSX transform as the dev server. Test files sit
// next to their source and are never imported by the app.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
  },
});
```

- [ ] **Step 3: `prompt-chat/.gitignore`**

```gitignore
node_modules/
dist/
```

- [ ] **Step 4: `prompt-chat/src/test-setup.js`**

```js
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

// One test's leftovers must never decide another test's outcome: unmount what was rendered, drop
// the fake fetch, hand the clock back, and forget the stored key. Without globals enabled,
// Testing Library's own auto cleanup does not run, so it is done here explicitly.
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
  localStorage.clear();
});
```

- [ ] **Step 5: `prompt-chat/index.html`**

```html
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>prompt-chat</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 6: `prompt-chat/src/main.jsx`**

```jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./app.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

- [ ] **Step 7: `prompt-chat/src/app.css`**

```css
:root {
  --bg: #16181c;
  --panel: #1e2126;
  --line: #2c3038;
  --ink: #e6e8ea;
  --ink-dim: #9aa0a6;
  --accent: #7aa2f7;
  --danger: #f7768e;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 15px/1.6 ui-sans-serif, system-ui, sans-serif;
}

.app { height: 100vh; display: flex; flex-direction: column; }

header { display: flex; gap: 8px; padding: 10px; border-bottom: 1px solid var(--line); }
header input { flex: 1; }
header .model { max-width: 180px; }

input, textarea, button {
  font: inherit;
  color: var(--ink);
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 8px 10px;
}
input:focus, textarea:focus { outline: 1px solid var(--accent); }

.chat { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 14px; }
.msg { width: 100%; max-width: 760px; margin: 0 auto; }
.role { font-size: 11px; color: var(--ink-dim); margin-bottom: 4px; }

/* Raw text: the copied prompt must match what the model wrote, line breaks included. */
.body { white-space: pre-wrap; word-wrap: break-word; padding: 10px 12px; border-radius: 8px; }
.user .body { background: var(--panel); border: 1px solid var(--line); }
.assistant .body { background: transparent; }
.error .body { color: var(--danger); border: 1px solid var(--danger); }

footer { display: flex; gap: 8px; padding: 10px; border-top: 1px solid var(--line); }
footer textarea { flex: 1; resize: none; height: 76px; }
footer button { min-width: 92px; cursor: pointer; }
footer button:disabled { opacity: .5; cursor: default; }

/* Overrides the shared button styling above — this is a quiet link, not a control. */
.copy {
  margin-top: 6px;
  padding: 3px 8px;
  font-size: 12px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--ink-dim);
  cursor: pointer;
}
.copy:hover { color: var(--ink); border-color: var(--line); }
```

- [ ] **Step 8: Düşen testi yaz — `prompt-chat/src/App.test.jsx`**

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
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
```

- [ ] **Step 9: Testin düştüğünü gör**

Run: `cd prompt-chat && npm install && npm test`
Expected: FAIL — `Failed to resolve import "./App.jsx"`.

- [ ] **Step 10: `prompt-chat/src/App.jsx`'i yaz**

```jsx
import { useEffect, useState } from "react";

const DEFAULT_MODEL = "grok-4.3";

// The key and the model name outlive the page; the conversation deliberately does not.
function usePersisted(storageKey, fallback) {
  const [value, setValue] = useState(() => localStorage.getItem(storageKey) ?? fallback);
  useEffect(() => {
    localStorage.setItem(storageKey, value);
  }, [storageKey, value]);
  return [value, setValue];
}

export default function App() {
  const [apiKey, setApiKey] = usePersisted("xai_key", "");
  const [model, setModel] = usePersisted("xai_model", DEFAULT_MODEL);

  return (
    <div className="app">
      <header>
        <input
          type="password"
          placeholder="xAI API anahtarı"
          autoComplete="off"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
        />
        <input
          className="model"
          placeholder="model"
          autoComplete="off"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        />
      </header>
    </div>
  );
}
```

- [ ] **Step 11: Testin geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 4 test.

- [ ] **Step 12: Tarayıcı kontrolü**

Run: `cd prompt-chat && npm run dev` → `http://localhost:5173`

Beklenen: koyu bir sayfa; üstte iki alan (anahtar boş ve yazdığın gizli, model `grok-4.3`). Anahtar alanına bir şey yaz, sayfayı yenile → duruyor.

- [ ] **Step 13: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/
git commit -m "feat(prompt-chat): scaffold Vite/React app with persisted key and model"
```

---

### Task 2: `chat.js` — saf mantık

İstek gövdesini kuran ve hata metnini biçimlendiren iki fonksiyon. Ağ yok, React yok, tarayıcı yok — bu yüzden testi en ucuz olan katman.

**Files:**
- Create: `prompt-chat/src/chat.js`
- Test: `prompt-chat/src/chat.test.js`

**Interfaces:**
- Consumes: —
- Produces:
  - `toRequestBody(messages, model)` → `{ model: string, messages: Array<{role, content}> }`. `messages` girdisi `{role: "user"|"assistant"|"error", content: string}` kayıtlarıdır; `"error"` olanlar ayıklanır.
  - `formatHttpError(status, body)` → `string`.
  - Task 3 ikisini de kullanır.

- [ ] **Step 1: Düşen testi yaz — `prompt-chat/src/chat.test.js`**

```js
import { describe, it, expect } from "vitest";
import { toRequestBody, formatHttpError } from "./chat.js";

describe("toRequestBody", () => {
  it("modeli ve mesajları taşır", () => {
    const body = toRequestBody([{ role: "user", content: "selam" }], "grok-4.3");
    expect(body).toEqual({
      model: "grok-4.3",
      messages: [{ role: "user", content: "selam" }],
    });
  });

  it("hata satırlarını dışarıda bırakır", () => {
    const body = toRequestBody(
      [
        { role: "user", content: "selam" },
        { role: "error", content: "HTTP 401 — nope" },
        { role: "assistant", content: "merhaba" },
      ],
      "grok-4.3"
    );
    expect(body.messages).toEqual([
      { role: "user", content: "selam" },
      { role: "assistant", content: "merhaba" },
    ]);
  });

  it("ekranın kendi alanlarını göndermez", () => {
    const body = toRequestBody([{ role: "user", content: "selam", copied: true }], "grok-4.3");
    expect(body.messages[0]).toEqual({ role: "user", content: "selam" });
  });

  it("boş sohbette boş liste verir", () => {
    expect(toRequestBody([], "grok-4.3").messages).toEqual([]);
  });
});

describe("formatHttpError", () => {
  it("kodu ve gövdeyi olduğu gibi birleştirir", () => {
    expect(formatHttpError(401, '{"error":"bad key"}')).toBe('HTTP 401 — {"error":"bad key"}');
  });

  it("boş gövdeyi de olduğu gibi geçirir", () => {
    expect(formatHttpError(500, "")).toBe("HTTP 500 — ");
  });
});
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `cd prompt-chat && npm test`
Expected: FAIL — `Failed to resolve import "./chat.js"`.

- [ ] **Step 3: `prompt-chat/src/chat.js`'i yaz**

```js
// The screen keeps error rows so the user can see what happened, but xAI rejects any role it does
// not know, so they are dropped on the way out. Only role and content travel: anything the screen
// adds to a message stays on the screen.
export function toRequestBody(messages, model) {
  return {
    model,
    messages: messages
      .filter((m) => m.role === "user" || m.role === "assistant")
      .map((m) => ({ role: m.role, content: m.content })),
  };
}

// The service's own words: a 401 is equally a bad key and a bad model id, so naming one cause here
// would send the reader down the wrong path.
export function formatHttpError(status, body) {
  return `HTTP ${status} — ${body}`;
}
```

- [ ] **Step 4: Testin geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 6 yeni test, toplam 10.

- [ ] **Step 5: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/src/chat.js prompt-chat/src/chat.test.js
git commit -m "feat(prompt-chat): request body and error formatting"
```

---

### Task 3: `api.js` — tek ağ noktası

xAI'a giden tek `fetch`. Testi sahte `fetch` ile koşar, ağ görmez.

**Files:**
- Create: `prompt-chat/src/api.js`
- Test: `prompt-chat/src/api.test.js`

**Interfaces:**
- Consumes: Task 2'nin `toRequestBody(messages, model)` ve `formatHttpError(status, body)` fonksiyonları.
- Produces: `sendChat({ key, model, messages })` → `Promise<string>` — cevabın metni. 200 dışında ve ağ hatasında `Error` fırlatır. Task 4 bunu çağırır.

- [ ] **Step 1: Düşen testi yaz — `prompt-chat/src/api.test.js`**

```js
import { describe, it, expect, vi } from "vitest";
import { sendChat } from "./api.js";

// Hand-built stubs rather than a real Response: jsdom does not provide one, and these say exactly
// what sendChat reads.
const ok = (content) => ({
  ok: true,
  status: 200,
  text: async () => JSON.stringify({ choices: [{ message: { content } }] }),
});
const fail = (status, body) => ({ ok: false, status, text: async () => body });

describe("sendChat", () => {
  it("cevabın metnini döndürür", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok("merhaba")));
    const text = await sendChat({ key: "k", model: "grok-4.3", messages: [] });
    expect(text).toBe("merhaba");
  });

  it("anahtarı Authorization başlığına koyar, boşlukları kırpar", async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok("ok"));
    vi.stubGlobal("fetch", fetchMock);
    await sendChat({ key: "  xai-123  ", model: "grok-4.3", messages: [] });
    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer xai-123");
  });

  it("model ve mesajları gövdeye koyar", async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok("ok"));
    vi.stubGlobal("fetch", fetchMock);
    await sendChat({
      key: "k",
      model: " grok-4.3 ",
      messages: [{ role: "user", content: "selam" }],
    });
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(init.body)).toEqual({
      model: "grok-4.3",
      messages: [{ role: "user", content: "selam" }],
    });
  });

  it("200 dışında gövdeyi olduğu gibi hataya taşır", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(fail(404, '{"error":"model yok"}')));
    await expect(sendChat({ key: "k", model: "yok", messages: [] })).rejects.toThrow(
      'HTTP 404 — {"error":"model yok"}'
    );
  });

  it("ağ hatasını yutmaz", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    await expect(sendChat({ key: "k", model: "m", messages: [] })).rejects.toThrow(
      "Failed to fetch"
    );
  });
});
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `cd prompt-chat && npm test`
Expected: FAIL — `Failed to resolve import "./api.js"`.

- [ ] **Step 3: `prompt-chat/src/api.js`'i yaz**

```js
import { toRequestBody, formatHttpError } from "./chat.js";

const ENDPOINT = "https://api.x.ai/v1/chat/completions";

// The only place in the app that touches the network. Reaching xAI straight from the browser works
// because it allows cross-origin requests; a proxy here would add a second thing to run and solve
// nothing.
export async function sendChat({ key, model, messages }) {
  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${key.trim()}`,
    },
    body: JSON.stringify(toRequestBody(messages, model.trim())),
  });

  const raw = await res.text();
  if (!res.ok) throw new Error(formatHttpError(res.status, raw));
  return JSON.parse(raw).choices[0].message.content;
}
```

- [ ] **Step 4: Testin geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 5 yeni test, toplam 15.

- [ ] **Step 5: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/src/api.js prompt-chat/src/api.test.js
git commit -m "feat(prompt-chat): xAI chat completions client"
```

---

### Task 4: Sohbet — gönder, cevap al, hatayı göster

Arayüz bağlanır: mesaj yazılır, cevap düşer, beklerken buton kapanır, hata kırmızı satır olur.

**Files:**
- Create: `prompt-chat/src/Message.jsx`
- Modify: `prompt-chat/src/App.jsx` — Task 1'in iskeletine sohbet durumu eklenir
- Test: `prompt-chat/src/App.test.jsx` — Task 1'in testlerine yeni blok eklenir

**Interfaces:**
- Consumes: Task 3'ün `sendChat({key, model, messages})`; Task 1'in `App` iskeleti ve `.chat` / `.msg` / `.role` / `.body` CSS sınıfları.
- Produces: `Message({ role, content })` (default export) — `role` `"user" | "assistant" | "error"`. Task 5 bunu genişletir.

- [ ] **Step 1: Düşen testleri yaz — `App.test.jsx`'in sonuna ekle**

Dosyanın en üstündeki import satırı şununla değiştirilir:

```jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App.jsx";
```

Dosyanın sonuna eklenir:

```jsx
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
```

- [ ] **Step 2: Testlerin düştüğünü gör**

Run: `cd prompt-chat && npm test`
Expected: FAIL — `Unable to find an element with the placeholder text: /Mesaj yaz/`.

- [ ] **Step 3: `prompt-chat/src/Message.jsx`'i yaz**

```jsx
const ROLE_LABEL = { user: "Sen", assistant: "Grok", error: "Hata" };

export default function Message({ role, content }) {
  return (
    <div className={`msg ${role}`}>
      <div className="role">{ROLE_LABEL[role]}</div>
      {/* A JSX child, never dangerouslySetInnerHTML: the reply is text to be copied, not markup. */}
      <div className="body">{content}</div>
    </div>
  );
}
```

- [ ] **Step 4: `App.jsx`'i sohbetle genişlet**

`import` satırları şununla değiştirilir:

```jsx
import { useEffect, useRef, useState } from "react";
import Message from "./Message.jsx";
import { sendChat } from "./api.js";
```

`export default function App() { … }` bloğunun **tamamı** şununla değiştirilir. Üstündeki `DEFAULT_MODEL` sabiti ve `usePersisted` fonksiyonu Task 1'deki hâliyle **olduğu gibi kalır**:

```jsx
export default function App() {
  const [apiKey, setApiKey] = usePersisted("xai_key", "");
  const [model, setModel] = usePersisted("xai_model", DEFAULT_MODEL);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const chatRef = useRef(null);

  useEffect(() => {
    const el = chatRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  async function send() {
    const text = draft.trim();
    if (!text || pending) return;

    // The request carries the new message too, so the array is built first and used for both.
    const asked = [...messages, { role: "user", content: text }];
    setMessages(asked);
    setDraft("");
    setPending(true);
    try {
      const reply = await sendChat({ key: apiKey, model, messages: asked });
      setMessages([...asked, { role: "assistant", content: reply }]);
    } catch (err) {
      // Covers a non-200 response and a request that never left: network, CORS, unparsable body.
      setMessages([...asked, { role: "error", content: err.message }]);
    }
    setPending(false);
  }

  return (
    <div className="app">
      <header>
        <input
          type="password"
          placeholder="xAI API anahtarı"
          autoComplete="off"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
        />
        <input
          className="model"
          placeholder="model"
          autoComplete="off"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        />
      </header>

      <main className="chat" ref={chatRef}>
        {messages.map((m, i) => (
          <Message key={i} role={m.role} content={m.content} />
        ))}
      </main>

      <footer>
        <textarea
          placeholder="Mesaj yaz — Enter gönderir, Shift+Enter alt satıra geçer"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
        />
        <button onClick={send} disabled={pending}>
          {pending ? "…" : "Gönder"}
        </button>
      </footer>
    </div>
  );
}
```

- [ ] **Step 5: Testlerin geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 9 yeni test, toplam 24.

- [ ] **Step 6: Tarayıcı kontrolü**

Run: `cd prompt-chat && npm run dev`

Anahtarını yapıştır, "merhaba" yazıp Enter'a bas. Beklenen: mesajın "Sen" etiketiyle görünür, buton "…" olur, cevap "Grok" etiketiyle düşer. Ardından "az önce ne dedim?" sor → bağlamı hatırlar. Sayfayı yenile → sohbet boş, anahtar dolu.

- [ ] **Step 7: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/src/
git commit -m "feat(prompt-chat): chat flow with pending state and verbatim errors"
```

---

### Task 5: Kopyala

Aracın varlık sebebi olan döngünün son adımı: üret → kopyala → `api.ipynb`'ye yapıştır.

**Files:**
- Modify: `prompt-chat/src/Message.jsx`
- Test: `prompt-chat/src/Message.test.jsx` (yeni)

**Interfaces:**
- Consumes: Task 4'ün `Message({role, content})`'ı; Task 1'in `.copy` CSS sınıfı.
- Produces: Değişiklik yok — `Message` artık `role === "assistant"` olduğunda bir **Kopyala** butonu çizer.

- [ ] **Step 1: Düşen testi yaz — `prompt-chat/src/Message.test.jsx`**

```jsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import Message from "./Message.jsx";

const copyButton = () => screen.getByRole("button", { name: /Kopyala/ });

// Replacing the whole navigator object would drop userAgent and friends that React and Testing
// Library read; defining just the one property keeps the rest intact.
function stubClipboard(writeText) {
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
}

describe("Kopyala", () => {
  it("yalnız cevaplarda görünür", () => {
    const { rerender } = render(<Message role="user" content="selam" />);
    expect(screen.queryByRole("button")).toBeNull();

    rerender(<Message role="error" content="HTTP 500 — patladı" />);
    expect(screen.queryByRole("button")).toBeNull();

    rerender(<Message role="assistant" content="merhaba" />);
    expect(copyButton()).toBeTruthy();
  });

  it("metnin tamamını, satır sonlarıyla birlikte panoya yazar", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    stubClipboard(writeText);

    // A JSX expression, not an attribute string: content="a\nb" would pass a literal backslash-n.
    const iki = "birinci satır\nikinci satır";
    render(<Message role="assistant" content={iki} />);
    fireEvent.click(copyButton());

    await waitFor(() => expect(writeText).toHaveBeenCalledWith(iki));
  });

  it("kopyalayınca geri bildirim verir", async () => {
    stubClipboard(vi.fn().mockResolvedValue(undefined));

    render(<Message role="assistant" content="merhaba" />);
    fireEvent.click(copyButton());

    expect(await screen.findByRole("button", { name: "Kopyalandı" })).toBeTruthy();
  });

  it("pano reddederse tarayıcının kendi metnini gösterir", async () => {
    stubClipboard(vi.fn().mockRejectedValue(new Error("izin yok")));

    render(<Message role="assistant" content="merhaba" />);
    fireEvent.click(copyButton());

    expect(await screen.findByRole("button", { name: /izin yok/ })).toBeTruthy();
  });
});
```

- [ ] **Step 2: Testin düştüğünü gör**

Run: `cd prompt-chat && npm test`
Expected: FAIL — `Unable to find an accessible element with the role "button"`.

- [ ] **Step 3: `Message.jsx`'e Kopyala'yı ekle**

Dosyanın tamamı şununla değiştirilir:

```jsx
import { useState } from "react";

const ROLE_LABEL = { user: "Sen", assistant: "Grok", error: "Hata" };

export default function Message({ role, content }) {
  const [label, setLabel] = useState("Kopyala");

  async function copy() {
    try {
      await navigator.clipboard.writeText(content);
      setLabel("Kopyalandı");
    } catch (err) {
      // Clipboard access needs a secure context. http://localhost is one, so this should not fire
      // in normal use; if it does, the browser's own reason is more useful than a guess.
      setLabel(`Kopyalanamadı: ${err.message}`);
    }
    setTimeout(() => setLabel("Kopyala"), 1500);
  }

  return (
    <div className={`msg ${role}`}>
      <div className="role">{ROLE_LABEL[role]}</div>
      {/* A JSX child, never dangerouslySetInnerHTML: the reply is text to be copied, not markup. */}
      <div className="body">{content}</div>
      {role === "assistant" && (
        <button className="copy" onClick={copy}>
          {label}
        </button>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Testlerin geçtiğini gör**

Run: `cd prompt-chat && npm test`
Expected: PASS — 4 yeni test, toplam 28.

- [ ] **Step 5: Tarayıcı kontrolü**

Bir mesaj gönder, cevabın altındaki **Kopyala**'ya bas → yazı kısa süre "Kopyalandı" olur. Boş bir dosyaya yapıştır → metin birebir aynı, satır sonları dahil.

- [ ] **Step 6: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/src/Message.jsx prompt-chat/src/Message.test.jsx
git commit -m "feat(prompt-chat): copy button on each reply"
```

---

### Task 6: README ve CLAUDE.md

Araç repo'da belgelenir — kural: her araç kendi klasöründe durur ve `CLAUDE.md`'de bir bölümü olur.

**Files:**
- Create: `prompt-chat/README.md`
- Modify: `CLAUDE.md` — giriş cümlesi ve yeni bölüm

**Interfaces:**
- Consumes: Task 1-5'in bitmiş uygulaması.
- Produces: —

- [ ] **Step 1: `prompt-chat/README.md`'i oluştur**

````markdown
# prompt-chat

Grok ile düz sohbet eden bir deney tezgâhı. Amaç: WAN 2.2 T2V prompt'larını üretirken
modelin ne kadar işe yaradığını rahat denemek.

## Çalıştırma

```bash
cd prompt-chat
npm install     # bir kez
npm run dev     # http://localhost:5173
```

İlk açılışta üstteki alana [console.x.ai](https://console.x.ai)'dan aldığın API anahtarını
yapıştır. Anahtar tarayıcının `localStorage`'ında kalır, kaynağa yazılmaz; bu yüzden kod
rahatça commit edilebilir. (`.env` de kullanılmaz — Vite `VITE_` ile başlayan değişkenleri
derlenmiş çıktıya gömer, yani saklamış olmazdın.)

Yanındaki alan model adıdır (varsayılan `grok-4.3`). Konsolda görünen id farklıysa buradan
düzelt — kod değiştirmen gerekmez. Başka bir modele geçmek de aynı kutu.

## Kullanım

Enter gönderir, Shift+Enter alt satıra geçer. Her cevabın altındaki **Kopyala** metnin
tamamını panoya alır; oradan `api.ipynb`'nin `PROMPTS` listesine yapıştırırsın.

Sohbet bellekte durur: sayfayı yenilersen sıfırlanır. Anahtar ve model adı kalır.

System prompt yoktur — talimatını ilk mesaj olarak sen yapıştırırsın. Böylece talimatı
değiştirmek için kodu açman gerekmez; denenen şey modelin yanı sıra talimatın kendisi de.

## Test

```bash
npm test
```

Vitest, jsdom ortamında koşar: tarayıcı açılmaz, ağa çıkılmaz, `fetch` sahtelenir.

## Sınırlar

Bu bir tezgâh, ürün değil: tek kullanıcı, `localhost`, kalıcılık yok, deploy yok.
`dist/` repo'ya girmez. Grok'un çıktısı yeterince iyiyse aynı mantık Queen Editor'ın içine
yazılır ve bu araç düşer.
````

- [ ] **Step 2: `CLAUDE.md`'nin giriş cümlesini güncelle**

Dosyanın başındaki şu cümle:

```markdown
Internal tools monorepo. Each tool lives in its own subfolder; currently two tools: **collab-toolbox** and **queen-editor**. Tool documentation lives in this file — when adding a tool, create a subfolder and add a section here.
```

şununla değiştirilir:

```markdown
Internal tools monorepo. Each tool lives in its own subfolder; currently three tools: **collab-toolbox**, **queen-editor** and **prompt-chat**. Tool documentation lives in this file — when adding a tool, create a subfolder and add a section here.
```

- [ ] **Step 3: `CLAUDE.md`'nin sonuna yeni bölüm ekle**

Dosyanın en altına, `## queen-editor` bölümünden sonra:

```markdown
## prompt-chat — Grok sohbet tezgâhı

A small React chat UI for drafting WAN 2.2 T2V prompts with Grok: [prompt-chat/](prompt-chat/).
`npm run dev`, then `http://localhost:5173`. It calls `api.x.ai` straight from the browser, which
works because xAI allows cross-origin requests — there is no backend and adding one would solve
nothing.

**A bench, not a product.** One user, `localhost`, nothing persisted, never deployed. It shares no
code or folder with any other tool here. If Grok's output proves good enough, the same logic gets
written into Queen Editor and this tool goes away — which is why it uses Queen Editor's exact
frontend stack and versions (React 18.3 / Vite 5.4 / Vitest 3.2): that move should be a copy, not a
rewrite.

**`dist/` is not committed here.** Queen Editor commits its build because Colab never runs npm; this
tool never reaches Colab, so the rule does not carry over.

The API key and the model name live in the browser's `localStorage`, entered through fields on the
page — never in the source, and never in `.env` (Vite inlines `VITE_` variables into the build, so
that would not hide anything). Keep it that way: a key committed into the source stays in git
history and has to be revoked.

Layering: `chat.js` is pure (no network, no React), `api.js` holds the only `fetch`, `App.jsx` and
`Message.jsx` only render. `npm test` runs Vitest against jsdom with `fetch` stubbed. Design
decisions:
[docs/superpowers/specs/2026-08-08-prompt-chat-design.md](docs/superpowers/specs/2026-08-08-prompt-chat-design.md).
```

- [ ] **Step 4: Kontrol**

`prompt-chat/README.md`'yi baştan sona oku ve yazdığı her adımı sırayla uygula — kur, çalıştır, anahtarı gir, mesaj gönder, kopyala, `npm test`. Her cümle gerçekle uyuşuyor mu? Uyuşmayan varsa **README düzeltilir**, kod değil.

`CLAUDE.md`'de araç sayısının üç olduğunu ve yeni bölümün linklerinin çalıştığını doğrula.

- [ ] **Step 5: Commit (kullanıcı onayı bekler)**

```bash
git add prompt-chat/README.md CLAUDE.md
git commit -m "docs(prompt-chat): README and CLAUDE.md entry"
```

---

## Bitince: spec'in elle doğrulama listesi

28 otomatik test yeşil olsa bile üç şeyi görmezler: gerçek ağ, gerçek pano, gerçek model. Spec'in
[6. bölümündeki](../specs/2026-08-08-prompt-chat-design.md) altı madde baştan sona bir kez geçilir.

Asıl sınav 5. madde: uzun bir WAN talimatını ilk mesaj olarak yapıştır (Shift+Enter ile çok
satırlı), ardından bir sahne özeti gönder → talimata uygun bir prompt gelmeli; üçüncü mesajda "daha
kısa yaz" de → bağlamı koruduğu görülmeli.

Bu tur, "Grok bu iş için yeterli mi" sorusunun ilk gerçek cevabıdır — aracın yapılma sebebi de o.
